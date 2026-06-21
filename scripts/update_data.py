import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DATASETS = {
    "dashboard": ("dash/data/dashboard.json", "dash/data/dashboard.js", "MAXNOW_DASHBOARD_DATA"),
    "ai-news": ("dash/data/ai-news.json", "dash/data/ai-news.js", "MAXNOW_AI_NEWS_DATA"),
    "last-30": ("dash/data/last-30.json", "dash/data/last-30.js", "MAXNOW_LAST30_DATA"),
    "wiki-todos": ("dash/data/wiki-todos.json", "dash/data/wiki-todos.js", "MAXNOW_WIKI_TODO_DATA"),
    "openclaw-usage": ("dash/data/openclaw-usage.json", "dash/data/openclaw-usage.js", "MAXNOW_OPENCLAW_USAGE_DATA"),
}
LOG_DIR = ROOT / "logs"


def now_text():
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")


def load_json(rel_path):
    return json.loads((ROOT / rel_path).read_text(encoding="utf-8"))


def write_json(rel_path, data):
    (ROOT / rel_path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_wrapper(dataset):
    json_rel, js_rel, global_name = DATASETS[dataset]
    data = load_json(json_rel)
    wrapper = f"window.{global_name} = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    (ROOT / js_rel).write_text(wrapper, encoding="utf-8")
    print(f"[ok] regenerated {js_rel}")


def run_python(script, log_name=None):
    if not log_name:
        subprocess.run([sys.executable, script], cwd=ROOT, check=True)
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / log_name
    with log_path.open("a", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, script],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
            log.write(line)
            log.flush()
        code = process.wait()
    if code:
        raise subprocess.CalledProcessError(code, [sys.executable, script])


def run_check():
    subprocess.run([sys.executable, "scripts/check.py"], cwd=ROOT, check=True)


def collect_roadmap_sections():
    text = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    sections = []
    current_area = ""
    current = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            if current:
                sections.append(current)
            current_area = line[3:].strip()
            current = None
            continue
        if line.startswith("### "):
            if current:
                sections.append(current)
            current = {"area": current_area, "title": line[4:].strip(), "bullets": []}
            continue
        if current and line.startswith("- "):
            current["bullets"].append(line[2:].strip())

    if current:
        sections.append(current)
    return sections


def first_bullet(section):
    return section["bullets"][0] if section["bullets"] else ""


def refresh_project_status():
    sections = collect_roadmap_sections()
    now_sections = [item for item in sections if item["area"] == "Now"]
    next_sections = [item for item in sections if item["area"] == "Next"]

    mainline_source = now_sections[:3] or sections[:3]
    action_source = (now_sections + next_sections)[:3]

    dashboard = load_json("dash/data/dashboard.json")
    dashboard["feedSource"] = "ROADMAP.md"
    dashboard["journalSource"] = "Repo status"
    dashboard["mainlines"] = [
        {
            "title": section["title"],
            "note": first_bullet(section),
            "label": section["area"],
            "status": "active",
        }
        for section in mainline_source
    ]
    dashboard["actions"] = [
        {
            "title": section["title"],
            "note": first_bullet(section),
            "label": section["area"],
            "status": "active" if section["area"] == "Now" else "waiting",
        }
        for section in action_source
    ]
    existing_feeds = [
        feed for feed in dashboard.get("feeds", [])
        if feed.get("source") not in {"Roadmap", "Automation"}
    ]
    dashboard["feeds"] = [
        {
            "source": "Roadmap",
            "title": "当前可执行任务",
            "summary": "Home 的当前主线和今日推进由 scripts/update_data.py project-status 从 ROADMAP.md 显式刷新。",
            "url": "https://github.com/V-ioi-V/MaxNow/blob/main/ROADMAP.md",
        },
        {
            "source": "Automation",
            "title": "服务器同步链路",
            "summary": "wiki-todos 与系统状态每 10 分钟由服务器 crontab 刷新，失败信息进入系统状态列表。",
            "url": "",
        },
    ] + existing_feeds[:1]

    today = dashboard.setdefault("today", {})
    today["focus"] = action_source[0]["title"] if action_source else today.get("focus", "")
    today["updatedAt"] = now_text()
    if action_source:
        today["summary"] = f"当前优先推进：{action_source[0]['title']}。"

    write_json("dash/data/dashboard.json", dashboard)
    write_wrapper("dashboard")
    print("[ok] refreshed dashboard project status from ROADMAP.md")


def parse_args():
    parser = argparse.ArgumentParser(description="Update MaxNow runtime data and wrappers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    wrap = subparsers.add_parser("wrap", help="Regenerate JS wrappers from JSON.")
    wrap.add_argument("dataset", choices=[*DATASETS.keys(), "all"])

    subparsers.add_parser("wiki-todos", help="Sync personal-wiki todos and validate data.")
    subparsers.add_parser("system-status", help="Refresh machine-collected system status and validate data.")
    subparsers.add_parser("openclaw-usage", help="Refresh OpenClaw token usage ledger and validate data.")
    subparsers.add_parser("runtime", help="Run server runtime sync without changing owner judgment fields.")
    subparsers.add_parser("project-status", help="Refresh Home project status from ROADMAP.md and validate data.")
    subparsers.add_parser("all", help="Run wiki todos, system status, project status, wrappers, and checks.")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.command == "wrap":
        datasets = DATASETS if args.dataset == "all" else [args.dataset]
        for dataset in datasets:
            write_wrapper(dataset)
        run_check()
        return

    if args.command in {"wiki-todos", "runtime", "all"}:
        run_python("scripts/sync_wiki_todos.py", "wiki-todos.log")

    if args.command in {"system-status", "runtime", "all"}:
        run_python("scripts/sync_system_status.py", "system-status.log")

    if args.command in {"openclaw-usage", "all"}:
        run_python("scripts/sync_openclaw_usage.py", "openclaw-usage.log")
        write_wrapper("openclaw-usage")

    if args.command in {"project-status", "all"}:
        refresh_project_status()

    if args.command == "all":
        for dataset in DATASETS:
            write_wrapper(dataset)

    run_check()


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode or 1)
    except Exception as error:
        print(f"[fail] {error}", file=sys.stderr)
        sys.exit(1)
