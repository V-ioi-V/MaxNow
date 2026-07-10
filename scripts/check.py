import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


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
        "scripts/maxnow_auth_service.py",
        "server/maxnow-auth.service",
        "server/maxnow-auth-rate-limit.conf",
        "server/maxnow-auth-locations.conf",
        "server/maxnow-dashboard.conf",
        "openclaw/maxnow-dashboard/SKILL.md",
        "openclaw/last-30/SKILL.md",
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

    if account and "remaining_flow_mb" in account:
        remaining = float(account["remaining_flow_mb"])
        if remaining < 0:
            raise ValueError("dounai-checkin: account.remaining_flow_mb cannot be negative")

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


def check_usage_ledger(name, rel_path, allowed_pricing_basis):
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
    return f"{name}: ledger shape is valid"


def check_codex_usage():
    return check_usage_ledger("codex-usage", "dash/data/codex-usage.json", {"openai-api-equivalent"})


def check_codex_macos_usage():
    return check_usage_ledger("codex-macos-usage", "dash/data/codex-macos-usage.json", {"openai-api-equivalent"})


def check_codex_server_usage():
    return check_usage_ledger("codex-server-usage", "dash/data/codex-server-usage.json", {"openai-api-equivalent"})


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
    if "conic-gradient(" not in dashboard_css or "--today-progress-angle: 0deg" not in dashboard_css:
        raise ValueError("Today progress ring: circular theme progress style is missing")
    if 'setProperty("--today-progress-angle", progressAngle)' not in dashboard_js:
        raise ValueError("Today progress ring: angle update is missing")
    if 'setText("#today-pulse-percent", progressPercent)' not in dashboard_js:
        raise ValueError("Today progress ring: inner percentage update is missing")
    retired_axis_copy = ("summary-live-start", "summary-live-end", "today-marker-ratio")
    if any(value in dashboard_html or value in dashboard_css or value in dashboard_js for value in retired_axis_copy):
        raise ValueError("Today progress ring: retired vertical axis remains")
    if ".summary-live-item::before" not in dashboard_css or "top: 2px" not in dashboard_css:
        raise ValueError("Today progress ring: signal node alignment rule is missing")
    return "Today progress ring: theme ring, inner percentage, outside time, and node alignment are valid"


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
    checks.append(check_ai_frontier_brief())
    checks.append(check_today_progress_ring())
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
