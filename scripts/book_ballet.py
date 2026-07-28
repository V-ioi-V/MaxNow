from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import query_ballet_live as live
import sync_ballet as ballet


sys.dont_write_bytecode = True

BOOKING_SUBMIT_PATH = f"/gm/weixin/classtable/do_addbook/{ballet.STORE_ID}"
CARD_TYPE_PATH = (
    f"/gm/weixin/classtable/check_cardtypecourse/{ballet.STORE_ID}"
)
GET_USING_CARD_PATH = (
    f"/gm/weixin/classtable/getusingcard/{ballet.STORE_ID}"
)
CHECK_RULES_PREFIX = (
    f"/gm/weixin/classtable/check_rules/{ballet.STORE_ID}/"
)
MAX_COURSES = 10
TIME_PATTERN = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d")


class BookingFailure(Exception):
    def __init__(self, code: str, diagnostic: dict[str, Any] | None = None):
        super().__init__(code)
        self.code = code
        self.diagnostic = diagnostic


class BookingControlParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.div_depth = 0
        self.root_depth = 0
        self.current: dict[str, Any] | None = None
        self.controls: list[dict[str, Any]] = []
        self.scripts: list[str] = []
        self.script_sources: list[str] = []
        self.in_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        values = {key: html.unescape(value or "") for key, value in attrs}
        if tag == "script":
            self.in_script = True
            if values.get("src"):
                self.script_sources.append(values["src"])
        if tag == "div":
            self.div_depth += 1
            classes = set(values.get("class", "").split())
            if self.current is None and "classtable" in classes:
                self.root_depth = self.div_depth
                self.current = {"controls": []}
        if self.current is None:
            return
        self.current["controls"].append(
            {
                "tag": tag,
                "attrs": values,
            }
        )
    def handle_endtag(self, tag: str):
        if tag == "script":
            self.in_script = False
        if tag == "div":
            if self.current is not None and self.div_depth == self.root_depth:
                self.controls.append(self.current)
                self.current = None
                self.root_depth = 0
            self.div_depth -= 1

    def handle_data(self, data: str):
        if self.in_script:
            self.scripts.append(data)


def safe_path_shape(value: str) -> str:
    path = urlsplit(value).path
    return re.sub(r"(?<=/)\d+(?=/|$)", ":id", path)


def safe_diagnostic(
    control: dict[str, Any],
    scripts: list[str],
    script_sources: list[str],
) -> dict[str, Any]:
    script_text = "\n".join(scripts)
    buttons = [
        item
        for item in control["controls"]
        if item["tag"] == "button"
        and "bookbtn" in item["attrs"].get("class", "").split()
    ]
    return {
        "bookingButtonCount": len(buttons),
        "bookingButtonAttributeNames": sorted(
            {name for item in buttons for name in item["attrs"]}
        ),
        "scriptSources": sorted({safe_path_shape(item) for item in script_sources}),
        "bookingPathShapes": sorted(
            {
                safe_path_shape(value)
                for value in re.findall(
                    r"[\"']((?:https?://[^\"']+)?/gm/weixin/classtable/"
                    r"[^\"']+)[\"']",
                    script_text,
                )
            }
        ),
    }


def parse_controls(
    text: str,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    parser = BookingControlParser()
    try:
        parser.feed(text)
    except BookingFailure:
        raise
    except Exception:
        raise BookingFailure("parse_error")
    return parser.controls, parser.scripts, parser.script_sources


def parse_request(text: str, execute: bool) -> list[dict[str, str]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        raise BookingFailure("configuration_error")
    if not isinstance(payload, dict) or set(payload) != {"courses", "confirm"}:
        raise BookingFailure("configuration_error")
    if execute and payload.get("confirm") is not True:
        raise BookingFailure("confirmation_required")
    courses = payload.get("courses")
    if not isinstance(courses, list) or not 1 <= len(courses) <= MAX_COURSES:
        raise BookingFailure("configuration_error")
    required = {
        "date",
        "startTime",
        "endTime",
        "courseName",
        "teacher",
        "venue",
    }
    normalized = []
    fingerprints = set()
    for raw in courses:
        if not isinstance(raw, dict) or set(raw) != required:
            raise BookingFailure("configuration_error")
        course = {key: ballet.normalize_space(str(raw[key])) for key in required}
        try:
            day = ballet.date.fromisoformat(course["date"])
        except ValueError:
            raise BookingFailure("configuration_error")
        if (
            day.year < 2020
            or not TIME_PATTERN.fullmatch(course["startTime"])
            or not TIME_PATTERN.fullmatch(course["endTime"])
            or not all(course[key] for key in ("courseName", "teacher", "venue"))
            or any(len(course[key]) > 100 for key in ("courseName", "teacher", "venue"))
        ):
            raise BookingFailure("configuration_error")
        fingerprint = tuple(course[key] for key in sorted(required))
        if fingerprint in fingerprints:
            raise BookingFailure("configuration_error")
        fingerprints.add(fingerprint)
        normalized.append(course)
    return normalized


def public_course(course: dict[str, Any]) -> dict[str, Any]:
    return {
        key: course.get(key)
        for key in (
            "date",
            "startTime",
            "endTime",
            "courseName",
            "teacher",
            "venue",
        )
    }


def same_course(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return all(
        ballet.normalize_space(str(left.get(key, "")))
        == ballet.normalize_space(str(right.get(key, "")))
        for key in (
            "date",
            "startTime",
            "endTime",
            "courseName",
            "teacher",
            "venue",
        )
    )


def timetable_candidates(
    source: Any, target: dict[str, str]
) -> list[dict[str, Any]]:
    path = f"{ballet.TIMETABLE_PATH}/{target['date']}"
    text = source.request(path, "classtable")
    records = ballet.parse_timetable(text, target["date"])["records"]
    controls, scripts, script_sources = parse_controls(text)
    if len(records) != len(controls):
        raise BookingFailure("source_changed")
    candidates = []
    for record, control in zip(records, controls):
        if not same_course(record, target):
            continue
        candidates.append(
            {
                "record": record,
                "control": control,
                "scripts": scripts,
                "scriptSources": script_sources,
            }
        )
    return candidates


def booking_contract(candidate: dict[str, Any]) -> dict[str, Any]:
    buttons = []
    for element in candidate["control"]["controls"]:
        classes = set(element["attrs"].get("class", "").split())
        if element["tag"] == "button" and "bookbtn" in classes:
            buttons.append(element["attrs"])
    if len(buttons) != 1:
        raise BookingFailure(
            "source_changed",
            safe_diagnostic(
                candidate["control"],
                candidate["scripts"],
                candidate["scriptSources"],
            ),
        )
    course_id = buttons[0].get("courseid", "")
    class_table_id = buttons[0].get("classtableid", "")
    if (
        not re.fullmatch(r"\d+", course_id)
        or not re.fullmatch(r"\d+", class_table_id)
    ):
        raise BookingFailure("source_changed")

    script_text = "\n".join(candidate["scripts"])
    customer_ids = set(
        re.findall(r"\bcustomerid\s*=\s*[\"']?(\d+)[\"']?", script_text)
    )
    if len(customer_ids) != 1:
        raise BookingFailure("source_changed")
    customer_id = next(iter(customer_ids))

    paths = set()
    for value in re.findall(
        r"[\"']((?:https?://[^\"']+)?/gm/weixin/classtable/[^\"']+)[\"']",
        script_text,
    ):
        parts = urlsplit(value)
        if parts.netloc and parts.netloc != urlsplit(ballet.BASE_URL).netloc:
            continue
        paths.add(parts.path)
    expected = {
        CARD_TYPE_PATH,
        BOOKING_SUBMIT_PATH,
        GET_USING_CARD_PATH,
    }
    rules_paths = {
        path
        for path in paths
        if re.fullmatch(re.escape(CHECK_RULES_PREFIX) + r"\d+", path)
    }
    if not expected.issubset(paths) or len(rules_paths) != 1:
        raise BookingFailure(
            "source_changed",
            safe_diagnostic(
                candidate["control"],
                candidate["scripts"],
                candidate["scriptSources"],
            ),
        )
    return {
        "courseId": course_id,
        "classTableId": class_table_id,
        "customerId": customer_id,
        "cardTypePath": CARD_TYPE_PATH,
        "rulesPath": next(iter(rules_paths)),
        "bookingPath": BOOKING_SUBMIT_PATH,
    }


def response_json(text: str) -> Any:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        raise BookingFailure("source_changed")


def eligible_card(source: Any, contract: dict[str, str]) -> str:
    cards = response_json(
        source.post_fields(
            contract["cardTypePath"],
            {
                "courseid": contract["courseId"],
                "customerid": contract["customerId"],
                "shopid": ballet.STORE_ID,
            },
            mutation=False,
        )
    )
    if not isinstance(cards, list):
        raise BookingFailure("source_changed")
    if not cards:
        raise BookingFailure("no_eligible_card")
    if len(cards) != 1:
        raise BookingFailure("card_selection_required")
    card = cards[0]
    if not isinstance(card, dict):
        raise BookingFailure("source_changed")
    card_id = str(card.get("id", ""))
    status = str(card.get("status", ""))
    if not re.fullmatch(r"\d+", card_id):
        raise BookingFailure("source_changed")
    if status == "NOTOPEN":
        raise BookingFailure("card_not_open")
    return card_id


def check_rules(source: Any, contract: dict[str, str], card_id: str) -> None:
    result = response_json(
        source.post_fields(
            contract["rulesPath"],
            {
                "classtableid": contract["classTableId"],
                "cardid": card_id,
            },
            mutation=False,
        )
    )
    if result != "OK":
        raise BookingFailure("rules_blocked")


def current_booking(source: Any, target: dict[str, str]) -> dict[str, Any] | None:
    data = live.query_bookings(source)
    matches = [record for record in data["records"] if same_course(record, target)]
    if len(matches) > 1:
        raise BookingFailure("source_changed")
    return matches[0] if matches else None


class WendaBookingSource:
    def __init__(self, credentials: ballet.Credentials):
        self.reader = ballet.WendaSource(credentials, retries=0)
        self.post_count = 0
        self.mutation_count = 0

    @property
    def request_count(self) -> int:
        return self.reader.request_count + self.post_count

    def request(self, path: str, expected_marker: str) -> str:
        return self.reader.request(path, expected_marker)

    def post_fields(
        self,
        path: str,
        fields: dict[str, str],
        mutation: bool,
    ) -> str:
        allowed = {
            CARD_TYPE_PATH,
            GET_USING_CARD_PATH,
            BOOKING_SUBMIT_PATH,
        }
        if path.startswith(CHECK_RULES_PREFIX):
            suffix = path.removeprefix(CHECK_RULES_PREFIX)
            path_allowed = bool(re.fullmatch(r"\d+", suffix))
        else:
            path_allowed = path in allowed
        if (
            not path_allowed
            or not fields
            or mutation != (path == BOOKING_SUBMIT_PATH)
        ):
            raise BookingFailure("configuration_error")
        self.post_count += 1
        if mutation:
            self.mutation_count += 1
        request = urllib.request.Request(
            ballet.BASE_URL + path,
            data=urllib.parse.urlencode(fields).encode("utf-8"),
            headers={
                **self.reader._headers(path),
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": ballet.BASE_URL,
                "Referer": ballet.BASE_URL + ballet.TIMETABLE_PATH,
            },
            method="POST",
        )
        try:
            with self.reader.opener.open(
                request, timeout=self.reader.timeout_seconds
            ) as response:
                status = int(response.status)
                headers = response.headers
                body = ballet._read_limited(response)
        except urllib.error.HTTPError as error:
            status = int(error.code)
            headers = error.headers
            body = ballet._read_limited(error)
        except (urllib.error.URLError, TimeoutError):
            raise BookingFailure("unknown_result")
        self.reader._update_session_in_memory(headers)
        text = body.decode("utf-8", "replace")
        if ballet._is_auth_response(status, headers, text):
            raise BookingFailure("auth_required")
        if status not in {200, 302, 303}:
            raise BookingFailure("unknown_result")
        if status in {302, 303}:
            location = str(headers.get("Location", ""))
            parts = urlsplit(location)
            if parts.netloc and parts.netloc != urlsplit(ballet.BASE_URL).netloc:
                raise BookingFailure("unknown_result")
        return text


def run(source: Any, courses: list[dict[str, str]], execute: bool) -> dict[str, Any]:
    recoverable_preflight_failures = {
        "card_not_open",
        "card_selection_required",
        "course_not_unique",
        "no_eligible_card",
        "rules_blocked",
    }
    prepared = []
    for target in courses:
        existing = current_booking(source, target)
        if existing:
            prepared.append(
                {
                    "target": target,
                    "status": "already_booked",
                    "bookingStatus": existing["bookingStatus"],
                }
            )
            continue
        candidates = timetable_candidates(source, target)
        if len(candidates) != 1:
            prepared.append({"target": target, "status": "course_not_unique"})
            continue
        candidate = candidates[0]
        availability = candidate["record"]["availability"]
        if availability != "available":
            prepared.append(
                {
                    "target": target,
                    "status": "not_available",
                    "availability": availability,
                }
            )
            continue
        try:
            contract = booking_contract(candidate)
            card_id = eligible_card(source, contract)
            check_rules(source, contract, card_id)
        except BookingFailure as failure:
            if failure.code not in recoverable_preflight_failures:
                raise
            prepared.append({"target": target, "status": failure.code})
            continue
        prepared.append(
            {
                "target": target,
                "status": "ready",
            }
        )

    results = [
        {
            **public_course(item["target"]),
            "status": item["status"],
            **(
                {"bookingStatus": item["bookingStatus"]}
                if "bookingStatus" in item
                else {}
            ),
            **(
                {"availability": item["availability"]}
                if "availability" in item
                else {}
            ),
        }
        for item in prepared
    ]
    preflight_blocked = any(
        item["status"] not in {"ready", "already_booked"} for item in prepared
    )
    if not execute or preflight_blocked:
        return {
            "schemaVersion": 1,
            "source": "wenda-live",
            "status": "preflight_failed" if preflight_blocked else "success",
            "live": True,
            "mode": "execute" if execute else "dry-run",
            "mutated": False,
            "fetchedAt": ballet.iso_now(),
            "requestsMade": source.request_count,
            "postsMade": getattr(source, "post_count", 0),
            "mutationAttempts": getattr(source, "mutation_count", 0),
            "data": {"records": results},
        }

    results = []
    stop_reason = ""
    for item in prepared:
        target = item["target"]
        if stop_reason:
            results.append({**public_course(target), "status": "not_attempted"})
            continue
        if item["status"] == "already_booked":
            results.append(
                {
                    **public_course(target),
                    "status": "already_booked",
                    "bookingStatus": item["bookingStatus"],
                }
            )
            continue
        mutation_attempts_before = getattr(source, "mutation_count", 0)
        try:
            candidate = timetable_candidates(source, target)
            if (
                len(candidate) != 1
                or candidate[0]["record"]["availability"] != "available"
            ):
                raise BookingFailure("not_available")
            contract = booking_contract(candidate[0])
            card_id = eligible_card(source, contract)
            check_rules(source, contract, card_id)
            mutation_result = response_json(
                source.post_fields(
                    contract["bookingPath"],
                    {
                        "classtableid": contract["classTableId"],
                        "cardid": card_id,
                    },
                    mutation=True,
                )
            )
            try:
                verified = current_booking(source, target)
            except (BookingFailure, ballet.SyncFailure):
                raise BookingFailure("unknown_result")
            if not verified:
                if mutation_result in {"FULL", "STOPPED", "NOTOPEN"}:
                    raise BookingFailure(str(mutation_result).lower())
                raise BookingFailure("unknown_result")
            results.append(
                {
                    **public_course(target),
                    "status": "booked",
                    "bookingStatus": verified["bookingStatus"],
                }
            )
        except (BookingFailure, ballet.SyncFailure) as failure:
            mutation_attempted = (
                getattr(source, "mutation_count", 0) > mutation_attempts_before
            )
            failure_code = getattr(failure, "code", "unknown_result")
            status = (
                "unknown_result"
                if mutation_attempted
                and failure_code
                not in {"full", "notopen", "stopped"}
                else failure_code
            )
            results.append({**public_course(target), "status": status})
            stop_reason = status

    return {
        "schemaVersion": 1,
        "source": "wenda-live",
        "status": "stopped" if stop_reason else "success",
        "live": stop_reason != "unknown_result",
        "mode": "execute" if execute else "dry-run",
        "mutated": any(record["status"] == "booked" for record in results),
        "fetchedAt": ballet.iso_now(),
        "requestsMade": source.request_count,
        "postsMade": getattr(source, "post_count", 0),
        "mutationAttempts": getattr(source, "mutation_count", 0),
        "data": {"records": results},
        **({"stopReason": stop_reason} if stop_reason else {}),
    }


def credential_path() -> Path:
    directory = os.environ.get("CREDENTIALS_DIRECTORY")
    if not directory:
        raise BookingFailure("configuration_error")
    return Path(directory) / "wenda-session.json"


def safe_error(
    code: str,
    execute: bool,
    diagnostic: dict[str, Any] | None = None,
    source: Any | None = None,
) -> dict[str, Any]:
    mutation_attempts = getattr(source, "mutation_count", 0)
    result = {
        "schemaVersion": 1,
        "source": "wenda-live",
        "status": code,
        "live": False,
        "mode": "execute" if execute else "dry-run",
        "mutated": None if mutation_attempts else False,
        "fetchedAt": ballet.iso_now(),
        "requestsMade": getattr(source, "request_count", 0),
        "postsMade": getattr(source, "post_count", 0),
        "mutationAttempts": mutation_attempts,
    }
    if diagnostic:
        result["diagnostic"] = diagnostic
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("dry-run", "execute"))
    parser.add_argument("--request-json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    execute = args.mode == "execute"
    source = None
    try:
        request_text = (
            args.request_json
            if args.request_json is not None
            else sys.stdin.read(20_000)
        )
        courses = parse_request(request_text, execute)
        source = WendaBookingSource(ballet.load_credentials(credential_path()))
        result = run(source, courses, execute)
        print(
            json.dumps(
                result,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return 0 if result["status"] == "success" else 4
    except (BookingFailure, ballet.SyncFailure) as failure:
        code = getattr(failure, "code", "unknown_result")
        diagnostic = getattr(failure, "diagnostic", None)
        print(
            json.dumps(
                safe_error(code, execute, diagnostic, source),
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return 2 if code == "auth_required" else 4


if __name__ == "__main__":
    raise SystemExit(main())
