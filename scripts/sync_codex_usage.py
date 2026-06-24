import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_DIR = Path.home() / ".codex"
OUTPUT_REL = "dash/data/codex-usage.json"
PRICING_SOURCE = "openai-api-pricing"
DEFAULT_PRICING_MODEL = "gpt-5.5"
MODEL_PRICING = {
    "gpt-5.5": {
        "input": 5.00,
        "cachedInput": 0.50,
        "output": 30.00,
    },
    "gpt-5.4": {
        "input": 2.50,
        "cachedInput": 0.25,
        "output": 15.00,
    },
    "gpt-5.4-mini": {
        "input": 0.75,
        "cachedInput": 0.075,
        "output": 4.50,
    },
}
try:
    TZ = ZoneInfo("Asia/Shanghai")
except ZoneInfoNotFoundError:
    TZ = timezone(timedelta(hours=8), "Asia/Shanghai")


def now_text():
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M")


def parse_ts(value):
    if value is None:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).astimezone(TZ)
    except ValueError:
        return None


def to_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def display_label(cwd, originator, source_label):
    if cwd:
        normalized = str(cwd).rstrip("\\/")
        parts = [part for part in normalized.replace("\\", "/").split("/") if part]
        if parts:
            return parts[-1]
    return originator or source_label


def normalize_model(value):
    text = str(value or "").strip()
    lowered = text.lower()
    if "gpt-5.4" in lowered and "mini" in lowered:
        return "gpt-5.4-mini"
    if "gpt-5.5" in lowered:
        return "gpt-5.5"
    if "gpt-5.4" in lowered:
        return "gpt-5.4"
    return DEFAULT_PRICING_MODEL


def estimate_cost(usage, pricing_model):
    pricing = MODEL_PRICING.get(pricing_model)
    if not pricing:
        return 0.0
    input_tokens = to_int(usage.get("inputTokens"))
    cache_tokens = min(to_int(usage.get("cacheReadTokens")), input_tokens)
    uncached_input = max(input_tokens - cache_tokens, 0)
    output_tokens = to_int(usage.get("outputTokens"))
    return (
        (uncached_input / 1_000_000) * pricing["input"]
        + (cache_tokens / 1_000_000) * pricing["cachedInput"]
        + (output_tokens / 1_000_000) * pricing["output"]
    )


def empty_usage():
    return {
        "inputTokens": 0,
        "outputTokens": 0,
        "cacheReadTokens": 0,
        "cacheBaseTokens": 0,
        "totalTokens": 0,
        "estimatedCostUsd": 0.0,
        "runs": 0,
    }


def add_usage(target, usage):
    target["inputTokens"] += to_int(usage.get("inputTokens"))
    target["outputTokens"] += to_int(usage.get("outputTokens"))
    target["cacheReadTokens"] += to_int(usage.get("cacheReadTokens"))
    target["cacheBaseTokens"] += to_int(usage.get("cacheBaseTokens"))
    target["totalTokens"] += to_int(usage.get("totalTokens"))
    target["runs"] += 1


def rounded_cost(value):
    return round(float(value or 0), 6)


def iter_rollout_files(state_dir):
    sessions_dir = state_dir / "sessions"
    if not sessions_dir.exists():
        return
    yield from sorted(sessions_dir.rglob("*.jsonl"))


def load_session_usage(path, source_key, source_label, cutoff):
    session_meta = {}
    event_count = 0
    final_total = None
    last_timestamp = None
    last_model = DEFAULT_PRICING_MODEL
    last_context_window = 0

    try:
        handle = path.open(encoding="utf-8", errors="replace")
    except OSError:
        return []

    with handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            record_type = record.get("type")
            if record_type == "session_meta":
                payload = record.get("payload") or {}
                session_meta = {
                    "sessionId": payload.get("session_id") or payload.get("id") or path.stem,
                    "cwd": payload.get("cwd") or "",
                    "originator": payload.get("originator") or "Codex",
                    "source": payload.get("source") or "",
                    "modelProvider": payload.get("model_provider") or "openai",
                }
                continue
            if record_type == "turn_context":
                turn_model = (record.get("payload") or {}).get("model")
                if turn_model:
                    last_model = normalize_model(turn_model)
                continue

            if record_type != "event_msg":
                continue
            payload = record.get("payload") or {}
            if payload.get("type") != "token_count":
                continue

            happened_at = parse_ts(record.get("timestamp"))
            if not happened_at or happened_at < cutoff:
                continue
            info = payload.get("info") or {}
            total_usage = info.get("total_token_usage") or {}
            if not total_usage:
                continue
            event_count += 1
            final_total = total_usage
            last_timestamp = happened_at
            rate_limits = record.get("rate_limits") or {}
            last_model = normalize_model(rate_limits.get("limit_name") or last_model)
            last_context_window = to_int(info.get("model_context_window"))

    if not final_total or not last_timestamp:
        return []

    session_id = session_meta.get("sessionId") or path.stem
    label = display_label(session_meta.get("cwd"), session_meta.get("originator"), source_label)
    item = {
        "date": last_timestamp.strftime("%Y-%m-%d"),
        "timestamp": last_timestamp.isoformat(timespec="seconds"),
        "source": source_key,
        "provider": session_meta.get("modelProvider") or "openai",
        "model": last_model,
        "openrouterModel": None,
        "sessionId": session_id,
        "runId": session_id,
        "kind": "codex-session",
        "label": label,
        "inputTokens": to_int(final_total.get("input_tokens")),
        "outputTokens": to_int(final_total.get("output_tokens")),
        "cacheReadTokens": to_int(final_total.get("cached_input_tokens")),
        "cacheBaseTokens": to_int(final_total.get("input_tokens")),
        "reasoningOutputTokens": to_int(final_total.get("reasoning_output_tokens")),
        "totalTokens": to_int(final_total.get("total_tokens")),
        "pricingEstimated": True,
        "pricingModel": last_model,
        "contextWindow": last_context_window,
        "tokenCountEvents": event_count,
    }
    item["estimatedCostUsd"] = round(estimate_cost(item, last_model), 8)
    return [item]


def collect_runs(state_dir, source_key, source_label, since_days):
    cutoff = datetime.now(TZ) - timedelta(days=since_days)
    runs = []
    for path in iter_rollout_files(state_dir) or []:
        runs.extend(load_session_usage(path, source_key, source_label, cutoff))
    return sorted(runs, key=lambda item: item["timestamp"])


def summarize_runs(runs, source_key, source_label, since_days):
    days = {}
    for run in runs:
        day = days.setdefault(
            run["date"],
            {
                "date": run["date"],
                "sources": [],
                **empty_usage(),
                "byModel": {},
                "byTask": {},
                "pricingEstimated": True,
            },
        )
        add_usage(day, run)
        day["estimatedCostUsd"] += float(run.get("estimatedCostUsd") or 0)
        if run["source"] not in day["sources"]:
            day["sources"].append(run["source"])

        model_key = run["model"] or "Codex"
        model = day["byModel"].setdefault(
            model_key,
            {
                "model": model_key,
                "provider": run["provider"],
                "openrouterModel": run["openrouterModel"],
                **empty_usage(),
                "pricingEstimated": True,
                "pricingModel": run.get("pricingModel") or run["model"],
            },
        )
        add_usage(model, run)
        model["estimatedCostUsd"] += float(run.get("estimatedCostUsd") or 0)

        task_key = f"{run['kind']}:{run['label']}:{model_key}"
        task = day["byTask"].setdefault(
            task_key,
            {
                "kind": run["kind"],
                "label": run["label"],
                "model": model_key,
                **empty_usage(),
                "pricingEstimated": True,
                "pricingModel": run.get("pricingModel") or model_key,
            },
        )
        add_usage(task, run)
        task["estimatedCostUsd"] += float(run.get("estimatedCostUsd") or 0)

    day_list = []
    for day in sorted(days.values(), key=lambda item: item["date"], reverse=True):
        day["estimatedCostUsd"] = rounded_cost(day["estimatedCostUsd"])
        day["byModel"] = sorted(day["byModel"].values(), key=lambda item: item["totalTokens"], reverse=True)
        day["byTask"] = sorted(day["byTask"].values(), key=lambda item: item["totalTokens"], reverse=True)
        for group in [*day["byModel"], *day["byTask"]]:
            group["estimatedCostUsd"] = rounded_cost(group["estimatedCostUsd"])
        day_list.append(day)

    total = empty_usage()
    by_source = defaultdict(empty_usage)
    for run in runs:
        add_usage(total, run)
        add_usage(by_source[run["source"]], run)
        cost = float(run.get("estimatedCostUsd") or 0)
        total["estimatedCostUsd"] += cost
        by_source[run["source"]]["estimatedCostUsd"] += cost
    total["estimatedCostUsd"] = rounded_cost(total["estimatedCostUsd"])

    sources = []
    for key, usage in sorted(by_source.items()):
        usage["estimatedCostUsd"] = rounded_cost(usage["estimatedCostUsd"])
        sources.append(
            {
                "key": key,
                "label": source_label if key == source_key else key,
                **usage,
            }
        )

    return {
        "updatedAt": now_text(),
        "timezone": "Asia/Shanghai",
        "currency": "USD",
        "pricingBasis": "openai-api-equivalent",
        "pricingSource": PRICING_SOURCE,
        "pricingStale": False,
        "sinceDays": since_days,
        "summary": total,
        "sources": sources,
        "days": day_list,
        "recentRuns": list(reversed(runs[-30:])),
        "pricingSnapshot": [
            {
                "model": model,
                "pricing": pricing,
            }
            for model, pricing in sorted(MODEL_PRICING.items())
        ],
        "notes": [
            "Codex usage is collected from local session token_count events.",
            "No prompt or response body is exported into this ledger.",
            "estimatedCostUsd is an OpenAI API-equivalent estimate, not an actual Codex subscription bill.",
        ],
    }


def write_output(data, output_path=None):
    path = output_path or (ROOT / OUTPUT_REL)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        display = path.relative_to(ROOT)
    except ValueError:
        display = path
    print(f"[ok] wrote {display}")


def parse_args():
    parser = argparse.ArgumentParser(description="Sync Codex usage into MaxNow token ledger data.")
    parser.add_argument("--state-dir", default=os.environ.get("CODEX_STATE_DIR", str(DEFAULT_STATE_DIR)))
    parser.add_argument("--source-key", default=os.environ.get("MAXNOW_CODEX_SOURCE_KEY", "codex-local"))
    parser.add_argument("--source-label", default=os.environ.get("MAXNOW_CODEX_SOURCE_LABEL", "Codex local"))
    parser.add_argument("--since-days", type=int, default=3650)
    parser.add_argument("--output", default=str(ROOT / OUTPUT_REL), help="Output JSON path.")
    return parser.parse_args()


def main():
    args = parse_args()
    state_dir = Path(args.state_dir)
    output_path = Path(args.output)
    if not state_dir.exists():
        data = summarize_runs([], args.source_key, args.source_label, args.since_days)
        data["warning"] = f"Codex state directory not found: {state_dir}"
        write_output(data, output_path)
        return

    runs = collect_runs(state_dir, args.source_key, args.source_label, args.since_days)
    data = summarize_runs(runs, args.source_key, args.source_label, args.since_days)
    data["sourcePath"] = str(state_dir)
    write_output(data, output_path)
    print(f"[ok] collected {len(runs)} Codex usage sessions")


if __name__ == "__main__":
    main()
