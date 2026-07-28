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


def balanced_region(text: str, opening: int, opener: str, closer: str) -> str:
    depth = 0
    quote = ""
    escaped = False
    for index in range(opening, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in {"'", '"', "`"}:
            quote = char
        elif char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return text[opening : index + 1]
    return ""


def property_expression(text: str, name: str) -> str:
    match = re.search(rf"(?:^|[,{{\s]){re.escape(name)}\s*:\s*", text)
    if not match:
        return ""
    start = match.end()
    depths = {"(": 0, "[": 0, "{": 0}
    pairs = {")": "(", "]": "[", "}": "{"}
    quote = ""
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in {"'", '"', "`"}:
            quote = char
        elif char in depths:
            depths[char] += 1
        elif char in pairs:
            opener = pairs[char]
            if depths[opener] == 0:
                return text[start:index].strip()
            depths[opener] -= 1
        elif char == "," and not any(depths.values()):
            return text[start:index].strip()
    return text[start:].strip()


def expression_contract(expression: str) -> dict[str, Any]:
    literals = re.findall(r"[\"']([^\"']*)[\"']", expression)
    field_names = sorted(
        {
            match
            for literal in literals
            for match in re.findall(r"(?:^|[?&])([A-Za-z_$][\w$]*)=", literal)
        }
    )
    path_shapes = sorted(
        {
            safe_path_shape(literal)
            for literal in literals
            if literal.startswith("/")
        }
    )
    identifiers = sorted(
        {
            value
            for value in re.findall(r"\b([A-Za-z_$][\w$]*)\b", expression)
            if value
            not in {
                "false",
                "null",
                "true",
                "undefined",
            }
            and all(value not in literal for literal in literals)
        }
    )
    contract: dict[str, Any] = {
        "fieldNames": field_names,
        "identifiers": identifiers,
    }
    if path_shapes:
        contract["pathShapes"] = path_shapes
    return contract


def safe_ajax_contracts(script_text: str) -> list[dict[str, Any]]:
    contracts = []
    for selector_match in re.finditer(
        r"\$\(\s*([\"'])\.bookbtn\1\s*\)\s*"
        r"(?:\.on\(\s*([\"'])click\2\s*,|\.click\()\s*function\s*\([^)]*\)\s*\{",
        script_text,
    ):
        opening = selector_match.end() - 1
        handler = balanced_region(script_text, opening, "{", "}")
        if not handler:
            continue
        jquery_targets = {
            variable
            for variable in re.findall(
                r"(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*"
                r"\$\(\s*this\s*\)",
                handler,
            )
        }
        direct_bindings = set(
            re.findall(
                r"(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*"
                r"\$\(\s*(?:this|[A-Za-z_$][\w$]*(?:\.currentTarget|\.target))"
                r"\s*\)\.attr\(\s*[\"']([^\"']+)[\"']",
                handler,
            )
        )
        indirect_bindings = {
            (variable, attribute)
            for variable, target, attribute in re.findall(
                r"(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*"
                r"([A-Za-z_$][\w$]*)\.attr\(\s*[\"']([^\"']+)[\"']",
                handler,
            )
            if target in jquery_targets
        }
        bindings = sorted(direct_bindings | indirect_bindings)
        requests = []
        for ajax_match in re.finditer(r"\$\.ajax\s*\(\s*\{", handler):
            ajax_object = balanced_region(
                handler, ajax_match.end() - 1, "{", "}"
            )
            if not ajax_object:
                continue
            method_match = re.search(
                r"(?:type|method)\s*:\s*[\"']([A-Za-z]+)[\"']",
                ajax_object,
            )
            url_expression = property_expression(ajax_object, "url")
            data_expression = property_expression(ajax_object, "data")
            data_keys = []
            if data_expression.startswith("{") and data_expression.endswith("}"):
                data_keys = sorted(
                    set(
                        re.findall(
                            r"(?:^|,)\s*([A-Za-z_$][\w$]*)\s*:",
                            data_expression[1:-1],
                        )
                    )
                )
            data_contract = expression_contract(data_expression)
            data_keys = sorted(set(data_keys) | set(data_contract["fieldNames"]))
            effects = []
            if re.search(r"\.html\s*\(", ajax_object):
                effects.append("replace-html")
            if re.search(r"\.(?:modal|popup|openPopup)\s*\(", ajax_object):
                effects.append("open-dialog")
            if re.search(r"(?:window\.)?location(?:\.href)?\s*=", ajax_object):
                effects.append("navigate")
            request: dict[str, Any] = {
                "method": method_match.group(1).upper() if method_match else "",
                "dataKeys": data_keys,
                "urlContract": expression_contract(url_expression),
                "dataIdentifiers": data_contract["identifiers"],
                "effects": effects,
            }
            path_shapes = request["urlContract"].get("pathShapes", [])
            if len(path_shapes) == 1:
                request["urlShape"] = path_shapes[0]
            requests.append(request)
        contracts.append(
            {
                "selector": ".bookbtn",
                "attributeBindings": [
                    {"variable": variable, "attribute": attribute}
                    for variable, attribute in bindings
                ],
                "requests": requests,
            }
        )
    return contracts


def safe_diagnostic(
    control: dict[str, Any],
    scripts: list[str],
    script_sources: list[str],
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
    script_signals = {
        "selectors": sorted(
            {
                value
                for value in re.findall(
                    r"\$\(\s*[\"']([^\"']+)[\"']\s*\)", script_text
                )
                if "book" in value.lower()
            }
        ),
        "attributeNames": sorted(
            set(re.findall(r"\.attr\(\s*[\"']([^\"']+)[\"']", script_text))
        ),
        "requestCalls": sorted(
            set(re.findall(r"\$\.(post|get|ajax)\s*\(", script_text))
        ),
        "pathShapes": sorted(
            {
                safe_path_shape(value)
                for value in re.findall(r"[\"'](/[^\"']+)[\"']", script_text)
                if "book" in value.lower()
            }
        ),
        "objectKeys": sorted(
            set(
                re.findall(
                    r"(?:^|[,{\s])([A-Za-z_][\w-]*)\s*:",
                    script_text,
                )
            )
        ),
        "bookingHandlers": safe_ajax_contracts(script_text),
    }
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
        "scriptSources": sorted({safe_path_shape(item) for item in script_sources}),
        "scriptSignals": script_signals,
        "elements": elements,
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
            safe_diagnostic(
                candidate["control"],
                candidate["scripts"],
                candidate["scriptSources"],
            ),
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
