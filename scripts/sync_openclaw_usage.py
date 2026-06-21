import argparse
import json
import os
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_DIR = Path("/root/.openclaw")
OUTPUT_REL = "dash/data/openclaw-usage.json"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
try:
    TZ = ZoneInfo("Asia/Shanghai")
except ZoneInfoNotFoundError:
    TZ = timezone(timedelta(hours=8), "Asia/Shanghai")

BUILTIN_OPENROUTER_IDS = {
    "deepseek-v4-flash": "deepseek/deepseek-v4-flash",
    "deepseek-v4-pro": "deepseek/deepseek-v4-pro",
}

FALLBACK_PRICING = {
    "deepseek/deepseek-v4-flash": {
        "prompt": "0.00000009",
        "completion": "0.00000018",
        "input_cache_read": "0.00000002",
    },
    "deepseek/deepseek-v4-pro": {
        "prompt": "0.000000435",
        "completion": "0.00000087",
        "input_cache_read": "0.000000003625",
    },
}


def now_text():
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M")


def parse_ts(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).astimezone(TZ)
    if isinstance(value, str):
        text = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(text).astimezone(TZ)
        except ValueError:
            return None
    return None


def read_json(path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def load_existing_output(output_path=None):
    return read_json(output_path or (ROOT / OUTPUT_REL), {}) or {}


def openrouter_id(model):
    if not model:
        return None
    normalized = str(model).strip()
    lowered = normalized.lower()
    if "/" in normalized:
        return normalized
    return BUILTIN_OPENROUTER_IDS.get(lowered)


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def load_pricing(disable_network=False, output_path=None):
    existing = load_existing_output(output_path)
    cached = {
        item.get("openrouterModel"): item.get("pricing", {})
        for item in existing.get("pricingSnapshot", [])
        if item.get("openrouterModel")
    }
    source = "cache"
    stale = True

    pricing = {**FALLBACK_PRICING, **cached}
    if disable_network:
        return pricing, source, stale

    try:
        with urllib.request.urlopen(OPENROUTER_MODELS_URL, timeout=12) as response:
            models = json.load(response).get("data", [])
        pricing = {
            item["id"]: item.get("pricing", {})
            for item in models
            if item.get("id") and item.get("pricing")
        }
        source = "openrouter-api"
        stale = False
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        pass

    return pricing, source, stale


def estimate_cost(usage, pricing):
    prompt = to_float(pricing.get("prompt"))
    completion = to_float(pricing.get("completion"))
    cache_read = to_float(pricing.get("input_cache_read"))
    if not any([prompt, completion, cache_read]):
        return None
    return (
        usage.get("inputTokens", 0) * prompt
        + usage.get("outputTokens", 0) * completion
        + usage.get("cacheReadTokens", 0) * cache_read
    )


def empty_usage():
    return {
        "inputTokens": 0,
        "outputTokens": 0,
        "cacheReadTokens": 0,
        "totalTokens": 0,
        "estimatedCostUsd": 0.0,
        "runs": 0,
    }


def add_usage(target, usage, estimated_cost):
    target["inputTokens"] += int(usage.get("inputTokens", 0))
    target["outputTokens"] += int(usage.get("outputTokens", 0))
    target["cacheReadTokens"] += int(usage.get("cacheReadTokens", 0))
    target["totalTokens"] += int(usage.get("totalTokens", 0))
    target["runs"] += 1
    if estimated_cost is not None:
        target["estimatedCostUsd"] += estimated_cost


def extract_usage(data):
    usage = data.get("usage") if isinstance(data, dict) else None
    if not isinstance(usage, dict):
        return None
    return {
        "inputTokens": int(usage.get("input") or usage.get("prompt") or 0),
        "outputTokens": int(usage.get("output") or usage.get("completion") or 0),
        "cacheReadTokens": int(usage.get("cacheRead") or usage.get("cached") or 0),
        "totalTokens": int(usage.get("total") or 0),
    }


def task_kind(session_key):
    key = session_key or ""
    if ":cron:" in key:
        return "cron"
    if "openclaw-weixin" in key:
        return "weixin"
    if ":subagent:" in key:
        return "subagent"
    if ":direct:" in key:
        return "direct"
    return "agent"


def task_label(session_key, cron_labels):
    key = session_key or ""
    if ":cron:" in key:
        job_id = key.split(":cron:", 1)[1].split(":", 1)[0]
        return cron_labels.get(job_id) or f"Cron {job_id[:8]}"
    if "openclaw-weixin" in key:
        return "WeChat direct"
    if ":subagent:" in key:
        return "Subagent"
    return "OpenClaw session"


def load_cron_labels(state_dir):
    labels = {}
    sessions = read_json(state_dir / "agents/main/sessions/sessions.json", {}) or {}
    for key, item in sessions.items():
        if not isinstance(item, dict) or ":cron:" not in key:
            continue
        job_id = key.split(":cron:", 1)[1].split(":", 1)[0]
        if item.get("label"):
            labels[job_id] = item["label"].replace("Cron: ", "")
    return labels


def iter_trajectory_records(state_dir):
    session_dir = state_dir / "agents/main/sessions"
    for path in sorted(session_dir.glob("*.trajectory.jsonl")):
        try:
            with path.open(encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    try:
                        yield path, json.loads(line)
                    except json.JSONDecodeError:
                        continue
        except OSError:
            continue


def collect_runs(state_dir, since_days, pricing):
    cutoff = datetime.now(TZ) - timedelta(days=since_days)
    cron_labels = load_cron_labels(state_dir)
    primary = []
    artifacts = {}

    for path, record in iter_trajectory_records(state_dir):
        record_type = record.get("type")
        if record_type not in {"model.completed", "trace.artifacts"}:
            continue
        happened_at = parse_ts(record.get("ts"))
        if not happened_at or happened_at < cutoff:
            continue
        usage = extract_usage(record.get("data") or {})
        if not usage:
            continue

        run_id = record.get("runId") or record.get("sessionId") or path.stem
        session_key = record.get("sessionKey") or ""
        item = {
            "date": happened_at.strftime("%Y-%m-%d"),
            "timestamp": happened_at.isoformat(timespec="seconds"),
            "source": "openclaw",
            "provider": record.get("provider") or "",
            "model": record.get("modelId") or "",
            "openrouterModel": openrouter_id(record.get("modelId")),
            "sessionId": record.get("sessionId") or "",
            "runId": run_id,
            "kind": task_kind(session_key),
            "label": task_label(session_key, cron_labels),
            **usage,
        }
        model_pricing = pricing.get(item["openrouterModel"] or "", {})
        estimated_cost = estimate_cost(item, model_pricing)
        item["estimatedCostUsd"] = round(estimated_cost, 8) if estimated_cost is not None else None
        item["pricingEstimated"] = estimated_cost is not None

        if record_type == "model.completed":
            primary.append(item)
        else:
            artifacts.setdefault(run_id, item)

    primary_keys = {item["runId"] for item in primary}
    fallback = [item for run_id, item in artifacts.items() if run_id not in primary_keys]
    return sorted(primary + fallback, key=lambda item: item["timestamp"])


def rounded_cost(value):
    return round(float(value or 0), 6)


def summarize_runs(runs, pricing, pricing_source, pricing_stale, since_days):
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
        cost = run["estimatedCostUsd"]
        add_usage(day, run, cost)
        if "openclaw" not in day["sources"]:
            day["sources"].append("openclaw")

        model_key = run["model"] or "unknown"
        model = day["byModel"].setdefault(
            model_key,
            {
                "model": model_key,
                "provider": run["provider"],
                "openrouterModel": run["openrouterModel"],
                **empty_usage(),
                "pricingEstimated": True,
            },
        )
        add_usage(model, run, cost)

        task_key = f"{run['kind']}:{run['label']}:{model_key}"
        task = day["byTask"].setdefault(
            task_key,
            {
                "kind": run["kind"],
                "label": run["label"],
                "model": model_key,
                **empty_usage(),
                "pricingEstimated": True,
            },
        )
        add_usage(task, run, cost)

    day_list = []
    for day in sorted(days.values(), key=lambda item: item["date"], reverse=True):
        day["estimatedCostUsd"] = rounded_cost(day["estimatedCostUsd"])
        day["byModel"] = sorted(day["byModel"].values(), key=lambda item: item["totalTokens"], reverse=True)
        day["byTask"] = sorted(day["byTask"].values(), key=lambda item: item["totalTokens"], reverse=True)
        for group in [*day["byModel"], *day["byTask"]]:
            group["estimatedCostUsd"] = rounded_cost(group["estimatedCostUsd"])
        day_list.append(day)

    total = empty_usage()
    by_source = {"openclaw": empty_usage()}
    for run in runs:
        add_usage(total, run, run["estimatedCostUsd"])
        add_usage(by_source["openclaw"], run, run["estimatedCostUsd"])
    total["estimatedCostUsd"] = rounded_cost(total["estimatedCostUsd"])
    by_source["openclaw"]["estimatedCostUsd"] = rounded_cost(by_source["openclaw"]["estimatedCostUsd"])

    used_models = sorted({run["openrouterModel"] for run in runs if run.get("openrouterModel")})
    pricing_snapshot = [
        {
            "openrouterModel": model,
            "pricing": pricing.get(model, {}),
        }
        for model in used_models
    ]

    return {
        "updatedAt": now_text(),
        "timezone": "Asia/Shanghai",
        "currency": "USD",
        "pricingBasis": "openrouter-equivalent",
        "pricingSource": pricing_source,
        "pricingStale": pricing_stale,
        "sinceDays": since_days,
        "summary": total,
        "sources": [
            {
                "key": "openclaw",
                "label": "OpenClaw",
                **by_source["openclaw"],
            }
        ],
        "days": day_list,
        "recentRuns": list(reversed(runs[-30:])),
        "pricingSnapshot": pricing_snapshot,
        "futureSources": [
            {
                "key": "codex",
                "label": "Codex",
                "status": "planned",
                "note": "Reserved for local and server Codex usage collectors.",
            }
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
    parser = argparse.ArgumentParser(description="Sync OpenClaw usage into MaxNow token ledger data.")
    parser.add_argument("--state-dir", default=os.environ.get("OPENCLAW_STATE_DIR", str(DEFAULT_STATE_DIR)))
    parser.add_argument("--since-days", type=int, default=3650)
    parser.add_argument("--no-network", action="store_true", help="Do not fetch OpenRouter model prices.")
    parser.add_argument("--output", default=str(ROOT / OUTPUT_REL), help="Output JSON path.")
    return parser.parse_args()


def main():
    args = parse_args()
    state_dir = Path(args.state_dir)
    output_path = Path(args.output)
    pricing, pricing_source, pricing_stale = load_pricing(args.no_network, output_path)

    if not state_dir.exists():
        data = summarize_runs([], pricing, pricing_source, pricing_stale, args.since_days)
        data["warning"] = f"OpenClaw state directory not found: {state_dir}"
        write_output(data, output_path)
        return

    runs = collect_runs(state_dir, args.since_days, pricing)
    data = summarize_runs(runs, pricing, pricing_source, pricing_stale, args.since_days)
    data["sourcePath"] = str(state_dir)
    write_output(data, output_path)
    print(f"[ok] collected {len(runs)} OpenClaw usage runs")


if __name__ == "__main__":
    main()
