import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_REL = "dash/data/token-usage.json"
SOURCE_RELS = [
    "dash/data/openclaw-usage.json",
    "dash/data/codex-usage.json",
]
try:
    TZ = ZoneInfo("Asia/Shanghai")
except ZoneInfoNotFoundError:
    TZ = timezone(timedelta(hours=8), "Asia/Shanghai")


def now_text():
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M")


def read_json(rel_path):
    path = ROOT / rel_path
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def empty_usage():
    return {
        "inputTokens": 0,
        "outputTokens": 0,
        "cacheReadTokens": 0,
        "totalTokens": 0,
        "estimatedCostUsd": 0.0,
        "runs": 0,
    }


def add_usage(target, usage):
    target["inputTokens"] += int(usage.get("inputTokens") or usage.get("input") or 0)
    target["outputTokens"] += int(usage.get("outputTokens") or usage.get("output") or 0)
    target["cacheReadTokens"] += int(usage.get("cacheReadTokens") or usage.get("cacheRead") or 0)
    target["totalTokens"] += int(usage.get("totalTokens") or usage.get("total") or 0)
    target["estimatedCostUsd"] += float(usage.get("estimatedCostUsd") or usage.get("cost") or 0)
    target["runs"] += int(usage.get("runs") or 0)


def rounded_cost(value):
    return round(float(value or 0), 6)


def merge_usage_groups(existing, incoming, key_name):
    for item in incoming or []:
        key = item.get(key_name) or item.get("name") or item.get("label") or "unknown"
        current = existing.setdefault(
            key,
            {
                **item,
                **empty_usage(),
            },
        )
        add_usage(current, item)


def source_label(item):
    key = item.get("key") or item.get("source") or ""
    label = item.get("label") or key
    if key == "openclaw":
        return "OpenClaw"
    if key == "codex-local":
        return "Codex local"
    if key == "codex-server":
        return "Codex server"
    return label


def merge_ledgers(ledgers):
    days = {}
    total = empty_usage()
    sources = {}
    recent_runs = []
    pricing_snapshot = []
    warnings = []

    for ledger in ledgers:
        if not ledger:
            continue
        if ledger.get("warning"):
            warnings.append(ledger["warning"])

        for source in ledger.get("sources", []):
            key = source.get("key") or "unknown"
            current = sources.setdefault(
                key,
                {
                    "key": key,
                    "label": source_label(source),
                    **empty_usage(),
                },
            )
            add_usage(current, source)

        for day in ledger.get("days", []):
            date = day.get("date")
            if not date:
                continue
            current = days.setdefault(
                date,
                {
                    "date": date,
                    "sources": [],
                    **empty_usage(),
                    "byModel": {},
                    "byTask": {},
                    "pricingEstimated": True,
                },
            )
            add_usage(current, day)
            for source in day.get("sources", []):
                if source not in current["sources"]:
                    current["sources"].append(source)
            merge_usage_groups(current["byModel"], day.get("byModel"), "model")
            merge_usage_groups(current["byTask"], day.get("byTask"), "label")

        for run in ledger.get("recentRuns", []):
            recent_runs.append(run)
        for item in ledger.get("pricingSnapshot", []):
            if item not in pricing_snapshot:
                pricing_snapshot.append(item)

    for source in sources.values():
        source["estimatedCostUsd"] = rounded_cost(source["estimatedCostUsd"])
        add_usage(total, source)
    total["estimatedCostUsd"] = rounded_cost(total["estimatedCostUsd"])
    total["runs"] = sum(int(source.get("runs", 0)) for source in sources.values())

    day_list = []
    for day in sorted(days.values(), key=lambda item: item["date"], reverse=True):
        day["estimatedCostUsd"] = rounded_cost(day["estimatedCostUsd"])
        day["byModel"] = sorted(day["byModel"].values(), key=lambda item: item["totalTokens"], reverse=True)
        day["byTask"] = sorted(day["byTask"].values(), key=lambda item: item["totalTokens"], reverse=True)
        for group in [*day["byModel"], *day["byTask"]]:
            group["estimatedCostUsd"] = rounded_cost(group["estimatedCostUsd"])
        day_list.append(day)

    recent_runs = sorted(recent_runs, key=lambda item: item.get("timestamp") or item.get("date") or "", reverse=True)

    return {
        "updatedAt": now_text(),
        "timezone": "Asia/Shanghai",
        "currency": "USD",
        "pricingBasis": "mixed",
        "pricingSource": "openclaw-openrouter-equivalent-and-codex-openai-api-equivalent",
        "pricingStale": any(ledger.get("pricingStale") for ledger in ledgers if ledger),
        "summary": total,
        "sources": sorted(sources.values(), key=lambda item: item["totalTokens"], reverse=True),
        "days": day_list,
        "recentRuns": recent_runs[:30],
        "pricingSnapshot": pricing_snapshot,
        "notes": [
            "OpenClaw cost is OpenRouter-equivalent estimation.",
            "Codex cost is OpenAI API-equivalent estimation from session token_count events.",
        ],
        "warnings": warnings,
    }


def write_output(data):
    path = ROOT / OUTPUT_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[ok] wrote {OUTPUT_REL}")


def main():
    ledgers = [read_json(rel_path) for rel_path in SOURCE_RELS]
    write_output(merge_ledgers(ledgers))


if __name__ == "__main__":
    main()
