import argparse
import json
import os
import platform
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


def default_source_key():
    system = platform.system().lower()
    if system == "windows":
        return "codex-windows"
    if system == "darwin":
        return "codex-macos"
    if system == "linux":
        return "codex-linux"
    return "codex-local"


def default_source_label():
    key = default_source_key()
    if key == "codex-windows":
        return "Codex Windows"
    if key == "codex-macos":
        return "Codex macOS"
    if key == "codex-linux":
        return "Codex Linux"
    return "Codex local"


def parse_ts(value):
    if value is None:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).astimezone(TZ)
    except ValueError:
        return None


def parse_event_ts(value):
    if isinstance(value, (int, float)):
        seconds = float(value)
        if seconds > 10_000_000_000:
            seconds /= 1000
        try:
            return datetime.fromtimestamp(seconds, tz=timezone.utc).astimezone(TZ)
        except (OSError, OverflowError, ValueError):
            return None
    return parse_ts(value)


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
        "activeSeconds": 0,
        "completedTurns": 0,
    }


def add_usage(target, usage):
    target["inputTokens"] += to_int(usage.get("inputTokens"))
    target["outputTokens"] += to_int(usage.get("outputTokens"))
    target["cacheReadTokens"] += to_int(usage.get("cacheReadTokens"))
    target["cacheBaseTokens"] += to_int(usage.get("cacheBaseTokens"))
    target["totalTokens"] += to_int(usage.get("totalTokens"))
    target["runs"] += 1
    target["activeSeconds"] += to_int(usage.get("activeSeconds"))
    target["completedTurns"] += to_int(usage.get("completedTurns"))


def rounded_cost(value):
    return round(float(value or 0), 6)


def iter_rollout_files(state_dir):
    sessions_dir = state_dir / "sessions"
    if not sessions_dir.exists():
        return
    yield from sorted(sessions_dir.rglob("*.jsonl"))


TOKEN_FIELDS = (
    ("inputTokens", "input_tokens"),
    ("outputTokens", "output_tokens"),
    ("cacheReadTokens", "cached_input_tokens"),
    ("reasoningOutputTokens", "reasoning_output_tokens"),
    ("totalTokens", "total_tokens"),
)


def normalized_total(raw_usage):
    return {name: to_int(raw_usage.get(raw_name)) for name, raw_name in TOKEN_FIELDS}


def usage_key(usage):
    return tuple(usage[name] for name, _ in TOKEN_FIELDS)


def usage_delta(current, previous):
    return {name: current[name] - previous[name] for name, _ in TOKEN_FIELDS}


def parse_session_file(path):
    session_meta = None
    token_events = []
    completion_events = []
    last_model = DEFAULT_PRICING_MODEL

    try:
        handle = path.open(encoding="utf-8", errors="replace")
    except OSError:
        return None

    with handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            record_type = record.get("type")
            if record_type == "session_meta":
                payload = record.get("payload") or {}
                if session_meta is None:
                    session_id = payload.get("id") or payload.get("session_id") or path.stem
                    parent_id = payload.get("forked_from_id") or payload.get("parent_thread_id")
                    session_meta = {
                        "sessionId": session_id,
                        "parentId": parent_id if parent_id != session_id else None,
                        "cwd": payload.get("cwd") or "",
                        "originator": payload.get("originator") or "Codex",
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
            if payload.get("type") == "task_complete":
                duration_ms = to_int(payload.get("duration_ms"))
                completed_at = parse_event_ts(payload.get("completed_at")) or parse_ts(record.get("timestamp"))
                if duration_ms > 0 and completed_at:
                    completion_events.append(
                        {
                            "timestamp": completed_at,
                            "durationMs": duration_ms,
                            "fingerprint": json.dumps(payload, sort_keys=True, separators=(",", ":")),
                        }
                    )
                continue
            if payload.get("type") != "token_count":
                continue

            happened_at = parse_ts(record.get("timestamp"))
            if not happened_at:
                continue
            info = payload.get("info") or {}
            total_usage = info.get("total_token_usage") or {}
            if not total_usage:
                continue
            rate_limits = record.get("rate_limits") or {}
            last_model = normalize_model(rate_limits.get("limit_name") or last_model)
            token_events.append(
                {
                    "timestamp": happened_at,
                    "model": last_model,
                    "contextWindow": to_int(info.get("model_context_window")),
                    "total": normalized_total(total_usage),
                }
            )

    if session_meta is None:
        session_meta = {
            "sessionId": path.stem,
            "parentId": None,
            "cwd": "",
            "originator": "Codex",
            "modelProvider": "openai",
        }
    return {
        "meta": session_meta,
        "tokenEvents": token_events,
        "completionEvents": completion_events,
    }


def collect_runs(state_dir, source_key, source_label, since_days):
    cutoff = datetime.now(TZ) - timedelta(days=since_days)
    sessions = []
    parents = {}
    for path in iter_rollout_files(state_dir) or []:
        session = parse_session_file(path)
        if not session:
            continue
        sessions.append(session)
        meta = session["meta"]
        parents[meta["sessionId"]] = meta.get("parentId")

    def root_id(session_id):
        seen = set()
        current = session_id
        while parents.get(current) and current not in seen:
            seen.add(current)
            current = parents[current]
        return current

    seen_edges = set()
    seen_completions = set()
    runs_by_key = {}
    active_by_session = defaultdict(lambda: defaultdict(lambda: {"activeSeconds": 0, "completedTurns": 0}))
    zero_total = normalized_total({})

    for session in sessions:
        meta = session["meta"]
        session_id = meta["sessionId"]
        session_root = root_id(session_id)
        label = display_label(meta.get("cwd"), meta.get("originator"), source_label)
        previous = zero_total
        segment = 0

        for event in session["tokenEvents"]:
            current = event["total"]
            if current == previous:
                continue
            if any(current[name] < previous[name] for name, _ in TOKEN_FIELDS):
                segment += 1
                previous = zero_total
            edge_key = (session_root, segment, usage_key(previous), usage_key(current))
            delta = usage_delta(current, previous)
            previous = current
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)

            happened_at = event["timestamp"]
            if happened_at < cutoff:
                continue
            date = happened_at.strftime("%Y-%m-%d")
            run_key = (session_id, date)
            run = runs_by_key.setdefault(
                run_key,
                {
                    "date": date,
                    "timestamp": happened_at.isoformat(timespec="seconds"),
                    "source": source_key,
                    "provider": meta.get("modelProvider") or "openai",
                    "model": event["model"],
                    "openrouterModel": None,
                    "sessionId": session_id,
                    "runId": f"{session_id}:{date}",
                    "kind": "codex-session",
                    "label": label,
                    "inputTokens": 0,
                    "outputTokens": 0,
                    "cacheReadTokens": 0,
                    "cacheBaseTokens": 0,
                    "reasoningOutputTokens": 0,
                    "totalTokens": 0,
                    "pricingEstimated": True,
                    "pricingModel": event["model"],
                    "contextWindow": event["contextWindow"],
                    "tokenCountEvents": 0,
                    "activeSeconds": 0,
                    "completedTurns": 0,
                    "activeByDate": [],
                },
            )
            for name, _ in TOKEN_FIELDS:
                run[name] += delta[name]
            run["cacheBaseTokens"] = run["inputTokens"]
            run["tokenCountEvents"] += 1
            if happened_at.isoformat(timespec="seconds") >= run["timestamp"]:
                run["timestamp"] = happened_at.isoformat(timespec="seconds")
                run["model"] = event["model"]
                run["pricingModel"] = event["model"]
                run["contextWindow"] = event["contextWindow"]

        for event in session["completionEvents"]:
            completion_key = (session_root, event["fingerprint"])
            if completion_key in seen_completions:
                continue
            seen_completions.add(completion_key)
            completed_at = event["timestamp"]
            if completed_at < cutoff:
                continue
            active = active_by_session[session_id][completed_at.strftime("%Y-%m-%d")]
            active["activeSeconds"] += (event["durationMs"] + 999) // 1000
            active["completedTurns"] += 1

    runs = list(runs_by_key.values())
    for run in runs:
        run["estimatedCostUsd"] = round(estimate_cost(run, run["pricingModel"]), 8)

    for session_id, by_date in active_by_session.items():
        for date, usage in by_date.items():
            run = runs_by_key.get((session_id, date))
            if not run:
                continue
            run["activeByDate"] = [{"date": date, **usage}]
            run["activeSeconds"] = usage["activeSeconds"]
            run["completedTurns"] = usage["completedTurns"]

    return sorted(runs, key=lambda item: item["timestamp"])


def summarize_runs(runs, source_key, source_label, since_days):
    days = {}

    def day_for(date):
        return days.setdefault(
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

    for run in runs:
        day = day_for(run["date"])
        usage_run = {**run, "activeSeconds": 0, "completedTurns": 0}
        add_usage(day, usage_run)
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
        add_usage(model, usage_run)
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
        add_usage(task, usage_run)
        task["estimatedCostUsd"] += float(run.get("estimatedCostUsd") or 0)

        for active in run.get("activeByDate") or []:
            active_day = day_for(active["date"])
            if run["source"] not in active_day["sources"]:
                active_day["sources"].append(run["source"])
            active_day["activeSeconds"] += to_int(active.get("activeSeconds"))
            active_day["completedTurns"] += to_int(active.get("completedTurns"))

            active_model = active_day["byModel"].setdefault(
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
            active_model["activeSeconds"] += to_int(active.get("activeSeconds"))
            active_model["completedTurns"] += to_int(active.get("completedTurns"))

            active_task = active_day["byTask"].setdefault(
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
            active_task["activeSeconds"] += to_int(active.get("activeSeconds"))
            active_task["completedTurns"] += to_int(active.get("completedTurns"))

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
            "Codex usage is collected as per-event deltas from local session token_count events.",
            "Inherited history in forked session files is deduplicated within each session tree.",
            "Active time is the sum of completed task duration_ms values; idle time between turns is excluded.",
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
    parser.add_argument("--source-key", default=os.environ.get("MAXNOW_CODEX_SOURCE_KEY", default_source_key()))
    parser.add_argument("--source-label", default=os.environ.get("MAXNOW_CODEX_SOURCE_LABEL", default_source_label()))
    parser.add_argument("--since-days", type=int, default=3650)
    parser.add_argument("--output", default=str(ROOT / OUTPUT_REL), help="Output JSON path.")
    parser.add_argument("--missing-ok", action="store_true", default=os.environ.get("MAXNOW_CODEX_MISSING_OK") == "1")
    return parser.parse_args()


def main():
    args = parse_args()
    state_dir = Path(args.state_dir)
    output_path = Path(args.output)
    if not state_dir.exists():
        data = summarize_runs([], args.source_key, args.source_label, args.since_days)
        if not args.missing_ok:
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
