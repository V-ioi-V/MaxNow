from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import http.cookies
import json
import math
import os
import re
import socket
import stat
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
STORE_ID = "54114"
BASE_URL = "https://gm.wendaosoft.com"
HOME_PATH = f"/gm/weixin/home/index/{STORE_ID}"
ATTENDANCE_PATH = f"/gm/weixin/my/checkrecord/{STORE_ID}"
BOOKING_PATH = f"/gm/weixin/my/bookrecord/{STORE_ID}"
MEMBERSHIP_PATH = f"/gm/weixin/my/mycard/{STORE_ID}"
DETAIL_PATH_PATTERN = re.compile(
    rf"^/gm/weixin/my/bookrecordone/{STORE_ID}/([1-9][0-9]{{0,19}})$"
)
TIMEZONE = timezone(timedelta(hours=8), "Asia/Shanghai")
CLASSIFICATION_VERSION = 1
SCHEMA_VERSION = 1
DEFAULT_STATE_DIR = Path("/var/lib/maxnow-ballet")
DEFAULT_OUTPUT = ROOT / "dash" / "data" / "ballet.json"
GLOBAL_NAME = "MAXNOW_BALLET_DATA"
MAX_RESPONSE_BYTES = 2_000_000
ROLLING_DAYS = 60
CACHE_TTL_HOURS = 36

COURSE_TYPE_ORDER = (
    "ballet",
    "soft_open",
    "conditioning",
    "technique",
    "other",
)
COURSE_TYPE_LABELS = {
    "ballet": "芭蕾",
    "soft_open": "软开",
    "conditioning": "肌肉素质",
    "technique": "技术技巧",
    "other": "其他",
}
LEVEL_ORDER = ("L1", "L1.5", "L2", "L3", "L4", "none")
LEVEL_LABELS = {
    "L1": "L1",
    "L1.5": "L1.5",
    "L2": "L2",
    "L3": "L3",
    "L4": "L4",
    "none": "无级别",
}

SAFE_ERROR_MESSAGES = {
    "auth_required": "微信授权或闻道会话已失效，请在电脑微信重新登录并打开约课页面后更新服务器凭据。",
    "network_error": "闻道暂时无法连接，已保留上次成功数据。",
    "http_error": "闻道只读接口暂时异常，已保留上次成功数据。",
    "source_changed": "闻道页面结构或数据范围发生变化，需要检查采集规则。",
    "parse_error": "闻道返回的数据无法安全解析，需要检查采集规则。",
    "duplicate_key": "上课记录出现无法安全合并的重复场次，需要人工确认。",
    "configuration_error": "芭蕾同步配置不完整或不安全。",
    "write_error": "本地缓存写入失败，已保留可恢复的数据文件。",
}


class SyncFailure(Exception):
    def __init__(self, code: str):
        super().__init__(SAFE_ERROR_MESSAGES.get(code, "芭蕾数据同步失败。"))
        self.code = code


@dataclass
class Credentials:
    session_id: str
    user_agent: str


@dataclass
class SyncPaths:
    state_dir: Path
    ledger: Path
    sync_state: Path
    booking: Path
    membership: Path
    output: Path
    wrapper: Path


@dataclass
class SyncResult:
    exit_code: int
    status: str
    source_records: int
    merged_records: int
    changed_records: int
    session_rotated: bool


def iso_now(now: datetime | None = None) -> str:
    value = now or datetime.now(TIMEZONE)
    if value.tzinfo is None:
        value = value.replace(tzinfo=TIMEZONE)
    return value.astimezone(TIMEZONE).isoformat(timespec="seconds")


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=TIMEZONE)
    return parsed.astimezone(TIMEZONE)


def normalize_space(value: str) -> str:
    return " ".join(html.unescape(value or "").replace("\u3000", " ").split())


def normalize_course_name(value: str) -> str:
    return normalize_space(value).replace("．", ".").replace("。", ".").upper()


def safe_read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise SyncFailure("parse_error")


def _fsync_directory(path: Path) -> None:
    if os.name == "nt" or not hasattr(os, "O_DIRECTORY"):
        return
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_write_text(path: Path, text: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        if os.name != "nt":
            os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        if os.name != "nt":
            path.chmod(mode)
        _fsync_directory(path.parent)
    except Exception:
        try:
            temporary.unlink(missing_ok=True)
        finally:
            raise


def atomic_write_json(path: Path, payload: Any, mode: int = 0o644) -> None:
    atomic_write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        mode=mode,
    )


def load_credentials(path: Path) -> Credentials:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError:
        raise SyncFailure("configuration_error")
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise SyncFailure("configuration_error")
        if os.name != "nt" and stat.S_IMODE(info.st_mode) not in {
            0o400,
            0o440,
            0o600,
        }:
            raise SyncFailure("configuration_error")
        with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
            descriptor = -1
            payload = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise SyncFailure("configuration_error")
    finally:
        if descriptor >= 0:
            os.close(descriptor)

    if not isinstance(payload, dict) or set(payload) != {
        "PHPSESSID",
        "user_agent",
    }:
        raise SyncFailure("configuration_error")
    session_id = str(payload.get("PHPSESSID", "")).strip()
    user_agent = str(payload.get("user_agent", "")).strip()
    if (
        not re.fullmatch(r"[A-Za-z0-9,-]{16,256}", session_id)
        or "\r" in user_agent
        or "\n" in user_agent
        or not 10 <= len(user_agent) <= 512
    ):
        raise SyncFailure("configuration_error")
    return Credentials(session_id=session_id, user_agent=user_agent)


def load_credential_version(path: Path) -> str:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError:
        raise SyncFailure("configuration_error")
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise SyncFailure("configuration_error")
        if os.name != "nt" and stat.S_IMODE(info.st_mode) not in {
            0o400,
            0o440,
            0o600,
        }:
            raise SyncFailure("configuration_error")
        with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
            descriptor = -1
            value = handle.read(128).strip()
    except (OSError, UnicodeError):
        raise SyncFailure("configuration_error")
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", value):
        raise SyncFailure("configuration_error")
    return value


def auth_retry_is_blocked(path: Path, credential_version: str) -> bool:
    state = safe_read_json(path, empty_sync_state())
    return (
        state.get("lastAttemptStatus") == "auth_required"
        and state.get("credentialVersion") == credential_version
    )


def validate_read_only_path(path: str) -> str:
    if path in {ATTENDANCE_PATH, BOOKING_PATH, MEMBERSHIP_PATH}:
        return path
    if DETAIL_PATH_PATTERN.fullmatch(path):
        return path
    raise SyncFailure("configuration_error")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _read_limited(response: Any) -> bytes:
    body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise SyncFailure("source_changed")
    return body


def _is_auth_response(status: int, headers: Any, text: str) -> bool:
    if status in {401, 403}:
        return True
    location = str(headers.get("Location", "")) if headers else ""
    if status in {301, 302, 303, 307, 308}:
        lowered = location.lower()
        return "open.weixin.qq.com" in lowered or "oauth" in lowered or "/login" in lowered
    lowered_text = text.lower()
    return any(
        marker in lowered_text
        for marker in (
            "open.weixin.qq.com/connect/oauth2",
            "请在微信客户端打开链接",
            "请先登录",
        )
    )


class WendaSource:
    def __init__(
        self,
        credentials: Credentials,
        timeout_seconds: int = 20,
        retries: int = 2,
    ):
        self.credentials = credentials
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.session_rotated = False
        self.request_count = 0
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), NoRedirect()
        )

    def _headers(self, path: str) -> dict[str, str]:
        referer = (
            BASE_URL + ATTENDANCE_PATH
            if DETAIL_PATH_PATTERN.fullmatch(path)
            else BASE_URL + HOME_PATH
        )
        return {
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "close",
            "Cookie": f"PHPSESSID={self.credentials.session_id}",
            "Referer": referer,
            "User-Agent": self.credentials.user_agent,
        }

    def _update_session_in_memory(self, headers: Any) -> None:
        values = []
        getter = getattr(headers, "get_all", None)
        if callable(getter):
            values = getter("Set-Cookie", [])
        elif headers and headers.get("Set-Cookie"):
            values = [headers.get("Set-Cookie")]
        for raw in values:
            parsed = http.cookies.SimpleCookie()
            try:
                parsed.load(str(raw))
            except http.cookies.CookieError:
                continue
            if "PHPSESSID" not in parsed:
                continue
            next_value = parsed["PHPSESSID"].value
            if re.fullmatch(r"[A-Za-z0-9,-]{16,256}", next_value):
                if next_value != self.credentials.session_id:
                    self.credentials.session_id = next_value
                    self.session_rotated = True

    def request(self, path: str, expected_marker: str) -> str:
        path = validate_read_only_path(path)
        last_network_failure = False
        for attempt in range(self.retries + 1):
            self.request_count += 1
            request = urllib.request.Request(
                BASE_URL + path,
                headers=self._headers(path),
                method="GET",
            )
            try:
                with self.opener.open(
                    request, timeout=self.timeout_seconds
                ) as response:
                    status = int(response.status)
                    headers = response.headers
                    body = _read_limited(response)
            except urllib.error.HTTPError as error:
                status = int(error.code)
                headers = error.headers
                body = _read_limited(error)
            except (urllib.error.URLError, TimeoutError, socket.timeout):
                last_network_failure = True
                if attempt < self.retries:
                    time.sleep(min(2**attempt, 3))
                    continue
                raise SyncFailure("network_error")

            self._update_session_in_memory(headers)
            text = body.decode("utf-8", "replace")
            if _is_auth_response(status, headers, text):
                raise SyncFailure("auth_required")
            if status >= 500 and attempt < self.retries:
                time.sleep(min(2**attempt, 3))
                continue
            if status != 200:
                raise SyncFailure("http_error")
            if expected_marker not in text:
                raise SyncFailure("source_changed")
            return text
        if last_network_failure:
            raise SyncFailure("network_error")
        raise SyncFailure("http_error")


class FixtureSource:
    def __init__(self, fixture_dir: Path):
        self.fixture_dir = fixture_dir
        self.session_rotated = False
        self.request_count = 0

    def request(self, path: str, expected_marker: str) -> str:
        path = validate_read_only_path(path)
        self.request_count += 1
        if path == ATTENDANCE_PATH:
            fixture = self.fixture_dir / "attendance.html"
        elif path == BOOKING_PATH:
            fixture = self.fixture_dir / "booking.html"
        elif path == MEMBERSHIP_PATH:
            fixture = self.fixture_dir / "membership.html"
        else:
            match = DETAIL_PATH_PATTERN.fullmatch(path)
            if not match:
                raise SyncFailure("configuration_error")
            fixture = self.fixture_dir / "details" / f"{match.group(1)}.html"
        try:
            text = fixture.read_text(encoding="utf-8")
        except OSError:
            raise SyncFailure("parse_error")
        if expected_marker not in text:
            raise SyncFailure("source_changed")
        return text


class DetailLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_href: str | None = None
        self.current_parts: list[str] = []
        self.current_course_parts: list[str] = []
        self.in_course = False
        self.links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        values = dict(attrs)
        if tag == "a":
            href = values.get("href") or ""
            parts = urlsplit(html.unescape(href))
            path = parts.path if parts.scheme or parts.netloc else href.split("?", 1)[0]
            if DETAIL_PATH_PATTERN.fullmatch(path):
                self.current_href = path
                self.current_parts = []
                self.current_course_parts = []
        elif tag == "p" and self.current_href:
            self.in_course = True

    def handle_endtag(self, tag: str):
        if tag == "p":
            self.in_course = False
        elif tag == "a" and self.current_href:
            text = normalize_space("".join(self.current_parts))
            course = normalize_space("".join(self.current_course_parts))
            date_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
            status = next(
                (
                    label
                    for label in ("已预约", "排队中", "候补中", "已上课", "已完成", "已取消")
                    if label in text
                ),
                "",
            )
            self.links.append(
                {
                    "detailPath": self.current_href,
                    "sourceRecordId": self.current_href.rsplit("/", 1)[-1],
                    "courseName": course,
                    "date": date_match.group(1) if date_match else "",
                    "status": status,
                    "text": text,
                }
            )
            self.current_href = None
            self.current_parts = []
            self.current_course_parts = []

    def handle_data(self, data: str):
        if self.current_href:
            self.current_parts.append(data)
            if self.in_course:
                self.current_course_parts.append(data)


class DetailCellParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.div_stack: list[set[str]] = []
        self.current: dict[str, list[str]] | None = None
        self.root_depth = 0
        self.section: str | None = None
        self.cells: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag != "div":
            return
        classes = set((dict(attrs).get("class") or "").split())
        self.div_stack.append(classes)
        if self.current is None and "weui-cell" in classes:
            self.current = {"label": [], "value": []}
            self.root_depth = len(self.div_stack)
        elif self.current is not None:
            if "weui-cell__bd" in classes:
                self.section = "label"
            elif "weui-cell__ft" in classes:
                self.section = "value"

    def handle_endtag(self, tag: str):
        if tag != "div" or not self.div_stack:
            return
        classes = self.div_stack[-1]
        if self.current is not None:
            if "weui-cell__bd" in classes or "weui-cell__ft" in classes:
                self.section = None
            if len(self.div_stack) == self.root_depth:
                label = normalize_space("".join(self.current["label"]))
                value = normalize_space("".join(self.current["value"]))
                if label:
                    self.cells.append((label, value))
                self.current = None
                self.root_depth = 0
                self.section = None
        self.div_stack.pop()

    def handle_data(self, data: str):
        if self.current is not None and self.section:
            self.current[self.section].append(data)


class MembershipCardParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_href: str | None = None
        self.current_parts: list[str] = []
        self.cards: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag != "a":
            return
        href = html.unescape(dict(attrs).get("href") or "")
        path = urlsplit(href).path if href else ""
        if re.fullmatch(
            rf"/gm/weixin/my/mycardone/{STORE_ID}/[1-9][0-9]{{0,19}}",
            path,
        ):
            self.current_href = path
            self.current_parts = []

    def handle_endtag(self, tag: str):
        if tag == "a" and self.current_href:
            parts = [
                normalize_space(value)
                for value in self.current_parts
                if normalize_space(value)
            ]
            if parts:
                self.cards.append(parts)
            self.current_href = None
            self.current_parts = []

    def handle_data(self, data: str):
        if self.current_href:
            self.current_parts.append(data)


def parse_index(text: str, kind: str) -> list[dict[str, str]]:
    parser = DetailLinkParser()
    try:
        parser.feed(text)
    except Exception:
        raise SyncFailure("parse_error")
    unique: dict[str, dict[str, str]] = {}
    for item in parser.links:
        source_id = item["sourceRecordId"]
        if source_id in unique:
            raise SyncFailure("duplicate_key")
        unique[source_id] = item

    if kind == "attendance":
        total_match = re.search(r"共\s*(\d+)\s*次", text)
        if not total_match or int(total_match.group(1)) != len(unique):
            raise SyncFailure("source_changed")
    return list(unique.values())


def parse_detail(text: str, source_record_id: str) -> dict[str, Any]:
    parser = DetailCellParser()
    try:
        parser.feed(text)
    except Exception:
        raise SyncFailure("parse_error")
    fields = {normalize_space(label): normalize_space(value) for label, value in parser.cells}
    aliases = {
        "courseName": ("课程名称",),
        "dateText": ("课程日期",),
        "timeText": ("课程时间",),
        "teacher": ("教师名称", "老师名称"),
        "venue": ("场地名称", "教室名称"),
        "studio": ("门店名称", "门店"),
        "bookingStatus": ("预约状态",),
        "bookedAt": ("预约时间",),
        "attendedAt": ("上课时间", "签到时间"),
        "cancelDeadline": ("取消时间",),
    }
    result: dict[str, Any] = {"sourceRecordId": source_record_id}
    for target, candidates in aliases.items():
        result[target] = next(
            (fields[candidate] for candidate in candidates if candidate in fields),
            "",
        )

    date_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", result["dateText"])
    if not result["courseName"] or not date_match:
        raise SyncFailure("parse_error")
    result["date"] = date_match.group(1)
    try:
        date.fromisoformat(result["date"])
    except ValueError:
        raise SyncFailure("parse_error")

    time_match = re.search(
        r"([01]\d|2[0-3]):([0-5]\d)\s*[~～—–-]\s*([01]\d|2[0-3]):([0-5]\d)",
        result["timeText"],
    )
    if time_match:
        start_minutes = int(time_match.group(1)) * 60 + int(time_match.group(2))
        end_minutes = int(time_match.group(3)) * 60 + int(time_match.group(4))
        if end_minutes < start_minutes:
            end_minutes += 24 * 60
        duration = end_minutes - start_minutes
        if not 0 < duration <= 8 * 60:
            raise SyncFailure("parse_error")
        result["startTime"] = f"{time_match.group(1)}:{time_match.group(2)}"
        result["endTime"] = f"{time_match.group(3)}:{time_match.group(4)}"
        result["durationMinutes"] = duration
    else:
        result["startTime"] = ""
        result["endTime"] = ""
        result["durationMinutes"] = None
    return result


def parse_membership(text: str) -> list[dict[str, Any]]:
    parser = MembershipCardParser()
    try:
        parser.feed(text)
    except Exception:
        raise SyncFailure("parse_error")
    cards: list[dict[str, Any]] = []
    for parts in parser.cards:
        combined = normalize_space(" ".join(parts))
        validity = re.search(
            r"有效期\s*[:：]?\s*(20\d{2}-\d{2}-\d{2})"
            r"\s*[~～—–]\s*(20\d{2}-\d{2}-\d{2})",
            combined,
        )
        balance = re.search(
            r"卡内余\s*[:：]?\s*(\d+)\s*次\s*/\s*总\s*(\d+)\s*次",
            combined,
        )
        name = next(
            (
                part
                for part in parts
                if "有效期" not in part and "卡内余" not in part
            ),
            "",
        )
        if not name or not validity or not balance:
            raise SyncFailure("source_changed")
        valid_from, valid_through = validity.groups()
        remaining, total = (int(value) for value in balance.groups())
        try:
            date.fromisoformat(valid_from)
            date.fromisoformat(valid_through)
        except ValueError:
            raise SyncFailure("parse_error")
        if valid_through < valid_from or remaining < 0 or total <= 0 or remaining > total:
            raise SyncFailure("parse_error")
        cards.append(
            {
                "name": name,
                "validFrom": valid_from,
                "validThrough": valid_through,
                "remainingClasses": remaining,
                "totalClasses": total,
                "usedClasses": total - remaining,
            }
        )
    return cards


def parse_cancellation_rule(
    raw_value: str,
    course_date: str,
    start_time: str,
) -> dict[str, Any]:
    rule_text = normalize_space(raw_value)
    result = {
        "cancelRuleText": rule_text,
        "cancelHoursBefore": None,
        "cancelDeadlineAt": None,
    }
    match = re.search(r"课前\s*(\d+)\s*小时(?:前)?可取消", rule_text)
    if not match or not start_time:
        return result
    hours_before = int(match.group(1))
    if not 0 < hours_before <= 168:
        return result
    try:
        starts_at = datetime.fromisoformat(f"{course_date}T{start_time}").replace(
            tzinfo=TIMEZONE
        )
    except ValueError:
        return result
    result["cancelHoursBefore"] = hours_before
    result["cancelDeadlineAt"] = (
        starts_at - timedelta(hours=hours_before)
    ).isoformat(timespec="minutes")
    return result


def classify_course(course_name: str) -> tuple[str, str]:
    normalized = normalize_course_name(course_name)
    if any(
        marker in normalized
        for marker in ("软开", "柔韧", "前后腿", "横叉", "竖叉")
    ):
        course_type = "soft_open"
    elif "芭蕾" in normalized:
        course_type = "ballet"
    elif any(marker in normalized for marker in ("肌肉素质", "体能", "力量")):
        course_type = "conditioning"
    elif any(marker in normalized for marker in ("技术技巧", "足尖", "技巧专项")):
        course_type = "technique"
    else:
        course_type = "other"

    compact = re.sub(r"\s+", "", normalized)
    if re.search(r"L1[.]5(?!\d)", compact):
        level = "L1.5"
    else:
        level_match = re.search(r"L([1-4])(?![.\d])", compact)
        level = f"L{level_match.group(1)}" if level_match else "none"
    return course_type, level


def stable_key(record: dict[str, Any]) -> tuple[str, bool]:
    source_id = str(record.get("sourceRecordId", "")).strip()
    if source_id:
        return f"attendance:{source_id}", False
    course_instance_id = str(record.get("courseInstanceId", "")).strip()
    if course_instance_id:
        return f"class:{course_instance_id}", False
    components = [
        normalize_space(str(record.get("studio", ""))).lower(),
        str(record.get("date", "")),
        str(record.get("startTime", "")),
        str(record.get("endTime", "")),
        normalize_course_name(str(record.get("courseName", ""))),
        normalize_space(str(record.get("teacher", ""))).lower(),
    ]
    if not all(components[1:5]):
        raise SyncFailure("parse_error")
    digest = hashlib.sha256("\x1f".join(components).encode("utf-8")).hexdigest()
    return f"fallback:{digest}", True


def normalize_attendance(
    detail: dict[str, Any],
    observed_at: str,
    existing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    status = normalize_space(detail.get("bookingStatus", ""))
    if status not in {"已上课", "已完成"}:
        raise SyncFailure("source_changed")
    course_type, level = classify_course(detail["courseName"])
    key, fallback = stable_key(detail)
    record = {
        "stableKey": key,
        "keySource": "fallback" if fallback else "source_record_id",
        "source": {
            "attendanceRecordId": detail.get("sourceRecordId") or None,
            "courseInstanceId": detail.get("courseInstanceId") or None,
        },
        "courseName": normalize_space(detail["courseName"]),
        "courseType": course_type,
        "level": level,
        "date": detail["date"],
        "startTime": detail.get("startTime") or "",
        "endTime": detail.get("endTime") or "",
        "durationMinutes": detail.get("durationMinutes"),
        "teacher": normalize_space(detail.get("teacher", "")),
        "venue": normalize_space(detail.get("venue", "")),
        "studio": normalize_space(detail.get("studio", "")),
        "attendanceStatus": "attended",
        "bookedAt": normalize_space(detail.get("bookedAt", "")),
        "attendedAt": normalize_space(detail.get("attendedAt", "")),
        "firstSeenAt": (existing or {}).get("firstSeenAt") or observed_at,
        "lastSeenAt": observed_at,
        "missingFullSyncCount": 0,
        "recordState": "active",
    }
    return record


def normalize_manual_attendance(
    detail: dict[str, Any], observed_at: str
) -> dict[str, Any]:
    course_name = normalize_space(str(detail.get("courseName", "")))
    day = str(detail.get("date", ""))
    start_time = str(detail.get("startTime", ""))
    end_time = str(detail.get("endTime", ""))
    teacher = normalize_space(str(detail.get("teacher", "")))
    if (
        not course_name
        or not teacher
        or not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", day)
        or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", start_time)
        or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", end_time)
    ):
        raise SyncFailure("configuration_error")
    try:
        date.fromisoformat(day)
    except ValueError:
        raise SyncFailure("configuration_error")
    start_minutes = int(start_time[:2]) * 60 + int(start_time[3:])
    end_minutes = int(end_time[:2]) * 60 + int(end_time[3:])
    duration = end_minutes - start_minutes
    if not 0 < duration <= 8 * 60:
        raise SyncFailure("configuration_error")
    course_type, level = classify_course(course_name)
    components = [day, start_time, end_time, normalize_course_name(course_name), teacher]
    digest = hashlib.sha256("\x1f".join(components).encode("utf-8")).hexdigest()
    return {
        "stableKey": f"manual:{digest}",
        "keySource": "manual",
        "source": {"manual": True},
        "courseName": course_name,
        "courseType": course_type,
        "level": level,
        "date": day,
        "startTime": start_time,
        "endTime": end_time,
        "durationMinutes": duration,
        "teacher": teacher,
        "venue": normalize_space(str(detail.get("venue", ""))),
        "studio": normalize_space(str(detail.get("studio", ""))),
        "attendanceStatus": "attended",
        "bookedAt": "",
        "attendedAt": "",
        "firstSeenAt": observed_at,
        "lastSeenAt": observed_at,
        "missingFullSyncCount": 0,
        "recordState": "active",
    }


def normalize_upcoming(detail: dict[str, Any]) -> dict[str, Any] | None:
    raw_status = normalize_space(detail.get("bookingStatus", ""))
    statuses = {
        "已预约": "booked",
        "排队中": "waitlist",
        "候补中": "waitlist",
    }
    normalized_status = (
        "waitlist" if raw_status.startswith("等候中") else statuses.get(raw_status)
    )
    if normalized_status is None:
        return None
    queue_match = re.search(
        r"排队序号\s*(\d+)",
        raw_status,
    )
    cancellation = parse_cancellation_rule(
        detail.get("cancelDeadline", ""),
        detail["date"],
        detail.get("startTime") or "",
    )
    course_type, level = classify_course(detail["courseName"])
    key = "booking:" + str(detail.get("sourceRecordId") or "")
    return {
        "stableKey": key,
        "source": {"bookingRecordId": detail.get("sourceRecordId") or None},
        "courseName": normalize_space(detail["courseName"]),
        "courseType": course_type,
        "level": level,
        "date": detail["date"],
        "startTime": detail.get("startTime") or "",
        "endTime": detail.get("endTime") or "",
        "durationMinutes": detail.get("durationMinutes"),
        "teacher": normalize_space(detail.get("teacher", "")),
        "venue": normalize_space(detail.get("venue", "")),
        "studio": normalize_space(detail.get("studio", "")),
        "bookingStatus": normalized_status,
        "waitlistPosition": (
            int(queue_match.group(1))
            if normalized_status == "waitlist" and queue_match
            else None
        ),
        **cancellation,
    }


def empty_ledger() -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "timezone": "Asia/Shanghai",
        "classificationVersion": CLASSIFICATION_VERSION,
        "lastSuccessfulSyncAt": None,
        "lastFullSyncAt": None,
        "contentFingerprint": None,
        "records": [],
        "aliases": {},
    }


def empty_booking() -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "timezone": "Asia/Shanghai",
        "dataAsOf": None,
        "ttlHours": CACHE_TTL_HOURS,
        "records": [],
    }


def empty_membership() -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "timezone": "Asia/Shanghai",
        "dataAsOf": None,
        "cards": [],
    }


def empty_sync_state() -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "logicalDate": None,
        "lastAttemptAt": None,
        "lastSuccessAt": None,
        "lastDataChangeAt": None,
        "lastAttemptStatus": "never",
        "consecutiveFailures": 0,
        "errorCode": None,
        "errorMessage": None,
        "window": None,
        "sourceRecords": 0,
        "mergedRecords": 0,
        "changedRecords": 0,
        "requestsMade": 0,
        "sessionRotatedInMemory": False,
        "credentialVersion": None,
    }


def _business_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in record.items()
        if key not in {"firstSeenAt", "lastSeenAt", "missingFullSyncCount"}
    }


def content_fingerprint(records: list[dict[str, Any]]) -> str:
    payload = [_business_record(item) for item in records]
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_ledger(ledger: dict[str, Any]) -> None:
    if ledger.get("schemaVersion") != SCHEMA_VERSION:
        raise SyncFailure("parse_error")
    records = ledger.get("records")
    if not isinstance(records, list):
        raise SyncFailure("parse_error")
    keys: set[str] = set()
    fallback_keys: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise SyncFailure("parse_error")
        key = record.get("stableKey")
        if not isinstance(key, str) or key in keys:
            raise SyncFailure("duplicate_key")
        keys.add(key)
        if record.get("keySource") == "fallback":
            if key in fallback_keys:
                raise SyncFailure("duplicate_key")
            fallback_keys.add(key)
        duration = record.get("durationMinutes")
        if duration is not None and (
            isinstance(duration, bool)
            or not isinstance(duration, int)
            or not 0 < duration <= 480
        ):
            raise SyncFailure("parse_error")
        if record.get("courseType") not in COURSE_TYPE_ORDER:
            raise SyncFailure("parse_error")
        if record.get("level") not in LEVEL_ORDER:
            raise SyncFailure("parse_error")


def _period_bucket() -> dict[str, Any]:
    return {
        "classes": 0,
        "minutes": 0,
        "missingDurationClasses": 0,
        "byCourseType": {
            key: {"classes": 0, "minutes": 0} for key in COURSE_TYPE_ORDER
        },
        "byLevel": {key: {"classes": 0, "minutes": 0} for key in LEVEL_ORDER},
    }


def _add_to_bucket(bucket: dict[str, Any], record: dict[str, Any]) -> None:
    bucket["classes"] += 1
    duration = record.get("durationMinutes")
    if duration is None:
        bucket["missingDurationClasses"] += 1
    else:
        bucket["minutes"] += duration
    bucket["byCourseType"][record["courseType"]]["classes"] += 1
    bucket["byLevel"][record["level"]]["classes"] += 1
    if duration is not None:
        bucket["byCourseType"][record["courseType"]]["minutes"] += duration
        bucket["byLevel"][record["level"]]["minutes"] += duration


def _display_bucket(period: str, bucket: dict[str, Any]) -> dict[str, Any]:
    return {
        "period": period,
        "classes": bucket["classes"],
        "minutes": bucket["minutes"],
        "hours": round(bucket["minutes"] / 60, 2),
        "missingDurationClasses": bucket["missingDurationClasses"],
        "byCourseType": [
            {
                "key": key,
                "label": COURSE_TYPE_LABELS[key],
                **bucket["byCourseType"][key],
            }
            for key in COURSE_TYPE_ORDER
        ],
        "byLevel": [
            {
                "key": key,
                "label": LEVEL_LABELS[key],
                **bucket["byLevel"][key],
            }
            for key in LEVEL_ORDER
        ],
    }


def _month_range(start: str, end: str) -> list[str]:
    year, month = map(int, start.split("-"))
    end_year, end_month = map(int, end.split("-"))
    values = []
    while (year, month) <= (end_year, end_month):
        values.append(f"{year:04d}-{month:02d}")
        month += 1
        if month == 13:
            year += 1
            month = 1
    return values


def compute_aggregates(
    records: list[dict[str, Any]], now: datetime
) -> tuple[dict[str, Any], dict[str, Any]]:
    active = [
        item
        for item in records
        if item.get("recordState") == "active"
        and item.get("attendanceStatus") == "attended"
    ]
    daily: dict[str, dict[str, Any]] = {}
    monthly: dict[str, dict[str, Any]] = {}
    yearly: dict[str, dict[str, Any]] = {}
    total = _period_bucket()
    for record in active:
        day = record["date"]
        month = day[:7]
        year = day[:4]
        daily.setdefault(day, _period_bucket())
        monthly.setdefault(month, _period_bucket())
        yearly.setdefault(year, _period_bucket())
        for bucket in (total, daily[day], monthly[month], yearly[year]):
            _add_to_bucket(bucket, record)

    if active:
        first_month = min(item["date"][:7] for item in active)
        current_month = now.astimezone(TIMEZONE).strftime("%Y-%m")
        for month in _month_range(first_month, max(first_month, current_month)):
            monthly.setdefault(month, _period_bucket())
        first_year = min(item["date"][:4] for item in active)
        current_year = now.astimezone(TIMEZONE).strftime("%Y")
        for year in range(int(first_year), max(int(first_year), int(current_year)) + 1):
            yearly.setdefault(str(year), _period_bucket())

    summary = _display_bucket("all", total)
    aggregates = {
        "daily": [_display_bucket(key, daily[key]) for key in sorted(daily)],
        "monthly": [_display_bucket(key, monthly[key]) for key in sorted(monthly)],
        "yearly": [_display_bucket(key, yearly[key]) for key in sorted(yearly)],
    }
    return summary, aggregates


def _cache_state(last_success: str | None, now: datetime) -> str:
    parsed = parse_iso(last_success)
    if not parsed:
        return "unavailable"
    age = now.astimezone(TIMEZONE) - parsed
    return "fresh" if age <= timedelta(hours=CACHE_TTL_HOURS) else "stale"


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "courseName": record["courseName"],
        "courseType": record["courseType"],
        "level": record["level"],
        "date": record["date"],
        "startTime": record["startTime"],
        "endTime": record["endTime"],
        "durationMinutes": record["durationMinutes"],
        "teacher": record["teacher"],
        "venue": record["venue"],
        "studio": record["studio"],
        "attendanceStatus": record["attendanceStatus"],
        "recordOrigin": (
            "manual" if record.get("keySource") == "manual" else "wenda"
        ),
    }


def _public_upcoming(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "courseName": record["courseName"],
        "courseType": record["courseType"],
        "level": record["level"],
        "date": record["date"],
        "startTime": record["startTime"],
        "endTime": record["endTime"],
        "durationMinutes": record["durationMinutes"],
        "teacher": record["teacher"],
        "venue": record["venue"],
        "studio": record["studio"],
        "bookingStatus": record["bookingStatus"],
        "waitlistPosition": record.get("waitlistPosition"),
        "cancelRuleText": record.get("cancelRuleText") or "",
        "cancelHoursBefore": record.get("cancelHoursBefore"),
        "cancelDeadlineAt": record.get("cancelDeadlineAt"),
    }


def compute_week_summary(
    records: list[dict[str, Any]],
    upcoming: list[dict[str, Any]],
    now: datetime,
) -> dict[str, Any]:
    today = now.astimezone(TIMEZONE).date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    def in_week(item: dict[str, Any]) -> bool:
        try:
            day = date.fromisoformat(str(item.get("date", "")))
        except ValueError:
            return False
        return week_start <= day <= week_end

    completed = [item for item in records if in_week(item)]
    booked = [
        item
        for item in upcoming
        if in_week(item) and item.get("bookingStatus") == "booked"
    ]
    waitlist = [
        item
        for item in upcoming
        if in_week(item) and item.get("bookingStatus") == "waitlist"
    ]

    def minutes(items: list[dict[str, Any]]) -> int:
        return sum(
            int(item["durationMinutes"])
            for item in items
            if item.get("durationMinutes") is not None
        )

    completed_minutes = minutes(completed)
    booked_minutes = minutes(booked)
    waitlist_minutes = minutes(waitlist)
    return {
        "weekStart": week_start.isoformat(),
        "weekEnd": week_end.isoformat(),
        "completedClasses": len(completed),
        "completedMinutes": completed_minutes,
        "bookedClasses": len(booked),
        "bookedMinutes": booked_minutes,
        "waitlistClasses": len(waitlist),
        "waitlistMinutes": waitlist_minutes,
        "expectedClassesMin": len(completed) + len(booked),
        "expectedClassesMax": len(completed) + len(booked) + len(waitlist),
        "expectedMinutesMin": completed_minutes + booked_minutes,
        "expectedMinutesMax": completed_minutes + booked_minutes + waitlist_minutes,
    }


def _round_pace(value: float) -> float:
    return round(value + 1e-9, 1)


def build_membership_view(
    membership: dict[str, Any],
    records: list[dict[str, Any]],
    now: datetime,
) -> dict[str, Any]:
    today = now.astimezone(TIMEZONE).date()
    recent_start = today - timedelta(days=27)
    recent_classes = sum(
        1
        for item in records
        if recent_start.isoformat() <= str(item.get("date", "")) <= today.isoformat()
    )
    current_weekly_rate = recent_classes / 4
    cards = []
    for card in membership.get("cards", []):
        valid_through = date.fromisoformat(card["validThrough"])
        remaining_days = max(0, (valid_through - today).days + 1)
        remaining_weeks = remaining_days / 7
        remaining_classes = int(card["remainingClasses"])
        required_rate = (
            remaining_classes / remaining_weeks
            if remaining_classes and remaining_weeks > 0
            else 0
        )
        additional_rate = max(0, required_rate - current_weekly_rate)
        projected_capacity = current_weekly_rate * remaining_weeks
        cards.append(
            {
                **card,
                "pace": {
                    "historyWindowDays": 28,
                    "historyClasses": recent_classes,
                    "currentClassesPerWeek": _round_pace(current_weekly_rate),
                    "remainingDays": remaining_days,
                    "remainingWeeks": _round_pace(remaining_weeks),
                    "requiredClassesPerWeek": _round_pace(required_rate),
                    "recommendedWholeClassesPerWeek": (
                        math.ceil(required_rate) if required_rate > 0 else 0
                    ),
                    "additionalClassesPerWeek": _round_pace(additional_rate),
                    "canFinishAtCurrentPace": (
                        remaining_classes == 0
                        or (
                            remaining_weeks > 0
                            and projected_capacity + 1e-9 >= remaining_classes
                        )
                    ),
                },
            }
        )
    return {
        "dataAsOf": membership.get("dataAsOf"),
        "cards": cards,
    }


def build_read_model(
    ledger: dict[str, Any],
    booking: dict[str, Any],
    membership: dict[str, Any],
    state: dict[str, Any],
    now: datetime,
) -> dict[str, Any]:
    records = [
        item
        for item in ledger.get("records", [])
        if item.get("recordState") == "active"
    ]
    records.sort(
        key=lambda item: (item.get("date", ""), item.get("startTime", "")),
        reverse=True,
    )
    summary, aggregates = compute_aggregates(records, now)
    upcoming = sorted(
        booking.get("records", []),
        key=lambda item: (item.get("date", ""), item.get("startTime", "")),
    )
    last_status = state.get("lastAttemptStatus") or "never"
    auth_status = (
        "needs_login"
        if last_status == "auth_required"
        else ("valid" if last_status == "success" else "unknown")
    )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "timezone": "Asia/Shanghai",
        "dataAsOf": ledger.get("lastSuccessfulSyncAt"),
        "sync": {
            "logicalDate": state.get("logicalDate"),
            "lastAttemptAt": state.get("lastAttemptAt"),
            "lastSuccessAt": state.get("lastSuccessAt"),
            "lastDataChangeAt": state.get("lastDataChangeAt"),
            "lastAttemptStatus": last_status,
            "cacheState": _cache_state(state.get("lastSuccessAt"), now),
            "consecutiveFailures": state.get("consecutiveFailures", 0),
            "errorCode": state.get("errorCode"),
            "errorMessage": state.get("errorMessage"),
            "window": state.get("window"),
            "sourceRecords": state.get("sourceRecords", 0),
            "mergedRecords": state.get("mergedRecords", 0),
            "changedRecords": state.get("changedRecords", 0),
        },
        "classification": {
            "version": CLASSIFICATION_VERSION,
            "courseTypes": [
                {"key": key, "label": COURSE_TYPE_LABELS[key]}
                for key in COURSE_TYPE_ORDER
            ],
            "levels": [
                {"key": key, "label": LEVEL_LABELS[key]}
                for key in LEVEL_ORDER
            ],
        },
        "summary": summary,
        "records": [_public_record(item) for item in records],
        "aggregates": aggregates,
        "upcoming": {
            "dataAsOf": booking.get("dataAsOf"),
            "ttlHours": booking.get("ttlHours", CACHE_TTL_HOURS),
            "records": [_public_upcoming(item) for item in upcoming],
        },
        "week": compute_week_summary(records, upcoming, now),
        "membership": build_membership_view(membership, records, now),
        "learningLogs": [],
        "authHealth": {
            "status": auth_status,
            "checkedAt": state.get("lastAttemptAt"),
            "message": (
                SAFE_ERROR_MESSAGES["auth_required"]
                if auth_status == "needs_login"
                else None
            ),
        },
        "automation": {
            "mode": "off",
            "nextRunAt": None,
            "lastResult": None,
        },
    }


def validate_read_model(model: dict[str, Any]) -> None:
    if model.get("schemaVersion") != SCHEMA_VERSION:
        raise SyncFailure("parse_error")
    summary = model.get("summary") or {}
    records = model.get("records")
    if not isinstance(records, list):
        raise SyncFailure("parse_error")
    if summary.get("classes") != len(records):
        raise SyncFailure("parse_error")
    expected_minutes = sum(
        int(item["durationMinutes"])
        for item in records
        if item.get("durationMinutes") is not None
    )
    if summary.get("minutes") != expected_minutes:
        raise SyncFailure("parse_error")
    week = model.get("week")
    membership = model.get("membership")
    if not isinstance(week, dict) or not isinstance(membership, dict):
        raise SyncFailure("parse_error")
    cards = membership.get("cards")
    if not isinstance(cards, list):
        raise SyncFailure("parse_error")
    for card in cards:
        if (
            not isinstance(card, dict)
            or not isinstance(card.get("remainingClasses"), int)
            or not isinstance(card.get("totalClasses"), int)
            or card["remainingClasses"] > card["totalClasses"]
            or not isinstance(card.get("pace"), dict)
        ):
            raise SyncFailure("parse_error")
    serialized = json.dumps(model, ensure_ascii=False)
    forbidden = (
        "PHPSESSID=",
        '"id":',
        '"source"',
        '"attendanceRecordId"',
        '"bookingRecordId"',
        '"courseInstanceId"',
        '"stableKey"',
    )
    if any(marker in serialized for marker in forbidden):
        raise SyncFailure("parse_error")


def _write_read_model(paths: SyncPaths, model: dict[str, Any]) -> None:
    validate_read_model(model)
    text = json.dumps(model, ensure_ascii=False, indent=2)
    atomic_write_text(paths.output, text + "\n", mode=0o644)
    atomic_write_text(
        paths.wrapper,
        f"window.{GLOBAL_NAME} = {text};\n",
        mode=0o644,
    )


def _logical_window(now: datetime, mode: str) -> dict[str, str]:
    logical_end = now.astimezone(TIMEZONE).date() - timedelta(days=1)
    if mode == "full":
        return {"mode": "full", "from": "all", "through": logical_end.isoformat()}
    logical_start = logical_end - timedelta(days=ROLLING_DAYS - 1)
    return {
        "mode": "rolling",
        "from": logical_start.isoformat(),
        "through": logical_end.isoformat(),
    }


def _needs_detail(
    index_item: dict[str, str],
    existing: dict[str, Any] | None,
    mode: str,
    window: dict[str, str],
) -> bool:
    if not existing or mode == "full":
        return True
    if index_item.get("date") >= window["from"]:
        return True
    return (
        normalize_course_name(index_item.get("courseName", ""))
        != normalize_course_name(existing.get("courseName", ""))
        or index_item.get("date") != existing.get("date")
    )


def _make_failure_state(
    old_state: dict[str, Any],
    now: datetime,
    window: dict[str, str],
    failure: SyncFailure,
    request_count: int,
    session_rotated: bool,
    credential_version: str | None,
    merged_records: int,
) -> dict[str, Any]:
    state = {**empty_sync_state(), **old_state}
    state.update(
        {
            "logicalDate": (now.astimezone(TIMEZONE).date() - timedelta(days=1)).isoformat(),
            "lastAttemptAt": iso_now(now),
            "lastAttemptStatus": failure.code,
            "consecutiveFailures": int(old_state.get("consecutiveFailures", 0)) + 1,
            "errorCode": failure.code,
            "errorMessage": SAFE_ERROR_MESSAGES.get(
                failure.code, "芭蕾数据同步失败。"
            ),
            "window": window,
            "sourceRecords": 0,
            "mergedRecords": merged_records,
            "changedRecords": 0,
            "requestsMade": request_count,
            "sessionRotatedInMemory": session_rotated,
            "credentialVersion": credential_version,
        }
    )
    return state


def synchronize(
    paths: SyncPaths,
    source: WendaSource | FixtureSource,
    mode: str,
    now: datetime,
    dry_run: bool = False,
    credential_version: str | None = None,
) -> SyncResult:
    if mode not in {"rolling", "full"}:
        raise SyncFailure("configuration_error")
    if not dry_run:
        paths.state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        if os.name != "nt":
            paths.state_dir.chmod(0o700)

    ledger = safe_read_json(paths.ledger, empty_ledger())
    booking = safe_read_json(paths.booking, empty_booking())
    membership = safe_read_json(paths.membership, empty_membership())
    old_state = safe_read_json(paths.sync_state, empty_sync_state())
    validate_ledger(ledger)
    window = _logical_window(now, mode)
    observed_at = iso_now(now)

    try:
        attendance_html = source.request(ATTENDANCE_PATH, "上课记录")
        attendance_index = parse_index(attendance_html, "attendance")
        existing_by_id = {
            str((item.get("source") or {}).get("attendanceRecordId")): item
            for item in ledger.get("records", [])
            if (item.get("source") or {}).get("attendanceRecordId")
        }
        detail_cache: dict[str, dict[str, Any]] = {}
        merged_by_key = {
            item["stableKey"]: dict(item) for item in ledger.get("records", [])
        }
        seen_keys: set[str] = set()
        changed_records = 0

        for item in attendance_index:
            source_id = item["sourceRecordId"]
            existing = existing_by_id.get(source_id)
            if _needs_detail(item, existing, mode, window):
                detail_html = source.request(item["detailPath"], "约课记录明细")
                detail = parse_detail(detail_html, source_id)
                detail_cache[source_id] = detail
                normalized = normalize_attendance(detail, observed_at, existing)
            elif existing:
                normalized = dict(existing)
                normalized["lastSeenAt"] = observed_at
                normalized["missingFullSyncCount"] = 0
                normalized["recordState"] = "active"
            else:
                raise SyncFailure("parse_error")

            key = normalized["stableKey"]
            if key in seen_keys:
                raise SyncFailure("duplicate_key")
            seen_keys.add(key)
            previous = merged_by_key.get(key)
            if previous is None or _business_record(previous) != _business_record(normalized):
                changed_records += 1
            merged_by_key[key] = normalized

        if mode == "full":
            for key, record in list(merged_by_key.items()):
                if key in seen_keys or record.get("keySource") == "manual":
                    continue
                missing = int(record.get("missingFullSyncCount", 0)) + 1
                updated = dict(record)
                updated["missingFullSyncCount"] = missing
                if missing >= 2:
                    updated["recordState"] = "tombstone"
                if _business_record(updated) != _business_record(record):
                    changed_records += 1
                merged_by_key[key] = updated

        merged_records = sorted(
            merged_by_key.values(),
            key=lambda item: (
                item.get("date", ""),
                item.get("startTime", ""),
                item.get("stableKey", ""),
            ),
        )
        proposed_ledger = {
            **ledger,
            "schemaVersion": SCHEMA_VERSION,
            "timezone": "Asia/Shanghai",
            "classificationVersion": CLASSIFICATION_VERSION,
            "lastSuccessfulSyncAt": observed_at,
            "lastFullSyncAt": (
                observed_at if mode == "full" else ledger.get("lastFullSyncAt")
            ),
            "records": merged_records,
        }
        fingerprint = content_fingerprint(merged_records)
        proposed_ledger["contentFingerprint"] = fingerprint
        validate_ledger(proposed_ledger)

        booking_html = source.request(BOOKING_PATH, "约课记录")
        booking_index = parse_index(booking_html, "booking")
        active_index = [
            item
            for item in booking_index
            if item.get("status") in {"已预约", "排队中", "候补中"}
        ]
        upcoming: list[dict[str, Any]] = []
        for item in active_index:
            source_id = item["sourceRecordId"]
            detail = detail_cache.get(source_id)
            if detail is None:
                detail_html = source.request(item["detailPath"], "约课记录明细")
                detail = parse_detail(detail_html, source_id)
                detail_cache[source_id] = detail
            normalized = normalize_upcoming(detail)
            if normalized:
                upcoming.append(normalized)
        proposed_booking = {
            "schemaVersion": SCHEMA_VERSION,
            "timezone": "Asia/Shanghai",
            "dataAsOf": observed_at,
            "ttlHours": CACHE_TTL_HOURS,
            "records": upcoming,
        }

        membership_html = source.request(MEMBERSHIP_PATH, "我的会员卡")
        proposed_membership = {
            "schemaVersion": SCHEMA_VERSION,
            "timezone": "Asia/Shanghai",
            "dataAsOf": observed_at,
            "cards": parse_membership(membership_html),
        }

        last_data_change = old_state.get("lastDataChangeAt")
        previous_business = {
            "attendance": ledger.get("contentFingerprint"),
            "upcoming": booking.get("records", []),
            "membership": membership.get("cards", []),
        }
        proposed_business = {
            "attendance": fingerprint,
            "upcoming": proposed_booking["records"],
            "membership": proposed_membership["cards"],
        }
        if previous_business != proposed_business:
            last_data_change = observed_at
        state = {
            **empty_sync_state(),
            "logicalDate": (now.astimezone(TIMEZONE).date() - timedelta(days=1)).isoformat(),
            "lastAttemptAt": observed_at,
            "lastSuccessAt": observed_at,
            "lastDataChangeAt": last_data_change,
            "lastAttemptStatus": "success",
            "consecutiveFailures": 0,
            "errorCode": None,
            "errorMessage": None,
            "window": window,
            "sourceRecords": len(attendance_index),
            "mergedRecords": len(merged_records),
            "changedRecords": changed_records,
            "requestsMade": source.request_count,
            "sessionRotatedInMemory": source.session_rotated,
            "credentialVersion": credential_version,
        }
        model = build_read_model(
            proposed_ledger,
            proposed_booking,
            proposed_membership,
            state,
            now,
        )
        validate_read_model(model)
        if not dry_run:
            atomic_write_json(paths.ledger, proposed_ledger, mode=0o600)
            atomic_write_json(paths.booking, proposed_booking, mode=0o600)
            atomic_write_json(paths.membership, proposed_membership, mode=0o600)
            atomic_write_json(paths.sync_state, state, mode=0o600)
            _write_read_model(paths, model)
        return SyncResult(
            exit_code=0,
            status="success",
            source_records=len(attendance_index),
            merged_records=len(merged_records),
            changed_records=changed_records,
            session_rotated=source.session_rotated,
        )
    except SyncFailure as failure:
        state = _make_failure_state(
            old_state,
            now,
            window,
            failure,
            source.request_count,
            source.session_rotated,
            credential_version,
            len(ledger.get("records", [])),
        )
        model = build_read_model(ledger, booking, membership, state, now)
        if not dry_run:
            atomic_write_json(paths.sync_state, state, mode=0o600)
            _write_read_model(paths, model)
        exit_codes = {
            "auth_required": 2,
            "network_error": 3,
            "http_error": 3,
        }
        return SyncResult(
            exit_code=exit_codes.get(failure.code, 4),
            status=failure.code,
            source_records=0,
            merged_records=len(ledger.get("records", [])),
            changed_records=0,
            session_rotated=source.session_rotated,
        )


def build_paths(state_dir: Path, output: Path) -> SyncPaths:
    return SyncPaths(
        state_dir=state_dir,
        ledger=state_dir / "attendance-ledger.json",
        sync_state=state_dir / "sync-state.json",
        booking=state_dir / "booking-snapshot.json",
        membership=state_dir / "membership-snapshot.json",
        output=output,
        wrapper=output.with_suffix(".js"),
    )


def parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(TIMEZONE)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise SyncFailure("configuration_error")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=TIMEZONE)
    return parsed.astimezone(TIMEZONE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safely sync read-only Wenda ballet attendance data."
    )
    parser.add_argument(
        "--credential-file",
        type=Path,
        help="Restricted JSON containing only PHPSESSID and user_agent.",
    )
    parser.add_argument(
        "--credential-version-file",
        type=Path,
        help="Restricted non-secret credential generation token.",
    )
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=DEFAULT_STATE_DIR,
        help="Private canonical-ledger directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Sanitized public read-model JSON.",
    )
    parser.add_argument("--mode", choices=("rolling", "full"), default="rolling")
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        help="Use local synthetic HTML fixtures instead of the network.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate only; make no network request without --fixture-dir and write nothing.",
    )
    parser.add_argument(
        "--now",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def _safe_stdout(result: SyncResult, dry_run: bool) -> None:
    print(
        json.dumps(
            {
                "event": "ballet_sync_result",
                "dryRun": dry_run,
                "status": result.status,
                "sourceRecords": result.source_records,
                "mergedRecords": result.merged_records,
                "changedRecords": result.changed_records,
                "sessionRotatedInMemory": result.session_rotated,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )


def main() -> int:
    args = parse_args()
    try:
        now = parse_now(args.now)
        paths = build_paths(args.state_dir, args.output)
        credential_version: str | None = None
        if args.fixture_dir:
            source: WendaSource | FixtureSource = FixtureSource(args.fixture_dir)
        elif args.dry_run:
            _safe_stdout(
                SyncResult(0, "configuration_valid", 0, 0, 0, False),
                dry_run=True,
            )
            return 0
        else:
            credential_path = args.credential_file
            if credential_path is None and os.environ.get("WENDA_CREDENTIAL_FILE"):
                credential_path = Path(os.environ["WENDA_CREDENTIAL_FILE"])
            version_path = args.credential_version_file
            if version_path is None:
                raise SyncFailure("configuration_error")
            credential_version = load_credential_version(version_path)
            if auth_retry_is_blocked(paths.sync_state, credential_version):
                _safe_stdout(
                    SyncResult(2, "auth_blocked", 0, 0, 0, False),
                    dry_run=False,
                )
                return 2
            if credential_path is None:
                raise SyncFailure("configuration_error")
            source = WendaSource(load_credentials(credential_path))
        result = synchronize(
            paths,
            source,
            args.mode,
            now,
            dry_run=args.dry_run,
            credential_version=(
                credential_version if not args.fixture_dir else None
            ),
        )
        _safe_stdout(result, dry_run=args.dry_run)
        return result.exit_code
    except SyncFailure as failure:
        _safe_stdout(
            SyncResult(
                4,
                failure.code,
                0,
                0,
                0,
                False,
            ),
            dry_run=bool(args.dry_run),
        )
        return 4
    except Exception:
        _safe_stdout(
            SyncResult(4, "write_error", 0, 0, 0, False),
            dry_run=bool(args.dry_run),
        )
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
