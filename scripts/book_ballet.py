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
    match = re.search(rf"{re.escape(name)}[\"']?\s*:\s*", text)
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


def safe_script_skeleton(text: str) -> str:
    allowed_literals = {
        ".bookbtn",
        "POST",
        "bookid",
        "cardid",
        "cardstatus",
        "classtableid",
        "courseid",
        "coursetype",
        "custid",
        "date",
    }

    def replace_literal(match: re.Match[str]) -> str:
        quote = match.group(1)
        value = match.group(2)
        following = text[match.end() :]
        is_object_key = bool(re.match(r"\s*:", following))
        is_bracket_key = bool(
            re.search(r"\[\s*$", text[: match.start()])
            and re.match(r"\s*\]", following)
        )
        if value.startswith("/") or value.startswith(("http://", "https://")):
            safe_value = f"<path:{safe_path_shape(value)}>"
        elif value in allowed_literals or (
            (is_object_key or is_bracket_key)
            and re.fullmatch(r"[A-Za-z_$][\w$]*", value)
        ) or re.fullmatch(
            r"(?:[A-Z][A-Z_]*|true|false|success|ok)", value
        ):
            safe_value = value
        else:
            safe_value = "<string>"
        return f"{quote}{safe_value}{quote}"

    text = re.sub(r"([\"'])(.*?)(?<!\\)\1", replace_literal, text)
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    text = re.sub(r"//[^\r\n]*", " ", text)
    text = re.sub(r"\b\d+(?:\.\d+)?\b", "<number>", text)
    return re.sub(r"\s+", " ", text).strip()[:12_000]


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
                r"(?:(?:var|let|const)\s+)?([A-Za-z_$][\w$]*)\s*=\s*"
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
                r"[\"']?(?:type|method)[\"']?\s*:\s*[\"']([A-Za-z]+)[\"']",
                ajax_object,
            )
            direct_url_match = re.search(
                r"url\s*:\s*[\"']([^\"']+)[\"']", ajax_object
            )
            direct_data_match = re.search(
                r"data\s*:\s*([\"'])(.*?)\1",
                ajax_object,
                re.DOTALL,
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
            if direct_data_match:
                data_contract["fieldNames"] = sorted(
                    set(data_contract["fieldNames"])
                    | {
                        value
                        for value in re.findall(
                            r"(?:^|[?&])([A-Za-z_$][\w$]*)=",
                            direct_data_match.group(2),
                        )
                    }
                )
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
            elif direct_url_match:
                request["urlShape"] = safe_path_shape(direct_url_match.group(1))
            requests.append(request)
        contracts.append(
            {
                "selector": ".bookbtn",
                "attributeBindings": [
                    {"variable": variable, "attribute": attribute}
                    for variable, attribute in bindings
                ],
                "requests": requests,
                "skeleton": safe_script_skeleton(handler),
            }
        )
    return contracts


def safe_endpoint_roles(script_text: str) -> dict[str, Any]:
    customer_ids = set(
        re.findall(r"\bcustomerid\s*=\s*[\"']?(\d+)[\"']?", script_text)
    )
    customer_id = next(iter(customer_ids)) if len(customer_ids) == 1 else ""
    endpoints: dict[str, list[list[str]]] = {}
    for name, suffix in re.findall(
        r"/gm/weixin/classtable/"
        r"(check_cardtypecourse|check_rules|do_addbook|getusingcard)"
        r"((?:/\d+)+)",
        script_text,
    ):
        roles = []
        for value in suffix.strip("/").split("/"):
            if value == ballet.STORE_ID:
                roles.append("store")
            elif customer_id and value == customer_id:
                roles.append("customer")
            else:
                roles.append("other")
        endpoints.setdefault(name, []).append(roles)
    return {
        "customerIdAssignmentCount": len(customer_ids),
        "endpointSegmentRoles": endpoints,
    }


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
        "bookingContract": safe_endpoint_roles(script_text),
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
    expected_rules_path = CHECK_RULES_PREFIX + customer_id
    expected = {
        CARD_TYPE_PATH,
        expected_rules_path,
        BOOKING_SUBMIT_PATH,
        GET_USING_CARD_PATH,
    }
    if not expected.issubset(paths):
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
        "rulesPath": expected_rules_path,
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
        contract = booking_contract(candidate)
        card_id = eligible_card(source, contract)
        check_rules(source, contract, card_id)
        prepared.append(
            {
                "target": target,
                "status": "ready",
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
                results.append(
                    {
                        **public_course(target),
                        "status": "not_available",
                        "reason": str(mutation_result).lower(),
                    }
                )
                continue
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
        "mutated": any(record["status"] == "booked" for record in results),
        "fetchedAt": ballet.iso_now(),
        "requestsMade": source.request_count,
        "postsMade": getattr(source, "post_count", 0),
        "mutationAttempts": getattr(source, "mutation_count", 0),
        "data": {"records": results},
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
                safe_error(code, execute, diagnostic, source),
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return 2 if code == "auth_required" else 4


if __name__ == "__main__":
    raise SystemExit(main())
