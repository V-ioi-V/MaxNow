import base64
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = "V-ioi-V/personal-wiki"
REF = "main"
SOURCE_PATH = "wiki/tasks/todo.json"
SOURCE_URL = f"https://github.com/{REPO}/blob/{REF}/{SOURCE_PATH}"
JSON_PATH = ROOT / "data" / "wiki-todos.json"
JS_PATH = ROOT / "data" / "wiki-todos.js"
GLOBAL_NAME = "MAXNOW_WIKI_TODO_DATA"


def run_gh_api():
    api_path = f"repos/{REPO}/contents/{SOURCE_PATH}?ref={REF}"
    result = subprocess.run(
        ["gh", "api", api_path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def decode_content(payload):
    if payload.get("encoding") != "base64":
        raise ValueError(f"unsupported GitHub content encoding: {payload.get('encoding')}")
    raw = base64.b64decode(payload["content"])
    return json.loads(raw.decode("utf-8-sig"))


def build_cache(source):
    tasks = source.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("personal-wiki todo.json must contain a tasks array")

    return {
        "schema_version": 1,
        "updated_at": source.get("updated_at") or "",
        "source_file": SOURCE_PATH,
        "source_url": SOURCE_URL,
        "synced_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "tasks": tasks,
    }


def write_outputs(cache):
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(cache, ensure_ascii=False, indent=2)
    JSON_PATH.write_text(text + "\n", encoding="utf-8")

    wrapper = f"window.{GLOBAL_NAME} = " + json.dumps(cache, ensure_ascii=False, indent=2) + ";\n"
    JS_PATH.write_text(wrapper, encoding="utf-8")


def main():
    payload = run_gh_api()
    cache = build_cache(decode_content(payload))
    write_outputs(cache)
    print(f"[ok] synced {len(cache['tasks'])} personal-wiki todos")
    print(f"[ok] wrote {JSON_PATH.relative_to(ROOT)}")
    print(f"[ok] wrote {JS_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        print("[fail] gh CLI is required and must be on PATH", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or str(error)
        print(f"[fail] gh api failed: {detail}", file=sys.stderr)
        sys.exit(error.returncode or 1)
    except Exception as error:
        print(f"[fail] {error}", file=sys.stderr)
        sys.exit(1)
