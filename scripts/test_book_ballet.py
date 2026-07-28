import json
import unittest

import book_ballet as booking
import sync_ballet as ballet
from test_sync_ballet import detail_html, index_html, timetable_html


TARGET = {
    "date": "2026-07-30",
    "startTime": "20:15",
    "endTime": "21:15",
    "courseName": "肌肉素质",
    "teacher": "戴俊瑶",
    "venue": "小教室",
}
TARGET_2 = {**TARGET, "date": "2026-07-31"}
TARGET_3 = {**TARGET, "date": "2026-08-01"}


def timetable_with_booking_control() -> str:
    return timetable_html(
        course=TARGET["courseName"],
        time_text=f"{TARGET['startTime']} ~ {TARGET['endTime']}",
        teacher=TARGET["teacher"],
        venue=TARGET["venue"],
        status="4 / 10",
    ).replace(
        "</div></div></body>",
        (
            '<button class="bookbtn" courseid="70001" '
            'classtableid="70002">预约</button>'
            "</div></div></body>"
        ),
    ).replace(
        "</body>",
        (
            "<script>"
            "customerid=80001;"
            f'var a="{booking.CARD_TYPE_PATH}";'
            f'var b="{booking.CHECK_RULES_PREFIX}80001";'
            f'var c="{booking.BOOKING_SUBMIT_PATH}";'
            f'var d="{booking.GET_USING_CARD_PATH}";'
            "</script></body>"
        ),
    )


class FakeSource:
    def __init__(self):
        self.request_count = 0
        self.post_count = 0
        self.mutation_count = 0
        self.active_date = TARGET["date"]
        self.posted_dates = set()
        self.fail_rules_after_first_mutation = False

    def request(self, path, expected_marker):
        self.request_count += 1
        if path.startswith(ballet.TIMETABLE_PATH):
            self.active_date = path.rsplit("/", 1)[-1]
            return timetable_with_booking_control()
        if path == ballet.BOOKING_PATH:
            rows = [
                (
                    str(90001 + index),
                    TARGET["courseName"],
                    day,
                    "已预约",
                )
                for index, day in enumerate(sorted(self.posted_dates))
            ]
            return index_html("约课记录", rows)
        if "/bookrecordone/" in path:
            source_id = int(path.rsplit("/", 1)[-1])
            day = sorted(self.posted_dates)[source_id - 90001]
            return detail_html(
                course=TARGET["courseName"],
                day=day,
                time_text=f"{TARGET['startTime']}~{TARGET['endTime']}",
                teacher=TARGET["teacher"],
                status="已预约",
            ).replace("测试教室", TARGET["venue"])
        raise AssertionError(path)

    def post_fields(self, path, fields, mutation):
        self.request_count += 1
        self.post_count += 1
        if path == booking.CARD_TYPE_PATH:
            return json.dumps([{"id": 90002, "status": "OPEN"}])
        if path.startswith(booking.CHECK_RULES_PREFIX):
            if self.fail_rules_after_first_mutation and self.mutation_count:
                return json.dumps("BLOCKED")
            return json.dumps("OK")
        if path == booking.BOOKING_SUBMIT_PATH and mutation:
            self.mutation_count += 1
            self.posted_dates.add(self.active_date)
            self.last_post = (path, dict(fields))
            return json.dumps(91000)
        raise AssertionError((path, fields, mutation))


class BalletBookingTests(unittest.TestCase):
    def test_dry_run_is_read_only_and_redacted(self):
        source = FakeSource()
        result = booking.run(source, [TARGET], execute=False)
        serialized = json.dumps(result, ensure_ascii=False)
        self.assertEqual(source.mutation_count, 0)
        self.assertEqual(result["mutationAttempts"], 0)
        self.assertEqual(result["data"]["records"][0]["status"], "ready")
        self.assertNotIn("70001", serialized)
        self.assertNotIn("70002", serialized)
        self.assertNotIn("80001", serialized)
        self.assertNotIn("90002", serialized)

    def test_execute_posts_once_and_verifies_booking(self):
        source = FakeSource()
        result = booking.run(source, [TARGET], execute=True)
        self.assertEqual(source.mutation_count, 1)
        self.assertEqual(result["mutationAttempts"], 1)
        self.assertEqual(result["postsMade"], 5)
        self.assertEqual(result["data"]["records"][0]["status"], "booked")
        self.assertEqual(
            result["data"]["records"][0]["bookingStatus"], "booked"
        )

    def test_execute_requires_explicit_confirmation(self):
        payload = json.dumps({"courses": [TARGET], "confirm": False})
        with self.assertRaises(booking.BookingFailure) as caught:
            booking.parse_request(payload, execute=True)
        self.assertEqual(caught.exception.code, "confirmation_required")

    def test_batch_stops_after_first_execution_failure(self):
        source = FakeSource()
        source.fail_rules_after_first_mutation = True
        result = booking.run(
            source,
            [TARGET, TARGET_2, TARGET_3],
            execute=True,
        )
        statuses = [record["status"] for record in result["data"]["records"]]
        self.assertEqual(statuses, ["booked", "rules_blocked", "not_attempted"])
        self.assertEqual(source.mutation_count, 1)
        self.assertEqual(result["status"], "stopped")

    def test_unknown_control_fails_closed_with_safe_diagnostic(self):
        source = FakeSource()
        original = source.request

        def without_control(path, marker):
            return original(path, marker).replace(
                'class="bookbtn"',
                'class="changedbtn" onclick="reserve(70001)"',
            )

        source.request = without_control
        with self.assertRaises(booking.BookingFailure) as caught:
            booking.run(source, [TARGET], execute=False)
        self.assertEqual(caught.exception.code, "source_changed")
        serialized = json.dumps(caught.exception.diagnostic)
        self.assertNotIn("70001", serialized)


if __name__ == "__main__":
    unittest.main()
