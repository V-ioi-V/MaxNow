import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

import probe_ballet_session as probe


SESSION_A = "a" * 32
SESSION_B = "b" * 32
USER_AGENT = "Synthetic-WeChat-Test-Agent"


def config_for(log_path, *, once=False, duration_seconds=120):
    return probe.Config(
        api_url=probe.ALLOWED_API_URL,
        credential_file=Path(log_path).with_name("unused-credential.json"),
        log_path=Path(log_path),
        interval_seconds=60,
        duration_seconds=duration_seconds,
        timeout_seconds=3,
        retries=0,
        once=once,
        dry_run=False,
    )


class BalletSessionProbeTests(unittest.TestCase):
    def test_zero_duration_selects_indefinite_mode(self):
        with mock.patch.dict(
            os.environ, {"WENDA_DURATION_SECONDS": "0"}, clear=False
        ):
            self.assertIsNone(probe.env_duration_seconds())

    def test_url_allowlist_is_exact(self):
        probe.validate_read_only_url(probe.ALLOWED_API_URL)
        rejected = (
            probe.ALLOWED_API_URL + "?member=1",
            probe.ALLOWED_API_URL + "/",
            probe.ALLOWED_API_URL.replace("/54114/430", "/54115/430"),
            probe.ALLOWED_API_URL.replace("gm.wendaosoft.com", "gm.wendaosoft.com:444"),
            "https://gm.wendaosoft.com/gm/weixin/classtable/do_addbook/1",
        )
        for url in rejected:
            with self.subTest(url=url), self.assertRaises(ValueError):
                probe.validate_read_only_url(url)

    def test_credentials_accept_only_php_session(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "credential.json"
            path.write_text(
                json.dumps(
                    {
                        "authorization": "",
                        "cookies": {"PHPSESSID": SESSION_A},
                        "metadata": {"source": "synthetic-test"},
                        "referer": "ignored",
                        "user_agent": USER_AGENT,
                    }
                ),
                encoding="utf-8",
            )
            credentials = probe.load_credentials(path)
            self.assertEqual(credentials.session_id, SESSION_A)
            headers = probe.request_headers(credentials)
            self.assertEqual(headers["Cookie"], f"PHPSESSID={SESSION_A}")
            self.assertEqual(headers["Referer"], probe.ALLOWED_REFERER)

            data = json.loads(path.read_text(encoding="utf-8"))
            data["cookies"]["other"] = "not-allowed"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                probe.load_credentials(path)

            data["cookies"] = {"PHPSESSID": SESSION_A}
            data["authorization"] = "Bearer not-allowed"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                probe.load_credentials(path)

    def test_opener_disables_environment_proxies(self):
        opener = probe.build_http_opener()
        proxy_handlers = [
            handler
            for handler in opener.handlers
            if isinstance(handler, urllib.request.ProxyHandler)
        ]
        self.assertTrue(
            all(handler.proxies == {} for handler in proxy_handlers)
        )

    def test_login_classification_is_fail_closed(self):
        marker_body = " ".join(probe.AUTHENTICATED_HTML_MARKERS).encode()
        authenticated = probe.ResponseSnapshot(200, {}, marker_body, None, 1)
        self.assertEqual(
            probe.classify_response(
                authenticated, probe.AUTHENTICATED_HTML_MARKERS
            )[0],
            "authenticated",
        )

        ordinary_html = probe.ResponseSnapshot(200, {}, b"<html>ok</html>", None, 1)
        self.assertEqual(
            probe.classify_response(
                ordinary_html, probe.AUTHENTICATED_HTML_MARKERS
            )[0],
            "unknown",
        )

        generic_json = probe.ResponseSnapshot(200, {}, b'{"code":0}', None, 1)
        self.assertEqual(
            probe.classify_response(
                generic_json, probe.AUTHENTICATED_HTML_MARKERS
            )[0],
            "unknown",
        )

        oauth_redirect = probe.ResponseSnapshot(
            302,
            {
                "Location": (
                    "https://open.weixin.qq.com/connect/oauth2/authorize"
                    "?appid=synthetic"
                )
            },
            b"",
            None,
            1,
        )
        self.assertEqual(
            probe.classify_response(
                oauth_redirect, probe.AUTHENTICATED_HTML_MARKERS
            )[0],
            "expired",
        )

    def test_rotation_is_in_memory_and_logs_never_contain_session(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "probe.jsonl"
            credentials = probe.Credentials(SESSION_A, USER_AGENT)
            marker_body = " ".join(probe.AUTHENTICATED_HTML_MARKERS).encode()
            snapshot = probe.ResponseSnapshot(
                200,
                {"Set-Cookie": f"PHPSESSID={SESSION_B}; Path=/; HttpOnly"},
                marker_body,
                None,
                1,
            )
            with mock.patch.object(probe, "perform_request", return_value=snapshot):
                result = probe.run(
                    config_for(log_path, once=True), credentials
                )
            self.assertEqual(result, 0)
            self.assertEqual(credentials.session_id, SESSION_B)

            log_text = log_path.read_text(encoding="utf-8")
            self.assertNotIn(SESSION_A, log_text)
            self.assertNotIn(SESSION_B, log_text)
            records = [json.loads(line) for line in log_text.splitlines()]
            sample = next(record for record in records if "sample" in record)
            self.assertTrue(sample["session_changed"])
            self.assertEqual(sample["set_cookie_names"], ["PHPSESSID"])
            if os.name != "nt":
                self.assertEqual(
                    stat.S_IMODE(log_path.stat().st_mode), 0o600
                )

    def test_three_network_errors_stop_the_probe(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "network.jsonl"
            snapshot = probe.ResponseSnapshot(
                None, {}, b"", "TimeoutError", 1
            )
            with (
                mock.patch.object(
                    probe, "scheduled_offsets", return_value=[0, 0, 0]
                ),
                mock.patch.object(
                    probe, "perform_request", return_value=snapshot
                ),
            ):
                result = probe.run(
                    config_for(log_path),
                    probe.Credentials(SESSION_A, USER_AGENT),
                )
            self.assertEqual(result, 3)
            records = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(
                records[-1]["event"], "stopped_consecutive_unknown"
            )
            self.assertEqual(
                records[-1]["last_login_state"], "network_error"
            )

    def test_indefinite_mode_still_stops_after_three_unknown_results(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "indefinite.jsonl"
            snapshot = probe.ResponseSnapshot(
                None, {}, b"", "TimeoutError", 1
            )
            with (
                mock.patch.object(
                    probe, "perform_request", return_value=snapshot
                ),
                mock.patch.object(probe.time, "sleep"),
                mock.patch.object(
                    probe.time,
                    "monotonic",
                    side_effect=[0, 0, 0, 60, 60, 120, 120],
                ),
            ):
                result = probe.run(
                    config_for(log_path, duration_seconds=None),
                    probe.Credentials(SESSION_A, USER_AGENT),
                )
            self.assertEqual(result, 3)
            records = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertIsNone(records[0]["duration_seconds"])
            self.assertEqual(
                records[-1]["event"], "stopped_consecutive_unknown"
            )

    def test_thirty_day_schedule_has_expected_sample_count(self):
        offsets = probe.scheduled_offsets(30 * 86_400, 600)
        self.assertEqual(len(offsets), 4_321)
        self.assertEqual(offsets[0], 0)
        self.assertEqual(offsets[-1], 30 * 86_400)

    def test_dry_run_does_not_open_credential_file(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "dry-run.jsonl"
            environment = os.environ.copy()
            environment.update(
                {
                    "WENDA_API_URL": probe.ALLOWED_API_URL,
                    "WENDA_CREDENTIAL_FILE": str(
                        Path(directory) / "does-not-exist.json"
                    ),
                    "WENDA_LOG_PATH": str(log_path),
                }
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(Path(__file__).with_name("probe_ballet_session.py")),
                    "--dry-run",
                ],
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            records = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(records[-1]["event"], "dry_run_complete")
            self.assertEqual(records[0]["session_fingerprints"], {})


if __name__ == "__main__":
    unittest.main()
