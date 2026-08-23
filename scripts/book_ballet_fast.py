from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import queue
import ssl
import sys
import threading
import time
import urllib.parse
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import book_ballet as booking
import query_ballet_live as live
import sync_ballet as ballet


sys.dont_write_bytecode = True

WEEKDAY_LABELS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
COURSE_TYPE_LABELS = {
    "ballet": "芭蕾",
    "soft_open": "软开",
    "conditioning": "肌肉素质",
    "technique": "技巧",
    "other": "其他",
}
MAX_RETRIES = 3
RETRY_DELAYS_SECONDS = (0.08, 0.16, 0.32)
PREFETCH_WORKERS = 3
DISCOVERY_WORKERS = 2
PREFLIGHT_WORKERS = 2
PREFLIGHT_TTL_SECONDS = 15
MAX_DISCOVERED_TARGETS = 30
RETRIABLE_PREFLIGHT_CODES = {
    "card_not_open",
    "course_not_unique",
    "http_error",
    "network_error",
    "rules_blocked",
    "unknown_result",
}
GLOBAL_STOP_CODES = {
    "auth_required",
    "configuration_error",
    "parse_error",
    "source_changed",
}
PUBLIC_ERROR_LABELS = {
    "auth_required": "闻道登录已失效，未执行预约。",
    "configuration_error": "自动抢课配置无效，未执行预约。",
    "network_error": "连接闻道失败，未执行预约。",
    "outside_window": "不在周日抢课时间窗内，未执行预约。",
    "source_changed": "闻道页面结构发生变化，已停止后续课程。",
    "unknown_result": "预约结果无法安全确认，未重复提交该课。",
}


class FastBookingFailure(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class PersistentWendaBookingSource:
    def __init__(
        self,
        credentials: ballet.Credentials,
        timeout_seconds: int = 5,
        pool_size: int = PREFETCH_WORKERS,
        connection_factory: Any = None,
    ):
        parts = urllib.parse.urlsplit(ballet.BASE_URL)
        if parts.scheme != "https" or not parts.hostname:
            raise FastBookingFailure("configuration_error")
        self.reader = ballet.WendaSource(
            credentials,
            timeout_seconds=timeout_seconds,
            retries=0,
        )
        self.timeout_seconds = timeout_seconds
        self.post_count = 0
        self.mutation_count = 0
        self._counter_lock = threading.Lock()
        self._credential_lock = threading.Lock()
        self._timing_lock = threading.Lock()
        self._request_timings: dict[str, list[int]] = {}
        self._connection_factory = connection_factory or (
            lambda: http.client.HTTPSConnection(
                parts.hostname,
                port=parts.port or 443,
                timeout=timeout_seconds,
                context=ssl.create_default_context(),
            )
        )
        self._pool: queue.LifoQueue[Any] = queue.LifoQueue()
        for _ in range(max(1, pool_size)):
            self._pool.put(self._connection_factory())

    @property
    def request_count(self) -> int:
        with self._counter_lock:
            return self.reader.request_count + self.post_count

    def _stage_for_path(self, path: str, mutation: bool = False) -> str:
        if mutation:
            return "mutation"
        if path.startswith(ballet.TIMETABLE_PATH):
            return "timetable"
        if path == booking.CARD_TYPE_PATH:
            return "card"
        if path.startswith(booking.CHECK_RULES_PREFIX):
            return "rules"
        if path == ballet.BOOKING_PATH:
            return "verificationIndex"
        if path.startswith(f"/gm/weixin/my/bookrecordone/{ballet.STORE_ID}/"):
            return "verificationDetail"
        return "other"

    def _record_timing(self, stage: str, started: float) -> None:
        elapsed = round((time.monotonic() - started) * 1000)
        with self._timing_lock:
            self._request_timings.setdefault(stage, []).append(elapsed)

    def timing_summary(self) -> dict[str, dict[str, int]]:
        with self._timing_lock:
            return {
                stage: {
                    "count": len(values),
                    "totalMilliseconds": sum(values),
                    "maxMilliseconds": max(values),
                }
                for stage, values in sorted(self._request_timings.items())
                if values
            }

    def _headers(self, path: str) -> dict[str, str]:
        with self._credential_lock:
            headers = self.reader._headers(path)
        headers["Connection"] = "keep-alive"
        return headers

    def _replace_connection(self, connection: Any) -> None:
        try:
            connection.close()
        except Exception:
            pass
        self._pool.put(self._connection_factory())

    def _perform_once(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        body: bytes | None,
        stage: str,
    ) -> tuple[int, Any, bytes]:
        connection = self._pool.get()
        reusable = False
        started = time.monotonic()
        try:
            with self._counter_lock:
                if method == "GET":
                    self.reader.request_count += 1
                else:
                    self.post_count += 1
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            status = int(response.status)
            response_headers = response.headers
            response_body = ballet._read_limited(response)
            reusable = not bool(getattr(response, "will_close", True))
            return status, response_headers, response_body
        finally:
            self._record_timing(stage, started)
            if reusable:
                self._pool.put(connection)
            else:
                self._replace_connection(connection)

    def _perform(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        body: bytes | None,
        mutation: bool,
    ) -> tuple[int, Any, bytes]:
        stage = self._stage_for_path(path, mutation)
        attempts = 1 if mutation else 2
        for transport_attempt in range(attempts):
            try:
                return self._perform_once(method, path, headers, body, stage)
            except (OSError, TimeoutError, http.client.HTTPException):
                if transport_attempt + 1 >= attempts:
                    raise
        raise OSError("unreachable")

    def request(self, path: str, expected_marker: str) -> str:
        path = ballet.validate_read_only_path(path)
        try:
            status, headers, body = self._perform(
                "GET",
                path,
                self._headers(path),
                None,
                mutation=False,
            )
        except (OSError, TimeoutError, http.client.HTTPException):
            raise ballet.SyncFailure("network_error")
        with self._credential_lock:
            self.reader._update_session_in_memory(headers)
        text = body.decode("utf-8", "replace")
        if ballet._is_auth_response(status, headers, text):
            raise ballet.SyncFailure("auth_required")
        if status != 200:
            raise ballet.SyncFailure("http_error")
        if expected_marker not in text:
            raise ballet.SyncFailure("source_changed")
        return text

    def post_fields(
        self,
        path: str,
        fields: dict[str, str],
        mutation: bool,
    ) -> str:
        allowed = {
            booking.CARD_TYPE_PATH,
            booking.GET_USING_CARD_PATH,
            booking.BOOKING_SUBMIT_PATH,
        }
        path_allowed = (
            bool(
                path.removeprefix(booking.CHECK_RULES_PREFIX).isdigit()
            )
            if path.startswith(booking.CHECK_RULES_PREFIX)
            else path in allowed
        )
        if (
            not path_allowed
            or not fields
            or mutation != (path == booking.BOOKING_SUBMIT_PATH)
        ):
            raise booking.BookingFailure("configuration_error")
        if mutation:
            with self._counter_lock:
                self.mutation_count += 1
        body = urllib.parse.urlencode(fields).encode("utf-8")
        headers = {
            **self._headers(path),
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(body)),
            "Origin": ballet.BASE_URL,
            "Referer": ballet.BASE_URL + ballet.TIMETABLE_PATH,
        }
        try:
            status, response_headers, response_body = self._perform(
                "POST",
                path,
                headers,
                body,
                mutation=mutation,
            )
        except (OSError, TimeoutError, http.client.HTTPException):
            raise booking.BookingFailure("unknown_result")
        with self._credential_lock:
            self.reader._update_session_in_memory(response_headers)
        text = response_body.decode("utf-8", "replace")
        if ballet._is_auth_response(status, response_headers, text):
            raise booking.BookingFailure("auth_required")
        if status not in {200, 302, 303}:
            raise booking.BookingFailure("unknown_result")
        if status in {302, 303}:
            location = str(response_headers.get("Location", ""))
            parts = urllib.parse.urlsplit(location)
            base = urllib.parse.urlsplit(ballet.BASE_URL)
            if parts.netloc and parts.netloc != base.netloc:
                raise booking.BookingFailure("unknown_result")
        return text

    def close(self) -> None:
        while True:
            try:
                connection = self._pool.get_nowait()
            except queue.Empty:
                break
            try:
                connection.close()
            except Exception:
                pass


def parse_hhmm(value: str) -> tuple[int, int]:
    try:
        hour_text, minute_text = value.split(":", 1)
        hour, minute = int(hour_text), int(minute_text)
    except (AttributeError, TypeError, ValueError):
        raise FastBookingFailure("configuration_error")
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise FastBookingFailure("configuration_error")
    return hour, minute


def load_config(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise FastBookingFailure("configuration_error")
    if (
        not isinstance(data, dict)
        or data.get("schemaVersion") != 6
        or data.get("timezone") != "Asia/Shanghai"
        or not isinstance(data.get("enabled"), bool)
        or not isinstance(data.get("allowWaitlist"), bool)
        or not isinstance(data.get("release"), dict)
        or not isinstance(data.get("discoveryRefreshSeconds"), list)
        or not isinstance(data.get("unknownVerificationSeconds"), list)
        or data["release"].get("weekday") != 6
        or not isinstance(data.get("priorityWeekdays"), list)
        or not isinstance(data.get("priorityCourses"), list)
        or not isinstance(data.get("venuePriority"), list)
        or not isinstance(data.get("weekdayStartTimes"), dict)
        or not isinstance(data.get("selectionRules"), list)
        or not data["selectionRules"]
        or len(data["selectionRules"]) > 4
    ):
        raise FastBookingFailure("configuration_error")
    parse_hhmm(data["release"].get("time"))
    discovery_refresh_seconds = data["discoveryRefreshSeconds"]
    unknown_verification_seconds = data["unknownVerificationSeconds"]
    if (
        discovery_refresh_seconds != sorted(discovery_refresh_seconds)
        or unknown_verification_seconds != sorted(unknown_verification_seconds)
        or not 1 <= len(discovery_refresh_seconds) <= 5
        or not 1 <= len(unknown_verification_seconds) <= 5
        or any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or value < 0
            or value > 15
            for value in discovery_refresh_seconds + unknown_verification_seconds
        )
    ):
        raise FastBookingFailure("configuration_error")
    priorities = data["priorityWeekdays"]
    if priorities != [5, 0, 1, 2, 3, 4]:
        raise FastBookingFailure("configuration_error")
    course_priorities = data["priorityCourses"]
    expected_course_priorities = [
        {"courseType": "ballet", "level": "L1"},
        {"courseType": "ballet", "level": "L1.5"},
        {"courseType": "soft_open", "level": "none"},
    ]
    if course_priorities != expected_course_priorities:
        raise FastBookingFailure("configuration_error")
    if data["venuePriority"] != ["大教室", "小教室"]:
        raise FastBookingFailure("configuration_error")
    expected_start_times = {
        "0": "18:40",
        "1": "18:40",
        "2": "18:40",
        "3": "18:40",
        "4": "18:40",
        "5": "00:00",
    }
    if data["weekdayStartTimes"] != expected_start_times:
        raise FastBookingFailure("configuration_error")
    for value in data["weekdayStartTimes"].values():
        parse_hhmm(value)
    required = {"key", "weekdays", "courseType", "level", "exactCourseNames"}
    keys = set()
    for rule in data["selectionRules"]:
        if not isinstance(rule, dict) or set(rule) != required:
            raise FastBookingFailure("configuration_error")
        if (
            not isinstance(rule["key"], str)
            or not rule["key"]
            or rule["key"] in keys
            or rule["weekdays"] != [0, 1, 2, 3, 4, 5]
            or rule["courseType"] not in COURSE_TYPE_LABELS
            or rule["level"] not in {"none", "L1", "L1.5", "L2", "L3", "L4"}
            or (
                rule["exactCourseNames"] is not None
                and (
                    not isinstance(rule["exactCourseNames"], list)
                    or not rule["exactCourseNames"]
                    or any(
                        not isinstance(name, str)
                        or not ballet.normalize_course_name(name)
                        for name in rule["exactCourseNames"]
                    )
                )
            )
        ):
            raise FastBookingFailure("configuration_error")
        keys.add(rule["key"])
    configured_priorities = {
        (item["courseType"], item["level"])
        for item in course_priorities
    }
    if any(
        (rule["courseType"], rule["level"])
        not in configured_priorities
        for rule in data["selectionRules"]
    ):
        raise FastBookingFailure("configuration_error")
    soft_open_rule = next(
        (rule for rule in data["selectionRules"] if rule["key"] == "soft-open"),
        None,
    )
    if (
        soft_open_rule is None
        or soft_open_rule["exactCourseNames"] != ["软开", "软开课"]
    ):
        raise FastBookingFailure("configuration_error")
    return data


def priority_rank(weekday: int, priorities: list[int]) -> tuple[int, int]:
    try:
        return priorities.index(weekday), weekday
    except ValueError:
        return len(priorities), weekday


def course_priority_rank(
    target: dict[str, Any], priorities: list[dict[str, str]]
) -> int:
    key = (target["courseType"], target["level"])
    for index, priority in enumerate(priorities):
        if key == (priority["courseType"], priority["level"]):
            return index
    return len(priorities)


def next_release_at(now: datetime, config: dict[str, Any]) -> datetime:
    local_now = now.astimezone(ballet.TIMEZONE)
    hour, minute = parse_hhmm(config["release"]["time"])
    days_ahead = (config["release"]["weekday"] - local_now.weekday()) % 7
    candidate = datetime.combine(
        local_now.date() + timedelta(days=days_ahead),
        datetime.min.time(),
        tzinfo=ballet.TIMEZONE,
    ).replace(hour=hour, minute=minute)
    if candidate < local_now:
        candidate += timedelta(days=7)
    return candidate


def target_date(release_day: date, weekday: int) -> date:
    days_ahead = (weekday - release_day.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return release_day + timedelta(days=days_ahead)


def materialize_targets(
    config: dict[str, Any], release_at: datetime
) -> list[dict[str, Any]]:
    targets = []
    order = 0
    for configured in config["selectionRules"]:
        for weekday in configured["weekdays"]:
            targets.append(
                {
                    "key": f"{configured['key']}-{weekday}",
                    "weekday": weekday,
                    "courseType": configured["courseType"],
                    "level": configured["level"],
                    "exactCourseNames": configured["exactCourseNames"],
                    "_notBeforeTime": config["weekdayStartTimes"][str(weekday)],
                    "venuePriority": list(config["venuePriority"]),
                    "date": target_date(
                        release_at.astimezone(ballet.TIMEZONE).date(), weekday
                    ).isoformat(),
                    "startTime": "",
                    "endTime": "",
                    "_ruleKey": configured["key"],
                    "_order": order,
                }
            )
            order += 1
    targets.sort(
        key=lambda item: (
            course_priority_rank(item, config["priorityCourses"]),
            priority_rank(item["weekday"], config["priorityWeekdays"]),
            item["_order"],
        )
    )
    return targets


def rule_matches(record: dict[str, Any], target: dict[str, Any]) -> bool:
    if (
        record.get("date") != target["date"]
        or record.get("courseType") != target["courseType"]
        or record.get("level") != target["level"]
    ):
        return False
    try:
        record_start = parse_hhmm(str(record.get("startTime", "")))
        not_before = parse_hhmm(str(target["_notBeforeTime"]))
    except FastBookingFailure:
        return False
    if record_start < not_before:
        return False
    exact_names = target.get("exactCourseNames")
    return exact_names is None or (
        ballet.normalize_course_name(str(record.get("courseName", "")))
        in {ballet.normalize_course_name(str(name)) for name in exact_names}
    )


def discover_targets(
    config: dict[str, Any],
    planned_targets: list[dict[str, Any]],
    prefetched_pages: dict[str, str | Exception],
) -> list[dict[str, Any]]:
    parsed_by_date: dict[str, list[dict[str, Any]]] = {}
    targets: list[dict[str, Any]] = []
    for planned in planned_targets:
        page = prefetched_pages[planned["date"]]
        if isinstance(page, Exception):
            targets.append({**planned, "_discoveryFailure": page})
            continue
        if planned["date"] not in parsed_by_date:
            parsed_by_date[planned["date"]] = parse_timetable_entries(
                page, planned["date"]
            )
        matches = [
            entry
            for entry in parsed_by_date[planned["date"]]
            if rule_matches(entry["record"], planned)
        ]
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for entry in matches:
            record = entry["record"]
            group_key = (
                str(record.get("startTime", "")),
                str(record.get("endTime", "")),
                ballet.normalize_course_name(str(record.get("courseName", ""))),
            )
            grouped.setdefault(group_key, []).append(entry)
        for group_order, ((start_time, end_time, course_name), entries) in enumerate(
            sorted(grouped.items())
        ):
            selected: list[dict[str, Any]] = []
            selected_venue = ""
            for venue in planned["venuePriority"]:
                selected = [
                    entry
                    for entry in entries
                    if ballet.normalize_space(
                        str(entry["record"].get("venue", ""))
                    )
                    == ballet.normalize_space(venue)
                ]
                if selected:
                    selected_venue = venue
                    break
            if not selected:
                continue
            targets.append(
                {
                    **planned,
                    "key": (
                        f"{planned['_ruleKey']}-{planned['date']}-"
                        f"{start_time.replace(':', '')}-{end_time.replace(':', '')}-"
                        f"{group_order}"
                    ),
                    "startTime": start_time,
                    "endTime": end_time,
                    "_courseName": course_name,
                    "_selectedVenue": selected_venue,
                }
            )
    if len(targets) > MAX_DISCOVERED_TARGETS:
        raise FastBookingFailure("source_changed")
    targets.sort(
        key=lambda item: (
            course_priority_rank(item, config["priorityCourses"]),
            priority_rank(item["weekday"], config["priorityWeekdays"]),
            item["startTime"],
            item["_order"],
        )
    )
    return targets


def public_target(target: dict[str, Any]) -> dict[str, Any]:
    course = COURSE_TYPE_LABELS[target["courseType"]]
    if target["level"] != "none":
        course = f"{course} {target['level']}"
    return {
        "key": target["key"],
        "weekday": WEEKDAY_LABELS[target["weekday"]],
        "date": target.get("date"),
        "startTime": target["startTime"] or (
            "全天"
            if target.get("_notBeforeTime") == "00:00"
            else f"{target.get('_notBeforeTime')} 后"
        ),
        "endTime": target["endTime"],
        "course": course,
        "teacher": "不限老师",
        "venue": target.get("_selectedVenue") or "大教室优先，小教室兜底",
    }


def record_matches(record: dict[str, Any], target: dict[str, Any]) -> bool:
    return (
        record.get("date") == target["date"]
        and record.get("courseType") == target["courseType"]
        and record.get("level") == target["level"]
        and record.get("startTime") == target["startTime"]
        and record.get("endTime") == target["endTime"]
        and (
            not target.get("_courseName")
            or ballet.normalize_course_name(str(record.get("courseName", "")))
            == ballet.normalize_course_name(str(target["_courseName"]))
        )
        and (
            not target.get("_selectedVenue")
            or ballet.normalize_space(str(record.get("venue", "")))
            == ballet.normalize_space(str(target["_selectedVenue"]))
        )
    )


def parse_timetable_entries(
    text: str, target_date: str
) -> list[dict[str, Any]]:
    return booking.parse_timetable_entries(text, target_date)


def timetable_candidates(
    source: Any,
    target: dict[str, Any],
    prefetched_text: str | None = None,
) -> list[dict[str, Any]]:
    text = prefetched_text
    if text is None:
        path = f"{ballet.TIMETABLE_PATH}/{target['date']}"
        text = source.request(path, "classtable")
    matches = [
        entry
        for entry in parse_timetable_entries(text, target["date"])
        if record_matches(entry["record"], target)
    ]
    for venue in target["venuePriority"]:
        preferred = [
            entry
            for entry in matches
            if ballet.normalize_space(str(entry["record"].get("venue", "")))
            == ballet.normalize_space(venue)
        ]
        if preferred:
            return preferred
    return []


def prepare_candidate(
    source: Any, candidate: dict[str, Any]
) -> dict[str, Any]:
    started = time.monotonic()
    contract = booking.booking_contract(candidate)
    card_id = booking.eligible_card(source, contract)
    booking.check_rules(source, contract, card_id)
    return {
        "contract": contract,
        "cardId": card_id,
        "completedAt": time.monotonic(),
        "elapsedMilliseconds": round((time.monotonic() - started) * 1000),
    }


def query_bookings_parallel(
    source: Any,
    max_workers: int = PREFETCH_WORKERS,
    target_dates: set[str] | None = None,
) -> dict[str, Any]:
    html = source.request(ballet.BOOKING_PATH, "约课记录")
    index = ballet.parse_index(html, "booking")
    active = [
        item
        for item in index
        if item.get("status") in {"已预约", "排队中", "候补中"}
        and (target_dates is None or item.get("date") in target_dates)
    ]
    if len(active) > live.MAX_DETAIL_RECORDS:
        raise ballet.SyncFailure("source_changed")

    def load_detail(item: dict[str, Any]) -> dict[str, Any] | None:
        detail_html = source.request(item["detailPath"], "约课记录明细")
        detail = ballet.parse_detail(detail_html, item["sourceRecordId"])
        normalized = ballet.normalize_upcoming(detail)
        if normalized is None:
            return None
        return live.public_record(
            normalized,
            (
                "bookingStatus",
                "waitlistPosition",
                "cancelRuleText",
                "cancelHoursBefore",
                "cancelDeadlineAt",
            ),
        )

    with ThreadPoolExecutor(
        max_workers=min(max_workers, max(1, len(active)))
    ) as executor:
        records = [
            record
            for record in executor.map(load_detail, active)
            if record is not None
        ]
    records.sort(
        key=lambda item: (item["date"], item["startTime"], item["courseName"])
    )
    return {"records": records}


def occurrence_key(target: dict[str, Any]) -> str:
    value = "\x1f".join(
        str(target[field])
        for field in (
            "key",
            "date",
            "startTime",
            "endTime",
            "courseType",
            "level",
        )
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def default_state() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "totalRuns": 0,
        "totalBooked": 0,
        "totalWaitlisted": 0,
        "lastAttemptAt": None,
        "lastSuccessAt": None,
        "bookedOccurrences": [],
        "terminalOutcomes": {},
        "lastRun": None,
    }


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return default_state()
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise FastBookingFailure("configuration_error")
    if (
        not isinstance(state, dict)
        or state.get("schemaVersion") != 1
        or not isinstance(state.get("bookedOccurrences"), list)
        or not isinstance(state.get("terminalOutcomes", {}), dict)
    ):
        raise FastBookingFailure("configuration_error")
    return {**default_state(), **state}


def safe_record(target: dict[str, Any], status: str, **extra: Any) -> dict[str, Any]:
    allowed_extra = {
        key: value
        for key, value in extra.items()
        if key
        in {
            "attempts",
            "availability",
            "bookingStatus",
            "waitlistPosition",
            "elapsedMilliseconds",
            "verified",
            "verificationAttempts",
        }
    }
    return {**public_target(target), "status": status, **allowed_extra}


def existing_booking_matches(
    records: list[dict[str, Any]], target: dict[str, Any]
) -> dict[str, Any] | None:
    return next(
        (record for record in records if record_matches(record, target)),
        None,
    )


def run_fast(
    source: Any,
    config: dict[str, Any],
    state: dict[str, Any],
    release_at: datetime,
    execute: bool,
    sleeper: Any = time.sleep,
) -> tuple[dict[str, Any], dict[str, Any]]:
    run_started = time.monotonic()
    planned_targets = materialize_targets(config, release_at)
    booked_occurrences = set(state.get("bookedOccurrences", []))
    terminal_outcomes = dict(state.get("terminalOutcomes", {}))
    records: list[dict[str, Any]] = []
    verification_targets: list[tuple[int, dict[str, Any], bool, str]] = []
    newly_booked_occurrences: set[str] = set()
    newly_waitlisted_occurrences: set[str] = set()
    global_stop_reason = ""
    mutation_wall_milliseconds = 0
    last_mutation_at_milliseconds = 0

    prefetch_started = time.monotonic()
    unique_dates = list(
        dict.fromkeys(target["date"] for target in planned_targets)
    )
    prefetched_pages: dict[str, str | Exception] = {}

    def fetch_date(target_date: str) -> str:
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                return source.request(
                    f"{ballet.TIMETABLE_PATH}/{target_date}", "classtable"
                )
            except (booking.BookingFailure, ballet.SyncFailure) as failure:
                if (
                    getattr(failure, "code", "")
                    not in {"network_error", "http_error"}
                    or attempt > MAX_RETRIES
                ):
                    raise
                sleeper(RETRY_DELAYS_SECONDS[attempt - 1])
        raise FastBookingFailure("network_error")

    def page_target_count(target_date: str, page: str) -> int:
        date_rules = [
            target for target in planned_targets if target["date"] == target_date
        ]
        return sum(
            1
            for entry in parse_timetable_entries(page, target_date)
            if any(rule_matches(entry["record"], rule) for rule in date_rules)
        )

    def refresh_discovery_pages(
        initial_pages: dict[str, str | Exception],
    ) -> dict[str, str | Exception]:
        pages = dict(initial_pages)
        refresh_started = time.monotonic()
        for offset in config["discoveryRefreshSeconds"]:
            sleeper(
                max(
                    0.0,
                    float(offset) - (time.monotonic() - refresh_started),
                )
            )
            with ThreadPoolExecutor(
                max_workers=min(DISCOVERY_WORKERS, len(unique_dates))
            ) as refresh_pool:
                futures = {
                    target_date: refresh_pool.submit(fetch_date, target_date)
                    for target_date in unique_dates
                }
                for target_date, future in futures.items():
                    try:
                        refreshed = future.result()
                        current = pages.get(target_date)
                        if (
                            isinstance(current, Exception)
                            or page_target_count(target_date, refreshed)
                            >= page_target_count(target_date, current)
                        ):
                            pages[target_date] = refreshed
                    except (booking.BookingFailure, ballet.SyncFailure) as failure:
                        if isinstance(pages.get(target_date), Exception):
                            pages[target_date] = failure
        return pages

    with ThreadPoolExecutor(
        max_workers=min(PREFETCH_WORKERS, len(unique_dates))
    ) as prefetch_executor:
        page_futures = {
            target_date: prefetch_executor.submit(fetch_date, target_date)
            for target_date in unique_dates
        }
        for target_date, future in page_futures.items():
            try:
                prefetched_pages[target_date] = future.result()
            except (booking.BookingFailure, ballet.SyncFailure) as failure:
                prefetched_pages[target_date] = failure
    prefetch_wall_milliseconds = round(
        (time.monotonic() - prefetch_started) * 1000
    )
    discovery_executor = ThreadPoolExecutor(max_workers=1)
    discovery_started = time.monotonic()
    discovery_future = discovery_executor.submit(
        refresh_discovery_pages, prefetched_pages
    )
    targets = discover_targets(config, planned_targets, prefetched_pages)

    cached_candidates: dict[str, list[dict[str, Any]] | Exception] = {}
    preflight_executor = ThreadPoolExecutor(max_workers=PREFLIGHT_WORKERS)
    preflight_futures: dict[str, Future[dict[str, Any]]] = {}
    for target in targets:
        if target.get("_discoveryFailure") is not None:
            cached_candidates[target["key"]] = target["_discoveryFailure"]
            continue
        occurrence = occurrence_key(target)
        if occurrence in booked_occurrences:
            continue
        page = prefetched_pages[target["date"]]
        if isinstance(page, Exception):
            cached_candidates[target["key"]] = page
            continue
        try:
            candidates = timetable_candidates(source, target, page)
            cached_candidates[target["key"]] = candidates
            if len(candidates) != 1:
                continue
            availability = candidates[0]["record"]["availability"]
            actionable = availability == "available" or (
                availability == "queue_available" and config["allowWaitlist"]
            )
            if actionable:
                preflight_futures[target["key"]] = preflight_executor.submit(
                    prepare_candidate, source, candidates[0]
                )
        except (booking.BookingFailure, ballet.SyncFailure) as failure:
            cached_candidates[target["key"]] = failure

    target_index = 0
    discovery_settled = False
    discovery_wall_milliseconds = 0
    while True:
        needs_settle = not discovery_settled and (
            target_index >= len(targets)
            or course_priority_rank(
                targets[target_index], config["priorityCourses"]
            )
            != 0
        )
        if needs_settle:
            settled_pages = discovery_future.result()
            discovery_executor.shutdown(wait=True, cancel_futures=True)
            discovery_wall_milliseconds = round(
                (time.monotonic() - discovery_started) * 1000
            )
            discovery_settled = True
            processed_keys = {record["key"] for record in records}
            targets = [
                target
                for target in discover_targets(
                    config, planned_targets, settled_pages
                )
                if target["key"] not in processed_keys
            ]
            target_index = 0
            for target in targets:
                if target.get("_discoveryFailure") is not None:
                    cached_candidates[target["key"]] = target[
                        "_discoveryFailure"
                    ]
                    continue
                occurrence = occurrence_key(target)
                if occurrence in booked_occurrences:
                    continue
                page = settled_pages[target["date"]]
                if isinstance(page, Exception):
                    cached_candidates[target["key"]] = page
                    continue
                try:
                    candidates = timetable_candidates(source, target, page)
                    cached_candidates[target["key"]] = candidates
                    if len(candidates) != 1:
                        continue
                    availability = candidates[0]["record"]["availability"]
                    actionable = availability == "available" or (
                        availability == "queue_available"
                        and config["allowWaitlist"]
                    )
                    if actionable and target["key"] not in preflight_futures:
                        preflight_futures[target["key"]] = (
                            preflight_executor.submit(
                                prepare_candidate, source, candidates[0]
                            )
                        )
                except (booking.BookingFailure, ballet.SyncFailure) as failure:
                    cached_candidates[target["key"]] = failure
            continue

        if target_index >= len(targets):
            break
        target = targets[target_index]
        target_index += 1

        target_started = time.monotonic()
        if global_stop_reason:
            records.append(
                safe_record(
                    target,
                    "not_attempted",
                    attempts=0,
                    elapsedMilliseconds=0,
                )
            )
            continue
        if target.get("_discoveryFailure") is not None:
            failure = target["_discoveryFailure"]
            records.append(
                safe_record(
                    target,
                    getattr(failure, "code", "network_error"),
                    attempts=1,
                    elapsedMilliseconds=round(
                        (time.monotonic() - target_started) * 1000
                    ),
                )
            )
            continue
        occurrence = occurrence_key(target)
        if occurrence in booked_occurrences:
            outcome = terminal_outcomes.get(occurrence, "booked")
            records.append(
                safe_record(
                    target,
                    (
                        "already_waitlisted"
                        if outcome == "waitlisted"
                        else "already_booked"
                    ),
                    attempts=0,
                    elapsedMilliseconds=0,
                )
            )
            continue
        for attempt in range(1, MAX_RETRIES + 2):
            mutation_submitted = False
            result_target = target
            try:
                if attempt == 1:
                    candidates_or_failure = cached_candidates.get(target["key"])
                    if isinstance(candidates_or_failure, Exception):
                        raise candidates_or_failure
                    candidates = candidates_or_failure or []
                else:
                    candidates = timetable_candidates(source, target)
                if len(candidates) != 1:
                    raise FastBookingFailure("course_not_unique")
                candidate = candidates[0]
                result_target = {
                    **target,
                    "_selectedVenue": candidate["record"].get("venue"),
                }
                availability = candidate["record"]["availability"]
                if availability == "booked":
                    records.append(
                        safe_record(
                            result_target,
                            "already_booked",
                            attempts=attempt,
                            elapsedMilliseconds=round(
                                (time.monotonic() - target_started) * 1000
                            ),
                        )
                    )
                    break
                if availability == "waitlist":
                    records.append(
                        safe_record(
                            result_target,
                            "already_waitlisted",
                            attempts=attempt,
                            availability=availability,
                            **(
                                {
                                    "waitlistPosition": candidate["record"][
                                        "waitlistPosition"
                                    ]
                                }
                                if isinstance(
                                    candidate["record"].get("waitlistPosition"), int
                                )
                                else {}
                            ),
                            elapsedMilliseconds=round(
                                (time.monotonic() - target_started) * 1000
                            ),
                        )
                    )
                    break
                is_waitlist_action = (
                    availability == "queue_available" and config["allowWaitlist"]
                )
                if availability != "available" and not is_waitlist_action:
                    records.append(
                        safe_record(
                            result_target,
                            "not_available",
                            attempts=attempt,
                            availability=availability,
                            elapsedMilliseconds=round(
                                (time.monotonic() - target_started) * 1000
                            ),
                        )
                    )
                    break
                prepared = None
                if attempt == 1 and target["key"] in preflight_futures:
                    prepared = preflight_futures[target["key"]].result()
                    if (
                        time.monotonic() - prepared["completedAt"]
                        > PREFLIGHT_TTL_SECONDS
                    ):
                        prepared = None
                if prepared is None:
                    prepared = prepare_candidate(source, candidate)
                contract = prepared["contract"]
                card_id = prepared["cardId"]
                if not execute:
                    records.append(
                        safe_record(
                            result_target,
                            "ready_waitlist" if is_waitlist_action else "ready",
                            availability=availability,
                            attempts=attempt,
                            elapsedMilliseconds=round(
                                (time.monotonic() - target_started) * 1000
                            ),
                        )
                    )
                    break
                mutation_submitted = True
                mutation_started = time.monotonic()
                try:
                    mutation = booking.response_json(
                        source.post_fields(
                            contract["bookingPath"],
                            {
                                "classtableid": contract["classTableId"],
                                "cardid": card_id,
                            },
                            mutation=True,
                        )
                    )
                finally:
                    mutation_wall_milliseconds += round(
                        (time.monotonic() - mutation_started) * 1000
                    )
                    last_mutation_at_milliseconds = round(
                        (time.monotonic() - run_started) * 1000
                    )
                if (
                    isinstance(mutation, int)
                    and not isinstance(mutation, bool)
                    and mutation > 0
                ):
                    intended_outcome = (
                        "waitlisted" if is_waitlist_action else "booked"
                    )
                    records.append(
                        safe_record(
                            result_target,
                            intended_outcome,
                            availability=availability,
                            attempts=attempt,
                            elapsedMilliseconds=round(
                                (time.monotonic() - target_started) * 1000
                            ),
                            verified=False,
                        )
                    )
                    verification_targets.append(
                        (
                            len(records) - 1,
                            result_target,
                            True,
                            intended_outcome,
                        )
                    )
                    booked_occurrences.add(occurrence)
                    terminal_outcomes[occurrence] = intended_outcome
                    if intended_outcome == "waitlisted":
                        newly_waitlisted_occurrences.add(occurrence)
                    else:
                        newly_booked_occurrences.add(occurrence)
                    break
                if isinstance(mutation, str) and mutation in {
                    "FULL",
                    "STOPPED",
                    "NOTOPEN",
                }:
                    code = str(mutation).lower()
                    if code == "notopen" and attempt <= MAX_RETRIES:
                        sleeper(RETRY_DELAYS_SECONDS[attempt - 1])
                        continue
                    records.append(
                        safe_record(
                            result_target,
                            code,
                            attempts=attempt,
                            elapsedMilliseconds=round(
                                (time.monotonic() - target_started) * 1000
                            ),
                        )
                    )
                    break
                raise booking.BookingFailure("unknown_result")
            except (
                FastBookingFailure,
                booking.BookingFailure,
                ballet.SyncFailure,
            ) as failure:
                code = getattr(failure, "code", "unknown_result")
                if mutation_submitted and code != "auth_required":
                    code = "unknown_result"
                if code in GLOBAL_STOP_CODES:
                    records.append(
                        safe_record(
                            result_target,
                            code,
                            attempts=attempt,
                            elapsedMilliseconds=round(
                                (time.monotonic() - target_started) * 1000
                            ),
                        )
                    )
                    global_stop_reason = code
                    break
                if (
                    not mutation_submitted
                    and code in RETRIABLE_PREFLIGHT_CODES
                    and attempt <= MAX_RETRIES
                ):
                    sleeper(RETRY_DELAYS_SECONDS[attempt - 1])
                    continue
                records.append(
                    safe_record(
                        result_target,
                        code,
                        attempts=attempt,
                        elapsedMilliseconds=round(
                            (time.monotonic() - target_started) * 1000
                        ),
                        **(
                            {"verified": False}
                            if mutation_submitted
                            else {}
                        ),
                    )
                )
                if mutation_submitted:
                    verification_targets.append(
                        (
                            len(records) - 1,
                            result_target,
                            False,
                            "waitlisted" if is_waitlist_action else "booked",
                        )
                    )
                break

    if not discovery_settled:
        discovery_future.result()
        discovery_executor.shutdown(wait=True, cancel_futures=True)
        discovery_wall_milliseconds = round(
            (time.monotonic() - discovery_started) * 1000
        )
    preflight_executor.shutdown(wait=True, cancel_futures=True)
    critical_path_milliseconds = round((time.monotonic() - run_started) * 1000)
    verification_error = ""
    verification_started = time.monotonic()
    if execute and verification_targets:
        unresolved = list(verification_targets)
        verification_retry_started = time.monotonic()
        verification_offsets = [0.0, *config["unknownVerificationSeconds"]]
        for verification_attempt, offset in enumerate(
            verification_offsets, start=1
        ):
            if verification_attempt > 1:
                retryable = [item for item in unresolved if not item[2]]
                if not retryable:
                    break
                sleeper(
                    max(
                        0.0,
                        float(offset)
                        - (time.monotonic() - verification_retry_started),
                    )
                )
                selected = retryable
                target_dates = {item[1]["date"] for item in selected}
            else:
                selected = unresolved
                target_dates = None
            try:
                bookings = query_bookings_parallel(
                    source, target_dates=target_dates
                )["records"]
            except (booking.BookingFailure, ballet.SyncFailure):
                continue
            remaining = []
            selected_indexes = {item[0] for item in selected}
            for index, target, acknowledged, intended_outcome in unresolved:
                if index not in selected_indexes:
                    remaining.append(
                        (index, target, acknowledged, intended_outcome)
                    )
                    continue
                records[index]["verificationAttempts"] = verification_attempt
                matched = existing_booking_matches(bookings, target)
                verified = matched is not None
                records[index]["verified"] = verified
                if matched is not None:
                    booking_status = matched.get("bookingStatus")
                    final_outcome = (
                        "waitlisted" if booking_status == "waitlist" else "booked"
                    )
                    records[index]["status"] = final_outcome
                    records[index]["bookingStatus"] = booking_status
                    if (
                        final_outcome == "waitlisted"
                        and isinstance(matched.get("waitlistPosition"), int)
                    ):
                        records[index]["waitlistPosition"] = matched["waitlistPosition"]
                    occurrence = occurrence_key(target)
                    booked_occurrences.add(occurrence)
                    terminal_outcomes[occurrence] = final_outcome
                    if final_outcome == "waitlisted":
                        newly_booked_occurrences.discard(occurrence)
                        newly_waitlisted_occurrences.add(occurrence)
                    else:
                        newly_waitlisted_occurrences.discard(occurrence)
                        newly_booked_occurrences.add(occurrence)
                else:
                    remaining.append(
                        (index, target, acknowledged, intended_outcome)
                    )
                    if not acknowledged:
                        records[index]["status"] = "unknown_result"
            unresolved = remaining
        if any(
            not records[index]["verified"]
            for index, _, _, _ in verification_targets
        ):
            verification_error = "verification_unavailable"
    verification_wall_milliseconds = round(
        (time.monotonic() - verification_started) * 1000
    )

    now_text = ballet.iso_now()
    record_failures = any(
        record["status"]
        not in {
            "already_booked",
            "already_waitlisted",
            "booked",
            "waitlisted",
            "ready",
            "ready_waitlist",
        }
        for record in records
    )
    run_status = (
        "stopped"
        if global_stop_reason
        else "partial"
        if record_failures
        else "completed_unverified"
        if verification_error
        else "success"
    )
    result = {
        "status": run_status,
        "mode": "execute" if execute else "dry-run",
        "attemptedAt": now_text,
        "releaseAt": release_at.isoformat(timespec="seconds"),
        "records": records,
        "requestsMade": getattr(source, "request_count", 0),
        "mutationAttempts": getattr(source, "mutation_count", 0),
        "criticalPathMilliseconds": critical_path_milliseconds,
        "totalMilliseconds": round((time.monotonic() - run_started) * 1000),
        "timings": {
            "prefetchWallMilliseconds": prefetch_wall_milliseconds,
            "discoveryWallMilliseconds": discovery_wall_milliseconds,
            "mutationWallMilliseconds": mutation_wall_milliseconds,
            "lastMutationAtMilliseconds": last_mutation_at_milliseconds,
            "verificationWallMilliseconds": verification_wall_milliseconds,
            "requestsByStage": (
                source.timing_summary()
                if callable(getattr(source, "timing_summary", None))
                else {}
            ),
        },
        **(
            {"stopReason": global_stop_reason}
            if global_stop_reason
            else {}
        ),
        **({"verification": verification_error} if verification_error else {}),
    }
    if execute:
        state = {
            **state,
            "schemaVersion": 1,
            "totalRuns": int(state.get("totalRuns", 0)) + 1,
            "totalBooked": int(state.get("totalBooked", 0))
            + len(newly_booked_occurrences),
            "totalWaitlisted": int(state.get("totalWaitlisted", 0))
            + len(newly_waitlisted_occurrences),
            "lastAttemptAt": now_text,
            "lastSuccessAt": (
                now_text
                if run_status in {"success", "completed_unverified"}
                else state.get("lastSuccessAt")
            ),
            "bookedOccurrences": sorted(booked_occurrences),
            "terminalOutcomes": terminal_outcomes,
            "lastRun": result,
        }
    return result, state


def build_public(
    config: dict[str, Any],
    state: dict[str, Any],
    now: datetime,
    preview_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    next_run = next_release_at(now, config)
    targets = materialize_targets(config, next_run)
    last_run = state.get("lastRun")
    return {
        "schemaVersion": 1,
        "timezone": "Asia/Shanghai",
        "enabled": config["enabled"],
        "waitlistEnabled": config["allowWaitlist"],
        "schedule": "每周日 14:20（北京时间）",
        "planMode": "weekly-rules",
        "coursePriorityOrder": ["芭蕾 L1", "芭蕾 L1.5", "软开 / 软开课"],
        "priorityOrder": ["周六", "周一", "周二", "周三", "周四", "周五"],
        "prioritySummary": (
            "芭蕾 L1 > 芭蕾 L1.5 > 软开 / 软开课；每类先周六，再周一至周五；"
            "工作日仅 18:40 后、周六全天；"
            "软开严格排除软开专项 / 软开-胯；教室按大教室 > 小教室兜底"
        ),
        "lastAttemptAt": state.get("lastAttemptAt"),
        "lastSuccessAt": state.get("lastSuccessAt"),
        "nextRunAt": next_run.isoformat(timespec="seconds"),
        "totalRuns": int(state.get("totalRuns", 0)),
        "totalBooked": int(state.get("totalBooked", 0)),
        "totalWaitlisted": int(state.get("totalWaitlisted", 0)),
        "lastStatus": (
            last_run.get("status")
            if isinstance(last_run, dict)
            else "waiting"
        ),
        "targets": [public_target(target) for target in targets],
        "lastRun": (
            {
                key: last_run.get(key)
                for key in (
                    "status",
                    "attemptedAt",
                    "releaseAt",
                    "records",
                    "criticalPathMilliseconds",
                    "totalMilliseconds",
                    "timings",
                )
            }
            if isinstance(last_run, dict)
            else None
        ),
        "preview": (
            {
                key: preview_result.get(key)
                for key in (
                    "status",
                    "attemptedAt",
                    "releaseAt",
                    "records",
                    "criticalPathMilliseconds",
                    "totalMilliseconds",
                    "timings",
                )
            }
            if isinstance(preview_result, dict)
            else None
        ),
        "generatedAt": ballet.iso_now(now),
    }


def atomic_write(path: Path, text: str, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8")
    os.chmod(temporary, mode)
    temporary.replace(path)


def write_outputs(
    state_path: Path,
    public_path: Path,
    wrapper_path: Path,
    state: dict[str, Any],
    public: dict[str, Any],
) -> None:
    atomic_write(
        state_path,
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        0o600,
    )
    public_text = json.dumps(public, ensure_ascii=False, indent=2)
    atomic_write(public_path, public_text + "\n", 0o640)
    atomic_write(
        wrapper_path,
        f"window.MAXNOW_BALLET_BOOKING_FAST_DATA = {public_text};\n",
        0o640,
    )


def wait_until(release_at: datetime) -> None:
    while True:
        remaining = release_at.timestamp() - time.time()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 0.25))


def credential_path() -> Path:
    directory = os.environ.get("CREDENTIALS_DIRECTORY")
    if not directory:
        raise FastBookingFailure("configuration_error")
    return Path(directory) / "wenda-session.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", choices=("status", "preview", "dry-run", "execute")
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/ballet-booking-fast.json"),
    )
    parser.add_argument(
        "--state",
        type=Path,
        default=Path("/var/lib/maxnow-ballet-booking-fast/state.json"),
    )
    parser.add_argument(
        "--public",
        type=Path,
        default=Path(
            "/var/lib/maxnow-ballet-booking-fast-public/ballet-booking-fast.json"
        ),
    )
    parser.add_argument(
        "--wrapper",
        type=Path,
        default=Path(
            "/var/lib/maxnow-ballet-booking-fast-public/ballet-booking-fast.js"
        ),
    )
    parser.add_argument("--now", help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    now = (
        datetime.fromisoformat(args.now).astimezone(ballet.TIMEZONE)
        if args.now
        else datetime.now(ballet.TIMEZONE)
    )
    config = load_config(args.config)
    state = load_state(args.state)
    result = None
    try:
        if args.mode == "status":
            public = build_public(config, state, now)
            print(json.dumps(public, ensure_ascii=False, separators=(",", ":")))
            return 0
        if args.mode == "preview":
            public = build_public(config, state, now)
            write_outputs(
                args.state,
                args.public,
                args.wrapper,
                state,
                public,
            )
            print(json.dumps(public, ensure_ascii=False, separators=(",", ":")))
            return 0
        release_at = next_release_at(now, config)
        if args.mode == "execute":
            seconds_until = release_at.timestamp() - now.timestamp()
            if (
                not config["enabled"]
                or now.weekday() != config["release"]["weekday"]
                or not -60 <= seconds_until <= 90
            ):
                raise FastBookingFailure("outside_window")
        source = PersistentWendaBookingSource(
            ballet.load_credentials(credential_path()),
            timeout_seconds=5,
        )
        try:
            if args.mode == "execute":
                source.request(
                    f"{ballet.TIMETABLE_PATH}/{now.date().isoformat()}",
                    "classtable",
                )
                wait_until(release_at)
            result, state = run_fast(
                source,
                config,
                state,
                release_at,
                execute=args.mode == "execute",
            )
        finally:
            source.close()
        public = build_public(
            config,
            state,
            datetime.now(ballet.TIMEZONE),
            preview_result=result if args.mode == "dry-run" else None,
        )
        write_outputs(
            args.state,
            args.public,
            args.wrapper,
            state,
            public,
        )
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return (
            0
            if result["status"]
            in {"success", "partial", "completed_unverified"}
            else 4
        )
    except (FastBookingFailure, booking.BookingFailure, ballet.SyncFailure) as failure:
        code = getattr(failure, "code", "unknown_result")
        if args.mode == "execute":
            attempted_at = ballet.iso_now()
            error_run = {
                "status": code,
                "attemptedAt": attempted_at,
                "releaseAt": None,
                "records": [],
            }
            state = {
                **state,
                "totalRuns": int(state.get("totalRuns", 0)) + 1,
                "lastAttemptAt": attempted_at,
                "lastRun": error_run,
            }
        error = {
            "status": code,
            "message": PUBLIC_ERROR_LABELS.get(
                code, "自动抢课未完成，详细错误已安全隐藏。"
            ),
            "attemptedAt": ballet.iso_now(),
        }
        public = build_public(config, state, datetime.now(ballet.TIMEZONE))
        public["lastStatus"] = code
        public["lastError"] = error["message"]
        write_outputs(
            args.state,
            args.public,
            args.wrapper,
            state,
            public,
        )
        print(json.dumps(error, ensure_ascii=False, separators=(",", ":")))
        return 2 if code == "auth_required" else 4


if __name__ == "__main__":
    raise SystemExit(main())
