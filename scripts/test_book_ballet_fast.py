import copy
import json
import tempfile
import threading
import time
import unittest
from datetime import datetime
from pathlib import Path

import book_ballet as booking
import book_ballet_fast as fast
import sync_ballet as ballet
from test_book_ballet import timetable_with_reordered_controls
from test_sync_ballet import detail_html, index_html, timetable_html


def config():
    data = fast.load_config(
        Path(__file__).resolve().parents[1]
        / "config"
        / "ballet-booking-fast.json"
    )
    data["discoveryRefreshSeconds"] = [0, 0, 0]
    data["unknownVerificationSeconds"] = [0, 0, 0]
    return data


class FakeFastSource:
    def __init__(
        self,
        unknown_on_mutation=0,
        timetable_failures=0,
        notopen_mutations=0,
        queue_target_keys=None,
        request_delay=0,
        progressive_l15_after_requests=None,
        unknown_commits=False,
        verification_visibility_delay=0,
    ):
        self.request_count = 0
        self.post_count = 0
        self.mutation_count = 0
        self.lock = threading.Lock()
        self.unknown_on_mutation = unknown_on_mutation
        self.timetable_failures = timetable_failures
        self.notopen_mutations = notopen_mutations
        self.queue_target_keys = set(queue_target_keys or [])
        self.course_by_class_table_id = {}
        self.waitlisted_records = []
        self.request_delay = request_delay
        self.progressive_l15_after_requests = dict(
            progressive_l15_after_requests or {}
        )
        self.timetable_requests_by_date = {}
        self.unknown_commits = unknown_commits
        self.verification_visibility_delay = verification_visibility_delay
        self.booking_query_count = 0
        self.active_timetable = 0
        self.max_active_timetable = 0
        self.active_preflight = 0
        self.max_active_preflight = 0
        self.active_mutation = 0
        self.max_active_mutation = 0
        self.mutation_order = []
        self.mutation_timestamps = []

    def request(self, path, marker):
        with self.lock:
            self.request_count += 1
        if path.startswith(ballet.TIMETABLE_PATH):
            with self.lock:
                self.active_timetable += 1
                self.max_active_timetable = max(
                    self.max_active_timetable, self.active_timetable
                )
                should_fail = self.timetable_failures > 0
                if should_fail:
                    self.timetable_failures -= 1
            try:
                if self.request_delay:
                    time.sleep(self.request_delay)
                if should_fail:
                    raise ballet.SyncFailure("network_error")
                active_date = path.rsplit("/", 1)[-1]
                with self.lock:
                    date_request_count = (
                        self.timetable_requests_by_date.get(active_date, 0) + 1
                    )
                    self.timetable_requests_by_date[active_date] = (
                        date_request_count
                    )
                day = datetime.fromisoformat(active_date).weekday()
                courses = (
                    [
                        ("软开课", "10:00", "11:00", "李俊"),
                        ("软开专项", "11:00", "12:00", "李俊"),
                        ("软开-胯", "12:00", "13:00", "李俊"),
                        ("芭蕾 L1", "13:00", "14:30", "王嘉豪"),
                        ("芭蕾 L1.5", "14:30", "16:00", "李俊"),
                    ]
                    if day == 5
                    else [
                        ("软开", "10:00", "11:00", "李俊"),
                        ("芭蕾 L1", "13:00", "14:30", "王嘉豪"),
                        ("软开专项", "18:45", "19:45", "李俊"),
                        ("软开-胯", "18:45", "19:45", "李俊"),
                        (
                            "软开课" if day % 2 else "软开",
                            "18:45",
                            "19:45",
                            "李俊",
                        ),
                        ("芭蕾 L1", "19:45", "21:15", "王嘉豪"),
                        ("芭蕾 L1.5", "21:15", "22:45", "李俊"),
                    ]
                    if day in {0, 1, 2, 3, 4}
                    else [("肌肉素质", "19:00", "20:00", "戴俊瑶")]
                )
                if date_request_count <= self.progressive_l15_after_requests.get(
                    active_date, 0
                ):
                    courses = [course for course in courses if "L1.5" not in course[0]]
                pages = []
                for index, (course, start, end, teacher) in enumerate(courses, start=1):
                    rule_key = (
                        "ballet-l1-5"
                        if "L1.5" in course
                        else "ballet-l1"
                        if course.startswith("芭蕾")
                        else "soft-open"
                    )
                    target_key = (
                        f"{rule_key}-{active_date}-"
                        f"{start.replace(':', '')}-{end.replace(':', '')}-0"
                    )
                    class_table_id = f"71{day}{index:02d}"
                    with self.lock:
                        self.course_by_class_table_id[class_table_id] = {
                            "key": target_key,
                            "course": course,
                            "date": active_date,
                            "start": start,
                            "end": end,
                            "teacher": teacher,
                        }
                    is_queue = target_key in self.queue_target_keys
                    pages.append(
                        timetable_html(
                            course=course,
                            time_text=f"{start} ~ {end}",
                            teacher=teacher,
                            venue="大教室",
                            status="4 / 10 可排队" if is_queue else "4 / 10",
                        ).replace(
                            "</div></div></body>",
                            (
                                f'<button class="bookbtn" courseid="7000{index}" '
                                f'classtableid="{class_table_id}">'
                                f'{"排队" if is_queue else "预约"}</button>'
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
            finally:
                with self.lock:
                    self.active_timetable -= 1
        if path == ballet.BOOKING_PATH:
            with self.lock:
                self.booking_query_count += 1
                visible = (
                    self.booking_query_count > self.verification_visibility_delay
                )
            return index_html(
                "约课记录",
                [
                    (record["id"], record["course"], record["date"], "排队中")
                    for record in self.waitlisted_records if visible
                ],
            )
        detail_prefix = f"/gm/weixin/my/bookrecordone/{ballet.STORE_ID}/"
        if path.startswith(detail_prefix):
            record_id = path.rsplit("/", 1)[-1]
            record = next(
                item for item in self.waitlisted_records if item["id"] == record_id
            )
            return detail_html(
                course=record["course"],
                day=record["date"],
                time_text=f'{record["start"]}~{record["end"]}',
                teacher=record["teacher"],
                status="等候中, 排队序号 3",
            ).replace("测试教室", "大教室")
        raise AssertionError(path)

    def post_fields(self, path, fields, mutation):
        with self.lock:
            self.request_count += 1
            self.post_count += 1
            if mutation:
                self.active_mutation += 1
                self.max_active_mutation = max(
                    self.max_active_mutation, self.active_mutation
                )
            else:
                self.active_preflight += 1
                self.max_active_preflight = max(
                    self.max_active_preflight, self.active_preflight
                )
        try:
            if self.request_delay:
                time.sleep(self.request_delay)
            if path == booking.CARD_TYPE_PATH:
                return json.dumps([{"id": 90002, "status": "OPEN"}])
            if path.startswith(booking.CHECK_RULES_PREFIX):
                return json.dumps("OK")
            if path == booking.BOOKING_SUBMIT_PATH and mutation:
                with self.lock:
                    self.mutation_count += 1
                    self.mutation_timestamps.append(time.monotonic())
                    mutation_count = self.mutation_count
                    selected = self.course_by_class_table_id[
                        str(fields["classtableid"])
                    ]
                    self.mutation_order.append(selected["key"])
                    unknown = mutation_count == self.unknown_on_mutation
                    notopen = self.notopen_mutations > 0
                    if notopen:
                        self.notopen_mutations -= 1
                if unknown:
                    if self.unknown_commits and selected["key"] in self.queue_target_keys:
                        with self.lock:
                            self.waitlisted_records.append(
                                {**selected, "id": str(92000 + mutation_count)}
                            )
                    return json.dumps({"changed": True})
                if notopen:
                    return json.dumps("NOTOPEN")
                if selected["key"] in self.queue_target_keys:
                    with self.lock:
                        self.waitlisted_records.append(
                            {**selected, "id": str(92000 + mutation_count)}
                        )
                return json.dumps(91000 + mutation_count)
            raise AssertionError((path, fields, mutation))
        finally:
            with self.lock:
                if mutation:
                    self.active_mutation -= 1
                else:
                    self.active_preflight -= 1


class FakeHttpResponse:
    def __init__(self, body, status=200, will_close=False):
        self.status = status
        self.headers = {}
        self.will_close = will_close
        self.body = body.encode("utf-8")

    def read(self, limit=-1):
        return self.body if limit < 0 else self.body[:limit]


class FakeHttpConnection:
    def __init__(self, responses=None, fail=False):
        self.responses = list(responses or [])
        self.fail = fail
        self.requests = []
        self.closed = False

    def request(self, method, path, body=None, headers=None):
        self.requests.append((method, path, body, dict(headers or {})))
        if self.fail:
            raise OSError("transport failed")

    def getresponse(self):
        return self.responses.pop(0)

    def close(self):
        self.closed = True


class FakeBookingQuerySource:
    def __init__(self):
        self.lock = threading.Lock()
        self.active_details = 0
        self.max_active_details = 0

    def request(self, path, marker):
        if path == ballet.BOOKING_PATH:
            return index_html(
                "约课记录",
                [
                    ("93001", "芭蕾 L1", "2026-08-04", "已预约"),
                    ("93002", "芭蕾 L1", "2026-08-07", "已预约"),
                    ("93003", "软开", "2026-08-06", "已预约"),
                ],
            )
        record_id = path.rsplit("/", 1)[-1]
        facts = {
            "93001": ("芭蕾 L1", "2026-08-04", "19:45~21:15"),
            "93002": ("芭蕾 L1", "2026-08-07", "19:45~21:15"),
            "93003": ("软开", "2026-08-06", "18:45~19:45"),
        }
        with self.lock:
            self.active_details += 1
            self.max_active_details = max(
                self.max_active_details, self.active_details
            )
        try:
            time.sleep(0.02)
            course, day, time_text = facts[record_id]
            return detail_html(
                course=course,
                day=day,
                time_text=time_text,
                teacher="任意老师",
                status="已预约",
            ).replace("测试教室", "大教室")
        finally:
            with self.lock:
                self.active_details -= 1


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
                "ballet-l1-5",
                "ballet-l1-0",
                "ballet-l1-1",
                "ballet-l1-2",
                "ballet-l1-3",
                "ballet-l1-4",
                "ballet-l1-5-5",
                "ballet-l1-5-0",
                "ballet-l1-5-1",
                "ballet-l1-5-2",
                "ballet-l1-5-3",
                "ballet-l1-5-4",
                "soft-open-5",
                "soft-open-0",
                "soft-open-1",
                "soft-open-2",
                "soft-open-3",
                "soft-open-4",
            ],
        )
        self.assertEqual(
            [target["date"] for target in targets],
            [
                "2026-08-08",
                "2026-08-03",
                "2026-08-04",
                "2026-08-05",
                "2026-08-06",
                "2026-08-07",
                "2026-08-08",
                "2026-08-03",
                "2026-08-04",
                "2026-08-05",
                "2026-08-06",
                "2026-08-07",
                "2026-08-08",
                "2026-08-03",
                "2026-08-04",
                "2026-08-05",
                "2026-08-06",
                "2026-08-07",
            ],
        )

    def test_discovery_selects_only_exact_soft_open_and_standard_l1(self):
        planned = fast.materialize_targets(config(), self.release)
        source = FakeFastSource()
        pages = {
            target["date"]: source.request(
                f"{ballet.TIMETABLE_PATH}/{target['date']}", "classtable"
            )
            for target in planned
        }
        targets = fast.discover_targets(config(), planned, pages)
        self.assertEqual(len(targets), 18)
        self.assertEqual(
            {target["_courseName"] for target in targets},
            {"软开", "软开课", "芭蕾 L1", "芭蕾 L1.5"},
        )
        self.assertNotIn("软开专项", {target["_courseName"] for target in targets})
        self.assertNotIn("软开-胯", {target["_courseName"] for target in targets})
        self.assertTrue(
            all(
                target["weekday"] == 5 or target["startTime"] >= "18:40"
                for target in targets
            )
        )

    def test_target_matches_when_teacher_changes(self):
        target = fast.materialize_targets(config(), self.release)[0]
        target = {
            **target,
            "startTime": "10:00",
            "endTime": "11:00",
            "_courseName": "软开",
            "_selectedVenue": "小教室",
        }
        record = {
            "date": target["date"],
            "courseType": target["courseType"],
            "level": target["level"],
            "startTime": target["startTime"],
            "endTime": target["endTime"],
            "teacher": "临时代课老师",
            "venue": "小教室",
            "courseName": "软开",
        }

        self.assertTrue(fast.record_matches(record, target))
        record["startTime"] = "18:46"
        self.assertFalse(fast.record_matches(record, target))

    def test_timetable_candidates_prefer_large_room_then_fall_back_to_small(self):
        target = {
            **fast.materialize_targets(config(), self.release)[2],
            "startTime": "17:30",
            "endTime": "19:00",
            "courseType": "ballet",
            "level": "L1",
            "exactCourseNames": None,
        }
        def candidate_page(venue, course_id, class_table_id):
            return timetable_html(
                course="芭蕾L1-入门",
                time_text="17:30 ~ 19:00",
                teacher="任意老师",
                venue=venue,
                status="4 / 10",
            ).replace(
                "</div></div></body>",
                (
                    f'<button class="bookbtn" courseid="{course_id}" '
                    f'classtableid="{class_table_id}">预约</button>'
                    "</div></div></body>"
                ),
            )

        small = candidate_page("小教室", "71001", "72001")
        large = candidate_page("大教室", "71002", "72002")
        for page in (small + large, large + small):
            with self.subTest(small_first=page.index("小教室") < page.index("大教室")):
                candidates = fast.timetable_candidates(
                    None, target, prefetched_text=page
                )
                self.assertEqual(len(candidates), 1)
                self.assertEqual(candidates[0]["record"]["venue"], "大教室")
                button = next(
                    item
                    for item in candidates[0]["control"]["controls"]
                    if item["tag"] == "button"
                )
                self.assertEqual(
                    button["attrs"]["classtableid"],
                    "72002",
                )

        candidates = fast.timetable_candidates(
            None, target, prefetched_text=small
        )
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["record"]["venue"], "小教室")

        duplicate_large = candidate_page("大教室", "71003", "72003")
        candidates = fast.timetable_candidates(
            None, target, prefetched_text=large + duplicate_large + small
        )
        self.assertEqual(len(candidates), 2)

    def test_fast_path_keeps_target_bound_to_its_own_button(self):
        target = fast.materialize_targets(config(), self.release)[0]
        target = {
            **target,
            "courseType": "ballet",
            "level": "L1",
            "exactCourseNames": None,
            "startTime": "20:00",
            "endTime": "21:30",
        }
        for reverse in (False, True):
            with self.subTest(reverse=reverse):
                page = timetable_with_reordered_controls(reverse=reverse)
                candidates = fast.timetable_candidates(
                    None, target, prefetched_text=page
                )
                self.assertEqual(len(candidates), 1)
                contract = booking.booking_contract(candidates[0])
                self.assertEqual(contract["courseId"], "72002")
                self.assertEqual(contract["classTableId"], "73002")

    def test_fast_path_mutates_sequentially_then_verifies_once(self):
        source = FakeFastSource()
        result, state = fast.run_fast(
            source,
            config(),
            fast.default_state(),
            self.release,
            execute=True,
        )
        self.assertEqual(source.mutation_count, 18)
        self.assertEqual(
            [record["status"] for record in result["records"]],
            ["booked"] * 18,
        )
        self.assertEqual(state["totalBooked"], 18)
        self.assertEqual(state["totalRuns"], 1)
        self.assertEqual(result["requestsMade"], 79)
        self.assertEqual(
            source.mutation_order,
            [
                "ballet-l1-2026-08-08-1300-1430-0",
                "ballet-l1-2026-08-03-1945-2115-0",
                "ballet-l1-2026-08-04-1945-2115-0",
                "ballet-l1-2026-08-05-1945-2115-0",
                "ballet-l1-2026-08-06-1945-2115-0",
                "ballet-l1-2026-08-07-1945-2115-0",
                "ballet-l1-5-2026-08-08-1430-1600-0",
                "ballet-l1-5-2026-08-03-2115-2245-0",
                "ballet-l1-5-2026-08-04-2115-2245-0",
                "ballet-l1-5-2026-08-05-2115-2245-0",
                "ballet-l1-5-2026-08-06-2115-2245-0",
                "ballet-l1-5-2026-08-07-2115-2245-0",
                "soft-open-2026-08-08-1000-1100-0",
                "soft-open-2026-08-03-1845-1945-0",
                "soft-open-2026-08-04-1845-1945-0",
                "soft-open-2026-08-05-1845-1945-0",
                "soft-open-2026-08-06-1845-1945-0",
                "soft-open-2026-08-07-1845-1945-0",
            ],
        )

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
                *(["booked"] * 17),
            ],
        )
        self.assertEqual(source.mutation_count, 18)
        self.assertEqual(result["records"][0]["attempts"], 1)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(state["totalBooked"], 17)

    def test_unknown_result_is_verified_later_without_duplicate_mutation(self):
        target_key = "ballet-l1-2026-08-08-1300-1430-0"
        source = FakeFastSource(
            unknown_on_mutation=1,
            queue_target_keys={target_key},
            unknown_commits=True,
            verification_visibility_delay=2,
        )
        result, state = fast.run_fast(
            source,
            config(),
            fast.default_state(),
            self.release,
            execute=True,
            sleeper=lambda _: None,
        )
        self.assertEqual(source.mutation_count, 18)
        self.assertEqual(result["records"][0]["status"], "waitlisted")
        self.assertEqual(result["records"][0]["verificationAttempts"], 3)
        self.assertTrue(result["records"][0]["verified"])
        self.assertEqual(state["totalWaitlisted"], 1)

    def test_progressive_release_discovers_late_l15_before_soft_open(self):
        source = FakeFastSource(
            progressive_l15_after_requests={
                "2026-08-06": 1,
                "2026-08-08": 1,
            }
        )
        result, _ = fast.run_fast(
            source,
            config(),
            fast.default_state(),
            self.release,
            execute=True,
            sleeper=lambda _: None,
        )
        self.assertEqual(source.mutation_count, 18)
        self.assertEqual([record["status"] for record in result["records"]], ["booked"] * 18)
        first_soft = next(
            index
            for index, key in enumerate(source.mutation_order)
            if key.startswith("soft-open-")
        )
        self.assertTrue(
            all(
                index < first_soft
                for index, key in enumerate(source.mutation_order)
                if key.startswith("ballet-l1-5-")
            )
        )

    def test_l1_mutation_pipeline_starts_before_discovery_settles(self):
        settings = config()
        settings["discoveryRefreshSeconds"] = [0.08, 0.1, 0.12]
        source = FakeFastSource(request_delay=0.002)
        started = time.monotonic()
        result, _ = fast.run_fast(
            source,
            settings,
            fast.default_state(),
            self.release,
            execute=True,
        )
        first_mutation_milliseconds = round(
            (source.mutation_timestamps[0] - started) * 1000
        )
        self.assertLess(
            first_mutation_milliseconds,
            result["timings"]["discoveryWallMilliseconds"],
        )
        self.assertEqual(source.max_active_mutation, 1)

    def test_transient_preflight_failures_recover_and_book(self):
        source = FakeFastSource(timetable_failures=2)
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
            ["booked"] * 18,
        )
        self.assertTrue(all(record["attempts"] == 1 for record in result["records"]))
        self.assertEqual(source.mutation_count, 18)
        self.assertEqual(state["totalBooked"], 18)

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
            ["booked"] * 18,
        )
        self.assertEqual(result["records"][0]["attempts"], 4)
        self.assertEqual(source.mutation_count, 21)
        self.assertEqual(state["totalBooked"], 18)

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
            ["ready"] * 18,
        )
        self.assertEqual(state["totalRuns"], 0)

    def test_queue_available_target_joins_waitlist_and_verifies_position(self):
        source = FakeFastSource(
            queue_target_keys={"ballet-l1-2026-08-08-1300-1430-0"}
        )
        result, state = fast.run_fast(
            source,
            config(),
            fast.default_state(),
            self.release,
            execute=True,
        )
        self.assertEqual(source.mutation_count, 18)
        self.assertEqual(result["records"][0]["status"], "waitlisted")
        self.assertEqual(result["records"][0]["bookingStatus"], "waitlist")
        self.assertEqual(result["records"][0]["waitlistPosition"], 3)
        self.assertTrue(result["records"][0]["verified"])
        self.assertEqual(state["totalBooked"], 17)
        self.assertEqual(state["totalWaitlisted"], 1)

    def test_queue_available_target_is_ready_in_dry_run(self):
        source = FakeFastSource(
            queue_target_keys={"ballet-l1-2026-08-08-1300-1430-0"}
        )
        result, state = fast.run_fast(
            source,
            config(),
            fast.default_state(),
            self.release,
            execute=False,
        )
        self.assertEqual(source.mutation_count, 0)
        self.assertEqual(result["records"][0]["status"], "ready_waitlist")
        self.assertEqual(result["records"][0]["availability"], "queue_available")
        self.assertEqual(state["totalRuns"], 0)

    def test_queue_available_target_is_not_mutated_when_disabled(self):
        disabled = copy.deepcopy(config())
        disabled["allowWaitlist"] = False
        source = FakeFastSource(
            queue_target_keys={"ballet-l1-2026-08-08-1300-1430-0"}
        )
        result, state = fast.run_fast(
            source,
            disabled,
            fast.default_state(),
            self.release,
            execute=True,
        )
        self.assertEqual(source.mutation_count, 17)
        self.assertEqual(result["records"][0]["status"], "not_available")
        self.assertEqual(result["records"][0]["availability"], "queue_available")
        self.assertEqual(state["totalBooked"], 17)
        self.assertEqual(state["totalWaitlisted"], 0)

    def test_read_and_preflight_are_bounded_concurrent_but_mutation_is_serial(self):
        source = FakeFastSource(request_delay=0.02)
        result, _ = fast.run_fast(
            source,
            config(),
            fast.default_state(),
            self.release,
            execute=True,
        )
        self.assertEqual(result["status"], "completed_unverified")
        self.assertEqual(source.max_active_timetable, 3)
        self.assertEqual(source.max_active_preflight, 2)
        self.assertEqual(source.max_active_mutation, 1)
        self.assertEqual(source.request_count, 79)

    def test_persistent_source_reuses_connection_and_requests_keep_alive(self):
        connection = FakeHttpConnection(
            [
                FakeHttpResponse("classtable one"),
                FakeHttpResponse("classtable two"),
            ]
        )
        source = fast.PersistentWendaBookingSource(
            ballet.Credentials("a" * 16, "test-agent"),
            pool_size=1,
            connection_factory=lambda: connection,
        )
        try:
            source.request(f"{ballet.TIMETABLE_PATH}/2026-08-04", "classtable")
            source.request(f"{ballet.TIMETABLE_PATH}/2026-08-05", "classtable")
        finally:
            source.close()
        self.assertEqual(len(connection.requests), 2)
        self.assertEqual(
            [item[3]["Connection"] for item in connection.requests],
            ["keep-alive", "keep-alive"],
        )
        self.assertEqual(source.request_count, 2)
        self.assertEqual(source.timing_summary()["timetable"]["count"], 2)

    def test_persistent_source_never_retries_mutation_transport_failure(self):
        connections = []

        def factory():
            connection = FakeHttpConnection(fail=True)
            connections.append(connection)
            return connection

        source = fast.PersistentWendaBookingSource(
            ballet.Credentials("a" * 16, "test-agent"),
            pool_size=1,
            connection_factory=factory,
        )
        try:
            with self.assertRaises(booking.BookingFailure) as raised:
                source.post_fields(
                    booking.BOOKING_SUBMIT_PATH,
                    {"classtableid": "1", "cardid": "2"},
                    mutation=True,
                )
        finally:
            source.close()
        self.assertEqual(raised.exception.code, "unknown_result")
        self.assertEqual(sum(len(item.requests) for item in connections), 1)
        self.assertEqual(source.mutation_count, 1)

    def test_final_booking_details_are_read_concurrently(self):
        source = FakeBookingQuerySource()
        result = fast.query_bookings_parallel(source)
        self.assertEqual(len(result["records"]), 3)
        self.assertEqual(source.max_active_details, 3)

    def test_public_output_exposes_no_booking_identifiers(self):
        public = fast.build_public(
            config(),
            fast.default_state(),
            datetime(2026, 7, 28, 12, 0, tzinfo=ballet.TIMEZONE),
        )
        serialized = json.dumps(public, ensure_ascii=False)
        self.assertEqual(public["nextRunAt"], "2026-08-02T14:20:00+08:00")
        self.assertTrue(public["waitlistEnabled"])
        self.assertEqual(public["totalWaitlisted"], 0)
        self.assertEqual(
            {target["teacher"] for target in public["targets"]},
            {"不限老师"},
        )
        self.assertEqual(
            {target["venue"] for target in public["targets"]},
            {"大教室优先，小教室兜底"},
        )
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
