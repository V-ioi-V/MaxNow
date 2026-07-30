import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]

DATASETS = [
    ("dashboard", "dash/data/dashboard.json", "dash/data/dashboard.js", "MAXNOW_DASHBOARD_DATA"),
    ("ai-news", "dash/data/ai-news.json", "dash/data/ai-news.js", "MAXNOW_AI_NEWS_DATA"),
    ("last-30", "dash/data/last-30.json", "dash/data/last-30.js", "MAXNOW_LAST30_DATA"),
    ("wiki-todos", "dash/data/wiki-todos.json", "dash/data/wiki-todos.js", "MAXNOW_WIKI_TODO_DATA"),
    ("openclaw-usage", "dash/data/openclaw-usage.json", "dash/data/openclaw-usage.js", "MAXNOW_OPENCLAW_USAGE_DATA"),
    ("codex-usage", "dash/data/codex-usage.json", "dash/data/codex-usage.js", "MAXNOW_CODEX_USAGE_DATA"),
    ("codex-macos-usage", "dash/data/codex-macos-usage.json", "dash/data/codex-macos-usage.js", "MAXNOW_CODEX_MACOS_USAGE_DATA"),
    ("codex-server-usage", "dash/data/codex-server-usage.json", "dash/data/codex-server-usage.js", "MAXNOW_CODEX_SERVER_USAGE_DATA"),
    ("token-usage", "dash/data/token-usage.json", "dash/data/token-usage.js", "MAXNOW_TOKEN_USAGE_DATA"),
    ("market-indices", "dash/data/market-indices.json", "dash/data/market-indices.js", "MAXNOW_MARKET_INDICES_DATA"),
    ("project-meta", "dash/data/project-meta.json", "dash/data/project-meta.js", "MAXNOW_PROJECT_META_DATA"),
    ("project-status", "dash/data/project-status.json", "dash/data/project-status.js", "MAXNOW_PROJECT_STATUS_DATA"),
    ("ricky", "dash/data/ricky.json", "dash/data/ricky.js", "MAXNOW_RICKY_DATA"),
    ("life-foods", "dash/data/life-foods.json", "dash/data/life-foods.js", "MAXNOW_LIFE_FOODS_DATA"),
    ("ballet", "dash/data/ballet.json", "dash/data/ballet.js", "MAXNOW_BALLET_DATA"),
    ("ballet-session", "dash/data/ballet-session.json", "dash/data/ballet-session.js", "MAXNOW_BALLET_SESSION_DATA"),
    ("ballet-booking-fast", "dash/data/ballet-booking-fast.json", "dash/data/ballet-booking-fast.js", "MAXNOW_BALLET_BOOKING_FAST_DATA"),
]


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_wrapper(path, global_name):
    text = path.read_text(encoding="utf-8")
    pattern = r"window\." + re.escape(global_name) + r"\s*=\s*(\{.*\})\s*;\s*$"
    match = re.match(pattern, text, re.S)
    if not match:
        raise ValueError(f"{path} does not assign window.{global_name}")
    return json.loads(match.group(1))


def check_dataset(name, json_rel, js_rel, global_name):
    json_path = ROOT / json_rel
    js_path = ROOT / js_rel
    source = load_json(json_path)
    wrapper = load_wrapper(js_path, global_name)
    if source != wrapper:
        raise ValueError(f"{name}: {json_rel} and {js_rel} differ")
    return f"{name}: json and wrapper match"


def check_required_files():
    required = [
        "index.html",
        "dash/index.html",
        "dash/login.html",
        "dash/login.js",
        "dash/styles.css",
        "dash/app.js",
        "dash/data/dounai_checkin.json",
        "dash/data/ricky.json",
        "dash/data/ricky.js",
        "dash/data/life-foods.json",
        "dash/data/life-foods.js",
        "dash/data/ballet.json",
        "dash/data/ballet.js",
        "dash/data/ballet-session.json",
        "dash/data/ballet-session.js",
        "dash/data/ballet-booking-fast.json",
        "dash/data/ballet-booking-fast.js",
        "dash/data/market-indices.json",
        "dash/data/market-indices.js",
        "dash/data/project-status.json",
        "dash/data/project-status.js",
        "blog/index.html",
        "blog/overview.html",
        "blog/topics.html",
        "blog/topic-algorithm.html",
        "blog/topic-cs.html",
        "blog/topic-algorithm-gap.html",
        "blog/topic-engineering.html",
        "blog/post-preview.html",
        "blog/random-articles.js",
        "blog/topic-tags.js",
        "blog/styles.css",
        "blog/preview.html",
        "blog/preview.css",
        "AGENTS.md",
        "CONTEXT.md",
        "SPEC.md",
        "BALLET_GROWTH_SCORING.md",
        "IDEAS.md",
        "UPDATE_LOG.md",
        "VERSION",
        "scripts/sync_system_status.py",
        "scripts/sync_wiki_todos.py",
        "scripts/sync_openclaw_usage.py",
        "scripts/sync_codex_usage.py",
        "scripts/sync_token_usage.py",
        "scripts/sync_ai_last30.py",
        "scripts/sync_market_indices.py",
        "scripts/sync_project_meta.py",
        "scripts/sync_weather.py",
        "scripts/sync_ricky_travel.py",
        "scripts/sync_life_foods.py",
        "scripts/update_data.py",
        "scripts/report_codex_usage.ps1",
        "scripts/report_codex_usage_hidden.vbs",
        "scripts/install_local_codex_usage_task.ps1",
        "scripts/report_codex_usage.sh",
        "scripts/install_local_codex_usage_launchd.sh",
        "scripts/refresh_token_usage_on_server.sh",
        "scripts/probe_ballet_session.py",
        "scripts/test_probe_ballet_session.py",
        "scripts/sync_ballet.py",
        "scripts/test_sync_ballet.py",
        "scripts/query_ballet_live.py",
        "scripts/run_ballet_live_query.sh",
        "scripts/test_query_ballet_live.py",
        "scripts/book_ballet.py",
        "scripts/run_ballet_booking.sh",
        "scripts/test_book_ballet.py",
        "scripts/book_ballet_fast.py",
        "scripts/run_ballet_booking_fast.sh",
        "scripts/test_book_ballet_fast.py",
        "config/ballet-booking-fast.json",
        "scripts/sync_ballet_session_status.py",
        "scripts/test_sync_ballet_session_status.py",
        "scripts/maxnow_auth_service.py",
        "server/maxnow-auth.service",
        "server/maxnow-ballet-sync.service",
        "server/maxnow-ballet-sync.timer",
        "server/maxnow-ballet-full-sync.service",
        "server/maxnow-ballet-full-sync.timer",
        "server/maxnow-ballet-session-status.service",
        "server/maxnow-ballet-session-status.timer",
        "server/maxnow-ballet-session-status.sysusers",
        "server/maxnow-ballet-booking-fast.service",
        "server/maxnow-ballet-booking-fast.timer",
        "server/maxnow-auth-rate-limit.conf",
        "server/maxnow-auth-locations.conf",
        "server/maxnow-dashboard.conf",
        "openclaw/maxnow-dashboard/SKILL.md",
        "openclaw/last-30/SKILL.md",
        "openclaw/maxnow-ballet-live/SKILL.md",
        "openclaw/maxnow-ballet-live/agents/openai.yaml",
    ]
    missing = [item for item in required if not (ROOT / item).exists()]
    if missing:
        raise FileNotFoundError("missing required files: " + ", ".join(missing))
    return "required files exist"


def check_auth_surface():
    login_html = (ROOT / "dash/login.html").read_text(encoding="utf-8")
    dashboard_html = (ROOT / "dash/index.html").read_text(encoding="utf-8")
    if 'action="/auth/login"' not in login_html:
        raise ValueError("auth surface: login form action is missing")
    if 'name="username"' not in login_html or 'name="password"' not in login_html:
        raise ValueError("auth surface: username/password fields are missing")
    if 'action="/auth/logout"' not in dashboard_html:
        raise ValueError("auth surface: dashboard logout action is missing")
    nginx_locations = (ROOT / "server/maxnow-auth-locations.conf").read_text(encoding="utf-8")
    if "auth_request /_auth;" not in nginx_locations or "@login_redirect" not in nginx_locations:
        raise ValueError("auth surface: nginx session gate is incomplete")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/maxnow_auth_service.py"), "--self-test"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=15,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError("auth surface: service self-test failed: " + result.stdout.strip())
    return "auth surface: login, logout, and session checks are valid"


def check_ballet_session_probe():
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "scripts/test_probe_ballet_session.py"),
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=20,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            "ballet session probe: self-test failed: "
            + result.stdout.strip()
        )
    return (
        "ballet session probe: fixed read-only URL, fail-closed auth, "
        "secret-safe logs, rotation, and stop paths are valid"
    )


def check_ballet_sync():
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "scripts/test_sync_ballet.py"),
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            "ballet sync: fixture self-test failed: " + result.stdout.strip()
        )
    return (
        "ballet sync: read-only allowlist, private ledger, idempotent upsert, "
        "safe auth failure, aggregates, redaction, and dry-run are valid"
    )


def check_ballet_live_query():
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "scripts/test_query_ballet_live.py"),
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            "ballet live query: fixture self-test failed: "
            + result.stdout.strip()
        )
    return (
        "ballet live query: no-cache scopes, date bounds, redaction, "
        "and fail-closed behavior are valid"
    )


def check_ballet_booking():
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "scripts/test_book_ballet.py"),
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            "ballet booking: fixture self-test failed: "
            + result.stdout.strip()
        )
    return (
        "ballet booking: exact matching, unified preflight, explicit "
        "confirmation, sequential execution, verification, and redaction are valid"
    )


def check_ballet_booking_fast():
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "scripts/test_book_ballet_fast.py"),
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            "ballet fast booking: fixture self-test failed: "
            + result.stdout.strip()
        )

    data = load_json(ROOT / "dash/data/ballet-booking-fast.json")
    if (
        data.get("schemaVersion") != 1
        or data.get("timezone") != "Asia/Shanghai"
        or data.get("priorityOrder") != ["周六", "周日", "周五", "其他日期"]
        or [item.get("key") for item in data.get("targets", [])]
        != [
            "saturday-soft-open",
            "friday-ballet-l1",
            "tuesday-ballet-l1",
        ]
    ):
        raise ValueError("ballet fast booking: public plan or priority is invalid")
    serialized = json.dumps(data, ensure_ascii=False)
    forbidden = (
        "PHPSESSID",
        "courseId",
        "classTableId",
        "customerId",
        "cardId",
        "/var/lib/",
        "/run/credentials/",
        "gm.wendaosoft.com",
    )
    if any(marker in serialized for marker in forbidden):
        raise ValueError("ballet fast booking: public state exposes internal data")

    service = (
        ROOT / "server/maxnow-ballet-booking-fast.service"
    ).read_text(encoding="utf-8")
    timer = (
        ROOT / "server/maxnow-ballet-booking-fast.timer"
    ).read_text(encoding="utf-8")
    locations = (
        ROOT / "server/maxnow-auth-locations.conf"
    ).read_text(encoding="utf-8")
    dashboard_html = (ROOT / "dash/index.html").read_text(encoding="utf-8")
    dashboard_js = (ROOT / "dash/app.js").read_text(encoding="utf-8")
    dashboard_css = (ROOT / "dash/styles.css").read_text(encoding="utf-8")
    skill = (
        ROOT / "openclaw/maxnow-ballet-live/SKILL.md"
    ).read_text(encoding="utf-8")
    required = (
        "OnCalendar=Sun *-*-* 14:19:35 Asia/Shanghai",
        "Persistent=false",
        "AccuracySec=1s",
        "LoadCredentialEncrypted=wenda-session.json:",
        "scripts/book_ballet_fast.py execute",
        "ConditionPathExists=/etc/maxnow-ballet/enable-fast-booking",
        "location = /data/ballet-booking-fast.json",
        "alias /var/lib/maxnow-ballet-booking-fast-public/ballet-booking-fast.json;",
        'const BALLET_BOOKING_FAST_URL = "./data/ballet-booking-fast.json"',
        "function renderBalletBookingFast()",
        'id="ballet-booking-fast-next"',
        "cloud-ballet-fast-card",
        'id="ballet-booking-fast-targets"',
        "周六 > 周日 > 周五 > 其他日期",
    )
    combined = "\n".join(
        (timer, service, locations, dashboard_js, dashboard_html, dashboard_css, skill)
    )
    if any(marker not in combined for marker in required):
        raise ValueError("ballet fast booking: service, UI, or Skill contract is incomplete")
    return (
        "ballet fast booking: Sunday precision timer, sequential fast path, "
        "priority, redaction, status UI, and fail-closed tests are valid"
    )


def check_ballet_read_model():
    data = load_json(ROOT / "dash/data/ballet.json")
    if data.get("schemaVersion") != 1 or data.get("timezone") != "Asia/Shanghai":
        raise ValueError("ballet: schemaVersion/timezone is invalid")
    sync = data.get("sync") or {}
    if sync.get("cacheState") not in {"fresh", "stale", "unavailable"}:
        raise ValueError("ballet: sync.cacheState is invalid")
    if sync.get("lastAttemptStatus") not in {
        "never",
        "success",
        "auth_required",
        "network_error",
        "http_error",
        "source_changed",
        "parse_error",
        "duplicate_key",
        "configuration_error",
        "write_error",
    }:
        raise ValueError("ballet: sync.lastAttemptStatus is invalid")
    records = data.get("records")
    if not isinstance(records, list):
        raise ValueError("ballet: records must be an array")
    summary = data.get("summary") or {}
    if summary.get("classes") != len(records):
        raise ValueError("ballet: summary.classes does not match records")
    expected_minutes = sum(
        item["durationMinutes"]
        for item in records
        if item.get("durationMinutes") is not None
    )
    if summary.get("minutes") != expected_minutes:
        raise ValueError("ballet: summary.minutes does not match records")
    text = json.dumps(data, ensure_ascii=False)
    forbidden = (
        "PHPSESSID=",
        '"id":',
        '"source"',
        '"attendanceRecordId"',
        '"bookingRecordId"',
        '"courseInstanceId"',
        '"stableKey"',
    )
    if any(marker in text for marker in forbidden):
        raise ValueError("ballet: public read model contains a private identifier")
    aggregates = data.get("aggregates") or {}
    if not all(isinstance(aggregates.get(key), list) for key in ("daily", "monthly", "yearly")):
        raise ValueError("ballet: daily/monthly/yearly aggregates are required")
    upcoming = (data.get("upcoming") or {}).get("records")
    if not isinstance(upcoming, list):
        raise ValueError("ballet: upcoming.records must be an array")
    for record in upcoming:
        if not {
            "waitlistPosition",
            "cancelRuleText",
            "cancelHoursBefore",
            "cancelDeadlineAt",
        }.issubset(record):
            raise ValueError("ballet: booking decision fields are incomplete")
    week = data.get("week")
    if not isinstance(week, dict) or not {
        "completedClasses",
        "bookedClasses",
        "waitlistClasses",
        "expectedClassesMin",
        "expectedClassesMax",
    }.issubset(week):
        raise ValueError("ballet: weekly training summary is incomplete")
    membership = data.get("membership")
    if not isinstance(membership, dict) or not isinstance(membership.get("cards"), list):
        raise ValueError("ballet: membership cards are missing")
    for card in membership["cards"]:
        if not {
            "name",
            "validFrom",
            "validThrough",
            "remainingClasses",
            "totalClasses",
            "usedClasses",
            "pace",
        }.issubset(card):
            raise ValueError("ballet: membership card fields are incomplete")
        pace = card["pace"]
        if not isinstance(pace, dict) or not {
            "validityDays",
            "openDayNumber",
            "remainingDays",
            "requiredClassesPerWeek",
            "recommendedWholeClassesPerWeek",
            "plannedFinishDate",
            "oneClassPerWeekProjectedRemaining",
            "sampleSufficient",
            "observedClassesPerWeek",
        }.issubset(pace):
            raise ValueError("ballet: membership forecast fields are incomplete")
        if "historyWindowDays" in pace or "currentClassesPerWeek" in pace:
            raise ValueError("ballet: retired fixed-window forecast remains")
        if not pace["sampleSufficient"] and pace["observedClassesPerWeek"] is not None:
            raise ValueError("ballet: short-sample observed pace must stay hidden")
    timetable = data.get("timetable")
    if not isinstance(timetable, dict) or timetable.get("displayMode") not in {
        "current_week",
        "sunday_plus_next_week",
    }:
        raise ValueError("ballet: timetable display mode is invalid")
    timetable_days = timetable.get("days")
    if not isinstance(timetable_days, list) or len(timetable_days) > 8:
        raise ValueError("ballet: timetable days are invalid")
    if timetable_days:
        expected_days = 8 if timetable["displayMode"] == "sunday_plus_next_week" else 7
        if len(timetable_days) != expected_days:
            raise ValueError("ballet: timetable display window is invalid")
        if (
            timetable.get("weekStart") != timetable_days[0].get("date")
            or timetable.get("weekEnd") != timetable_days[-1].get("date")
        ):
            raise ValueError("ballet: timetable boundary is invalid")
    for day in timetable_days:
        if not isinstance(day, dict) or not isinstance(day.get("records"), list):
            raise ValueError("ballet: timetable day is invalid")
        for record in day["records"]:
            required = {
                "date",
                "courseName",
                "courseType",
                "level",
                "startTime",
                "endTime",
                "durationMinutes",
                "teacher",
                "venue",
                "bookedCount",
                "capacity",
                "availability",
            }
            if not isinstance(record, dict) or not required.issubset(record):
                raise ValueError("ballet: timetable course fields are incomplete")
            if record["date"] != day.get("date") or record["availability"] not in {
                "available",
                "booked",
                "waitlist",
                "queue_available",
                "full",
                "cancelled",
                "past",
            }:
                raise ValueError("ballet: timetable course state is invalid")
            waitlist_count = record.get("waitlistCount")
            if (
                waitlist_count is not None
                and (
                    isinstance(waitlist_count, bool)
                    or not isinstance(waitlist_count, int)
                    or waitlist_count < 0
                )
            ):
                raise ValueError("ballet: timetable waitlist count is invalid")
    dashboard_js = (ROOT / "dash/app.js").read_text(encoding="utf-8")
    dashboard_html = (ROOT / "dash/index.html").read_text(encoding="utf-8")
    dashboard_css = (ROOT / "dash/styles.css").read_text(encoding="utf-8")
    if (
        "function balletClassBoundary" not in dashboard_js
        or "boundary >= Date.now()" not in dashboard_js
    ):
        raise ValueError("ballet: expired bookings are not filtered from the next class")
    if (
        'date.className = "ballet-upcoming-date"' not in dashboard_js
        or 'weekday: "long"' not in dashboard_js
        or 'const venue = String(record.venue || "").trim();' not in dashboard_js
        or "span.dataset.bookingStatus = item.status" not in dashboard_js
        or '[data-booking-status="waitlist"]' not in dashboard_css
    ):
        raise ValueError("ballet: booking weekday or status color contract is incomplete")
    if (
        "function formatBalletCancellation(" not in dashboard_js
        or "function renderBalletMembership()" not in dashboard_js
        or "function renderBalletWeek()" not in dashboard_js
        or "pace.sampleSufficient" not in dashboard_js
        or "近 28 天节奏" in dashboard_js
        or 'id="ballet-membership-list"' not in dashboard_html
        or 'id="ballet-week-completed"' not in dashboard_html
        or 'id="ballet-week-favorite-teacher"' not in dashboard_html
        or 'id="ballet-week-completion-ring"' not in dashboard_html
        or 'id="ballet-week-training-time"' not in dashboard_html
        or "function getBalletWeekFavoriteTeacher(week = {}, records = getBalletGrowthRecords())" not in dashboard_js
        or "function getBalletWeekCompletionState(week = {})" not in dashboard_js
        or "date >= start && date <= end" not in dashboard_js
        or "right.classes - left.classes" not in dashboard_js
        or "right.minutes - left.minutes" not in dashboard_js
        or "String(right.latestDate).localeCompare(String(left.latestDate))" not in dashboard_js
        or "completedClasses / confirmedClasses" not in dashboard_js
        or ".ballet-week-completion-ring {" not in dashboard_css
        or ".ballet-membership-card {" not in dashboard_css
        or ".ballet-week-grid {" not in dashboard_css
    ):
        raise ValueError("ballet: membership or weekly frontend contract is incomplete")
    timer = (ROOT / "server/maxnow-ballet-sync.timer").read_text(encoding="utf-8")
    if (
        "OnCalendar=*-*-* 00:00:00 Asia/Shanghai" not in timer
        or "OnCalendar=Sun *-*-* 14:30:00 Asia/Shanghai" not in timer
        or "Sunday 14:30" not in dashboard_html
        or "周日 14:30 检查下周课表" not in dashboard_js
        or "function renderBalletTimetable()" not in dashboard_js
        or 'id="ballet-timetable-grid"' not in dashboard_html
        or 'id="ballet-timetable-mobile"' not in dashboard_html
        or 'class="ballet-timetable-sticky-mask"' in dashboard_html
        or "function buildBalletTimetableRows(days = [])" not in dashboard_js
        or "function balletTimetableInterval(record = {})" not in dashboard_js
        or "function layoutBalletTimetableRecords(records = [])" not in dashboard_js
        or "const BALLET_TIMETABLE_ROOMS" not in dashboard_js
        or "function balletTimetableRoomKey(record = {})" not in dashboard_js
        or 'header.className = "ballet-timetable-room"' not in dashboard_js
        or 'roomGroup.className = "ballet-timetable-mobile-room"' not in dashboard_js
        or 'course.dataset.room = room.key' not in dashboard_js
        or "minuteGridLines.get(interval.start)" not in dashboard_js
        or 'grid.style.setProperty("--ballet-day-count"' not in dashboard_js
        or 'grid.style.setProperty("--ballet-time-rows"' not in dashboard_js
        or 'corner.textContent = "时间"' not in dashboard_js
        or 'marker.className = "ballet-timetable-now-line"' not in dashboard_js
        or 'course.dataset.overlap = laneCount > 1 ? "true" : "false"' not in dashboard_js
        or 'timeLabel.className = "ballet-timetable-time-label"' not in dashboard_js
        or 'endTime.className = "ballet-timetable-time ballet-timetable-end-time"' not in dashboard_js
        or "endTimeLabel.textContent = formatBalletTimetableHour(finalHour);" not in dashboard_js
        or 'article.title = [' not in dashboard_js
        or 'aria-label="横轴为日期和教室、纵轴为时间的本周课程表"' not in dashboard_html
        or 'class="ballet-timetable-legend"' not in dashboard_html
        or '.ballet-timetable-day[data-day-state="today"]' not in dashboard_css
        or ".ballet-timetable-grid > .ballet-timetable-course" not in dashboard_css
        or '.ballet-timetable-grid > .ballet-timetable-course[data-overlap="true"]' not in dashboard_css
        or '.ballet-timetable-cell[data-row-type="gap"]' not in dashboard_css
        or '.ballet-timetable-time[data-row-type="gap"]' not in dashboard_css
        or ".ballet-timetable-time-label {" not in dashboard_css
        or ".ballet-timetable-end-time {" not in dashboard_css
        or "grid-auto-rows: 14px;" not in dashboard_css
        or "border: 1px solid var(--card-border);" not in dashboard_css
        or "border-left: 3px solid var(--card-color);" in dashboard_css
        or "repeat(var(--ballet-day-count), minmax(0, 1fr) minmax(0, 1fr))" not in dashboard_css
        or ".ballet-timetable-room {" not in dashboard_css
        or "--ballet-day-divider: #dfccd4;" not in dashboard_css
        or "--ballet-room-divider: #f4eef1;" not in dashboard_css
        or '.ballet-timetable-room[data-room="large"] {' not in dashboard_css
        or '.ballet-timetable-cell[data-room="large"] {' not in dashboard_css
        or ".ballet-timetable-mobile-room {" not in dashboard_css
        or "var(--ballet-time-rows, repeat(60, var(--ballet-minute-height)))" not in dashboard_css
        or "@media (min-width: 861px) and (max-width: 1200px)" not in dashboard_css
        or "--ballet-minute-height: clamp(1.28px, calc(2.14px - 0.04vw), 1.48px);" not in dashboard_css
        or "--ballet-minute-height: clamp(1.65px, calc(3.26px - 0.1vw), 2.02px);" not in dashboard_css
        or '? "30px"' not in dashboard_js
        or ': "repeat(60, var(--ballet-minute-height))"' not in dashboard_js
        or "width: 66.6667%;" in dashboard_css
        or '.ballet-timetable-course[data-availability="booked"]' not in dashboard_css
        or '.ballet-timetable-course[data-availability="attended"]' not in dashboard_css
        or '.ballet-timetable-course[data-availability="waitlist"]' not in dashboard_css
        or '.ballet-timetable-state[data-availability="available"]' not in dashboard_css
        or '.ballet-timetable-state[data-availability="queue_available"]' not in dashboard_css
        or '.ballet-timetable-state[data-availability="full"]' not in dashboard_css
        or '.ballet-timetable-state[data-availability="cancelled"]' not in dashboard_css
        or "function isBalletTimetableAttended(record = {})" not in dashboard_js
        or "function getBalletTimetableCounts(record = {})" not in dashboard_js
        or "function getBalletTimetableWaitlistPosition(record = {})" not in dashboard_js
        or "getBalletTimetableUpcomingRecords" in dashboard_js
        or "waitlistPosition ? `排队中 ${waitlistPosition}`" not in dashboard_js
        or "rawWaitlistCount !== null" not in dashboard_js
        or 'article.dataset.compact = Number(record.durationMinutes) <= 60 ? "true" : "false";' not in dashboard_js
        or 'capacity.className = "ballet-timetable-capacity"' not in dashboard_js
        or 'waitlist.className = "ballet-timetable-waitlist"' not in dashboard_js
        or "article.append(detail, foot);" not in dashboard_js
        or ".ballet-timetable-capacity {" not in dashboard_css
        or ".ballet-timetable-waitlist {" not in dashboard_css
        or '.ballet-timetable-course[data-compact="true"] .ballet-timetable-meta-detail' in dashboard_css
        or "margin-top: auto;" not in dashboard_css
        or 'attended: "已上完"' not in dashboard_js
        or '.ballet-timetable-grid > .ballet-timetable-course[data-day-state="past"],' not in dashboard_css
        or '.ballet-timetable-course[data-day-state="past"]:not([data-availability="attended"])' in dashboard_css
        or "max-height: clamp(320px, 58vh, 500px);" in dashboard_css
        or "max-height: min(68vh, 560px);" in dashboard_css
        or ".ballet-timetable-sticky-mask" in dashboard_css
        or "overflow: visible;" not in dashboard_css
    ):
        raise ValueError("ballet: timetable frontend or refresh contract is incomplete")
    return "ballet: read model, timetable, decisions, totals, aggregates, and redaction are valid"


def check_ballet_session_status():
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "scripts/test_sync_ballet_session_status.py"),
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=20,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            "ballet session status: self-test failed: " + result.stdout.strip()
        )

    data = load_json(ROOT / "dash/data/ballet-session.json")
    expected_keys = {
        "schemaVersion",
        "timezone",
        "updatedAt",
        "status",
        "experimentStartedAt",
        "phaseStartedAt",
        "lastProbeAt",
        "lastAuthenticatedAt",
        "nextProbeAt",
        "scheduledEndAt",
        "refreshIntervalMinutes",
        "verifiedAliveSeconds",
        "phaseSamples",
        "totalSamples",
        "sessionChangedObserved",
        "setCookieObserved",
        "lastResult",
        "lastError",
    }
    if set(data) != expected_keys:
        raise ValueError("ballet session status: public field allowlist drifted")
    if data.get("schemaVersion") != 1 or data.get("timezone") != "Asia/Shanghai":
        raise ValueError("ballet session status: schemaVersion/timezone is invalid")
    if data.get("status") not in {
        "running",
        "complete",
        "auth_required",
        "delayed",
        "interrupted",
        "unknown",
    }:
        raise ValueError("ballet session status: status is invalid")
    if data.get("refreshIntervalMinutes") != 20:
        raise ValueError("ballet session status: current probe interval must be 20 minutes")
    if not all(
        isinstance(data.get(key), int)
        and not isinstance(data.get(key), bool)
        and data.get(key) >= 0
        for key in ("verifiedAliveSeconds", "phaseSamples", "totalSamples")
    ):
        raise ValueError("ballet session status: duration/sample counters are invalid")
    if data["totalSamples"] < data["phaseSamples"]:
        raise ValueError("ballet session status: phaseSamples exceeds totalSamples")

    def parse_timestamp(key):
        value = data.get(key)
        if value is None:
            return None
        try:
            parsed = datetime.fromisoformat(value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"ballet session status: {key} is invalid") from error
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError(f"ballet session status: {key} lacks timezone")
        return parsed

    started = parse_timestamp("experimentStartedAt")
    authenticated = parse_timestamp("lastAuthenticatedAt")
    last_probe = parse_timestamp("lastProbeAt")
    next_probe = parse_timestamp("nextProbeAt")
    scheduled_end = parse_timestamp("scheduledEndAt")
    parse_timestamp("updatedAt")
    parse_timestamp("phaseStartedAt")
    if not started:
        raise ValueError("ballet session status: experiment start is invalid")
    if scheduled_end is not None and scheduled_end <= started:
        raise ValueError("ballet session status: experiment time range is invalid")
    if authenticated:
        expected_seconds = max(0, int((authenticated - started).total_seconds()))
        if data["verifiedAliveSeconds"] != expected_seconds:
            raise ValueError("ballet session status: verified duration exceeds or trails evidence")
    elif data["verifiedAliveSeconds"] != 0:
        raise ValueError("ballet session status: duration exists without authenticated evidence")
    if data["status"] == "running":
        if not last_probe or not next_probe or next_probe <= last_probe:
            raise ValueError("ballet session status: running probe lacks its next schedule")
    if data["status"] in {"complete", "auth_required", "interrupted"} and next_probe is not None:
        raise ValueError("ballet session status: stopped state must not advertise another probe")

    last_result = data.get("lastResult")
    if last_result is not None and set(last_result) != {
        "httpStatus",
        "loginState",
        "attempts",
        "networkError",
    }:
        raise ValueError("ballet session status: lastResult exposes unsupported fields")
    if last_result is not None:
        http_status = last_result.get("httpStatus")
        attempts = last_result.get("attempts")
        if not (
            http_status is None
            or (
                isinstance(http_status, int)
                and not isinstance(http_status, bool)
                and 100 <= http_status <= 599
            )
        ):
            raise ValueError("ballet session status: lastResult httpStatus is invalid")
        if last_result.get("loginState") not in {
            "authenticated",
            "expired",
            "network_error",
            "redirect",
            "unknown",
        }:
            raise ValueError("ballet session status: lastResult loginState is invalid")
        if not (
            attempts is None
            or (
                isinstance(attempts, int)
                and not isinstance(attempts, bool)
                and 1 <= attempts <= 6
            )
        ):
            raise ValueError("ballet session status: lastResult attempts is invalid")
        if not isinstance(last_result.get("networkError"), bool):
            raise ValueError("ballet session status: lastResult networkError is invalid")
    last_error = data.get("lastError")
    if last_error is not None and (
        not isinstance(last_error, dict) or set(last_error) != {"code", "message"}
    ):
        raise ValueError("ballet session status: lastError is not controlled")
    controlled_errors = {
        "identity_expired": "PHPSESSID 已失效，请在电脑微信重新登录并刷新服务器凭据。",
        "probe_delayed": "只读检查已超过预期时间，当前登录状态待确认。",
        "probe_interrupted": "自动检查服务已停止，当前登录状态待确认。",
        "source_config_mismatch": "实验配置与日志中的检查间隔不一致。",
        "source_log_invalid": "实验状态日志暂时无法完整解析。",
        "invalid_completion": "实验完成标记尚未通过时间与样本完整性校验。",
        "probe_inconclusive": "连续检查无法确认登录状态，实验已安全停止。",
        "network_error": "最近一次只读检查遇到网络异常。",
        "unknown_response": "最近一次响应无法安全判断登录状态。",
        "http_error": "最近一次只读检查返回异常 HTTP 状态。",
        "status_unknown": "暂时无法确认 PHPSESSID 的当前状态。",
    }
    if last_error is not None and controlled_errors.get(
        last_error.get("code")
    ) != last_error.get("message"):
        raise ValueError("ballet session status: lastError value is outside the allowlist")

    serialized = json.dumps(data, ensure_ascii=False)
    forbidden = (
        "PHPSESSID=",
        '"run_id"',
        '"session_fingerprints"',
        '"response_sha256"',
        '"response_bytes"',
        '"api_host"',
        '"api_path"',
        '"source"',
        ".service",
        "/var/lib/",
        "/run/credentials/",
        "gm.wendaosoft.com",
        "credentialVersion",
    )
    if any(marker in serialized for marker in forbidden):
        raise ValueError("ballet session status: public model exposes an internal or secret field")

    dashboard_html = (ROOT / "dash/index.html").read_text(encoding="utf-8")
    dashboard_js = (ROOT / "dash/app.js").read_text(encoding="utf-8")
    dashboard_css = (ROOT / "dash/styles.css").read_text(encoding="utf-8")
    if (
        'const BALLET_SESSION_URL = "./data/ballet-session.json"' not in dashboard_js
        or "const BALLET_SESSION_PUBLISH_STALE_MS = 15 * 60 * 1000" not in dashboard_js
        or "const BALLET_SESSION_NEXT_RUN_INTERVAL_MINUTES = 20" not in dashboard_js
        or "function renderBalletSessionExperiment(now = new Date())" not in dashboard_js
        or "function isBalletSessionPublisherStale(" not in dashboard_js
        or "renderBalletSessionExperiment(now);" not in dashboard_js
        or "getBalletVerifiedAliveSeconds" not in dashboard_js
        or 'id="ballet-session-duration"' not in dashboard_html
        or 'id="ballet-session-next-plan"' not in dashboard_html
        or ".ballet-session-metrics {" not in dashboard_css
    ):
        raise ValueError("ballet session status: frontend card or frozen evidence rendering is incomplete")
    if "lastError?.message" in dashboard_js or "error?.message" in dashboard_js:
        raise ValueError("ballet session status: frontend renders an uncontrolled error message")

    service = (ROOT / "server/maxnow-ballet-session-status.service").read_text(encoding="utf-8")
    timer = (ROOT / "server/maxnow-ballet-session-status.timer").read_text(encoding="utf-8")
    sysusers = (ROOT / "server/maxnow-ballet-session-status.sysusers").read_text(encoding="utf-8")
    auth_locations = (ROOT / "server/maxnow-auth-locations.conf").read_text(encoding="utf-8")
    if (
        "RestrictAddressFamilies=AF_UNIX" not in service
        or "IPAddressDeny=any" not in service
        or "User=maxnow-ballet-status" not in service
        or "Group=maxnow-ballet-status" not in service
        or "StateDirectory=maxnow-ballet-session-status" not in service
        or "ReadWritePaths=/var/lib/maxnow-ballet-session-status" not in service
        or "ReadOnlyPaths=/var/lib/maxnow-ballet-session-source" not in service
        or "InaccessiblePaths=-/run/credentials -/etc/credstore.encrypted" not in service
        or "ExecStartPre=/usr/bin/test ! -r /run/credentials" not in service
        or (
            "ExecStartPre=/usr/bin/test ! -r "
            "/etc/credstore.encrypted/maxnow-ballet-wenda.cred"
        )
        not in service
        or "CapabilityBoundingSet=\n" not in service
        or (
            "ExecStart=/usr/bin/python3 -B "
            "/usr/local/lib/maxnow-ballet-session-status/"
            "sync_ballet_session_status.py"
        )
        not in service
        or "WorkingDirectory=/var/www/maxnow-dashboard" in service
        or "maxnow-ballet-status" not in sysusers
        or "location = /data/ballet-session.json" not in auth_locations
        or "auth_request /_auth;" not in auth_locations
        or (
            "alias /var/lib/maxnow-ballet-session-status/public/"
            "ballet-session.json;"
        )
        not in auth_locations
        or "OnUnitActiveSec=5min" not in timer
    ):
        raise ValueError("ballet session status: local-only publisher hardening or schedule is incomplete")
    return (
        "ballet session status: 20-minute indefinite evidence, redaction, frozen duration, "
        "local-only publisher, and frontend card are valid"
    )


def check_local_server(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if response.status != 200:
                raise RuntimeError(f"{url} returned HTTP {response.status}")
        return f"local server ok: {url}"
    except urllib.error.URLError as error:
        return f"local server skipped: {url} is not reachable ({error.reason})"


def check_dounai_checkin():
    data = load_json(ROOT / "dash/data/dounai_checkin.json")
    account = data.get("account")

    def check_remaining_precision(item, label):
        precision = item.get("remaining_flow_precision")
        if precision is None:
            return
        if precision not in {"byte", "rounded-label"}:
            raise ValueError(f"dounai-checkin: {label}.remaining_flow_precision is invalid")
        expected_mb = float(item["remaining_flow_mb"])
        if precision == "byte":
            remaining_bytes = item.get("remaining_flow_bytes")
            if isinstance(remaining_bytes, bool) or not isinstance(remaining_bytes, int) or remaining_bytes < 0:
                raise ValueError(f"dounai-checkin: {label}.remaining_flow_bytes must be a non-negative integer")
            expected_mb = round(remaining_bytes / 1024 / 1024, 2)
            if abs(float(item["remaining_flow_mb"]) - expected_mb) > 0.001:
                raise ValueError(f"dounai-checkin: {label}.remaining_flow_mb does not match byte precision")
        remaining_days_exact = item.get("remaining_days_exact")
        if remaining_days_exact is not None:
            remaining_days_exact = float(remaining_days_exact)
            if not math.isfinite(remaining_days_exact) or remaining_days_exact <= 0:
                raise ValueError(f"dounai-checkin: {label}.remaining_days_exact must be finite and positive")
            expected_daily = round(expected_mb / remaining_days_exact, 2)
            if abs(float(item["daily_available_mb"]) - expected_daily) > 0.001:
                raise ValueError(f"dounai-checkin: {label}.daily_available_mb does not match exact remaining duration")
            return
        days_remaining = int(item.get("days_remaining", 0))
        if days_remaining > 0:
            expected_daily = round(expected_mb / days_remaining, 2)
            if abs(float(item["daily_available_mb"]) - expected_daily) > 0.001:
                raise ValueError(f"dounai-checkin: {label}.legacy daily_available_mb does not match whole remaining days")

    if account and "remaining_flow_mb" in account:
        remaining = float(account["remaining_flow_mb"])
        if remaining < 0:
            raise ValueError("dounai-checkin: account.remaining_flow_mb cannot be negative")
        check_remaining_precision(account, "account")

    expiry = account.get("effective_expires_at") or account.get("vip_expires_at") or account.get("account_expires_at") if account else None
    if expiry:
        datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")

    if account and "daily_available_mb" in account:
        daily = float(account["daily_available_mb"])
        if daily < 0:
            raise ValueError("dounai-checkin: account.daily_available_mb cannot be negative")

    history = data.get("account_history", [])
    if not isinstance(history, list):
        raise ValueError("dounai-checkin: account_history must be a list")
    for item in history:
        datetime.strptime(item["date"], "%Y-%m-%d")
        daily = float(item["daily_available_mb"])
        if daily < 0:
            raise ValueError("dounai-checkin: account_history.daily_available_mb cannot be negative")
        check_remaining_precision(item, "account_history item")

    traffic_usage = data.get("traffic_usage")
    traffic_excludes_today = bool(traffic_usage.get("excluded_today")) if traffic_usage else False
    today_key = datetime.now().astimezone().strftime("%Y-%m-%d")
    if traffic_usage:
        daily_items = traffic_usage.get("daily", [])
        if not isinstance(daily_items, list):
            raise ValueError("dounai-checkin: traffic_usage.daily must be a list")
        for item in daily_items:
            datetime.strptime(item["date"], "%Y-%m-%d")
            if traffic_excludes_today and item["date"] == today_key:
                raise ValueError("dounai-checkin: traffic_usage.daily must exclude today when excluded_today is true")
            used = float(item["used_mb"])
            if used < 0:
                raise ValueError("dounai-checkin: traffic_usage.daily.used_mb cannot be negative")
        recent = float(traffic_usage.get("recent_traffic_mb", 0))
        if recent < 0:
            raise ValueError("dounai-checkin: traffic_usage.recent_traffic_mb cannot be negative")
        top_nodes = traffic_usage.get("top_nodes_12h", [])
        if top_nodes and not isinstance(top_nodes, list):
            raise ValueError("dounai-checkin: traffic_usage.top_nodes_12h must be a list")
        for item in top_nodes:
            traffic = float(item.get("traffic_mb", 0))
            if traffic < 0:
                raise ValueError("dounai-checkin: traffic_usage.top_nodes_12h.traffic_mb cannot be negative")

    traffic_history = data.get("traffic_usage_history", [])
    if not isinstance(traffic_history, list):
        raise ValueError("dounai-checkin: traffic_usage_history must be a list")
    for item in traffic_history:
        datetime.strptime(item["date"], "%Y-%m-%d")
        if traffic_excludes_today and item["date"] == today_key:
            raise ValueError("dounai-checkin: traffic_usage_history must exclude today when traffic_usage.excluded_today is true")
        used = float(item["used_mb"])
        if used < 0:
            raise ValueError("dounai-checkin: traffic_usage_history.used_mb cannot be negative")

    return "dounai-checkin: json, account snapshot, account history, and traffic usage are valid"


def check_openclaw_usage():
    data = load_json(ROOT / "dash/data/openclaw-usage.json")
    if data.get("pricingBasis") != "openrouter-equivalent":
        raise ValueError("openclaw-usage: pricingBasis must be openrouter-equivalent")
    if data.get("currency") != "USD":
        raise ValueError("openclaw-usage: currency must be USD")
    if not isinstance(data.get("days", []), list):
        raise ValueError("openclaw-usage: days must be a list")
    for day in data.get("days", []):
        datetime.strptime(day["date"], "%Y-%m-%d")
        for key in ["inputTokens", "outputTokens", "cacheReadTokens", "cacheBaseTokens", "totalTokens", "runs"]:
            if int(day.get(key, 0)) < 0:
                raise ValueError(f"openclaw-usage: {key} cannot be negative")
        if float(day.get("estimatedCostUsd", 0)) < 0:
            raise ValueError("openclaw-usage: estimatedCostUsd cannot be negative")
    return "openclaw-usage: ledger shape is valid"


def check_usage_ledger(name, rel_path, allowed_pricing_basis, require_unique_runs=False):
    data = load_json(ROOT / rel_path)
    if data.get("pricingBasis") not in allowed_pricing_basis:
        raise ValueError(f"{name}: pricingBasis is not supported")
    if data.get("currency") != "USD":
        raise ValueError(f"{name}: currency must be USD")
    if not isinstance(data.get("days", []), list):
        raise ValueError(f"{name}: days must be a list")
    if not isinstance(data.get("sources", []), list):
        raise ValueError(f"{name}: sources must be a list")
    for day in data.get("days", []):
        datetime.strptime(day["date"], "%Y-%m-%d")
        for key in ["inputTokens", "outputTokens", "cacheReadTokens", "cacheBaseTokens", "totalTokens", "runs", "activeSeconds", "completedTurns"]:
            if int(day.get(key, 0)) < 0:
                raise ValueError(f"{name}: {key} cannot be negative")
        if float(day.get("estimatedCostUsd", 0)) < 0:
            raise ValueError(f"{name}: estimatedCostUsd cannot be negative")
    if int(data.get("summary", {}).get("totalTokens", 0)) != sum(
        int(day.get("totalTokens", 0)) for day in data.get("days", [])
    ):
        raise ValueError(f"{name}: summary totalTokens must equal the sum of days")
    if require_unique_runs:
        run_ids = [run.get("runId") for run in data.get("recentRuns", [])]
        if any(not run_id for run_id in run_ids) or len(run_ids) != len(set(run_ids)):
            raise ValueError(f"{name}: recentRuns must have unique runId values")
    return f"{name}: ledger shape is valid"


def check_codex_usage():
    return check_usage_ledger("codex-usage", "dash/data/codex-usage.json", {"openai-api-equivalent"}, True)


def check_codex_macos_usage():
    return check_usage_ledger("codex-macos-usage", "dash/data/codex-macos-usage.json", {"openai-api-equivalent"}, True)


def check_codex_server_usage():
    return check_usage_ledger("codex-server-usage", "dash/data/codex-server-usage.json", {"openai-api-equivalent"}, True)


def check_token_usage():
    return check_usage_ledger("token-usage", "dash/data/token-usage.json", {"mixed", "openrouter-equivalent", "openai-api-equivalent"})


def check_project_meta():
    data = load_json(ROOT / "dash/data/project-meta.json")
    version = data.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+\.\d{2}", version):
        raise ValueError("project-meta: version must match x.x.x.xx")
    if data.get("versionLabel") != f"v{version}":
        raise ValueError("project-meta: versionLabel must be v + version")
    if not isinstance(data.get("recentUpdates", []), list):
        raise ValueError("project-meta: recentUpdates must be a list")
    return "project-meta: version and recent updates are valid"


def roadmap_titles_by_area():
    areas = {}
    current_area = ""
    for raw_line in (ROOT / "ROADMAP.md").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current_area = line[3:].strip()
        elif line.startswith("### "):
            areas.setdefault(current_area, set()).add(line[4:].strip())
    return areas


def check_project_status():
    path = ROOT / "dash/data/project-status.json"
    data = load_json(path)
    roadmap_text = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    expected_fingerprint = hashlib.sha256(roadmap_text.encode("utf-8")).hexdigest()
    if data.get("schemaVersion") != 1:
        raise ValueError("project-status: schemaVersion must be 1")
    if data.get("source") != "ROADMAP.md":
        raise ValueError("project-status: source must be ROADMAP.md")
    if data.get("sourceFingerprint") != expected_fingerprint:
        raise ValueError("project-status: ROADMAP.md changed; run python scripts/update_data.py project-status")
    for key in ["sourceUpdatedAt", "generatedAt"]:
        datetime.strptime(data[key], "%Y-%m-%d %H:%M")
    if int(data.get("staleAfterHours", 0)) <= 0:
        raise ValueError("project-status: staleAfterHours must be positive")
    dashboard = load_json(ROOT / "dash/data/dashboard.json")
    legacy_fields = [key for key in ["mainlines", "actions"] if key in dashboard]
    if legacy_fields:
        raise ValueError(f"project-status: generated fields must not remain in dashboard.json: {legacy_fields}")

    areas = roadmap_titles_by_area()
    active_titles = areas.get("Now", set()) | areas.get("Next", set())
    done_titles = areas.get("Done", set())
    overlap = active_titles & done_titles
    if overlap:
        raise ValueError(f"project-status: ROADMAP titles appear in active and Done: {sorted(overlap)}")

    mainlines = data.get("mainlines", [])
    actions = data.get("actions", [])
    if not isinstance(mainlines, list) or not isinstance(actions, list):
        raise ValueError("project-status: mainlines and actions must be lists")
    items = [*mainlines, *actions]
    item_titles = [item.get("title", "") for item in items]
    if len(item_titles) != len(set(item_titles)):
        raise ValueError("project-status: mainlines and actions must not contain duplicate titles")
    for item in items:
        title = item.get("title", "")
        if not title or title not in active_titles:
            raise ValueError(f"project-status: {title or '<missing title>'} is not in ROADMAP Now / Next")
        if title in done_titles:
            raise ValueError(f"project-status: {title} points to a ROADMAP Done item")
        if item.get("sourceArea") not in {"Now", "Next"}:
            raise ValueError(f"project-status: {title} sourceArea must be Now or Next")
    return "project-status: ROADMAP source, freshness metadata, and active items are valid"


def check_market_indices():
    data = load_json(ROOT / "dash/data/market-indices.json")
    if data.get("schemaVersion") != 1:
        raise ValueError("market-indices: schemaVersion must be 1")
    if int(data.get("refreshIntervalMinutes", 0)) != 10:
        raise ValueError("market-indices: refreshIntervalMinutes must be 10")
    indices = data.get("indices", [])
    if not isinstance(indices, list):
        raise ValueError("market-indices: indices must be a list")
    for item in indices:
        for key in ["key", "name", "symbol", "region"]:
            if not item.get(key):
                raise ValueError(f"market-indices: {key} is required")
        if item.get("stale") and item.get("price") is None:
            continue
        for key in ["price", "previousClose", "change", "changePercent"]:
            value = float(item[key])
            if key in {"price", "previousClose"} and value <= 0:
                raise ValueError(f"market-indices: {key} must be positive")
        trend = item.get("trend", [])
        if not isinstance(trend, list):
            raise ValueError("market-indices: trend must be a list")
        for point in trend:
            if "time" not in point:
                raise ValueError("market-indices: trend.time is required")
            if float(point["value"]) <= 0:
                raise ValueError("market-indices: trend.value must be positive")
    return "market-indices: quote shape is valid"


def check_dashboard_weather():
    data = load_json(ROOT / "dash/data/dashboard.json")
    weather = data.get("weather", {})
    if weather:
        if weather.get("location") != "北京市海淀区":
            raise ValueError("dashboard weather: location must be 北京市海淀区")
        if weather.get("icon") not in {"sun", "cloud", "rain", "storm", "snow", "fog"}:
            raise ValueError("dashboard weather: icon is not supported")
        for key in ["tempC", "highC", "lowC"]:
            value = float(weather[key])
            if value < -50 or value > 60:
                raise ValueError(f"dashboard weather: {key} is out of range")
        for key in ["precipitationMm", "rainMm", "showersMm"]:
            if key in weather and float(weather[key]) < 0:
                raise ValueError(f"dashboard weather: {key} cannot be negative")
    return "dashboard weather: shape is valid"


def check_special_dates():
    data = load_json(ROOT / "dash/data/dashboard.json")
    dashboard_html = (ROOT / "dash/index.html").read_text(encoding="utf-8")
    dashboard_css = (ROOT / "dash/styles.css").read_text(encoding="utf-8")
    dashboard_js = (ROOT / "dash/app.js").read_text(encoding="utf-8")
    special_dates = data.get("specialDates", [])
    if not isinstance(special_dates, list):
        raise ValueError("special dates: specialDates must be a list")
    for item in special_dates:
        if not item.get("title"):
            raise ValueError("special dates: title is required")
        day = int(item.get("day", 0))
        if item.get("repeat") == "monthly":
            if day < 1 or day > 31:
                raise ValueError("special dates: monthly day must be between 1 and 31")
        elif item.get("date"):
            datetime.strptime(str(item["date"]), "%Y-%m-%d")
        else:
            month = int(item.get("month", 0))
            if month < 1 or month > 12 or day < 1 or day > 31:
                raise ValueError("special dates: annual month/day is invalid")
    required_items = (
        ("77 生日", 7, 18),
        ("Max 生日", 8, 28),
        ("Codex 续费日", None, 25),
    )
    for title, month, day in required_items:
        if not any(
            item.get("title") == title
            and item.get("day") == day
            and (month is None or item.get("month") == month)
            for item in special_dates
        ):
            raise ValueError(f"special dates: missing {title}")
    if not any(
        item.get("title") == "Codex 续费日" and item.get("repeat") == "monthly"
        for item in special_dates
    ):
        raise ValueError("special dates: Codex renewal must repeat monthly")
    required_frontend = (
        'id="next-special-label"',
        ".summary-clock .next-special-label",
        'item.repeat === "monthly"',
        "function getNextSpecialDate(",
        "getHolidayLabels(candidate)",
        "occurrence > today",
        'setText("#next-special-label", formatNextSpecialDate(now))',
        "projectStatusData = projectStatus;\n    updateClock();",
    )
    combined = "\n".join((dashboard_html, dashboard_css, dashboard_js))
    if any(value not in combined for value in required_frontend):
        raise ValueError("special dates: upcoming-date UI or calculation is incomplete")
    return "special dates: holidays, birthdays, anniversaries, and monthly renewals are valid"


def check_ai_frontier_brief():
    data = load_json(ROOT / "dash/data/last-30.json")
    ai_news = load_json(ROOT / "dash/data/ai-news.json")
    dashboard_html = (ROOT / "dash/index.html").read_text(encoding="utf-8")
    dashboard_css = (ROOT / "dash/styles.css").read_text(encoding="utf-8")
    dashboard_js = (ROOT / "dash/app.js").read_text(encoding="utf-8")
    groups = [
        ("today", data.get("today", {}).get("items", []), 3),
        ("week", data.get("week", {}).get("items", []), 4),
        ("last30", data.get("last30", {}).get("mainlines", []), 5),
    ]
    if data.get("today", {}).get("title") != "最新发布":
        raise ValueError("AI frontier: today title must be 最新发布")
    if data.get("week", {}).get("title") != "本周前沿":
        raise ValueError("AI frontier: week title must be 本周前沿")
    if data.get("last30", {}).get("title") != "近 30 天关键进展":
        raise ValueError("AI frontier: last30 title must be 近 30 天关键进展")

    banned = ("关注它", "适合进入观察池", "关键词自动归类", "来源较稳", "自动观察")
    seen_urls = set()
    for group_name, items, limit in groups:
        group = data.get("last30" if group_name == "last30" else group_name, {})
        group_summary = str(group.get("summary", ""))
        if any(phrase in group_summary for phrase in banned):
            raise ValueError(f"AI frontier: internal classification copy leaked in {group_name} summary")
        if not isinstance(items, list) or len(items) > limit:
            raise ValueError(f"AI frontier: {group_name} must contain at most {limit} items")
        for item in items:
            title = str(item.get("title", ""))
            summary = str(item.get("summary", ""))
            visible = f"{title} {summary}"
            if not re.search(r"[\u4e00-\u9fff]", title) or not re.search(r"[\u4e00-\u9fff]", summary):
                raise ValueError(f"AI frontier: visible copy must be Chinese-first: {title or '<missing title>'}")
            if any(phrase in visible for phrase in banned) or item.get("status") == "active":
                raise ValueError(f"AI frontier: internal classification copy leaked: {title}")
            url = str(item.get("url", "")).strip()
            if url:
                if url in seen_urls:
                    raise ValueError(f"AI frontier: duplicate story across groups: {url}")
                seen_urls.add(url)

    for item in ai_news.get("items", []):
        if not re.search(r"[\u4e00-\u9fff]", str(item.get("title", ""))):
            raise ValueError("AI frontier: ai-news titles must be Chinese-first")

    for label in ("最近 3 天", "本周", "近 30 天"):
        if f"<span>{label}</span>" not in dashboard_html:
            raise ValueError(f"AI frontier: visible time-range label is missing: {label}")
    retired_ids = (
        "last30-today-title",
        "last30-week-title",
        "last30-mainline-title",
        "last30-today-summary",
        "last30-week-summary",
        "last30-mainline-summary",
    )
    if any(retired_id in dashboard_html or retired_id in dashboard_js for retired_id in retired_ids):
        raise ValueError("AI frontier: redundant column title or summary rendering remains")
    if ".last30-summary" in dashboard_css or ".last30-column-head strong" in dashboard_css:
        raise ValueError("AI frontier: retired column heading styles remain")

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/sync_ai_last30.py"), "--self-test"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=15,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError("AI frontier: collector self-test failed: " + result.stdout.strip())
    return "AI frontier: compact time-range headings, Chinese facts, ranking, deduplication, and collector checks are valid"


def check_today_progress_ring():
    dashboard_html = (ROOT / "dash/index.html").read_text(encoding="utf-8")
    dashboard_css = (ROOT / "dash/styles.css").read_text(encoding="utf-8")
    dashboard_js = (ROOT / "dash/app.js").read_text(encoding="utf-8")
    if 'class="summary-live-ring"' not in dashboard_html or 'id="today-pulse-percent"' not in dashboard_html:
        raise ValueError("Today progress ring: ring or inner percentage is missing")
    if '<time id="today-pulse-now">' not in dashboard_html:
        raise ValueError("Today progress ring: outside current time is missing")
    if 'class="summary-kicker"' not in dashboard_html:
        raise ValueError("Today progress ring: freshness must stay with the title kicker")
    if "conic-gradient(" not in dashboard_css or "--today-progress-angle: 0deg" not in dashboard_css:
        raise ValueError("Today progress ring: circular theme progress style is missing")
    if "grid-template-columns: 140px minmax(0, 1fr)" not in dashboard_css or "gap: 30px" not in dashboard_css:
        raise ValueError("Today progress ring: meter and signal columns are not separated")
    if "grid-template-columns: minmax(0, 1fr) 140px minmax(0, 1fr)" not in dashboard_css:
        raise ValueError("Today progress ring: desktop meter is not centered in equal side columns")
    if ".summary-live {\n    display: contents;" not in dashboard_css:
        raise ValueError("Today progress ring: desktop live group does not expose the centered grid columns")
    if "grid-template-rows: repeat(4, minmax(0, 1fr))" not in dashboard_css:
        raise ValueError("Today progress ring: signal rows are not evenly distributed")
    if ".summary-bar::before" in dashboard_css:
        raise ValueError("Today progress ring: retired card-top accent bar remains")
    if 'setProperty("--today-progress-angle", progressAngle)' not in dashboard_js:
        raise ValueError("Today progress ring: angle update is missing")
    if 'setText("#today-pulse-percent", progressPercent)' not in dashboard_js:
        raise ValueError("Today progress ring: inner percentage update is missing")
    retired_axis_copy = ("summary-live-start", "summary-live-end", "today-marker-ratio")
    if any(value in dashboard_html or value in dashboard_css or value in dashboard_js for value in retired_axis_copy):
        raise ValueError("Today progress ring: retired vertical axis remains")
    if (
        ".summary-live-item::before" not in dashboard_css
        or "position: static" not in dashboard_css
        or "grid-column: 1" not in dashboard_css
        or "grid-row: 1" not in dashboard_css
        or "align-self: center" not in dashboard_css
    ):
        raise ValueError("Today progress ring: signal node alignment rule is missing")
    return "Today progress ring: centered meter, equal side columns, first-line nodes, and responsive fallbacks are valid"


def check_secondary_view_style():
    dashboard_html = (ROOT / "dash/index.html").read_text(encoding="utf-8")
    login_html = (ROOT / "dash/login.html").read_text(encoding="utf-8")
    dashboard_css = (ROOT / "dash/styles.css").read_text(encoding="utf-8")
    dashboard_js = (ROOT / "dash/app.js").read_text(encoding="utf-8")
    for view_id in ("tokens-view", "dounai-view", "ballet-view", "cloud-view", "life-view", "ricky-view"):
        if f'class="view secondary-view" id="{view_id}"' not in dashboard_html:
            raise ValueError(f"secondary views: shared view class is missing on {view_id}")
    if 'class="view secondary-view" id="home-view"' in dashboard_html:
        raise ValueError("secondary views: Home must not inherit the secondary shell")
    if dashboard_html.count("secondary-page-head") != 1:
        raise ValueError("secondary views: only Dounai may keep the shared page head")
    required_css = (
        ".secondary-view {",
        ".secondary-page-head {",
        ".ballet-overview-grid {",
        ".ballet-course-plan-grid {",
        ".ballet-upcoming-item.is-nearest {",
        ".ballet-upcoming-nearest {",
        ".ballet-upcoming-note {",
        "#tokens-view {",
        "#dounai-view {",
        "#ballet-view {",
        "#cloud-view {",
        "#life-view {",
        "#ricky-view {",
    )
    if any(rule not in dashboard_css for rule in required_css):
        raise ValueError("secondary views: shared theme, accent, or card rules are incomplete")
    retired_top_bars = (
        ".secondary-page-head:not(.token-usage-head, .dounai-page-head)::before",
        ".secondary-view .token-head-card::before",
        ".secondary-view .dounai-title-tab::before",
        ".secondary-view .dounai-top-tabs::before",
        ".secondary-view .panel::before",
        ".secondary-view .token-summary article::before",
        ".secondary-view .ricky-stats article::before",
    )
    if any(rule in dashboard_css for rule in retired_top_bars):
        raise ValueError("secondary views: retired card-top accent bar remains")
    ballet_view_markup = dashboard_html.split('id="ballet-view"', 1)[1].split('id="cloud-view"', 1)[0]
    token_view_markup = dashboard_html.split('id="tokens-view"', 1)[1].split('id="ballet-view"', 1)[0]
    life_view_markup = dashboard_html.split('id="life-view"', 1)[1].split('id="tokens-view"', 1)[0]
    ricky_view_markup = dashboard_html.split('id="ricky-view"', 1)[1].split('id="life-view"', 1)[0]
    cloud_view_markup = dashboard_html.split('id="cloud-view"', 1)[1].split('id="dounai-view"', 1)[0]
    if "cloud-page-head" in cloud_view_markup or "Cloud Services" in cloud_view_markup:
        raise ValueError("secondary views: Cloud must not repeat the topbar page title")
    topbar_markup = dashboard_html.split('<header class="topbar"', 1)[1].split("</header>", 1)[0]
    if (
        'class="topbar-data-status topbar-ballet-status"' not in topbar_markup
        or 'id="ballet-updated"' not in topbar_markup
        or 'id="ballet-connection-status"' not in topbar_markup
        or 'id="ballet-updated"' in ballet_view_markup
        or 'body[data-view="ballet"] .topbar-ballet-status' not in dashboard_css
        or "function formatBalletUpdatedAtCompact()" not in dashboard_js
    ):
        raise ValueError("secondary views: ballet update status must stay in the global topbar")
    topbar_status_contracts = (
        ("token", "tokens", token_view_markup),
        ("life", "life", life_view_markup),
        ("ricky", "ricky", ricky_view_markup),
    )
    for status_key, view_key, view_markup in topbar_status_contracts:
        if (
            f'class="topbar-data-status topbar-{status_key}-status"' not in topbar_markup
            or f'id="{status_key}-updated"' not in topbar_markup
            or f'id="{status_key}-connection-status"' not in topbar_markup
            or f'id="{status_key}-updated"' in view_markup
            or f'body[data-view="{view_key}"] .topbar-{status_key}-status' not in dashboard_css
        ):
            raise ValueError(f"secondary views: {status_key} update status must stay in the global topbar")
    if (
        "function renderTopbarDataStatus(" not in dashboard_js
        or "token-main-tab" in dashboard_html
        or "token-usage-head" in dashboard_html
        or "ricky-page-head" in dashboard_html
        or "life-page-head" in dashboard_html
    ):
        raise ValueError("secondary views: repeated Token, Life, or Ricky title cards remain")
    layout_markers = (
        'class="ballet-overview-grid"',
        'class="panel ballet-week-panel"',
        'class="panel ballet-membership-card"',
        'class="panel ballet-course-plan-panel"',
        'class="panel ballet-training-panel"',
        'class="panel ballet-timetable-panel"',
    )
    layout_positions = [ballet_view_markup.find(marker) for marker in layout_markers]
    if any(position < 0 for position in layout_positions) or layout_positions != sorted(layout_positions):
        raise ValueError("secondary views: ballet information priority order is invalid")
    if any(retired in ballet_view_markup for retired in ("ballet-page-intro", "ballet-head-next", "ballet-page-head")):
        raise ValueError("secondary views: retired ballet title layout remains")
    if (
        "function createBalletUpcomingItem(record)" not in dashboard_js
        or "formatBalletCancellation(record)" not in dashboard_js
        or "const items = records.map(createBalletUpcomingItem);" not in dashboard_js
        or 'class="panel ballet-course-plan-panel"' not in ballet_view_markup
        or 'items[0].classList.add("is-nearest")' not in dashboard_js
        or 'nearest.textContent = "最近一节"' not in dashboard_js
        or 'cancellation.className = "ballet-upcoming-note"' not in dashboard_js
        or "is-featured" in dashboard_js
    ):
        raise ValueError("secondary views: nearest booking, course plan, or cancellation deadlines are incomplete")
    if any(retired in ballet_view_markup for retired in ("ballet-next-panel", 'id="ballet-next-class"', 'id="ballet-next-status"')):
        raise ValueError("secondary views: retired standalone next-class panel remains")
    if (
        "ballet-session-card" in ballet_view_markup
        or "ballet-booking-fast-status" in ballet_view_markup
        or '<details class="panel cloud-card ballet-session-card" open ' not in cloud_view_markup
        or 'class="panel cloud-card cloud-ballet-fast-card"' not in cloud_view_markup
        or '<summary class="ballet-session-summary">' not in cloud_view_markup
        or ".ballet-overview-grid {" not in dashboard_css
        or 'class="panel ballet-growth-panel"' not in ballet_view_markup
        or "@media (min-width: 1501px)" not in dashboard_css
        or "grid-template-columns: repeat(3, minmax(0, 1fr));" not in dashboard_css
        or ".ballet-growth-block:hover" not in dashboard_css
        or ".ballet-course-plan-grid {" not in dashboard_css
        or ".ballet-session-summary {" not in dashboard_css
        or ".ballet-session-card[open] .ballet-session-toggle {" not in dashboard_css
        or 'id="ballet-trend-placeholder"' not in ballet_view_markup
        or "const showTrend = sampleCount >= 5;" not in dashboard_js
        or "function renderBalletGrowth()" not in dashboard_js
    ):
        raise ValueError("secondary views: ballet learning layout or Cloud operations split is incomplete")
    if any(retired in dashboard_html for retired in ("ballet-page-head", "ballet-sync-status", "Ballet Progress")):
        raise ValueError("secondary views: retired ballet title tab remains")
    if (
        "styles.css?v=200" not in dashboard_html
        or "styles.css?v=127" not in login_html
        or "app.js?v=166" not in dashboard_html
    ):
        raise ValueError("secondary views: stylesheet cache version is stale")
    cloud_session_rule = dashboard_css.split("#cloud-view .ballet-session-card {", 1)[1].split("}", 1)[0]
    if "grid-column: auto;" not in cloud_session_rule:
        raise ValueError("secondary views: Cloud ballet operation cards must share one desktop row")
    polish_rules = (
        "--focus-ring:",
        "font-variant-numeric: tabular-nums;",
        ".side-nav-item:focus-visible {",
        ".life-count-control:focus-within {",
        ".line-chart > .empty-state {",
        "@media (prefers-reduced-motion: reduce) {",
    )
    if any(rule not in dashboard_css for rule in polish_rules):
        raise ValueError("secondary views: global typography, focus, empty-state, or reduced-motion polish is incomplete")
    mobile_rules = dashboard_css.split("@media (max-width: 560px) {", 1)[1]
    if ".side-nav {\n    grid-template-columns: repeat(2, minmax(0, 1fr));\n  }" not in mobile_rules:
        raise ValueError("secondary views: mobile navigation must remain a two-column grid")
    shared_hover = dashboard_css.split(".ballet-home-next:hover {", 1)[1].split(
        "\n  }\n\n  .dounai-page-head:hover", 1
    )[0]
    if "background: #ffffff;" in shared_hover:
        raise ValueError("secondary views: shared hover must preserve component backgrounds")
    return "secondary views: shared shells, interaction polish, and ballet priority layout are valid"


def check_ballet_growth_contract():
    dashboard_html = (ROOT / "dash/index.html").read_text(encoding="utf-8")
    dashboard_css = (ROOT / "dash/styles.css").read_text(encoding="utf-8")
    dashboard_js = (ROOT / "dash/app.js").read_text(encoding="utf-8")
    specification = (ROOT / "SPEC.md").read_text(encoding="utf-8")
    growth_standard = (ROOT / "BALLET_GROWTH_SCORING.md").read_text(encoding="utf-8")
    start_marker = "<!-- BALLET_GROWTH_CONTRACT_START -->"
    end_marker = "<!-- BALLET_GROWTH_CONTRACT_END -->"
    if start_marker not in growth_standard or end_marker not in growth_standard:
        raise ValueError("ballet growth contract: standalone document markers are missing")
    if (
        "BALLET_GROWTH_SCORING.md" not in specification
        or start_marker in specification
        or end_marker in specification
    ):
        raise ValueError("ballet growth contract: SPEC must point to the standalone document without duplicating it")
    contract = growth_standard.split(start_marker, 1)[1].split(end_marker, 1)[0]

    promotion_match = re.search(
        r"const BALLET_PROMOTION_RULES = \{\n(?P<body>.*?)\n\};",
        dashboard_js,
        re.DOTALL,
    )
    if not promotion_match:
        raise ValueError("ballet growth contract: promotion rules are missing from app.js")
    promotion_code = {}
    promotion_pattern = re.compile(
        r'^\s*(?:"(?P<quoted>[^"]+)"|(?P<bare>[A-Za-z0-9.]+)):\s*'
        r'\{\s*next:\s*(?:"(?P<next>[^"]+)"|(?P<none>null)),\s*'
        r"regular:\s*(?P<regular>\d+),\s*intermittent:\s*(?P<intermittent>\d+)\s*\},$",
        re.MULTILINE,
    )
    for match in promotion_pattern.finditer(promotion_match.group("body")):
        level = match.group("quoted") or match.group("bare")
        promotion_code[level] = (
            match.group("next") or None,
            int(match.group("regular")),
            int(match.group("intermittent")),
        )
    promotion_docs = {}
    for match in re.finditer(
        r"^\| (L(?:1(?:\.5)?|2|3|4|5)) \| ([^|]+) \| (\d+) \| (\d+) \|$",
        contract,
        re.MULTILINE,
    ):
        level, next_level, regular, intermittent = (
            value.strip() for value in match.groups()
        )
        promotion_docs[level] = (
            None if next_level == "—" else next_level,
            int(regular),
            int(intermittent),
        )
    if promotion_code != promotion_docs:
        raise ValueError("ballet growth contract: promotion table does not match app.js")

    growth_level_match = re.search(
        r"const BALLET_GROWTH_LEVELS = \[\n(?P<body>.*?)\n\];",
        dashboard_js,
        re.DOTALL,
    )
    if not growth_level_match:
        raise ValueError("ballet growth contract: class-count levels are missing from app.js")
    growth_level_code = [
        (int(level), int(threshold))
        for level, threshold in re.findall(
            r"\{\s*level:\s*(\d+),\s*threshold:\s*(\d+)\s*\}",
            growth_level_match.group("body"),
        )
    ]
    growth_level_docs = [
        (int(level), int(threshold))
        for level, threshold in re.findall(
            r"^\| (\d+) \| (\d+) \|$",
            contract,
            re.MULTILINE,
        )
    ]
    if growth_level_code != growth_level_docs:
        raise ValueError("ballet growth contract: class-count level table does not match app.js")
    if len(growth_level_code) != 10 or growth_level_code[-1] != (10, 200):
        raise ValueError("ballet growth contract: growth must contain 10 levels and reach Lv.10 at 200 classes")

    swan_assets = [
        ROOT / "dash/assets/ballet/swan-growth-sheet.png",
        *(ROOT / f"dash/assets/ballet/swan-lv{level}.png" for level in range(1, 11)),
    ]
    if any(not asset.exists() or asset.stat().st_size < 1024 for asset in swan_assets):
        raise ValueError("ballet growth contract: approved swan source or one of the 10 level assets is missing")
    if (
        'id="ballet-swan-icon"' not in dashboard_html
        or 'src="./assets/ballet/swan-lv1.png"' not in dashboard_html
        or 'icon.src = `./assets/ballet/swan-lv${safeLevel}.png`;' not in dashboard_js
        or "object-fit: contain;" not in dashboard_css
        or "transform: translateY(-10px);" not in dashboard_css
        or "transform: translateY(-6px);" not in dashboard_css
        or 'id="ballet-level-progress"' not in dashboard_html
        or 'id="ballet-level-progress-fill"' not in dashboard_html
        or ".ballet-level-progress {\n  min-width: 0;\n  width: 100%;" not in dashboard_css
        or not re.search(
            r'class="ballet-level-progress">\s*<div\s+class="ballet-growth-track".*?'
            r'id="ballet-level-progress".*?<div class="ballet-level-layout">',
            dashboard_html,
            re.DOTALL,
        )
        or "const levelCompleted = next ? Math.max(0, completed - current.threshold) : 1;" not in dashboard_js
        or "const levelTarget = next ? Math.max(1, next.threshold - current.threshold) : 1;" not in dashboard_js
        or "setText(\"#ballet-level-title\", `Lv.${growth.current.level}`);" not in dashboard_js
        or "还差 ${growth.remaining} 节升级到 Lv.${growth.next.level}" not in dashboard_js
        or "页面标题只显示当前成长等级 `Lv.N`" not in contract
    ):
        raise ValueError("ballet growth contract: current-to-next swan progress rendering is incomplete")
    if (
        'class="ballet-swan-icon" viewBox=' in dashboard_html
        or "data-swan-unlock" in dashboard_html
        or 'id="ballet-growth-level"' in dashboard_html
        or 'id="ballet-growth-stages"' in dashboard_html
        or "ballet-growth-stage" in dashboard_html
        or "ballet-growth-disclaimer" in dashboard_html
        or 'id="ballet-level-note"' in dashboard_html
        or "ballet-swan-step" in dashboard_html
    ):
        raise ValueError("ballet growth contract: retired all-level or duplicate progress remains")

    synchronized_behavior = (
        ("const sampleSufficient = observationDays >= 21;", "至少覆盖 21 天"),
        (
            "const isRegular = hasMetRegularTarget || (sampleSufficient && weeklyRate >= 2);",
            "不得把已经自动进入的等级回退",
        ),
        (
            "while (!promotion.isFinal && promotion.completed >= promotion.target)",
            "达到目标课次后自动进入下一等级",
        ),
        (
            "promotion.isFinal ? Math.max(1, promotion.completed) : promotion.completed",
            "升班进度 =",
        ),
        ("const completed = records.length;", "每节课固定计 1 节"),
        ("renderBalletSwanLevel(growth.current.level);", "十张本地透明 PNG"),
    )
    missing_behavior = [
        code
        for code, prose in synchronized_behavior
        if code not in dashboard_js or prose not in contract
    ]
    if missing_behavior:
        raise ValueError(
            "ballet growth contract: promotion behavior and standalone document are out of sync: "
            + ", ".join(missing_behavior)
        )
    if any(
        retired in dashboard_js
        for retired in (
            "foundationMonths",
            "promotion.score",
            "hasFoundationTarget",
            "BALLET_XP_BY_COURSE_TYPE",
            "BALLET_XP_LEVELS",
            "getBalletXpState",
        )
    ):
        raise ValueError("ballet growth contract: retired month, score, or XP logic remains")
    return "ballet growth contract: automatic promotion, current level and next-distance display, approved swan assets, and standalone document sync are valid"


def check_data_health_contract():
    dashboard_html = (ROOT / "dash/index.html").read_text(encoding="utf-8")
    dashboard_js = (ROOT / "dash/app.js").read_text(encoding="utf-8")
    system_status = (ROOT / "scripts/sync_system_status.py").read_text(encoding="utf-8")
    required_frontend = (
        'const DATA_CACHE_PREFIX = "maxnow:last-good:v1:"',
        'status: "failed"',
        'status: "unsynced"',
        'status: "stale"',
        'status: "empty"',
        "saveLastGood(sourceKey, data)",
        "readLastGood(sourceKey)",
    )
    if any(value not in dashboard_js for value in required_frontend):
        raise ValueError("data health: frontend state or last-good fallback is incomplete")
    if "app.js?v=166" not in dashboard_html:
        raise ValueError("data health: script cache version is stale")
    if "CONSECUTIVE_FAILURE_THRESHOLD = 3" not in system_status or '"data-health"' not in system_status:
        raise ValueError("data health: server source summary or failure threshold is missing")
    update_data = (ROOT / "scripts/update_data.py").read_text(encoding="utf-8")
    if 'script != "scripts/sync_system_status.py"' not in update_data:
        raise ValueError("data health: failed syncs do not refresh the alert snapshot")

    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import sync_system_status

        source_keys = {item[0] for item in sync_system_status.DATA_SOURCE_SPECS}
        if len(source_keys) != 11 or "ballet" not in source_keys:
            raise ValueError("data health: the 11-source summary does not include ballet")
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            path = temporary_root / "automation.log"
            path.write_text(
                "[1] job start\n[1] failed\n[2] job start\n[2] failed\n[3] job start\n[3] failed\n",
                encoding="utf-8",
            )
            old_time = path.stat().st_mtime - 3600
            path.touch()
            os.utime(path, (old_time, old_time))
            if sync_system_status.consecutive_failure_count(path, "job start", "job ok") != 3:
                raise ValueError("data health: three consecutive failures are not detected")
            with path.open("a", encoding="utf-8") as handle:
                handle.write("[4] job start\n[4] job ok\n")
            if sync_system_status.consecutive_failure_count(path, "job start", "job ok") != 0:
                raise ValueError("data health: a successful run does not clear the failure streak")
            ballet_path = temporary_root / "ballet.json"
            ballet_path.write_text(
                json.dumps(
                    {
                        "sync": {
                            "lastSuccessAt": datetime.now().astimezone().isoformat(),
                            "lastAttemptStatus": "network_error",
                            "errorMessage": "闻道暂时无法连接",
                        },
                        "records": [{"courseName": "fixture"}],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            old_root = sync_system_status.ROOT
            old_specs = sync_system_status.DATA_SOURCE_SPECS
            try:
                sync_system_status.ROOT = temporary_root
                sync_system_status.DATA_SOURCE_SPECS = [
                    ("ballet", "芭蕾", "ballet.json", ("sync.lastSuccessAt",), ("records",), 36)
                ]
                health, healthy = sync_system_status.data_source_health_state()
            finally:
                sync_system_status.ROOT = old_root
                sync_system_status.DATA_SOURCE_SPECS = old_specs
            ballet_health = health["sources"][0]
            if healthy is not False or ballet_health["status"] != "failed":
                raise ValueError("data health: a fresh ballet cache masks its latest sync failure")
        if not sync_system_status.is_success_log_line("[2026-07-15T17:10:02+08:00] maxnow dashboard sync ok"):
            raise ValueError("data health: outer automation success does not clear an old child failure")
    finally:
        sys.path.pop(0)
    return "data health: five states, last-good fallback, 11-source summary, and failure streak checks are valid"


def main():
    checks = [check_required_files()]
    checks.extend(check_dataset(*dataset) for dataset in DATASETS)
    checks.append(check_dounai_checkin())
    checks.append(check_openclaw_usage())
    checks.append(check_codex_usage())
    checks.append(check_codex_macos_usage())
    checks.append(check_codex_server_usage())
    checks.append(check_token_usage())
    checks.append(check_market_indices())
    checks.append(check_project_meta())
    checks.append(check_project_status())
    checks.append(check_dashboard_weather())
    checks.append(check_special_dates())
    checks.append(check_ai_frontier_brief())
    checks.append(check_today_progress_ring())
    checks.append(check_secondary_view_style())
    checks.append(check_ballet_growth_contract())
    checks.append(check_data_health_contract())
    checks.append(check_ballet_read_model())
    checks.append(check_ballet_sync())
    checks.append(check_ballet_live_query())
    checks.append(check_ballet_booking())
    checks.append(check_ballet_booking_fast())
    checks.append(check_ballet_session_probe())
    checks.append(check_ballet_session_status())
    checks.append(check_auth_surface())
    checks.append(check_local_server("http://127.0.0.1:4173/"))
    checks.append(check_local_server("http://127.0.0.1:4173/dash/"))
    checks.append(check_local_server("http://127.0.0.1:4173/dash/login.html"))
    checks.append(check_local_server("http://127.0.0.1:4173/blog/"))
    checks.append(check_local_server("http://127.0.0.1:4173/blog/overview.html"))
    checks.append(check_local_server("http://127.0.0.1:4173/blog/topics.html"))
    checks.append(check_local_server("http://127.0.0.1:4173/blog/topic-algorithm.html"))
    checks.append(check_local_server("http://127.0.0.1:4173/blog/topic-cs.html"))
    checks.append(check_local_server("http://127.0.0.1:4173/blog/topic-algorithm-gap.html"))
    checks.append(check_local_server("http://127.0.0.1:4173/blog/topic-engineering.html"))
    checks.append(check_local_server("http://127.0.0.1:4173/blog/post-preview.html"))
    checks.append(check_local_server("http://127.0.0.1:4173/blog/preview.html"))

    for line in checks:
        print("[ok]", line)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("[fail]", error, file=sys.stderr)
        sys.exit(1)
