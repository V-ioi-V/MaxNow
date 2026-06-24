import json
import re
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
    ("token-usage", "dash/data/token-usage.json", "dash/data/token-usage.js", "MAXNOW_TOKEN_USAGE_DATA"),
    ("project-meta", "dash/data/project-meta.json", "dash/data/project-meta.js", "MAXNOW_PROJECT_META_DATA"),
    ("ricky", "dash/data/ricky.json", "dash/data/ricky.js", "MAXNOW_RICKY_DATA"),
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
        "dash/styles.css",
        "dash/app.js",
        "dash/data/dounai_checkin.json",
        "dash/data/ricky.json",
        "dash/data/ricky.js",
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
        "scripts/sync_project_meta.py",
        "scripts/sync_weather.py",
        "scripts/sync_ricky_travel.py",
        "scripts/update_data.py",
        "openclaw/maxnow-dashboard/SKILL.md",
        "openclaw/last-30/SKILL.md",
    ]
    missing = [item for item in required if not (ROOT / item).exists()]
    if missing:
        raise FileNotFoundError("missing required files: " + ", ".join(missing))
    return "required files exist"


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

    return "dounai-checkin: json, account snapshot, and account history are valid"


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
        for key in ["inputTokens", "outputTokens", "cacheReadTokens", "totalTokens", "runs"]:
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
        for key in ["inputTokens", "outputTokens", "cacheReadTokens", "totalTokens", "runs"]:
            if int(day.get(key, 0)) < 0:
                raise ValueError(f"{name}: {key} cannot be negative")
        if float(day.get("estimatedCostUsd", 0)) < 0:
            raise ValueError(f"{name}: estimatedCostUsd cannot be negative")
    return f"{name}: ledger shape is valid"


def check_codex_usage():
    return check_usage_ledger("codex-usage", "dash/data/codex-usage.json", {"subscription-usage"})


def check_token_usage():
    return check_usage_ledger("token-usage", "dash/data/token-usage.json", {"mixed", "openrouter-equivalent", "subscription-usage"})


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
    return "dashboard weather: shape is valid"


def main():
    checks = [check_required_files()]
    checks.extend(check_dataset(*dataset) for dataset in DATASETS)
    checks.append(check_dounai_checkin())
    checks.append(check_openclaw_usage())
    checks.append(check_codex_usage())
    checks.append(check_token_usage())
    checks.append(check_project_meta())
    checks.append(check_dashboard_weather())
    checks.append(check_local_server("http://127.0.0.1:4173/"))
    checks.append(check_local_server("http://127.0.0.1:4173/dash/"))
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
