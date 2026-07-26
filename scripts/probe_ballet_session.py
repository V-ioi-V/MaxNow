#!/usr/bin/env python3
"""Probe the LIJUN Ballet read-only course page to measure session lifetime.

The probe deliberately supports only the known server-rendered course-list GET
route. It never follows redirects and cannot call booking, cancellation, or
transfer endpoints.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import http.cookies
import json
import os
import secrets
import socket
import stat
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


DEFAULT_INTERVAL_SECONDS = 600
DEFAULT_DURATION_SECONDS = 3 * 60 * 60
MAX_DURATION_SECONDS = 30 * 86_400
MAX_CONSECUTIVE_UNKNOWN = 3
DEFAULT_TIMEOUT_SECONDS = 20
DEFAULT_RETRIES = 2
ALLOWED_API_URL = (
    "https://gm.wendaosoft.com/gm/weixin/classtable/simpleclass/54114/430"
)
ALLOWED_REFERER = "https://gm.wendaosoft.com/gm/weixin/home/index/54114"
AUTHENTICATED_HTML_MARKERS = (
    "/gm/weixin/classtable/check_cardtypecourse/",
    "/gm/weixin/classtable/do_addbook/",
)
IDENTITY_ERROR_MARKERS = (
    "open.weixin.qq.com/connect/oauth2/authorize",
    "\u8bf7\u5728\u5fae\u4fe1\u5ba2\u6237\u7aef\u6253\u5f00\u94fe\u63a5",
    "\u767b\u5f55\u5df2\u5931\u6548",
    "\u672a\u767b\u5f55",
    "session expired",
    "login required",
)
BUSINESS_CODE_KEYS = ("errcode", "errorCode", "error_code", "code", "status")
LOGIN_STATE_KEYS = ("isLogin", "is_login", "loggedIn", "logged_in", "login")


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Return redirects to the caller instead of following OAuth."""

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


@dataclass
class Credentials:
    session_id: str
    user_agent: str


@dataclass
class Config:
    api_url: str
    credential_file: Path
    log_path: Path
    interval_seconds: int
    duration_seconds: int
    timeout_seconds: int
    retries: int
    once: bool
    dry_run: bool


@dataclass
class ResponseSnapshot:
    status: int | None
    headers: Any
    body: bytes
    network_error: str | None
    attempts: int


def env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    value = int(raw)
    if value < minimum or value > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure the lifetime of the read-only ballet course session."
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Send one read-only probe instead of running the timed experiment.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration without sending a request.",
    )
    return parser.parse_args()


def load_config(args: argparse.Namespace) -> Config:
    api_url = os.environ.get("WENDA_API_URL", "").strip()
    credential_file = os.environ.get("WENDA_CREDENTIAL_FILE", "").strip()
    log_path = os.environ.get("WENDA_LOG_PATH", "").strip()
    if not api_url:
        raise ValueError("WENDA_API_URL is required")
    if not credential_file:
        raise ValueError("WENDA_CREDENTIAL_FILE is required")
    if not log_path:
        raise ValueError("WENDA_LOG_PATH is required")
    validate_read_only_url(api_url)
    return Config(
        api_url=api_url,
        credential_file=Path(credential_file).expanduser().resolve(),
        log_path=Path(log_path).expanduser().resolve(),
        interval_seconds=env_int(
            "WENDA_INTERVAL_SECONDS", DEFAULT_INTERVAL_SECONDS, 60, 86_400
        ),
        duration_seconds=env_int(
            "WENDA_DURATION_SECONDS",
            DEFAULT_DURATION_SECONDS,
            60,
            MAX_DURATION_SECONDS,
        ),
        timeout_seconds=env_int(
            "WENDA_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS, 3, 120
        ),
        retries=env_int("WENDA_RETRIES", DEFAULT_RETRIES, 0, 5),
        once=args.once,
        dry_run=args.dry_run,
    )


def validate_read_only_url(url: str) -> None:
    if url != ALLOWED_API_URL:
        raise ValueError(
            "The probe only permits the fixed LIJUN read-only course-list URL"
        )


def load_credentials(path: Path) -> Credentials:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Credential file must be a JSON object")
    allowed_keys = {
        "authorization",
        "cookies",
        "metadata",
        "referer",
        "user_agent",
    }
    unexpected_keys = set(data) - allowed_keys
    if unexpected_keys:
        raise ValueError("Credential file contains unsupported fields")
    if str(data.get("authorization", "")).strip():
        raise ValueError("Authorization is not permitted by this probe")
    explicit_cookies = data.get("cookies")
    if not isinstance(explicit_cookies, dict) or set(explicit_cookies) != {
        "PHPSESSID"
    }:
        raise ValueError("Credential file must contain only the PHPSESSID cookie")
    session_id = str(explicit_cookies.get("PHPSESSID", "")).strip()
    if (
        len(session_id) < 16
        or len(session_id) > 256
        or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,-" for character in session_id)
    ):
        raise ValueError("PHPSESSID has an invalid shape")
    user_agent = str(data.get("user_agent", "")).strip()
    if (
        not user_agent
        or len(user_agent) > 512
        or "\r" in user_agent
        or "\n" in user_agent
    ):
        raise ValueError("user_agent is required and must be a single safe line")
    return Credentials(session_id=session_id, user_agent=user_agent)


def secret_fingerprint(value: str, fingerprint_key: bytes) -> str | None:
    if not value:
        return None
    return hmac.new(
        fingerprint_key, value.encode("utf-8"), hashlib.sha256
    ).hexdigest()[:12]


def session_fingerprints(
    credentials: Credentials, fingerprint_key: bytes
) -> dict[str, str]:
    fingerprint = secret_fingerprint(credentials.session_id, fingerprint_key)
    return {"cookie:PHPSESSID": fingerprint} if fingerprint else {}


def request_headers(credentials: Credentials) -> dict[str, str]:
    headers = {
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,*/*;q=0.8"
        ),
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Connection": "close",
    }
    headers["User-Agent"] = credentials.user_agent
    headers["Referer"] = ALLOWED_REFERER
    headers["Cookie"] = f"PHPSESSID={credentials.session_id}"
    return headers


def build_http_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}), NoRedirectHandler()
    )


def perform_request(config: Config, credentials: Credentials) -> ResponseSnapshot:
    opener = build_http_opener()
    attempts = 0
    last_error: str | None = None
    for attempt in range(config.retries + 1):
        attempts = attempt + 1
        request = urllib.request.Request(
            config.api_url,
            headers=request_headers(credentials),
            method="GET",
        )
        try:
            with opener.open(request, timeout=config.timeout_seconds) as response:
                body = response.read()
                status = response.getcode()
                snapshot = ResponseSnapshot(
                    status=status,
                    headers=response.headers,
                    body=body,
                    network_error=None,
                    attempts=attempts,
                )
        except urllib.error.HTTPError as error:
            snapshot = ResponseSnapshot(
                status=error.code,
                headers=error.headers,
                body=error.read(),
                network_error=None,
                attempts=attempts,
            )
        except (
            urllib.error.URLError,
            TimeoutError,
            socket.timeout,
            ConnectionError,
        ) as error:
            last_error = type(error).__name__
            if attempt < config.retries:
                time.sleep(min(2 ** attempt, 5))
                continue
            return ResponseSnapshot(
                status=None,
                headers={},
                body=b"",
                network_error=last_error,
                attempts=attempts,
            )
        if (
            snapshot.status is not None
            and 500 <= snapshot.status <= 599
            and attempt < config.retries
        ):
            time.sleep(min(2 ** attempt, 5))
            continue
        return snapshot
    return ResponseSnapshot(
        status=None,
        headers={},
        body=b"",
        network_error=last_error or "UnknownNetworkError",
        attempts=attempts,
    )


def header_values(headers: Any, name: str) -> list[str]:
    if headers is None:
        return []
    getter = getattr(headers, "get_all", None)
    if callable(getter):
        return [str(value) for value in getter(name, [])]
    value = headers.get(name) if hasattr(headers, "get") else None
    return [str(value)] if value else []


def update_sessions_from_response(
    credentials: Credentials,
    snapshot: ResponseSnapshot,
) -> tuple[list[str], bool]:
    set_cookie_names: list[str] = []
    saw_other_cookie = False
    changed = False
    for raw_set_cookie in header_values(snapshot.headers, "Set-Cookie"):
        parsed = http.cookies.SimpleCookie()
        try:
            parsed.load(raw_set_cookie)
        except http.cookies.CookieError:
            continue
        for name, morsel in parsed.items():
            if name != "PHPSESSID":
                saw_other_cookie = True
                continue
            set_cookie_names.append("PHPSESSID")
            if credentials.session_id != morsel.value:
                credentials.session_id = morsel.value
                changed = True
    if saw_other_cookie:
        set_cookie_names.append("<other>")
    return sorted(set(set_cookie_names)), changed


def first_json_value(data: Any, keys: tuple[str, ...]) -> Any:
    if not isinstance(data, dict):
        return None
    for key in keys:
        if key in data:
            return data[key]
    return None


def parse_json_body(body: bytes) -> Any:
    if not body:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def classify_response(
    snapshot: ResponseSnapshot,
    expected_markers: tuple[str, ...],
) -> tuple[str, Any, str | None, str | None]:
    """Return login state, business code, redirect host, and redirect path."""

    if snapshot.network_error:
        return "network_error", None, None, None
    status = snapshot.status
    location = (
        str(snapshot.headers.get("Location", ""))
        if hasattr(snapshot.headers, "get")
        else ""
    )
    location_parts = urlsplit(location) if location else None
    redirect_host = location_parts.hostname if location_parts else None
    redirect_path = location_parts.path if location_parts else None
    if status in (401, 403):
        return "expired", None, redirect_host, redirect_path
    if status in (301, 302, 303, 307, 308):
        location_lower = location.lower()
        if (
            redirect_host == "open.weixin.qq.com"
            or "/oauth" in location_lower
            or "/login" in location_lower
        ):
            return "expired", None, redirect_host, redirect_path
        return "redirect", None, redirect_host, redirect_path

    payload = parse_json_body(snapshot.body)
    business_code = first_json_value(payload, BUSINESS_CODE_KEYS)
    login_value = first_json_value(payload, LOGIN_STATE_KEYS)
    if login_value is False or login_value in (0, "0", "false", "False"):
        return "expired", business_code, redirect_host, redirect_path
    text = snapshot.body.decode("utf-8", "replace")
    text_lower = text.lower()
    if any(marker.lower() in text_lower for marker in IDENTITY_ERROR_MARKERS):
        return "expired", business_code, redirect_host, redirect_path
    if (
        status == 200
        and expected_markers
        and all(marker in text for marker in expected_markers)
    ):
        return "authenticated", business_code, redirect_host, redirect_path
    return "unknown", business_code, redirect_host, redirect_path


def make_log_record(
    sample_index: int,
    elapsed_seconds: int,
    snapshot: ResponseSnapshot,
    credentials: Credentials,
    fingerprint_key: bytes,
) -> tuple[dict[str, Any], str]:
    set_cookie_names, session_changed = update_sessions_from_response(
        credentials, snapshot
    )
    login_state, business_code, redirect_host, redirect_path = classify_response(
        snapshot, AUTHENTICATED_HTML_MARKERS
    )
    if not isinstance(business_code, (str, int, float, bool, type(None))):
        business_code = None
    if isinstance(business_code, str):
        business_code = business_code[:64]
    record = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "sample": sample_index,
        "elapsed_seconds": elapsed_seconds,
        "http_status": snapshot.status,
        "business_code": business_code,
        "login_state": login_state,
        "session_fingerprints": session_fingerprints(
            credentials, fingerprint_key
        ),
        "session_changed": session_changed,
        "set_cookie": bool(set_cookie_names),
        "set_cookie_names": set_cookie_names,
        "redirect_host": redirect_host,
        "redirect_path": redirect_path,
        "response_bytes": len(snapshot.body),
        "response_sha256": (
            hashlib.sha256(snapshot.body).hexdigest()[:12]
            if snapshot.body
            else None
        ),
        "attempts": snapshot.attempts,
        "network_error": snapshot.network_error,
    }
    return record, login_state


def append_log(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name != "nt":
        path.parent.chmod(0o700)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    file_descriptor = os.open(path, flags, 0o600)
    if os.name != "nt":
        file_status = os.fstat(file_descriptor)
        if not stat.S_ISREG(file_status.st_mode) or file_status.st_nlink != 1:
            os.close(file_descriptor)
            raise ValueError("Log path must be a regular single-link file")
        os.fchmod(file_descriptor, 0o600)
    with os.fdopen(
        file_descriptor, "a", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(line + "\n")


def scheduled_offsets(duration_seconds: int, interval_seconds: int) -> list[int]:
    offsets = list(range(0, duration_seconds + 1, interval_seconds))
    if offsets[-1] != duration_seconds:
        offsets.append(duration_seconds)
    return offsets


def run(config: Config, credentials: Credentials) -> int:
    fingerprint_key = secrets.token_bytes(32)
    start_record = {
        "event": "start",
        "run_id": secrets.token_hex(8),
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "api_host": urlsplit(config.api_url).hostname,
        "api_path": urlsplit(config.api_url).path,
        "interval_seconds": config.interval_seconds,
        "duration_seconds": 0 if config.once else config.duration_seconds,
        "timeout_seconds": config.timeout_seconds,
        "retries": config.retries,
        "session_fingerprints": session_fingerprints(
            credentials, fingerprint_key
        ),
    }
    append_log(config.log_path, start_record)
    if config.dry_run:
        append_log(
            config.log_path,
            {
                "event": "dry_run_complete",
                "timestamp": datetime.now()
                .astimezone()
                .isoformat(timespec="seconds"),
            },
        )
        return 0

    offsets = [0] if config.once else scheduled_offsets(
        config.duration_seconds, config.interval_seconds
    )
    monotonic_start = time.monotonic()
    consecutive_unknown = 0
    for sample_index, offset in enumerate(offsets, 1):
        wait_seconds = monotonic_start + offset - time.monotonic()
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        snapshot = perform_request(config, credentials)
        elapsed = int(round(time.monotonic() - monotonic_start))
        record, login_state = make_log_record(
            sample_index,
            elapsed,
            snapshot,
            credentials,
            fingerprint_key,
        )
        append_log(config.log_path, record)
        if login_state == "expired":
            append_log(
                config.log_path,
                {
                    "event": "stopped_identity_expired",
                    "timestamp": datetime.now()
                    .astimezone()
                    .isoformat(timespec="seconds"),
                    "sample": sample_index,
                },
            )
            return 2
        if login_state in {"unknown", "network_error", "redirect"}:
            consecutive_unknown += 1
        else:
            consecutive_unknown = 0
        if consecutive_unknown >= MAX_CONSECUTIVE_UNKNOWN:
            append_log(
                config.log_path,
                {
                    "event": "stopped_consecutive_unknown",
                    "timestamp": datetime.now()
                    .astimezone()
                    .isoformat(timespec="seconds"),
                    "sample": sample_index,
                    "consecutive_unknown": consecutive_unknown,
                    "last_login_state": login_state,
                },
            )
            return 3
    append_log(
        config.log_path,
        {
            "event": "complete",
            "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
            "samples": len(offsets),
        },
    )
    return 0


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args)
        if config.dry_run:
            return run(config, Credentials(session_id="", user_agent=""))
        credentials = load_credentials(config.credential_file)
        return run(config, credentials)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(
            json.dumps(
                {
                    "event": "configuration_error",
                    "error": type(error).__name__,
                    "message": str(error),
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
