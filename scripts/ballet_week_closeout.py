from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
TIMEZONE = timezone(timedelta(hours=8), "Asia/Shanghai")
DEFAULT_MODEL = ROOT / "dash" / "data" / "ballet.json"
DEFAULT_STATE = Path("/var/lib/maxnow-ballet-week-closeout/state.json")
SYNC_UNIT = "maxnow-ballet-sync.service"
MAX_ATTEMPTS_PER_CYCLE = 3
RETRY_INTERVAL_MINUTES = 5


def parse_iso(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=TIMEZONE)
    return parsed.astimezone(TIMEZONE)


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return dict(default)
    return payload if isinstance(payload, dict) else dict(default)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def current_cycle(model: dict[str, Any], now: datetime) -> dict[str, Any] | None:
    today = now.astimezone(TIMEZONE).date().isoformat()
    cycles = (model.get("weeklyBrief") or {}).get("cycles") or []
    matches = [
        cycle
        for cycle in cycles
        if isinstance(cycle, dict)
        and str(cycle.get("weekStart") or "") <= today <= str(cycle.get("weekEnd") or "")
    ]
    return matches[-1] if matches else None


def evaluate_closeout(
    model: dict[str, Any],
    state: dict[str, Any],
    now: datetime,
) -> dict[str, Any]:
    cycle = current_cycle(model, now)
    if not cycle:
        return {"action": "none", "reason": "no_current_cycle"}
    refresh_at = parse_iso(cycle.get("refreshAt"))
    last_course_end = parse_iso(cycle.get("lastCourseEndAt"))
    if refresh_at is None or last_course_end is None:
        return {"action": "none", "reason": "invalid_cycle"}
    cycle_key = f"{cycle.get('weekStart')}|{cycle.get('lastCourseEndAt')}"
    cycle_state = state if state.get("cycleKey") == cycle_key else {}
    source_as_of = parse_iso(model.get("dataAsOf") or (model.get("sync") or {}).get("lastSuccessAt"))
    base = {
        "cycleKey": cycle_key,
        "weekStart": cycle.get("weekStart"),
        "lastCourseEndAt": cycle.get("lastCourseEndAt"),
        "refreshAt": cycle.get("refreshAt"),
    }
    if now.astimezone(TIMEZONE) < refresh_at:
        return {**base, "action": "none", "reason": "not_due"}
    if source_as_of is not None and source_as_of >= refresh_at:
        return {**base, "action": "complete", "reason": "already_refreshed"}
    sync = model.get("sync") or {}
    auth = model.get("authHealth") or {}
    if auth.get("status") == "needs_login" or sync.get("lastAttemptStatus") == "auth_required":
        return {**base, "action": "none", "reason": "auth_required"}
    attempts = int(cycle_state.get("attempts") or 0)
    if attempts >= MAX_ATTEMPTS_PER_CYCLE:
        return {**base, "action": "none", "reason": "attempt_limit", "attempts": attempts}
    last_attempt = parse_iso(cycle_state.get("lastAttemptAt"))
    if last_attempt and now.astimezone(TIMEZONE) < last_attempt + timedelta(minutes=RETRY_INTERVAL_MINUTES):
        return {**base, "action": "none", "reason": "retry_wait", "attempts": attempts}
    return {**base, "action": "refresh", "reason": "closeout_due", "attempts": attempts}


def safe_result(result: dict[str, Any], now: datetime) -> dict[str, Any]:
    return {
        "status": result.get("reason"),
        "action": result.get("action"),
        "weekStart": result.get("weekStart"),
        "lastCourseEndAt": result.get("lastCourseEndAt"),
        "refreshAt": result.get("refreshAt"),
        "checkedAt": now.astimezone(TIMEZONE).isoformat(timespec="seconds"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh the safe Ballet read model after a weekly cycle closes.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--now")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)
    now = parse_iso(args.now) if args.now else datetime.now(TIMEZONE)
    if now is None:
        parser.error("--now must be an ISO-8601 timestamp")
    model = load_json(args.model, {})
    state = load_json(args.state, {})
    decision = evaluate_closeout(model, state, now)
    if decision.get("action") != "refresh" or args.check_only:
        print(json.dumps(safe_result(decision, now), ensure_ascii=False))
        return 0

    next_state = {
        "schemaVersion": 1,
        "cycleKey": decision["cycleKey"],
        "attempts": int(decision.get("attempts") or 0) + 1,
        "lastAttemptAt": now.astimezone(TIMEZONE).isoformat(timespec="seconds"),
        "lastResult": "started",
    }
    write_json(args.state, next_state)
    completed = subprocess.run(
        ["/usr/bin/systemctl", "start", "--wait", SYNC_UNIT],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=240,
        check=False,
    )
    refreshed_model = load_json(args.model, {})
    refreshed = evaluate_closeout(refreshed_model, next_state, datetime.now(TIMEZONE))
    success = refreshed.get("reason") == "already_refreshed"
    next_state["lastResult"] = "success" if success else f"sync_exit_{completed.returncode}"
    write_json(args.state, next_state)
    result = safe_result(refreshed if success else decision, datetime.now(TIMEZONE))
    result["status"] = "refreshed" if success else "refresh_failed"
    print(json.dumps(result, ensure_ascii=False))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
