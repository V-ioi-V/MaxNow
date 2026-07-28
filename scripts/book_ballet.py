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
        self.form: dict[str, Any] | None = None
        self.controls: list[dict[str, Any]] = []
        self.scripts: list[str] = []
        self.in_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        values = {key: html.unescape(value or "") for key, value in attrs}
        if tag == "script":
            self.in_script = True
        if tag == "div":
            self.div_depth += 1
            classes = set(values.get("class", "").split())
            if self.current is None and "classtable" in classes:
                self.root_depth = self.div_depth
                self.current = {"forms": [], "controls": []}
        if self.current is None:
            return
        self.current["controls"].append(
            {
                "tag": tag,
                "attrs": values,
            }
        )
        if tag == "form":
            if self.form is not None:
                raise BookingFailure("source_changed")
            self.form = {
                "action": values.get("action", ""),
                "method": values.get("method", "get").lower(),
                "fields": {},
            }
        elif tag == "input" and self.form is not None:
            name = values.get("name", "")
            input_type = values.get("type", "text").lower()
            if name and input_type not in {"submit", "button", "file"}:
                if name in self.form["fields"]:
                    raise BookingFailure("source_changed")
                if input_type not in {"checkbox", "radio"} or "checked" in values:
                    self.form["fields"][name] = values.get("value", "")
        elif tag == "button" and self.form is not None:
            name = values.get("name", "")
            if name:
                if name in self.form["fields"]:
                    raise BookingFailure("source_changed")
                self.form["fields"][name] = values.get("value", "")

    def handle_endtag(self, tag: str):
        if tag == "script":
            self.in_script = False
        if self.current is not None and tag == "form" and self.form is not None:
            self.current["forms"].append(self.form)
            self.form = None
        if tag == "div":
            if self.current is not None and self.div_depth == self.root_depth:
                if self.form is not None:
                    raise BookingFailure("source_changed")
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
    control: dict[str, Any], scripts: list[str]
) -> dict[str, Any]:
    forms = [
        {
            "method": form["method"],
            "actionShape": safe_path_shape(form["action"]),
            "fieldNames": sorted(form["fields"]),
        }
        for form in control["forms"]
    ]
    inline_functions = sorted(
        {
            match.group(1)
            for item in control["controls"]
            for value in item["attrs"].values()
            for match in [re.match(r"\s*([A-Za-z_$][\w$]*)\s*\(", value)]
            if match
        }
    )
    script_text = "\n".join(scripts)
    script_functions = sorted(
        set(re.findall(r"function\s+([A-Za-z_$][\w$]*)\s*\(", script_text))
    )
    elements = []
    seen = set()
    for item in control["controls"]:
        attrs = item["attrs"]
        safe_item: dict[str, Any] = {
            "tag": item["tag"],
            "attributeNames": sorted(attrs),
        }
        if attrs.get("class"):
            safe_item["classes"] = sorted(set(attrs["class"].split()))
        if attrs.get("href"):
            safe_item["hrefShape"] = safe_path_shape(attrs["href"])
        if attrs.get("action"):
            safe_item["actionShape"] = safe_path_shape(attrs["action"])
        if attrs.get("onclick"):
            match = re.match(
                r"\s*([A-Za-z_$][\w$]*)\s*\(", attrs["onclick"]
            )
            safe_item["onclickFunction"] = match.group(1) if match else "inline"
        signature = json.dumps(safe_item, sort_keys=True, ensure_ascii=False)
        if signature not in seen:
            seen.add(signature)
            elements.append(safe_item)
    return {
        "forms": forms,
        "inlineFunctions": inline_functions,
        "scriptFunctions": script_functions,
        "elements": elements,
    }


def parse_controls(text: str) -> tuple[list[dict[str, Any]], list[str]]:
    parser = BookingControlParser()
    try:
        parser.feed(text)
    except BookingFailure:
        raise
    except Exception:
        raise BookingFailure("parse_error")
    return parser.controls, parser.scripts


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
    controls, scripts = parse_controls(text)
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
            }
        )
    return candidates


def booking_form(candidate: dict[str, Any]) -> tuple[str, dict[str, str]]:
    forms = candidate["control"]["forms"]
    matching = []
    for form in forms:
        action = urlsplit(form["action"]).path
        if action == BOOKING_SUBMIT_PATH and form["method"] == "post":
            matching.append((action, form["fields"]))
    if len(matching) != 1 or not matching[0][1]:
        raise BookingFailure(
            "source_changed",
            safe_diagnostic(candidate["control"], candidate["scripts"]),
        )
    return matching[0]


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

    @property
    def request_count(self) -> int:
        return self.reader.request_count

    def request(self, path: str, expected_marker: str) -> str:
        return self.reader.request(path, expected_marker)

    def post_form(self, path: str, fields: dict[str, str], referer: str) -> None:
        if path != BOOKING_SUBMIT_PATH or not fields:
            raise BookingFailure("configuration_error")
        self.post_count += 1
        request = urllib.request.Request(
            ballet.BASE_URL + path,
            data=urllib.parse.urlencode(fields).encode("utf-8"),
            headers={
                **self.reader._headers(path),
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": ballet.BASE_URL,
                "Referer": ballet.BASE_URL + referer,
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


def run(source: Any, courses: list[dict[str, str]], execute: bool) -> dict[str, Any]:
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
            raise BookingFailure("course_not_unique")
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
        action, fields = booking_form(candidate)
        prepared.append(
            {
                "target": target,
                "status": "ready",
                "action": action,
                "fields": fields,
            }
        )

    results = []
    for item in prepared:
        target = item["target"]
        if item["status"] != "ready":
            results.append(
                {
                    **public_course(target),
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
            )
            continue
        if not execute:
            results.append({**public_course(target), "status": "ready"})
            continue
        candidate = timetable_candidates(source, target)
        if len(candidate) != 1 or candidate[0]["record"]["availability"] != "available":
            results.append({**public_course(target), "status": "not_available"})
            continue
        action, fields = booking_form(candidate[0])
        source.post_form(
            action,
            fields,
            f"{ballet.TIMETABLE_PATH}/{target['date']}",
        )
        verified = current_booking(source, target)
        if not verified:
            raise BookingFailure("unknown_result")
        results.append(
            {
                **public_course(target),
                "status": "booked",
                "bookingStatus": verified["bookingStatus"],
            }
        )

    return {
        "schemaVersion": 1,
        "source": "wenda-live",
        "status": "success",
        "live": True,
        "mode": "execute" if execute else "dry-run",
        "mutated": bool(execute and getattr(source, "post_count", 0)),
        "fetchedAt": ballet.iso_now(),
        "requestsMade": source.request_count,
        "postsMade": getattr(source, "post_count", 0),
        "data": {"records": results},
    }


def credential_path() -> Path:
    directory = os.environ.get("CREDENTIALS_DIRECTORY")
    if not directory:
        raise BookingFailure("configuration_error")
    return Path(directory) / "wenda-session.json"


def safe_error(
    code: str, execute: bool, diagnostic: dict[str, Any] | None = None
) -> dict[str, Any]:
    result = {
        "schemaVersion": 1,
        "source": "wenda-live",
        "status": code,
        "live": False,
        "mode": "execute" if execute else "dry-run",
        "mutated": False,
        "fetchedAt": ballet.iso_now(),
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
    try:
        request_text = (
            args.request_json
            if args.request_json is not None
            else sys.stdin.read(20_000)
        )
        courses = parse_request(request_text, execute)
        source = WendaBookingSource(ballet.load_credentials(credential_path()))
        print(
            json.dumps(
                run(source, courses, execute),
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return 0
    except (BookingFailure, ballet.SyncFailure) as failure:
        code = getattr(failure, "code", "unknown_result")
        diagnostic = getattr(failure, "diagnostic", None)
        print(
            json.dumps(
                safe_error(code, execute, diagnostic),
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return 2 if code == "auth_required" else 4


if __name__ == "__main__":
    raise SystemExit(main())
