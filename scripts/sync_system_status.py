import argparse
import json
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_JSON = ROOT / "data" / "dashboard.json"
DASHBOARD_JS = ROOT / "data" / "dashboard.js"
WIKI_TODOS_JSON = ROOT / "data" / "wiki-todos.json"
GLOBAL_NAME = "MAXNOW_DASHBOARD_DATA"
DEFAULT_SITE_URL = "https://dash.maxnow.cn/"
GENERATED_DATA_PATHS = {
    "data/dashboard.json",
    "data/dashboard.js",
    "data/wiki-todos.json",
    "data/wiki-todos.js",
}


def now_text():
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")


def run_command(args, timeout=5):
    try:
        result = subprocess.run(
            args,
            cwd=ROOT,
            capture_output=True,
            check=False,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"{args[0]} not found"
    except subprocess.TimeoutExpired:
        return 124, "", "command timed out"


def git_state():
    _, commit, _ = run_command(["git", "rev-parse", "--short", "HEAD"])
    _, branch, _ = run_command(["git", "branch", "--show-current"])
    _, status, _ = run_command(["git", "status", "--short"])
    changed_paths = []
    for line in status.splitlines():
        if len(line) < 3:
            continue
        changed_paths.append(line[2:].strip().replace("\\", "/"))
    dirty = any(path not in GENERATED_DATA_PATHS for path in changed_paths)
    value = commit or "--"
    if dirty:
        value = f"{value}*"
    note = f"{branch or 'unknown'} branch"
    if dirty:
        note += "; working tree has non-generated local changes"
    elif changed_paths:
        note += "; generated data has local updates"
    return {
        "key": "deploy",
        "name": "部署版本",
        "value": value,
        "note": note,
    }, dirty


def nginx_state():
    code, active, _ = run_command(["systemctl", "is-active", "nginx"])
    if code == 0 and active:
        return {
            "key": "nginx",
            "name": "nginx",
            "value": "Active",
            "note": "systemctl reports nginx is active",
        }, True
    if code == 127:
        return {
            "key": "nginx",
            "name": "nginx",
            "value": "Unknown",
            "note": "systemctl is not available in this environment",
        }, None
    return {
        "key": "nginx",
        "name": "nginx",
        "value": "Check",
        "note": active or "nginx is not active",
    }, False


def site_state(url):
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "MaxNow status check"})
        with urllib.request.urlopen(request, timeout=8) as response:
            status = response.status
            final_url = response.geturl()
        ok = 200 <= status < 400
        return {
            "key": "https",
            "name": "HTTPS",
            "value": str(status),
            "note": final_url if final_url != url else url,
        }, ok
    except (urllib.error.URLError, TimeoutError) as error:
        return {
            "key": "https",
            "name": "HTTPS",
            "value": "Fail",
            "note": str(getattr(error, "reason", error)),
        }, False


def disk_state():
    usage = shutil.disk_usage(ROOT)
    used_pct = round((usage.used / usage.total) * 100)
    free_gb = usage.free / (1024 ** 3)
    ok = used_pct < 85
    return {
        "key": "disk",
        "name": "磁盘",
        "value": f"{used_pct}%",
        "note": f"{free_gb:.1f} GB free on {ROOT.anchor or '/'}",
    }, ok


def memory_state():
    meminfo = Path("/proc/meminfo")
    if not meminfo.exists():
        return {
            "key": "memory",
            "name": "内存",
            "value": "Unknown",
            "note": "memory info is only collected on Linux",
        }, None

    values = {}
    for line in meminfo.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, rest = line.split(":", 1)
        number = rest.strip().split()[0]
        if number.isdigit():
            values[key] = int(number)

    total = values.get("MemTotal")
    available = values.get("MemAvailable")
    if not total or available is None:
        return {
            "key": "memory",
            "name": "内存",
            "value": "Unknown",
            "note": "MemTotal or MemAvailable missing",
        }, None

    used_pct = round(((total - available) / total) * 100)
    available_gb = available / (1024 ** 2)
    return {
        "key": "memory",
        "name": "内存",
        "value": f"{used_pct}%",
        "note": f"{available_gb:.1f} GB available",
    }, used_pct < 90


def wiki_todos_state():
    try:
        data = json.loads(WIKI_TODOS_JSON.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {
            "key": "wiki-todos",
            "name": "wiki 待办",
            "value": "Missing",
            "note": "data/wiki-todos.json does not exist",
        }, False
    except json.JSONDecodeError as error:
        return {
            "key": "wiki-todos",
            "name": "wiki 待办",
            "value": "Invalid",
            "note": str(error),
        }, False

    tasks = data.get("tasks") if isinstance(data, dict) else []
    open_count = len([
        task for task in tasks or []
        if not task.get("completed_at") and str(task.get("status", "")).lower() not in {"done", "completed", "closed"}
    ])
    synced_at = data.get("synced_at") or data.get("updated_at") or "unknown"
    return {
        "key": "wiki-todos",
        "name": "wiki 待办",
        "value": f"{open_count} open",
        "note": f"synced {synced_at}",
    }, True


def server_identity():
    return {
        "key": "server",
        "name": "服务器",
        "value": socket.gethostname(),
        "note": f"site root {ROOT}",
    }


def build_status(site_url):
    checks = []
    deploy, dirty = git_state()
    nginx, nginx_ok = nginx_state()
    https, https_ok = site_state(site_url)
    disk, disk_ok = disk_state()
    memory, memory_ok = memory_state()
    wiki, wiki_ok = wiki_todos_state()

    checks.extend([nginx_ok, https_ok, disk_ok, memory_ok, wiki_ok])
    failed = [item for item in checks if item is False]
    unknown = [item for item in checks if item is None]

    if failed:
        status = "异常"
    elif unknown or dirty:
        status = "注意"
    else:
        status = "正常"

    summary_parts = [
        f"HTTPS {https['value']}",
        f"nginx {nginx['value']}",
        f"wiki {wiki['value']}",
        f"commit {deploy['value']}",
    ]
    if failed:
        summary_parts.append(f"{len(failed)} checks failed")
    elif unknown:
        summary_parts.append(f"{len(unknown)} checks unknown")

    return {
        "automation": {
            "status": status,
            "summary": "；".join(summary_parts),
            "lastRun": now_text(),
        },
        "system": [
            server_identity(),
            nginx,
            https,
            deploy,
            wiki,
            disk,
            memory,
        ],
    }


def write_dashboard(next_status):
    data = json.loads(DASHBOARD_JSON.read_text(encoding="utf-8"))
    data["automation"] = next_status["automation"]
    data["system"] = next_status["system"]

    DASHBOARD_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DASHBOARD_JS.write_text(
        f"window.{GLOBAL_NAME} = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    return data


def main():
    parser = argparse.ArgumentParser(description="Update MaxNow machine-collected system status.")
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL, help="Public site URL to check.")
    parser.add_argument("--dry-run", action="store_true", help="Print collected status without writing files.")
    args = parser.parse_args()

    next_status = build_status(args.site_url)
    if args.dry_run:
        print(json.dumps(next_status, ensure_ascii=False, indent=2))
        return

    write_dashboard(next_status)
    print(f"[ok] updated {DASHBOARD_JSON.relative_to(ROOT)}")
    print(f"[ok] updated {DASHBOARD_JS.relative_to(ROOT)}")
    print(f"[ok] status {next_status['automation']['status']}: {next_status['automation']['summary']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"[fail] {error}", file=sys.stderr)
        sys.exit(1)
