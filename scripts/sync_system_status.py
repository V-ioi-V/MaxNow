import argparse
import json
import shutil
import ssl
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_JSON = ROOT / "dash" / "data" / "dashboard.json"
DASHBOARD_JS = ROOT / "dash" / "data" / "dashboard.js"
WIKI_TODOS_JSON = ROOT / "dash" / "data" / "wiki-todos.json"
GLOBAL_NAME = "MAXNOW_DASHBOARD_DATA"
DEFAULT_SITE_URL = "https://dash.maxnow.cn/"
METADATA_BASE_URL = "http://metadata.tencentyun.com/latest/meta-data"
LOG_DIR = ROOT / "logs"
SYNC_LOG = LOG_DIR / "maxnow-sync.log"
CRON_MARKER = "MAXNOW-DASHBOARD-SYNC"
KNOWN_TIMER_UNITS = [
    "maxnow-wiki-todos.timer",
    "maxnow-system-status.timer",
    "maxnow-dashboard-sync.timer",
]
KNOWN_SERVICE_UNITS = [
    "maxnow-wiki-todos.service",
    "maxnow-system-status.service",
    "maxnow-dashboard-sync.service",
]
GENERATED_DATA_PATHS = {
    "dash/data/dashboard.json",
    "dash/data/dashboard.js",
    "dash/data/wiki-todos.json",
    "dash/data/wiki-todos.js",
}


def now_text():
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")


def format_local_datetime(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")


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
    }, not dirty


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


def certificate_state(url):
    parsed = urlparse(url)
    hostname = parsed.hostname
    if parsed.scheme != "https" or not hostname:
        return {
            "key": "certificate",
            "name": "证书",
            "value": "Unknown",
            "note": "site URL is not HTTPS",
        }, None

    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=6) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as wrapped:
                cert = wrapped.getpeercert()
        expires_raw = cert.get("notAfter")
        expires = datetime.strptime(expires_raw, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        remaining_days = (expires - datetime.now(timezone.utc)).days
        return {
            "key": "certificate",
            "name": "证书",
            "value": f"{remaining_days}d",
            "note": f"expires {expires.astimezone().strftime('%Y-%m-%d %H:%M')}",
        }, remaining_days >= 14
    except Exception as error:
        return {
            "key": "certificate",
            "name": "证书",
            "value": "Check",
            "note": str(error),
        }, False


def metadata_value(path):
    try:
        url = f"{METADATA_BASE_URL}/{path}"
        request = urllib.request.Request(url, headers={"User-Agent": "MaxNow status check"})
        with urllib.request.urlopen(request, timeout=2) as response:
            return response.read().decode("utf-8").strip()
    except (urllib.error.URLError, TimeoutError, UnicodeDecodeError):
        return ""


def cloud_location_state():
    instance_id = metadata_value("instance-id")
    public_ip = metadata_value("public-ipv4")
    region = metadata_value("placement/region")
    zone = metadata_value("placement/zone")

    if not any([instance_id, public_ip, region, zone]):
        return {
            "key": "cloud-location",
            "name": "云位置",
            "value": "Unknown",
            "note": "Tencent Cloud metadata is not available",
        }, None

    value = zone or region or "Tencent Cloud"
    note_parts = []
    if region:
        note_parts.append(f"region {region}")
    if instance_id:
        note_parts.append(f"instance {instance_id}")
    if public_ip:
        note_parts.append(f"public IP {public_ip}")
    return {
        "key": "cloud-location",
        "name": "云位置",
        "value": value,
        "note": "; ".join(note_parts),
    }, True


def billing_state():
    charge_type = metadata_value("payment/charge-type")
    termination_time = metadata_value("payment/termination-time")
    create_time = metadata_value("payment/create-time")

    if not any([charge_type, termination_time, create_time]):
        return {
            "key": "billing",
            "name": "计费/有效期",
            "value": "Unknown",
            "note": "Tencent Cloud payment metadata is not available",
        }, None

    if charge_type == "POSTPAID_BY_HOUR":
        value = "按量计费"
    elif charge_type:
        value = charge_type
    else:
        value = "Unknown"

    note_parts = []
    if termination_time and termination_time != "null":
        note_parts.append(f"expires {termination_time}")
    elif charge_type == "POSTPAID_BY_HOUR":
        note_parts.append("no fixed expiry")
    elif termination_time == "null":
        note_parts.append("termination time null")
    if create_time:
        note_parts.append(f"created {create_time}")

    return {
        "key": "billing",
        "name": "计费/有效期",
        "value": value,
        "note": "; ".join(note_parts),
    }, value != "Unknown"


def disk_state():
    usage = shutil.disk_usage(ROOT)
    used_pct = round((usage.used / usage.total) * 100)
    free_gb = usage.free / (1024 ** 3)
    total_gb = usage.total / (1024 ** 3)
    mount = ROOT.anchor or "/"
    note = f"{free_gb:.1f} / {total_gb:.1f} GB available"
    if mount != "/":
        note = f"{note} on {mount}"
    ok = used_pct < 85
    return {
        "key": "disk",
        "name": "磁盘",
        "value": f"{used_pct}%",
        "note": note,
    }, ok


def read_cpu_totals():
    stat = Path("/proc/stat")
    if not stat.exists():
        return None
    first_line = stat.read_text(encoding="utf-8").splitlines()[0]
    parts = first_line.split()
    if not parts or parts[0] != "cpu":
        return None
    values = [int(part) for part in parts[1:]]
    idle = values[3] + (values[4] if len(values) > 4 else 0)
    total = sum(values)
    return total, idle


def cpu_state():
    first = read_cpu_totals()
    if first is None:
        return {
            "key": "cpu",
            "name": "CPU",
            "value": "Unknown",
            "note": "CPU info is only collected on Linux",
        }, None

    time.sleep(0.25)
    second = read_cpu_totals()
    if second is None:
        return {
            "key": "cpu",
            "name": "CPU",
            "value": "Unknown",
            "note": "could not read /proc/stat twice",
        }, None

    total_delta = second[0] - first[0]
    idle_delta = second[1] - first[1]
    usage_pct = 0 if total_delta <= 0 else round(((total_delta - idle_delta) / total_delta) * 100)

    cores = "unknown cores"
    core_count = None
    code, stdout, _ = run_command(["nproc"], timeout=2)
    if code == 0 and stdout:
        core_text = stdout.strip()
        cores = f"{core_text} cores"
        if core_text.isdigit() and int(core_text) > 0:
            core_count = int(core_text)

    loadavg = Path("/proc/loadavg")
    load_text = "1/5/15 min load unavailable"
    if loadavg.exists():
        loads = loadavg.read_text(encoding="utf-8").split()[:3]
        if len(loads) == 3 and core_count:
            load_pcts = [f"{round((float(load) / core_count) * 100)}%" for load in loads]
            load_text = f"1/5/15 min load {' / '.join(load_pcts)}"
        elif len(loads) == 3:
            load_text = f"1/5/15 min load {' / '.join(loads)}"

    return {
        "key": "cpu",
        "name": "CPU",
        "value": f"{usage_pct}%",
        "note": f"{cores}; {load_text}",
    }, usage_pct < 85


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
    total_gb = total / (1024 ** 2)
    return {
        "key": "memory",
        "name": "内存",
        "value": f"{used_pct}%",
        "note": f"{available_gb:.1f} / {total_gb:.1f} GB available",
    }, used_pct < 90


def uptime_state():
    uptime_path = Path("/proc/uptime")
    if uptime_path.exists():
        seconds = float(uptime_path.read_text(encoding="utf-8").split()[0])
        return {
            "key": "uptime",
            "name": "运行时间",
            "value": format_uptime(seconds),
            "note": "持续运行",
        }, True

    return {
        "key": "uptime",
        "name": "运行时间",
        "value": "Unknown",
        "note": "uptime is not available",
    }, None


def format_uptime(seconds):
    minutes = int(seconds // 60)
    days = minutes // (24 * 60)
    hours = (minutes % (24 * 60)) // 60
    mins = minutes % 60

    if days:
        return f"{days} 天 {hours} 小时" if hours else f"{days} 天"
    if hours:
        return f"{hours} 小时 {mins} 分钟" if mins else f"{hours} 小时"
    return f"{mins} 分钟"


def git_pull_state():
    fetch_head = ROOT / ".git" / "FETCH_HEAD"
    if not fetch_head.exists():
        return {
            "key": "git-pull",
            "name": "最近拉取",
            "value": "Unknown",
            "note": ".git/FETCH_HEAD is missing",
        }, None

    timestamp = fetch_head.stat().st_mtime
    return {
        "key": "git-pull",
        "name": "最近拉取",
        "value": format_local_datetime(timestamp),
        "note": "from .git/FETCH_HEAD mtime",
    }, True


def unit_state(unit):
    code, stdout, _ = run_command(["systemctl", "is-enabled", unit], timeout=2)
    enabled = stdout if code == 0 and stdout else "not-enabled"
    code, stdout, _ = run_command(["systemctl", "is-active", unit], timeout=2)
    active = stdout if stdout else "inactive"
    return enabled, active


def timer_state():
    code, crontab, _ = run_command(["crontab", "-l"], timeout=2)
    if code == 0 and CRON_MARKER in crontab:
        return {
            "key": "timers",
            "name": "定时同步",
            "value": "Cron 10m",
            "note": f"{CRON_MARKER} active; runs update_data.py runtime every 10 minutes",
        }, True

    code, _, _ = run_command(["systemctl", "--version"], timeout=2)
    if code == 127:
        return {
            "key": "timers",
            "name": "定时任务",
            "value": "Unknown",
            "note": "systemctl is not available",
        }, None

    states = []
    found = 0
    for unit in KNOWN_TIMER_UNITS:
        enabled, active = unit_state(unit)
        if enabled != "not-enabled" or active == "active":
            found += 1
        states.append(f"{unit}:{enabled}/{active}")

    value = f"{found} active" if found else "Not set"
    note = "; ".join(states) if states else "no known timer units"
    return {
        "key": "timers",
        "name": "定时任务",
        "value": value,
        "note": note,
    }, bool(found)


def failure_log_state():
    candidates = [
        LOG_DIR / "wiki-todos.log",
        LOG_DIR / "system-status.log",
        SYNC_LOG,
    ]
    existing = [path for path in candidates if path.exists()]
    if not existing:
        return {
            "key": "failure-log",
            "name": "失败日志",
            "value": "No log",
            "note": f"expected logs under {LOG_DIR}",
        }, True

    latest = max(existing, key=lambda path: path.stat().st_mtime)
    lines = latest.read_text(encoding="utf-8", errors="replace").splitlines()
    recent_lines = lines[-160:]
    for index in range(len(recent_lines) - 1, -1, -1):
        if "maxnow dashboard sync start" in recent_lines[index]:
            recent_lines = recent_lines[index:]
            break
    failure_markers = ("[fail]", "error", "traceback", "failed")
    failure_lines = [
        line for line in recent_lines
        if any(marker in line.lower() for marker in failure_markers)
    ]
    if failure_lines:
        return {
            "key": "failure-log",
            "name": "失败日志",
            "value": "Check",
            "note": failure_lines[-1][:140],
        }, False

    return {
        "key": "failure-log",
        "name": "失败日志",
        "value": "Clear",
        "note": f"latest {latest.relative_to(ROOT)} at {format_local_datetime(latest.stat().st_mtime)}",
    }, True


def wiki_todos_state():
    try:
        data = json.loads(WIKI_TODOS_JSON.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {
            "key": "wiki-todos",
            "name": "wiki 待办",
            "value": "Missing",
            "note": "dash/data/wiki-todos.json does not exist",
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
    server = server_identity()
    nginx, nginx_ok = nginx_state()
    site, site_ok = site_state(site_url)
    certificate, certificate_ok = certificate_state(site_url)
    deploy, deploy_ok = git_state()
    git_pull, git_pull_ok = git_pull_state()
    timers, timers_ok = timer_state()
    wiki_todos, wiki_todos_ok = wiki_todos_state()
    failure_log, failure_log_ok = failure_log_state()
    cloud_location, cloud_location_ok = cloud_location_state()
    billing, billing_ok = billing_state()
    cpu, cpu_ok = cpu_state()
    disk, disk_ok = disk_state()
    memory, memory_ok = memory_state()
    uptime, uptime_ok = uptime_state()

    checks.extend([
        nginx_ok,
        site_ok,
        certificate_ok,
        deploy_ok,
        git_pull_ok,
        timers_ok,
        wiki_todos_ok,
        failure_log_ok,
        cloud_location_ok,
        billing_ok,
        cpu_ok,
        disk_ok,
        memory_ok,
        uptime_ok,
    ])
    failed = [item for item in checks if item is False]
    unknown = [item for item in checks if item is None]

    if failed:
        status = "异常"
    elif unknown:
        status = "注意"
    else:
        status = "正常"

    summary_parts = [
        f"nginx {nginx['value']}",
        f"HTTPS {site['value']}",
        f"wiki {wiki_todos['value']}",
        f"cron {timers['value']}",
        f"log {failure_log['value']}",
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
            server,
            nginx,
            site,
            certificate,
            deploy,
            git_pull,
            timers,
            wiki_todos,
            failure_log,
            cpu,
            disk,
            memory,
            uptime,
            cloud_location,
            billing,
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
