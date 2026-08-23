from __future__ import annotations

import importlib.util
import unittest
from datetime import datetime
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("ballet_week_closeout.py")
SPEC = importlib.util.spec_from_file_location("ballet_week_closeout", MODULE_PATH)
closeout = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(closeout)


def model(data_as_of="2026-08-29T12:00:00+08:00", auth="valid"):
    return {
        "dataAsOf": data_as_of,
        "sync": {"lastAttemptStatus": "success"},
        "authHealth": {"status": auth},
        "weeklyBrief": {
            "cycles": [
                {
                    "weekStart": "2026-08-24",
                    "weekEnd": "2026-08-30",
                    "lastCourseEndAt": "2026-08-29T12:30:00+08:00",
                    "refreshAt": "2026-08-29T12:40:00+08:00",
                    "generateAt": "2026-08-29T12:50:00+08:00",
                }
            ]
        },
    }


class WeekCloseoutTests(unittest.TestCase):
    def test_waits_until_ten_minutes_after_last_course(self):
        decision = closeout.evaluate_closeout(
            model(), {}, datetime.fromisoformat("2026-08-29T12:39:59+08:00")
        )
        self.assertEqual((decision["action"], decision["reason"]), ("none", "not_due"))

    def test_requests_refresh_when_due_and_source_is_old(self):
        decision = closeout.evaluate_closeout(
            model(), {}, datetime.fromisoformat("2026-08-29T12:40:00+08:00")
        )
        self.assertEqual((decision["action"], decision["reason"]), ("refresh", "closeout_due"))

    def test_fresh_source_completes_without_starting_sync(self):
        decision = closeout.evaluate_closeout(
            model("2026-08-29T12:40:05+08:00"),
            {},
            datetime.fromisoformat("2026-08-29T12:40:10+08:00"),
        )
        self.assertEqual((decision["action"], decision["reason"]), ("complete", "already_refreshed"))

    def test_auth_failure_is_fail_closed(self):
        payload = model(auth="needs_login")
        payload["sync"]["lastAttemptStatus"] = "auth_required"
        decision = closeout.evaluate_closeout(
            payload, {}, datetime.fromisoformat("2026-08-29T12:45:00+08:00")
        )
        self.assertEqual((decision["action"], decision["reason"]), ("none", "auth_required"))

    def test_attempt_limit_prevents_unbounded_retries(self):
        state = {
            "cycleKey": "2026-08-24|2026-08-29T12:30:00+08:00",
            "attempts": 3,
        }
        decision = closeout.evaluate_closeout(
            model(), state, datetime.fromisoformat("2026-08-29T13:00:00+08:00")
        )
        self.assertEqual((decision["action"], decision["reason"]), ("none", "attempt_limit"))


if __name__ == "__main__":
    unittest.main()
