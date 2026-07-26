import json
import os
import stat
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import sync_ballet_session_status as status


NOW = datetime.fromisoformat("2026-07-26T22:50:00+08:00")
EXPERIMENT_START = "2026-07-26T19:07:15+08:00"
SCHEDULED_END = "2026-08-25T19:07:15+08:00"


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
            for record in records
        ),
        encoding="utf-8",
    )


def start_record(timestamp: str, interval: int, secret: str) -> dict:
    return {
        "event": "start",
        "run_id": f"secret-run-{secret}",
        "timestamp": timestamp,
        "api_host": "secret.example",
        "api_path": f"/secret/{secret}",
        "interval_seconds": interval,
        "session_fingerprints": {"cookie:PHPSESSID": secret},
    }


def sample_record(
    number: int,
    timestamp: str,
    *,
    login_state: str = "authenticated",
    status_code: int = 200,
    changed: bool = False,
    set_cookie: bool = False,
    attempts: int = 1,
    network_error=None,
    secret: str = "top-secret",
) -> dict:
    return {
        "sample": number,
        "timestamp": timestamp,
        "elapsed_seconds": number * 60,
        "http_status": status_code,
        "login_state": login_state,
        "attempts": attempts,
        "network_error": network_error,
        "session_changed": changed,
        "set_cookie": set_cookie,
        "set_cookie_names": ["PHPSESSID"] if set_cookie else [],
        "session_fingerprints": {"cookie:PHPSESSID": secret},
        "response_sha256": secret,
        "response_bytes": 999,
        "raw_body": secret,
    }


def terminal_record(event: str, timestamp: str) -> dict:
    return {"event": event, "timestamp": timestamp, "secret": "must-not-leak"}


def make_config(root: Path, *, current_phase: str = "v5-25m") -> dict:
    return {
        "schemaVersion": 1,
        "experimentStartedAt": EXPERIMENT_START,
        "scheduledEndAt": SCHEDULED_END,
        "currentPhase": current_phase,
        "phases": [
            {
                "key": "v3-10m",
                "unit": "probe-v3.service",
                "log": str((root / "v3.jsonl").resolve()),
                "intervalSeconds": 600,
                "handoffValidationSamples": 0,
            },
            {
                "key": "v4-20m",
                "unit": "probe-v4.service",
                "log": str((root / "v4.jsonl").resolve()),
                "intervalSeconds": 1200,
                "handoffValidationSamples": 1,
            },
            {
                "key": "v5-25m",
                "unit": "probe-v5.service",
                "log": str((root / "v5.jsonl").resolve()),
                "intervalSeconds": 1500,
                "handoffValidationSamples": 1,
            },
        ],
    }


def write_three_phases(root: Path) -> None:
    write_jsonl(
        root / "v3.jsonl",
        [
            start_record(EXPERIMENT_START, 600, "fingerprint-v3"),
            sample_record(1, "2026-07-26T19:07:15+08:00"),
            sample_record(2, "2026-07-26T19:17:16+08:00"),
        ],
    )
    write_jsonl(
        root / "v4.jsonl",
        [
            start_record(
                "2026-07-26T19:41:46+08:00", 1200, "fingerprint-v4"
            ),
            sample_record(1, "2026-07-26T19:41:47+08:00"),
            sample_record(2, "2026-07-26T20:01:47+08:00"),
        ],
    )
    write_jsonl(
        root / "v5.jsonl",
        [
            start_record(
                "2026-07-26T22:45:00+08:00", 1500, "fingerprint-v5"
            ),
            sample_record(1, "2026-07-26T22:45:01+08:00"),
        ],
    )


class BalletSessionStatusTests(unittest.TestCase):
    def test_three_phase_running_model_is_redacted_and_scheduled(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_three_phases(root)
            config = status.validate_config(make_config(root))
            model = status.build_public_model(
                config, now=NOW, service_state="active"
            )

            self.assertEqual(set(model), status.PUBLIC_KEYS)
            self.assertEqual(model["status"], "running")
            self.assertEqual(model["refreshIntervalMinutes"], 25)
            self.assertEqual(model["phaseSamples"], 1)
            self.assertEqual(model["totalSamples"], 5)
            self.assertEqual(
                model["phaseStartedAt"], "2026-07-26T22:45:00+08:00"
            )
            self.assertEqual(
                model["nextProbeAt"], "2026-07-26T23:10:00+08:00"
            )
            self.assertEqual(
                model["lastAuthenticatedAt"],
                "2026-07-26T22:45:01+08:00",
            )
            self.assertEqual(model["verifiedAliveSeconds"], 13066)
            self.assertIsNone(model["lastError"])

            serialized = json.dumps(model, ensure_ascii=False)
            for secret in (
                "fingerprint-v3",
                "fingerprint-v4",
                "fingerprint-v5",
                "top-secret",
                "secret.example",
                "/secret/",
                "run_id",
                "session_fingerprints",
                "response_sha256",
                "raw_body",
                "PHPSESSID=",
                str(root),
                "probe-v5.service",
            ):
                self.assertNotIn(secret, serialized)

    def test_delayed_probe_has_no_next_time(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_three_phases(root)
            config = status.validate_config(make_config(root))
            model = status.build_public_model(
                config,
                now=datetime.fromisoformat("2026-07-26T23:41:00+08:00"),
                service_state="active",
            )
            self.assertEqual(model["status"], "delayed")
            self.assertIsNone(model["nextProbeAt"])
            self.assertEqual(model["lastError"]["code"], "probe_delayed")

    def test_handoff_requires_configured_validation_samples(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_three_phases(root)
            payload = make_config(root)
            payload["phases"][-1]["handoffValidationSamples"] = 2
            model = status.build_public_model(
                status.validate_config(payload),
                now=NOW,
                service_state="active",
            )
            self.assertEqual(model["status"], "unknown")
            self.assertIsNone(model["nextProbeAt"])

    def test_identity_expiry_freezes_verified_duration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_three_phases(root)
            with (root / "v5.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        sample_record(
                            2,
                            "2026-07-26T23:10:01+08:00",
                            login_state="expired",
                            status_code=302,
                        )
                    )
                    + "\n"
                )
                handle.write(
                    json.dumps(
                        terminal_record(
                            "stopped_identity_expired",
                            "2026-07-26T23:10:01+08:00",
                        )
                    )
                    + "\n"
                )
            model = status.build_public_model(
                status.validate_config(make_config(root)),
                now=datetime.fromisoformat("2026-07-26T23:11:00+08:00"),
                service_state="inactive",
            )
            self.assertEqual(model["status"], "auth_required")
            self.assertEqual(model["verifiedAliveSeconds"], 13066)
            self.assertIsNone(model["nextProbeAt"])
            self.assertEqual(model["lastError"]["code"], "identity_expired")

    def test_clean_complete_beats_inactive_service(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_three_phases(root)
            with (root / "v5.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        sample_record(
                            2,
                            "2026-07-26T23:10:00+08:00",
                        )
                    )
                    + "\n"
                )
            with (root / "v5.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        terminal_record(
                            "complete", "2026-07-26T23:10:01+08:00"
                        )
                    )
                    + "\n"
                )
            payload = make_config(root)
            payload["scheduledEndAt"] = "2026-07-26T23:10:05+08:00"
            model = status.build_public_model(
                status.validate_config(payload),
                now=datetime.fromisoformat("2026-07-26T23:10:05+08:00"),
                service_state="inactive",
            )
            self.assertEqual(model["status"], "complete")
            self.assertIsNone(model["lastError"])
            self.assertIsNone(model["nextProbeAt"])

    def test_early_or_incomplete_complete_marker_is_not_trusted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_three_phases(root)
            with (root / "v5.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        terminal_record(
                            "complete", "2026-07-26T22:49:00+08:00"
                        )
                    )
                    + "\n"
                )
            model = status.build_public_model(
                status.validate_config(make_config(root)),
                now=NOW,
                service_state="inactive",
            )
            self.assertNotEqual(model["status"], "complete")
            self.assertEqual(
                model["lastError"]["code"], "invalid_completion"
            )

    def test_unknown_terminal_and_plain_stop_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_three_phases(root)
            config = status.validate_config(make_config(root))
            interrupted = status.build_public_model(
                config, now=NOW, service_state="inactive"
            )
            self.assertEqual(interrupted["status"], "interrupted")
            self.assertEqual(
                interrupted["lastError"]["code"], "probe_interrupted"
            )

            with (root / "v5.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        terminal_record(
                            "stopped_consecutive_unknown",
                            "2026-07-26T22:49:00+08:00",
                        )
                    )
                    + "\n"
                )
            inconclusive = status.build_public_model(
                config, now=NOW, service_state="inactive"
            )
            self.assertEqual(inconclusive["status"], "unknown")
            self.assertEqual(
                inconclusive["lastError"]["code"], "probe_inconclusive"
            )

    def test_network_failure_uses_a_controlled_public_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_three_phases(root)
            with (root / "v5.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        sample_record(
                            2,
                            "2026-07-26T23:10:01+08:00",
                            login_state="network_error",
                            status_code=599,
                            network_error="secret transport detail",
                        )
                    )
                    + "\n"
                )
            model = status.build_public_model(
                status.validate_config(make_config(root)),
                now=datetime.fromisoformat("2026-07-26T23:11:00+08:00"),
                service_state="active",
            )
            self.assertEqual(model["status"], "unknown")
            self.assertEqual(model["lastError"]["code"], "network_error")
            self.assertNotIn(
                "secret transport detail",
                json.dumps(model, ensure_ascii=False),
            )

    def test_malformed_record_types_do_not_crash_the_publisher(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_three_phases(root)
            with (root / "v5.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "event": [],
                            "timestamp": "2026-07-26T22:49:00+08:00",
                        }
                    )
                    + "\n"
                )
                malformed = sample_record(
                    2, "2026-07-26T22:49:01+08:00"
                )
                malformed["login_state"] = {}
                handle.write(json.dumps(malformed) + "\n")
            model = status.build_public_model(
                status.validate_config(make_config(root)),
                now=NOW,
                service_state="active",
            )
            self.assertEqual(model["status"], "unknown")
            self.assertEqual(
                model["lastError"]["code"], "source_log_invalid"
            )

    def test_config_interval_must_match_the_phase_start_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_three_phases(root)
            payload = make_config(root)
            payload["phases"][-1]["intervalSeconds"] = 1800
            model = status.build_public_model(
                status.validate_config(payload),
                now=NOW,
                service_state="active",
            )
            self.assertEqual(model["status"], "unknown")
            self.assertIsNone(model["nextProbeAt"])
            self.assertEqual(
                model["lastError"]["code"], "source_config_mismatch"
            )

    def test_wrapper_matches_json_and_existing_metadata_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_three_phases(root)
            output = root / "public" / "ballet-session.json"
            wrapper = root / "public" / "ballet-session.js"
            output.parent.mkdir()
            output.write_text("{}\n", encoding="utf-8")
            wrapper.write_text("window.OLD = {};\n", encoding="utf-8")
            if os.name != "nt":
                output.chmod(0o640)
                wrapper.chmod(0o644)
                before_output = output.stat()
                before_wrapper = wrapper.stat()

            model = status.publish(
                status.validate_config(make_config(root)),
                output,
                wrapper,
                now=NOW,
                service_state="active",
            )
            parsed = json.loads(output.read_text(encoding="utf-8"))
            wrapper_text = wrapper.read_text(encoding="utf-8")
            wrapped = json.loads(
                wrapper_text.split(" = ", 1)[1].removesuffix(";\n")
            )
            self.assertEqual(parsed, model)
            self.assertEqual(wrapped, model)

            if os.name != "nt":
                after_output = output.stat()
                after_wrapper = wrapper.stat()
                self.assertEqual(
                    stat.S_IMODE(after_output.st_mode), 0o640
                )
                self.assertEqual(
                    stat.S_IMODE(after_wrapper.st_mode), 0o644
                )
                self.assertEqual(after_output.st_uid, before_output.st_uid)
                self.assertEqual(after_output.st_gid, before_output.st_gid)
                self.assertEqual(after_wrapper.st_uid, before_wrapper.st_uid)
                self.assertEqual(after_wrapper.st_gid, before_wrapper.st_gid)

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_three_phases(root)
            output = root / "public" / "ballet-session.json"
            wrapper = root / "public" / "ballet-session.js"
            status.publish(
                status.validate_config(make_config(root)),
                output,
                wrapper,
                now=NOW,
                service_state="active",
                dry_run=True,
            )
            self.assertFalse(output.exists())
            self.assertFalse(wrapper.exists())

    def test_config_rejects_extra_fields_and_unsafe_units(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = make_config(root)
            payload["secret"] = "not allowed"
            with self.assertRaises(status.StatusPublishError):
                status.validate_config(payload)

            payload = make_config(root)
            payload["phases"][-1]["unit"] = "x.service;curl example"
            with self.assertRaises(status.StatusPublishError):
                status.validate_config(payload)

    @unittest.skipIf(os.name == "nt", "POSIX ownership and mode only")
    def test_root_only_config_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text("{}\n", encoding="utf-8")
            path.chmod(0o644)
            with self.assertRaises(status.StatusPublishError):
                status.assert_root_only_config(path)
            if os.geteuid() == 0:
                path.chmod(0o600)
                status.assert_root_only_config(path)


if __name__ == "__main__":
    unittest.main()
