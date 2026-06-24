import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_PATH = ROOT / "VERSION"
UPDATE_LOG_PATH = ROOT / "UPDATE_LOG.md"
JSON_PATH = ROOT / "dash" / "data" / "project-meta.json"
JS_PATH = ROOT / "dash" / "data" / "project-meta.js"
GLOBAL_NAME = "MAXNOW_PROJECT_META_DATA"
GENERATED_DATA_PATHS = {
    "dash/data/dashboard.json",
    "dash/data/dashboard.js",
    "dash/data/wiki-todos.json",
    "dash/data/wiki-todos.js",
    "dash/data/openclaw-usage.json",
    "dash/data/openclaw-usage.js",
    "dash/data/dounai_checkin.json",
    "dash/data/project-meta.json",
    "dash/data/project-meta.js",
    "dash/data/ricky.json",
    "dash/data/ricky.js",
}


def now_text():
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")


def run_git(args):
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def git_state():
    commit = run_git(["rev-parse", "--short", "HEAD"])
    branch = run_git(["branch", "--show-current"]) or "unknown"
    status = run_git(["status", "--short"])
    changed_paths = []
    for line in status.splitlines():
        if len(line) >= 3:
            changed_paths.append(line[2:].strip().replace("\\", "/"))

    code_dirty = any(path not in GENERATED_DATA_PATHS for path in changed_paths)
    generated_dirty = bool(changed_paths) and not code_dirty
    if code_dirty:
        level = "code"
        note = "有未提交代码改动"
    elif generated_dirty:
        level = "generated"
        note = "运行数据已更新"
    else:
        level = "clean"
        note = "干净"

    return {
        "branch": branch,
        "commit": commit,
        "dirty": bool(changed_paths),
        "dirtyLevel": level,
        "deployNote": f"{branch} · commit {commit or '--'} · {note}",
    }


def read_version():
    version = VERSION_PATH.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+\.\d{2}", version):
        raise ValueError("VERSION must match x.x.x.xx, for example 1.0.0.00")
    return version


def parse_recent_updates(limit=5):
    updates = []
    current_date = ""
    current = None

    for raw_line in UPDATE_LOG_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            if current:
                updates.append(current)
            current_date = line[3:].strip()
            current = None
            continue
        if line.startswith("### "):
            if current:
                updates.append(current)
            current = {"date": current_date, "title": line[4:].strip(), "summary": ""}
            continue
        if current and not current["summary"] and line.startswith("- "):
            current["summary"] = line[2:].strip()

    if current:
        updates.append(current)

    return updates[:limit]


def write_wrapper(data):
    JS_PATH.write_text(
        f"window.{GLOBAL_NAME} = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )


def main():
    version = read_version()
    data = {
        "schemaVersion": 1,
        "updatedAt": now_text(),
        "version": version,
        "versionLabel": f"v{version}",
        **git_state(),
        "recentUpdates": parse_recent_updates(),
    }
    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_wrapper(data)
    print(f"[ok] wrote {JSON_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
