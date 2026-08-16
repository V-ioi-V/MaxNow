import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest import mock

import query_ballet_live as live
import sync_ballet as ballet
from test_sync_ballet import (
    attendance_summary_html,
    detail_html,
    index_html,
    membership_html,
    paginated_attendance_html,
    timetable_html,
)


NOW = datetime.fromisoformat("2026-07-28T08:00:00+08:00")


def write_fixture(root: Path) -> None:
    (root / "details").mkdir(parents=True)
    (root / "timetable").mkdir(parents=True)
    (root / "attendance.html").write_text(
        index_html(
            "上课记录",
            [("10001", "芭蕾L1.5", "2026-07-26", "已上课")],
        ),
        encoding="utf-8",
    )
    (root / "booking.html").write_text(
        index_html(
            "约课记录",
            [
                ("10002", "芭蕾L2", "2026-08-02", "已预约"),
                ("10003", "芭蕾L1", "2026-08-03", "已取消"),
            ],
        ),
        encoding="utf-8",
    )
    (root / "membership.html").write_text(membership_html(), encoding="utf-8")
    (root / "timetable" / "default.html").write_text(
        timetable_html().replace("<title>课程表</title>", "<title>每日课表</title>"),
        encoding="utf-8",
    )
    (root / "details" / "10001.html").write_text(
        detail_html(course="芭蕾L1.5", day="2026-07-26"),
        encoding="utf-8",
    )
    (root / "details" / "10002.html").write_text(
        detail_html(
            course="芭蕾L2",
            day="2026-08-02",
            time_text="17:30~19:00",
            status="已预约",
        ),
        encoding="utf-8",
    )


class BalletLiveQueryTests(unittest.TestCase):
    def test_systemd_credential_directory_is_used(self):
        with mock.patch.dict(
            "os.environ",
            {"CREDENTIALS_DIRECTORY": "/run/credentials/example.service"},
            clear=False,
        ):
            self.assertEqual(
                live.credential_path(None),
                Path("/run/credentials/example.service/wenda-session.json"),
            )

    def test_timetable_is_live_shaped_and_date_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root)
            result = live.run_query(
                ballet.FixtureSource(root),
                "timetable",
                date.fromisoformat("2026-07-28"),
                date.fromisoformat("2026-07-29"),
                NOW,
            )
        self.assertTrue(result["live"])
        self.assertEqual(result["source"], "wenda-live")
        self.assertEqual(result["requestsMade"], 2)
        self.assertEqual(len(result["data"]["days"]), 2)
        self.assertEqual(
            result["data"]["days"][0]["records"][0]["courseName"],
            "芭蕾L1-入门",
        )

    def test_bookings_attendance_and_membership_hide_source_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root)
            results = [
                live.run_query(
                    ballet.FixtureSource(root), "bookings", None, None, NOW
                ),
                live.run_query(
                    ballet.FixtureSource(root),
                    "attendance",
                    date.fromisoformat("2026-07-01"),
                    date.fromisoformat("2026-07-31"),
                    NOW,
                ),
                live.run_query(
                    ballet.FixtureSource(root), "membership", None, None, NOW
                ),
            ]
        serialized = json.dumps(results, ensure_ascii=False)
        for forbidden in (
            "PHPSESSID",
            "sourceRecordId",
            "stableKey",
            "bookingRecordId",
            "attendanceRecordId",
            "10001",
            "10002",
        ):
            self.assertNotIn(forbidden, serialized)
        self.assertEqual(
            results[0]["data"]["records"][0]["bookingStatus"],
            "booked",
        )
        self.assertEqual(
            results[1]["data"]["records"][0]["attendanceStatus"],
            "attended",
        )
        self.assertEqual(results[2]["data"]["cards"][0]["remainingClasses"], 39)

    def test_invalid_or_large_ranges_fail_closed(self):
        source = ballet.FixtureSource(Path("/nonexistent"))
        with self.assertRaises(ballet.SyncFailure):
            live.run_query(
                source,
                "timetable",
                date.fromisoformat("2026-07-01"),
                date.fromisoformat("2026-07-15"),
                NOW,
            )
        with self.assertRaises(ballet.SyncFailure):
            live.run_query(
                source,
                "attendance",
                date.fromisoformat("2026-08-01"),
                date.fromisoformat("2026-07-01"),
                NOW,
            )

    def test_paginated_attendance_allows_recent_range_but_not_summary_only_row(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root)
            (root / "attendance-pages").mkdir()
            (root / "attendance.html").write_text(
                paginated_attendance_html(
                    [("10001", "芭蕾L1.5", "2026-07-26", "已上课")],
                    2,
                ),
                encoding="utf-8",
            )
            (root / "attendance-pages" / "1.html").write_text(
                attendance_summary_html(
                    [("软开专项【前后腿】", "2026-06-01")]
                ),
                encoding="utf-8",
            )
            recent = live.run_query(
                ballet.FixtureSource(root),
                "attendance",
                date.fromisoformat("2026-07-01"),
                date.fromisoformat("2026-07-31"),
                NOW,
            )
            with self.assertRaises(ballet.SyncFailure) as all_records:
                live.run_query(
                    ballet.FixtureSource(root), "attendance", None, None, NOW
                )

        self.assertEqual(len(recent["data"]["records"]), 1)
        self.assertEqual(recent["requestsMade"], 3)
        self.assertEqual(all_records.exception.code, "source_changed")

    def test_cli_fixture_writes_no_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root)
            before = sorted(str(path.relative_to(root)) for path in root.rglob("*"))
            completed = subprocess.run(
                [
                    sys.executable,
                    str(Path(live.__file__)),
                    "timetable",
                    "--from-date",
                    "2026-07-28",
                    "--through-date",
                    "2026-07-28",
                    "--fixture-dir",
                    str(root),
                    "--now",
                    NOW.isoformat(),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            after = sorted(str(path.relative_to(root)) for path in root.rglob("*"))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(before, after)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["live"])
        self.assertEqual(payload["fetchedAt"], NOW.isoformat(timespec="seconds"))


if __name__ == "__main__":
    unittest.main()
