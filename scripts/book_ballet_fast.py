from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
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
        or data.get("schemaVersion") != 1
        or data.get("timezone") != "Asia/Shanghai"
        or not isinstance(data.get("enabled"), bool)
        or not isinstance(data.get("release"), dict)
        or data["release"].get("weekday") != 6
        or not isinstance(data.get("priorityWeekdays"), list)
        or not isinstance(data.get("targets"), list)
        or not data["targets"]
        or len(data["targets"]) > 10
    ):
        raise FastBookingFailure("configuration_error")
    parse_hhmm(data["release"].get("time"))
    priorities = data["priorityWeekdays"]
    if priorities != [5, 6, 4]:
        raise FastBookingFailure("configuration_error")
    required = {
        "key",
        "weekday",
        "courseType",
        "level",
        "startTime",
        "endTime",
        "teacher",
        "allowBlankTeacher",
        "venue",
    }
    keys = set()
    for target in data["targets"]:
        if not isinstance(target, dict) or set(target) != required:
            raise FastBookingFailure("configuration_error")
        if (
            not isinstance(target["key"], str)
            or not target["key"]
            or target["key"] in keys
            or target["weekday"] not in range(7)
            or target["courseType"] not in COURSE_TYPE_LABELS
            or target["level"] not in {"none", "L1", "L1.5", "L2", "L3", "L4"}
            or not isinstance(target["allowBlankTeacher"], bool)
            or not all(
                isinstance(target[field], str) and target[field].strip()
                for field in ("teacher", "venue")
            )
        ):
            raise FastBookingFailure("configuration_error")
        parse_hhmm(target["startTime"])
        parse_hhmm(target["endTime"])
        keys.add(target["key"])
    return data


def priority_rank(weekday: int, priorities: list[int]) -> tuple[int, int]:
    try:
        return priorities.index(weekday), weekday
    except ValueError:
        return len(priorities), weekday


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
    for order, configured in enumerate(config["targets"]):
        targets.append(
            {
                **configured,
                "date": target_date(
                    release_at.astimezone(ballet.TIMEZONE).date(),
                    configured["weekday"],
                ).isoformat(),
                "_order": order,
            }
        )
    targets.sort(
        key=lambda item: (
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
        "startTime": target["startTime"],
        "endTime": target["endTime"],
        "course": course,
        "teacher": target["teacher"],
        "venue": target["venue"],
    }


def record_matches(record: dict[str, Any], target: dict[str, Any]) -> bool:
    teacher = ballet.normalize_space(str(record.get("teacher", "")))
    expected_teacher = ballet.normalize_space(target["teacher"])
    teacher_matches = teacher == expected_teacher or (
        target["allowBlankTeacher"] and not teacher
    )
    return (
        record.get("date") == target["date"]
        and record.get("courseType") == target["courseType"]
        and record.get("level") == target["level"]
        and record.get("startTime") == target["startTime"]
        and record.get("endTime") == target["endTime"]
        and ballet.normalize_space(str(record.get("venue", "")))
        == ballet.normalize_space(target["venue"])
        and teacher_matches
    )


def timetable_candidates(
    source: Any, target: dict[str, Any]
) -> list[dict[str, Any]]:
    path = f"{ballet.TIMETABLE_PATH}/{target['date']}"
    text = source.request(path, "classtable")
    records = ballet.parse_timetable(text, target["date"])["records"]
    controls, scripts, script_sources = booking.parse_controls(text)
    if len(records) != len(controls):
        raise booking.BookingFailure("source_changed")
    return [
        {
            "record": record,
            "control": control,
            "scripts": scripts,
            "scriptSources": script_sources,
        }
        for record, control in zip(records, controls)
        if record_matches(record, target)
    ]


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
            "teacher",
            "venue",
        )
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def default_state() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "totalRuns": 0,
        "totalBooked": 0,
        "lastAttemptAt": None,
        "lastSuccessAt": None,
        "bookedOccurrences": [],
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
            "elapsedMilliseconds",
            "verified",
        }
    }
    return {**public_target(target), "status": status, **allowed_extra}


def existing_booking_matches(
    records: list[dict[str, Any]], target: dict[str, Any]
) -> bool:
    return any(record_matches(record, target) for record in records)


def run_fast(
    source: Any,
    config: dict[str, Any],
    state: dict[str, Any],
    release_at: datetime,
    execute: bool,
    sleeper: Any = time.sleep,
) -> tuple[dict[str, Any], dict[str, Any]]:
    run_started = time.monotonic()
    targets = materialize_targets(config, release_at)
    booked_occurrences = set(state.get("bookedOccurrences", []))
    records: list[dict[str, Any]] = []
    verification_targets: list[tuple[int, dict[str, Any], bool]] = []
    newly_booked_occurrences: set[str] = set()
    global_stop_reason = ""

    for target in targets:
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
        occurrence = occurrence_key(target)
        if occurrence in booked_occurrences:
            records.append(
                safe_record(
                    target,
                    "already_booked",
                    attempts=0,
                    elapsedMilliseconds=0,
                )
            )
            continue
        for attempt in range(1, MAX_RETRIES + 2):
            mutation_submitted = False
            try:
                candidates = timetable_candidates(source, target)
                if len(candidates) != 1:
                    raise FastBookingFailure("course_not_unique")
                candidate = candidates[0]
                availability = candidate["record"]["availability"]
                if availability == "booked":
                    records.append(
                        safe_record(
                            target,
                            "already_booked",
                            attempts=attempt,
                            elapsedMilliseconds=round(
                                (time.monotonic() - target_started) * 1000
                            ),
                        )
                    )
                    break
                if availability != "available":
                    records.append(
                        safe_record(
                            target,
                            "not_available",
                            attempts=attempt,
                            availability=availability,
                            elapsedMilliseconds=round(
                                (time.monotonic() - target_started) * 1000
                            ),
                        )
                    )
                    break
                contract = booking.booking_contract(candidate)
                card_id = booking.eligible_card(source, contract)
                booking.check_rules(source, contract, card_id)
                if not execute:
                    records.append(
                        safe_record(
                            target,
                            "ready",
                            attempts=attempt,
                            elapsedMilliseconds=round(
                                (time.monotonic() - target_started) * 1000
                            ),
                        )
                    )
                    break
                mutation_submitted = True
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
                if (
                    isinstance(mutation, int)
                    and not isinstance(mutation, bool)
                    and mutation > 0
                ):
                    records.append(
                        safe_record(
                            target,
                            "booked",
                            attempts=attempt,
                            elapsedMilliseconds=round(
                                (time.monotonic() - target_started) * 1000
                            ),
                            verified=False,
                        )
                    )
                    verification_targets.append(
                        (len(records) - 1, target, True)
                    )
                    booked_occurrences.add(occurrence)
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
                            target,
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
                            target,
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
                        target,
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
                        (len(records) - 1, target, False)
                    )
                break

    critical_path_milliseconds = round((time.monotonic() - run_started) * 1000)
    verification_error = ""
    if execute and verification_targets:
        try:
            bookings = live.query_bookings(source)["records"]
            for index, target, acknowledged in verification_targets:
                verified = existing_booking_matches(bookings, target)
                records[index]["verified"] = verified
                if verified:
                    records[index]["status"] = "booked"
                    records[index]["bookingStatus"] = "booked"
                    occurrence = occurrence_key(target)
                    booked_occurrences.add(occurrence)
                    newly_booked_occurrences.add(occurrence)
                elif not acknowledged:
                    records[index]["status"] = "unknown_result"
            if any(
                not records[index]["verified"]
                for index, _, _ in verification_targets
            ):
                verification_error = "verification_unavailable"
        except (booking.BookingFailure, ballet.SyncFailure):
            verification_error = "verification_unavailable"

    now_text = ballet.iso_now()
    record_failures = any(
        record["status"] not in {"already_booked", "booked", "ready"}
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
            "lastAttemptAt": now_text,
            "lastSuccessAt": (
                now_text if run_status in {"success", "completed_unverified"} else state.get("lastSuccessAt")
            ),
            "bookedOccurrences": sorted(booked_occurrences),
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
        "schedule": "每周日 14:20（北京时间）",
        "priorityOrder": ["周六", "周日", "周五", "其他日期"],
        "lastAttemptAt": state.get("lastAttemptAt"),
        "lastSuccessAt": state.get("lastSuccessAt"),
        "nextRunAt": next_run.isoformat(timespec="seconds"),
        "totalRuns": int(state.get("totalRuns", 0)),
        "totalBooked": int(state.get("totalBooked", 0)),
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
        source = booking.WendaBookingSource(
            ballet.load_credentials(credential_path()),
            timeout_seconds=5,
        )
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
