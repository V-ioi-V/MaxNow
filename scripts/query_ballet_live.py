from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import sync_ballet as ballet


sys.dont_write_bytecode = True

MAX_TIMETABLE_DAYS = 14
MAX_DETAIL_RECORDS = 200
LIVE_ERROR_MESSAGES = {
    "auth_required": "实时查询未返回数据；微信授权或闻道会话已失效，请更新服务器凭据。",
    "network_error": "实时查询未返回数据；MaxNow 服务器暂时无法连接闻道。",
    "http_error": "实时查询未返回数据；闻道只读接口暂时异常。",
    "source_changed": "实时查询未返回数据；闻道页面结构或数据范围发生变化。",
    "parse_error": "实时查询未返回数据；闻道返回内容无法安全解析。",
    "configuration_error": "实时查询未执行；查询参数或服务器配置不安全。",
}
SAFE_RECORD_FIELDS = (
    "courseName",
    "courseType",
    "level",
    "date",
    "startTime",
    "endTime",
    "durationMinutes",
    "teacher",
    "venue",
    "studio",
)


def parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ballet.SyncFailure("configuration_error")


def credential_path(provided: Path | None) -> Path:
    if provided is not None:
        return provided
    directory = os.environ.get("CREDENTIALS_DIRECTORY")
    if not directory:
        raise ballet.SyncFailure("configuration_error")
    return Path(directory) / "wenda-session.json"


def date_range(from_date: date, through_date: date) -> list[date]:
    days = (through_date - from_date).days + 1
    if days < 1 or days > MAX_TIMETABLE_DAYS:
        raise ballet.SyncFailure("configuration_error")
    return [from_date + timedelta(days=offset) for offset in range(days)]


def public_record(
    record: dict[str, Any], extra_fields: tuple[str, ...] = ()
) -> dict[str, Any]:
    fields = SAFE_RECORD_FIELDS + extra_fields
    return {field: record.get(field) for field in fields}


def query_timetable(
    source: ballet.WendaSource | ballet.FixtureSource,
    from_date: date,
    through_date: date,
) -> dict[str, Any]:
    days = []
    for course_date in date_range(from_date, through_date):
        day = course_date.isoformat()
        html = source.request(f"{ballet.TIMETABLE_PATH}/{day}", "classtable")
        parsed = ballet.parse_timetable(html, day)
        days.append(
            {
                "date": day,
                "records": [
                    public_record(
                        record,
                        ("bookedCount", "capacity", "availability"),
                    )
                    for record in parsed["records"]
                ],
            }
        )
    return {
        "from": from_date.isoformat(),
        "through": through_date.isoformat(),
        "days": days,
    }


def query_bookings(
    source: ballet.WendaSource | ballet.FixtureSource,
) -> dict[str, Any]:
    html = source.request(ballet.BOOKING_PATH, "约课记录")
    index = ballet.parse_index(html, "booking")
    active = [
        item
        for item in index
        if item.get("status") in {"已预约", "排队中", "候补中"}
    ]
    if len(active) > MAX_DETAIL_RECORDS:
        raise ballet.SyncFailure("source_changed")
    records = []
    for item in active:
        detail_html = source.request(item["detailPath"], "约课记录明细")
        detail = ballet.parse_detail(detail_html, item["sourceRecordId"])
        normalized = ballet.normalize_upcoming(detail)
        if normalized is not None:
            records.append(
                public_record(
                    normalized,
                    (
                        "bookingStatus",
                        "waitlistPosition",
                        "cancelRuleText",
                        "cancelHoursBefore",
                        "cancelDeadlineAt",
                    ),
                )
            )
    records.sort(
        key=lambda item: (item["date"], item["startTime"], item["courseName"])
    )
    return {"records": records}


def query_attendance(
    source: ballet.WendaSource | ballet.FixtureSource,
    from_date: date | None,
    through_date: date | None,
) -> dict[str, Any]:
    index = ballet.fetch_attendance_index(source)
    selected = []
    for item in index:
        try:
            item_date = date.fromisoformat(item["date"])
        except ValueError:
            raise ballet.SyncFailure("source_changed")
        if from_date and item_date < from_date:
            continue
        if through_date and item_date > through_date:
            continue
        if item.get("summaryOnly") == "true":
            raise ballet.SyncFailure("source_changed")
        selected.append(item)
    if len(selected) > MAX_DETAIL_RECORDS:
        raise ballet.SyncFailure("source_changed")

    observed_at = ballet.iso_now()
    records = []
    for item in selected:
        detail_html = source.request(item["detailPath"], "约课记录明细")
        detail = ballet.parse_detail(detail_html, item["sourceRecordId"])
        normalized = ballet.normalize_attendance(detail, observed_at)
        records.append(public_record(normalized, ("attendanceStatus",)))
    records.sort(
        key=lambda item: (item["date"], item["startTime"], item["courseName"])
    )
    return {
        "from": from_date.isoformat() if from_date else None,
        "through": through_date.isoformat() if through_date else None,
        "records": records,
    }


def query_membership(
    source: ballet.WendaSource | ballet.FixtureSource,
) -> dict[str, Any]:
    html = source.request(ballet.MEMBERSHIP_PATH, "我的会员卡")
    return {"cards": ballet.parse_membership(html)}


def run_query(
    source: ballet.WendaSource | ballet.FixtureSource,
    scope: str,
    from_date: date | None,
    through_date: date | None,
    now: datetime | None = None,
) -> dict[str, Any]:
    current_date = (now or datetime.now(ballet.TIMEZONE)).astimezone(
        ballet.TIMEZONE
    ).date()
    if scope == "timetable":
        start = from_date or current_date
        end = through_date or start
        data = query_timetable(source, start, end)
    elif scope == "bookings":
        if from_date or through_date:
            raise ballet.SyncFailure("configuration_error")
        data = query_bookings(source)
    elif scope == "attendance":
        if from_date and through_date and through_date < from_date:
            raise ballet.SyncFailure("configuration_error")
        data = query_attendance(source, from_date, through_date)
    elif scope == "membership":
        if from_date or through_date:
            raise ballet.SyncFailure("configuration_error")
        data = query_membership(source)
    else:
        raise ballet.SyncFailure("configuration_error")

    return {
        "schemaVersion": 1,
        "source": "wenda-live",
        "status": "success",
        "live": True,
        "fetchedAt": ballet.iso_now(now),
        "scope": scope,
        "requestsMade": source.request_count,
        "data": data,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query live read-only Wenda ballet data without MaxNow caches."
    )
    parser.add_argument(
        "scope",
        choices=("timetable", "bookings", "attendance", "membership"),
    )
    parser.add_argument("--from-date")
    parser.add_argument("--through-date")
    parser.add_argument("--credential-file", type=Path)
    parser.add_argument("--fixture-dir", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--now", help=argparse.SUPPRESS)
    return parser.parse_args()


def safe_error(code: str, scope: str) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "source": "wenda-live",
        "status": code,
        "live": False,
        "fetchedAt": ballet.iso_now(),
        "scope": scope,
        "error": LIVE_ERROR_MESSAGES.get(code, "实时查询未返回数据。"),
    }


def main() -> int:
    args = parse_args()
    try:
        from_date = parse_date(args.from_date)
        through_date = parse_date(args.through_date)
        now = ballet.parse_now(args.now)
        if args.fixture_dir:
            source: ballet.WendaSource | ballet.FixtureSource = ballet.FixtureSource(
                args.fixture_dir
            )
        else:
            source = ballet.WendaSource(
                ballet.load_credentials(credential_path(args.credential_file))
            )
        result = run_query(source, args.scope, from_date, through_date, now)
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return 0
    except ballet.SyncFailure as failure:
        print(
            json.dumps(
                safe_error(failure.code, args.scope),
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return {
            "auth_required": 2,
            "network_error": 3,
            "http_error": 3,
        }.get(failure.code, 4)
    except Exception:
        print(
            json.dumps(
                safe_error("parse_error", args.scope),
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
