import base64
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = "V-ioi-V/personal-wiki"
REF = "main"
SOURCE_PATH = "wiki/relationships/ricky-travel.json"
SOURCE_URL = f"https://github.com/{REPO}/blob/{REF}/{SOURCE_PATH}"
LOCAL_CANDIDATES = [
    Path(os.environ["PERSONAL_WIKI_ROOT"]) if os.environ.get("PERSONAL_WIKI_ROOT") else None,
    ROOT.parent / "personal-wiki",
    Path("D:/Personal/personal-wiki"),
]
JSON_PATH = ROOT / "dash" / "data" / "ricky.json"
JS_PATH = ROOT / "dash" / "data" / "ricky.js"
GLOBAL_NAME = "MAXNOW_RICKY_DATA"


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
    return json.loads(raw.decode("utf-8-sig"))


def load_source():
    path = local_source_path()
    if path:
        return json.loads(path.read_text(encoding="utf-8-sig")), "local personal-wiki"
    return decode_content(run_gh_api()), "github"


def place_date_label(place):
    if place.get("date_status") == "needs_confirmation":
        return "待确认"
    return place.get("date") or place.get("date_start") or place.get("region") or ""


def record_date_label(record):
    if record.get("date_status") == "needs_confirmation":
        return "日期待确认"
    start = record.get("date_start") or ""
    end = record.get("date_end") or ""
    return f"{start} 至 {end}" if start and end and start != end else start or end


def build_cache(source, source_loaded_from):
    places = source.get("places") or []
    records = source.get("records") or []
    if not isinstance(places, list):
        raise ValueError("ricky-travel.json must contain a places array")
    if not isinstance(records, list):
        raise ValueError("ricky-travel.json must contain a records array")

    place_lookup = {place.get("id"): place for place in places}
    countries = {place.get("country") for place in places if place.get("country")}
    photo_count = sum(1 for item in [*places, *records] if item.get("photoUrl") or item.get("photo_url"))

    return {
        "schema_version": 1,
        "updated_at": source.get("updated_at") or "",
        "source_file": SOURCE_PATH,
        "source_url": SOURCE_URL,
        "source_loaded_from": source_loaded_from,
        "synced_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "title": "我和 Ricky",
        "subtitle": "一起走过的地方和以后还想去的地方。",
        "summary": source.get("summary") or "",
        "map": {
            "projection": "illustrative-world",
            "note": "x/y use percentage positions inside the map frame.",
        },
        "stats": [
            {"label": "地点", "value": len(places), "unit": "个"},
            {"label": "国家 / 地区", "value": len(countries), "unit": "个"},
            {"label": "记录", "value": len(records), "unit": "条"},
            {"label": "照片入口", "value": photo_count, "unit": "个"},
        ],
        "places": [
            {
                "id": place.get("id") or "",
                "name": place.get("name") or "",
                "city": place.get("name") or "",
                "country": place.get("country") or "",
                "region": place.get("region") or "",
                "lat": place.get("lat"),
                "lng": place.get("lng"),
                "x": place.get("x", 50),
                "y": place.get("y", 50),
                "date": place_date_label(place),
                "dateStatus": place.get("date_status") or "",
                "note": place.get("note") or "",
                "url": SOURCE_URL,
            }
            for place in places
        ],
        "records": [
            {
                "id": record.get("id") or "",
                "title": record.get("title") or "",
                "type": record.get("type") or "",
                "date": record_date_label(record),
                "dateStart": record.get("date_start") or "",
                "dateEnd": record.get("date_end") or "",
                "dateStatus": record.get("date_status") or "",
                "summary": record.get("summary") or "",
                "note": "；".join(record.get("details") or []),
                "places": [
                    place_lookup.get(place_id, {}).get("name", place_id)
                    for place_id in record.get("place_ids", [])
                ],
                "url": SOURCE_URL,
            }
            for record in records
        ],
    }


def write_outputs(cache):
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(cache, ensure_ascii=False, indent=2)
    JSON_PATH.write_text(text + "\n", encoding="utf-8")
    JS_PATH.write_text(f"window.{GLOBAL_NAME} = " + text + ";\n", encoding="utf-8")


def main():
    source, source_loaded_from = load_source()
    cache = build_cache(source, source_loaded_from)
    write_outputs(cache)
    print(f"[ok] synced {len(cache['places'])} Ricky places and {len(cache['records'])} records")
    print(f"[ok] wrote {JSON_PATH.relative_to(ROOT)}")
    print(f"[ok] wrote {JS_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        print("[fail] gh CLI is required if local personal-wiki is unavailable", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or str(error)
        print(f"[fail] gh api failed: {detail}", file=sys.stderr)
        sys.exit(error.returncode or 1)
    except Exception as error:
        print(f"[fail] {error}", file=sys.stderr)
        sys.exit(1)
