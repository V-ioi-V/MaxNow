import base64
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = "V-ioi-V/personal-wiki"
REF = "main"
SOURCE_PATH = "wiki/life/food-picker.md"
SOURCE_URL = f"https://github.com/{REPO}/blob/{REF}/{SOURCE_PATH}"
LOCAL_CANDIDATES = [
    Path(os.environ["PERSONAL_WIKI_ROOT"]) if os.environ.get("PERSONAL_WIKI_ROOT") else None,
    ROOT.parent / "personal-wiki",
    Path("D:/Personal/personal-wiki"),
]
JSON_PATH = ROOT / "dash" / "data" / "life-foods.json"
JS_PATH = ROOT / "dash" / "data" / "life-foods.js"
GLOBAL_NAME = "MAXNOW_LIFE_FOODS_DATA"


def local_source_path():
    for candidate in LOCAL_CANDIDATES:
        if not candidate:
            continue
        path = candidate / SOURCE_PATH
        if path.exists():
            return path
    return None


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
    return raw.decode("utf-8-sig")


def load_source():
    path = local_source_path()
    if path:
        return path.read_text(encoding="utf-8-sig"), "local personal-wiki"
    return decode_content(run_gh_api()), "github"


def slugify(text, index):
    ascii_slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if ascii_slug:
        return ascii_slug
    return f"food-{index + 1:02d}"


def parse_food_items(markdown):
    items = []
    in_food_section = False
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            in_food_section = line.lstrip("#").strip() == "菜品"
            continue
        if not in_food_section:
            continue
        match = re.match(r"^[-*]\s+(.+?)\s*$", line)
        if not match:
            continue
        name = match.group(1).strip()
        if not name:
            continue
        items.append({"id": slugify(name, len(items)), "name": name})
    return items


def build_cache(markdown, source_loaded_from):
    foods = parse_food_items(markdown)
    return {
        "schema_version": 1,
        "updated_at": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"),
        "source_file": SOURCE_PATH,
        "source_url": SOURCE_URL,
        "source_loaded_from": source_loaded_from,
        "synced_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "title": "生活",
        "sections": [
            {
                "id": "food-picker",
                "title": "吃啥",
                "summary": "从当前勾选的候选菜品里随机选取。",
                "defaultCount": 1,
                "items": foods,
            }
        ],
    }


def write_outputs(cache):
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(cache, ensure_ascii=False, indent=2)
    JSON_PATH.write_text(text + "\n", encoding="utf-8")
    JS_PATH.write_text(f"window.{GLOBAL_NAME} = " + text + ";\n", encoding="utf-8")


def keep_existing_outputs(reason):
    if not JSON_PATH.exists():
        return False
    cache = json.loads(JSON_PATH.read_text(encoding="utf-8-sig"))
    write_outputs(cache)
    item_count = len(cache.get("sections", [{}])[0].get("items", []))
    print(f"[warn] kept existing life food candidates: {reason}")
    print(f"[ok] synced {item_count} life food candidates")
    print(f"[ok] wrote {JS_PATH.relative_to(ROOT)}")
    return True


def main():
    markdown, source_loaded_from = load_source()
    cache = build_cache(markdown, source_loaded_from)
    write_outputs(cache)
    item_count = len(cache["sections"][0]["items"])
    print(f"[ok] synced {item_count} life food candidates")
    print(f"[ok] wrote {JSON_PATH.relative_to(ROOT)}")
    print(f"[ok] wrote {JS_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        if keep_existing_outputs("gh CLI is unavailable and local personal-wiki is unavailable"):
            sys.exit(0)
        print("[fail] gh CLI is required if local personal-wiki is unavailable", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or str(error)
        if keep_existing_outputs(f"gh api failed: {detail}"):
            sys.exit(0)
        print(f"[fail] gh api failed: {detail}", file=sys.stderr)
        sys.exit(error.returncode or 1)
    except Exception as error:
        print(f"[fail] {error}", file=sys.stderr)
        sys.exit(1)
