import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import book_ballet as booking
import book_ballet_fast as fast
import sync_ballet as ballet
from test_sync_ballet import index_html, timetable_html


def config():
    return fast.load_config(
        Path(__file__).resolve().parents[1]
        / "config"
        / "ballet-booking-fast.json"
    )


class FakeFastSource:
    def __init__(
        self,
        unknown_on_mutation=0,
        timetable_failures=0,
        notopen_mutations=0,
    ):
        self.request_count = 0
        self.post_count = 0
        self.mutation_count = 0
        self.active_date = ""
        self.unknown_on_mutation = unknown_on_mutation
        self.timetable_failures = timetable_failures
        self.notopen_mutations = notopen_mutations

    def request(self, path, marker):
        self.request_count += 1
        if path.startswith(ballet.TIMETABLE_PATH):
            if self.timetable_failures:
                self.timetable_failures -= 1
                raise ballet.SyncFailure("network_error")
            self.active_date = path.rsplit("/", 1)[-1]
            day = datetime.fromisoformat(self.active_date).weekday()
            courses = [("软开", "18:45", "19:45", "王嘉豪" if day == 1 else "李俊")]
            if day in {1, 4}:
                courses.append(("芭蕾 L1", "19:45", "21:15", "王嘉豪"))
            pages = []
            for index, (course, start, end, teacher) in enumerate(courses, start=1):
                pages.append(
                    timetable_html(
                        course=course,
                        time_text=f"{start} ~ {end}",
                        teacher=teacher,
                        venue="大教室",
                        status="4 / 10",
                    ).replace(
                        "</div></div></body>",
                        (
                            f'<button class="bookbtn" courseid="7000{index}" '
                            f'classtableid="7100{index}">预约</button>'
                            "</div></div></body>"
                        ),
                    )
                )
            return "".join(pages).replace(
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
        if path == ballet.BOOKING_PATH:
            return index_html("约课记录", [])
        raise AssertionError(path)

    def post_fields(self, path, fields, mutation):
        self.request_count += 1
        self.post_count += 1
        if path == booking.CARD_TYPE_PATH:
            return json.dumps([{"id": 90002, "status": "OPEN"}])
        if path.startswith(booking.CHECK_RULES_PREFIX):
            return json.dumps("OK")
        if path == booking.BOOKING_SUBMIT_PATH and mutation:
            self.mutation_count += 1
            if self.mutation_count == self.unknown_on_mutation:
                return json.dumps({"changed": True})
            if self.notopen_mutations:
                self.notopen_mutations -= 1
                return json.dumps("NOTOPEN")
            return json.dumps(91000 + self.mutation_count)
        raise AssertionError((path, fields, mutation))


class FastBookingTests(unittest.TestCase):
    def setUp(self):
        self.release = datetime(
            2026, 8, 2, 14, 20, tzinfo=ballet.TIMEZONE
        )

    def test_targets_follow_permanent_priority(self):
        targets = fast.materialize_targets(config(), self.release)
        self.assertEqual(
            [target["key"] for target in targets],
            [
                "friday-soft-open",
                "friday-ballet-l1",
                "tuesday-soft-open",
                "tuesday-ballet-l1",
                "thursday-soft-open",
            ],
        )
        self.assertEqual(
            [target["date"] for target in targets],
            [
                "2026-08-07",
                "2026-08-07",
                "2026-08-04",
                "2026-08-04",
                "2026-08-06",
            ],
        )

    def test_fast_path_mutates_sequentially_then_verifies_once(self):
        source = FakeFastSource()
        result, state = fast.run_fast(
            source,
            config(),
            fast.default_state(),
            self.release,
            execute=True,
        )
        self.assertEqual(source.mutation_count, 5)
        self.assertEqual(
            [record["status"] for record in result["records"]],
            ["booked", "booked", "booked", "booked", "booked"],
        )
        self.assertEqual(state["totalBooked"], 5)
        self.assertEqual(state["totalRuns"], 1)
        self.assertEqual(result["requestsMade"], 21)

    def test_unknown_result_does_not_block_remaining_courses(self):
        source = FakeFastSource(unknown_on_mutation=1)
        result, state = fast.run_fast(
            source,
            config(),
            fast.default_state(),
            self.release,
            execute=True,
            sleeper=lambda _: None,
        )
        self.assertEqual(
            [record["status"] for record in result["records"]],
            [
                "unknown_result",
                "booked",
                "booked",
                "booked",
                "booked",
            ],
        )
        self.assertEqual(source.mutation_count, 5)
        self.assertEqual(result["records"][0]["attempts"], 1)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(state["totalBooked"], 4)

    def test_retries_transient_preflight_three_times_then_books(self):
        source = FakeFastSource(timetable_failures=3)
        result, state = fast.run_fast(
            source,
            config(),
            fast.default_state(),
            self.release,
            execute=True,
            sleeper=lambda _: None,
        )
        self.assertEqual(
            [record["status"] for record in result["records"]],
            ["booked", "booked", "booked", "booked", "booked"],
        )
        self.assertEqual(result["records"][0]["attempts"], 4)
        self.assertEqual(source.mutation_count, 5)
        self.assertEqual(state["totalBooked"], 5)

    def test_retries_explicit_notopen_without_blocking_later_courses(self):
        source = FakeFastSource(notopen_mutations=3)
        result, state = fast.run_fast(
            source,
            config(),
            fast.default_state(),
            self.release,
            execute=True,
            sleeper=lambda _: None,
        )
        self.assertEqual(
            [record["status"] for record in result["records"]],
            ["booked", "booked", "booked", "booked", "booked"],
        )
        self.assertEqual(result["records"][0]["attempts"], 4)
        self.assertEqual(source.mutation_count, 8)
        self.assertEqual(state["totalBooked"], 5)

    def test_dry_run_never_mutates(self):
        source = FakeFastSource()
        result, state = fast.run_fast(
            source,
            config(),
            fast.default_state(),
            self.release,
            execute=False,
        )
        self.assertEqual(source.mutation_count, 0)
        self.assertEqual(
            [record["status"] for record in result["records"]],
            ["ready", "ready", "ready", "ready", "ready"],
        )
        self.assertEqual(state["totalRuns"], 0)

    def test_public_output_exposes_no_booking_identifiers(self):
        public = fast.build_public(
            config(),
            fast.default_state(),
            datetime(2026, 7, 28, 12, 0, tzinfo=ballet.TIMEZONE),
        )
        serialized = json.dumps(public, ensure_ascii=False)
        self.assertEqual(public["nextRunAt"], "2026-08-02T14:20:00+08:00")
        for marker in (
            "courseId",
            "classTableId",
            "customerId",
            "cardId",
            "PHPSESSID",
            "/var/lib/",
        ):
            self.assertNotIn(marker, serialized)

    def test_preview_writes_matching_json_and_wrapper(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / "private" / "state.json"
            public_path = root / "public" / "status.json"
            wrapper_path = root / "public" / "status.js"
            state = fast.default_state()
            public = fast.build_public(
                config(), state, datetime(2026, 7, 28, tzinfo=ballet.TIMEZONE)
            )
            fast.write_outputs(
                state_path,
                public_path,
                wrapper_path,
                state,
                public,
            )
            self.assertEqual(
                json.loads(public_path.read_text(encoding="utf-8")),
                public,
            )
            self.assertIn(
                "window.MAXNOW_BALLET_BOOKING_FAST_DATA = ",
                wrapper_path.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
