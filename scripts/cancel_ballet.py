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

import book_ballet as booking
import sync_ballet as ballet


sys.dont_write_bytecode = True

CHECK_CANCEL_PREFIX = (
    f"/gm/weixin/my/check_cancelrules/{ballet.STORE_ID}/"
)
CANCEL_SUBMIT_PATH = f"/gm/weixin/my/do_cancel/{ballet.STORE_ID}"
CANCEL_SUCCESS_PATH = f"/gm/weixin/my/cancelsuccess/{ballet.STORE_ID}"
CHECK_CANCEL_PATTERN = re.compile(
    re.escape(CHECK_CANCEL_PREFIX) + r"[1-9][0-9]{0,19}"
)
MAX_REQUEST_BYTES = 10_000


class CancellationFailure(Exception):
    def __init__(self, code: str, diagnostic: dict[str, Any] | None = None):
        super().__init__(code)
        self.code = code
        self.diagnostic = diagnostic


class CancellationContractParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cancel_controls = 0
        self.scripts: list[str] = []
        self.script_sources: list[str] = []
        self.in_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        values = {key: html.unescape(value or "") for key, value in attrs}
        if "cancelbook" in values.get("class", "").split():
            self.cancel_controls += 1
        if tag == "script":
            self.in_script = True
            if values.get("src"):
                self.script_sources.append(values["src"])

    def handle_endtag(self, tag: str):
        if tag == "script":
            self.in_script = False

    def handle_data(self, data: str):
        if self.in_script:
            self.scripts.append(data)


def safe_path_shape(value: str) -> str:
    path = urlsplit(value).path
    return re.sub(r"(?<=/)\d+(?=/|$)", ":id", path)


def safe_contract_diagnostic(parser: CancellationContractParser) -> dict[str, Any]:
    script_text = "\n".join(parser.scripts)
    paths = {
        safe_path_shape(value)
        for value in re.findall(
            r"[\"']((?:https?://[^\"']+)?/gm/weixin/my/[^\"']+)[\"']",
            script_text,
        )
    }
    return {
        "cancelControlCount": parser.cancel_controls,
        "scriptSources": sorted(
            {safe_path_shape(value) for value in parser.script_sources}
        ),
        "cancellationPathShapes": sorted(
            path
            for path in paths
            if any(
                marker in path
                for marker in ("cancelrules", "do_cancel", "cancelsuccess")
            )
        ),
    }


def _ajax_context(script_text: str, path: str) -> str:
    if script_text.count(path) != 1:
        raise CancellationFailure("source_changed")
    index = script_text.index(path)
    return script_text[max(0, index - 120) : index + 900]


def cancellation_contract(
    detail_html: str,
    source_record_id: str,
    detail_path: str,
) -> dict[str, str]:
    if not re.fullmatch(r"[1-9][0-9]{0,19}", source_record_id):
        raise CancellationFailure("source_changed")
    if not ballet.DETAIL_PATH_PATTERN.fullmatch(detail_path):
        raise CancellationFailure("source_changed")

    parser = CancellationContractParser()
    try:
        parser.feed(detail_html)
    except Exception:
        raise CancellationFailure("parse_error")
    script_text = "\n".join(parser.scripts)
    check_path = CHECK_CANCEL_PREFIX + source_record_id
    try:
        check_context = _ajax_context(script_text, check_path)
        cancel_context = _ajax_context(script_text, CANCEL_SUBMIT_PATH)
        _ajax_context(script_text, CANCEL_SUCCESS_PATH)
    except CancellationFailure:
        raise CancellationFailure(
            "source_changed", safe_contract_diagnostic(parser)
        )

    post_pattern = re.compile(r"\btype\s*:\s*[\"']post[\"']", re.I)
    book_id_pattern = re.compile(
        r"[\"']bookid[\"']\s*:\s*" + re.escape(source_record_id) + r"\b"
    )
    if (
        parser.cancel_controls != 1
        or not post_pattern.search(check_context)
        or not post_pattern.search(cancel_context)
        or not book_id_pattern.search(cancel_context)
        or "JSON.parse" not in check_context
        or not re.search(r"==\s*[\"']OK[\"']", check_context)
    ):
        raise CancellationFailure(
            "source_changed", safe_contract_diagnostic(parser)
        )
    return {
        "sourceRecordId": source_record_id,
        "detailPath": detail_path,
        "checkPath": check_path,
        "cancelPath": CANCEL_SUBMIT_PATH,
    }


def parse_request(text: str, execute: bool) -> dict[str, str]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        raise CancellationFailure("configuration_error")
    if not isinstance(payload, dict) or set(payload) != {"course", "confirm"}:
        raise CancellationFailure("configuration_error")
    try:
        return booking.parse_request(
            json.dumps(
                {
                    "courses": [payload["course"]],
                    "confirm": payload["confirm"],
                },
                ensure_ascii=False,
            ),
            execute,
        )[0]
    except booking.BookingFailure as failure:
        raise CancellationFailure(failure.code)


def _public_record(record: dict[str, Any], status: str) -> dict[str, Any]:
    return {
        **booking.public_course(record),
        "status": status,
        **(
            {"bookingStatus": record["bookingStatus"]}
            if record.get("bookingStatus")
            else {}
        ),
        **(
            {"cancelRuleText": record["cancelRuleText"]}
            if record.get("cancelRuleText")
            else {}
        ),
        **(
            {"cancelDeadlineAt": record["cancelDeadlineAt"]}
            if record.get("cancelDeadlineAt")
            else {}
        ),
    }


def find_active_booking(
    source: Any, target: dict[str, str]
) -> dict[str, Any] | None:
    index_html = source.request(ballet.BOOKING_PATH, "约课记录")
    try:
        index = ballet.parse_index(index_html, "booking")
    except ballet.SyncFailure as failure:
        raise CancellationFailure(failure.code)
    active = [
        item
        for item in index
        if item.get("status") in {"已预约", "排队中", "候补中"}
        and item.get("date") == target["date"]
    ]
    matches = []
    for item in active:
        detail_html = source.request(item["detailPath"], "约课记录明细")
        try:
            detail = ballet.parse_detail(
                detail_html, item["sourceRecordId"]
            )
            record = ballet.normalize_upcoming(detail)
        except ballet.SyncFailure as failure:
            raise CancellationFailure(failure.code)
        if record is not None and booking.same_course(record, target):
            matches.append(
                {
                    "record": record,
                    "sourceRecordId": item["sourceRecordId"],
                    "detailPath": item["detailPath"],
                    "detailHtml": detail_html,
                }
            )
    if len(matches) > 1:
        raise CancellationFailure("source_changed")
    return matches[0] if matches else None


def _response_json(text: str) -> Any:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        raise CancellationFailure("source_changed")


def check_cancel_rules(source: Any, contract: dict[str, str]) -> None:
    result = _response_json(
        source.post_fields(
            contract["checkPath"],
            {},
            mutation=False,
            referer=contract["detailPath"],
        )
    )
    if result != "OK":
        raise CancellationFailure("cancellation_blocked")


class WendaCancellationSource:
    def __init__(
        self,
        credentials: ballet.Credentials,
        timeout_seconds: int = 20,
    ):
        self.reader = ballet.WendaSource(
            credentials,
            timeout_seconds=timeout_seconds,
            retries=0,
        )
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
        referer: str,
    ) -> str:
        is_check = bool(CHECK_CANCEL_PATTERN.fullmatch(path))
        is_cancel = path == CANCEL_SUBMIT_PATH
        valid_referer = bool(ballet.DETAIL_PATH_PATTERN.fullmatch(referer))
        valid_fields = (
            not fields
            if is_check
            else set(fields) == {"bookid"}
            and bool(re.fullmatch(r"[1-9][0-9]{0,19}", fields["bookid"]))
        )
        if (
            not valid_referer
            or not valid_fields
            or mutation != is_cancel
            or not (is_check or is_cancel)
        ):
            raise CancellationFailure("configuration_error")
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
            raise CancellationFailure("unknown_result")
        self.reader._update_session_in_memory(headers)
        text = body.decode("utf-8", "replace")
        if ballet._is_auth_response(status, headers, text):
            raise CancellationFailure("auth_required")
        if status not in {200, 302, 303}:
            raise CancellationFailure("unknown_result")
        if status in {302, 303}:
            location = str(headers.get("Location", ""))
            parts = urlsplit(location)
            if parts.netloc and parts.netloc != urlsplit(ballet.BASE_URL).netloc:
                raise CancellationFailure("unknown_result")
        return text


def _result(
    source: Any,
    execute: bool,
    record: dict[str, Any],
    top_status: str,
    mutated: bool | None,
    live: bool,
) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "source": "wenda-live",
        "status": top_status,
        "live": live,
        "mode": "execute" if execute else "dry-run",
        "mutated": mutated,
        "fetchedAt": ballet.iso_now(),
        "requestsMade": getattr(source, "request_count", 0),
        "postsMade": getattr(source, "post_count", 0),
        "mutationAttempts": getattr(source, "mutation_count", 0),
        "data": {"records": [record]},
    }


def run(
    source: Any,
    target: dict[str, str],
    execute: bool,
) -> dict[str, Any]:
    candidate = find_active_booking(source, target)
    if candidate is None:
        return _result(
            source,
            execute,
            _public_record(target, "not_booked"),
            "preflight_failed",
            False,
            True,
        )
    contract = cancellation_contract(
        candidate["detailHtml"],
        candidate["sourceRecordId"],
        candidate["detailPath"],
    )
    try:
        check_cancel_rules(source, contract)
    except CancellationFailure as failure:
        if failure.code != "cancellation_blocked":
            raise
        return _result(
            source,
            execute,
            _public_record(candidate["record"], failure.code),
            "preflight_failed",
            False,
            True,
        )
    if not execute:
        return _result(
            source,
            False,
            _public_record(candidate["record"], "ready"),
            "success",
            False,
            True,
        )

    candidate = find_active_booking(source, target)
    if candidate is None:
        return _result(
            source,
            True,
            _public_record(target, "already_cancelled"),
            "success",
            False,
            True,
        )
    contract = cancellation_contract(
        candidate["detailHtml"],
        candidate["sourceRecordId"],
        candidate["detailPath"],
    )
    check_cancel_rules(source, contract)

    try:
        source.post_fields(
            contract["cancelPath"],
            {"bookid": contract["sourceRecordId"]},
            mutation=True,
            referer=contract["detailPath"],
        )
    except CancellationFailure:
        pass

    try:
        remaining = find_active_booking(source, target)
    except CancellationFailure:
        remaining = candidate
    if remaining is None:
        return _result(
            source,
            True,
            _public_record(candidate["record"], "cancelled"),
            "success",
            True,
            True,
        )
    return _result(
        source,
        True,
        _public_record(candidate["record"], "unknown_result"),
        "stopped",
        None,
        False,
    )


def credential_path() -> Path:
    directory = os.environ.get("CREDENTIALS_DIRECTORY")
    if not directory:
        raise CancellationFailure("configuration_error")
    return Path(directory) / "wenda-session.json"


def safe_error(
    code: str,
    execute: bool,
    source: Any | None = None,
    diagnostic: dict[str, Any] | None = None,
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    execute = args.mode == "execute"
    source = None
    try:
        request_text = sys.stdin.read(MAX_REQUEST_BYTES + 1)
        if not request_text or len(request_text.encode("utf-8")) > MAX_REQUEST_BYTES:
            raise CancellationFailure("configuration_error")
        target = parse_request(request_text, execute)
        source = WendaCancellationSource(
            ballet.load_credentials(credential_path())
        )
        result = run(source, target, execute)
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return 0 if result["status"] == "success" else 4
    except (CancellationFailure, ballet.SyncFailure) as failure:
        code = getattr(failure, "code", "unknown_result")
        diagnostic = getattr(failure, "diagnostic", None)
        print(
            json.dumps(
                safe_error(code, execute, source, diagnostic),
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return 2 if code == "auth_required" else 4


if __name__ == "__main__":
    raise SystemExit(main())
