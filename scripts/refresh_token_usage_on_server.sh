#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_PATH=""
SKIP_PULL=0
GIT_PULL_TIMEOUT_SECONDS="${GIT_PULL_TIMEOUT_SECONDS:-120}"

usage() {
  cat <<'USAGE'
Usage: scripts/refresh_token_usage_on_server.sh [options]

Options:
  --repo-root PATH  MaxNow server repository root. Defaults to this script's parent.
  --log PATH        Optional log path. Cron usually redirects stdout/stderr instead.
  --skip-pull       Merge current local ledgers without pulling origin/main first.
  --pull-timeout N   Seconds before aborting git pull. Defaults to 120.
  -h, --help        Show this help.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      REPO_ROOT="$(cd "$2" && pwd)"
      shift 2
      ;;
    --log)
      LOG_PATH="$2"
      shift 2
      ;;
    --skip-pull)
      SKIP_PULL=1
      shift
      ;;
    --pull-timeout)
      GIT_PULL_TIMEOUT_SECONDS="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

log() {
  local stamp
  stamp="$(date -Is)"
  if [[ -n "$LOG_PATH" ]]; then
    mkdir -p "$(dirname "$LOG_PATH")"
    printf '[%s] %s\n' "$stamp" "$*" | tee -a "$LOG_PATH"
  else
    printf '[%s] %s\n' "$stamp" "$*"
  fi
}

pull_origin_main() {
  log "pull latest origin/main"
  if command -v timeout >/dev/null 2>&1; then
    timeout "${GIT_PULL_TIMEOUT_SECONDS}s" git pull --ff-only origin main
  else
    git pull --ff-only origin main
  fi
}

usage_units() {
  python3 - "$1" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    print(0)
    raise SystemExit
summary = data.get("summary") if isinstance(data, dict) else {}
if not isinstance(summary, dict):
    summary = {}
total = int(summary.get("totalTokens") or data.get("totalTokens") or 0)
runs = int(summary.get("runs") or data.get("runs") or 0)
print(total + runs)
PY
}

restore_runtime_pair() {
  local name="$1"
  local backup_json="$BACKUP_DIR/$name.json"
  local backup_js="$BACKUP_DIR/$name.js"
  local target_json="dash/data/$name.json"
  local target_js="dash/data/$name.js"
  local backup_units
  local target_units

  if [[ ! -f "$backup_json" ]]; then
    return
  fi

  backup_units="$(usage_units "$backup_json")"
  target_units="$(usage_units "$target_json")"
  if [[ "$backup_units" -gt 0 || "$target_units" -eq 0 ]]; then
    cp -a "$backup_json" "$target_json"
    if [[ -f "$backup_js" ]]; then
      cp -a "$backup_js" "$target_js"
    fi
    log "restored $name from server runtime backup"
  else
    log "skipped empty $name backup because current ledger has usage"
  fi
}

refresh_openclaw_if_empty() {
  local openclaw_units
  openclaw_units="$(usage_units dash/data/openclaw-usage.json)"
  if [[ "$openclaw_units" -gt 0 ]]; then
    return
  fi
  if ! sudo -n test -d /root/.openclaw 2>/dev/null; then
    log "OpenClaw ledger is empty and /root/.openclaw is not readable via sudo"
    return
  fi

  log "OpenClaw ledger is empty; refreshing it with root OpenClaw state"
  sudo -n python3 scripts/update_data.py openclaw-usage
  sudo -n chown ubuntu:www-data \
    dash/data/openclaw-usage.json \
    dash/data/openclaw-usage.js \
    dash/data/token-usage.json \
    dash/data/token-usage.js \
    logs/openclaw-usage.log \
    logs/token-usage.log 2>/dev/null || true
}

cd "$REPO_ROOT"
mkdir -p logs
log "token usage server refresh start"

BACKUP_ROOT="/tmp/maxnow-token-usage-refresh"
BACKUP_DIR="$BACKUP_ROOT/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -a dash/data/openclaw-usage.json "$BACKUP_DIR/openclaw-usage.json" 2>/dev/null || true
cp -a dash/data/openclaw-usage.js "$BACKUP_DIR/openclaw-usage.js" 2>/dev/null || true
cp -a dash/data/codex-server-usage.json "$BACKUP_DIR/codex-server-usage.json" 2>/dev/null || true
cp -a dash/data/codex-server-usage.js "$BACKUP_DIR/codex-server-usage.js" 2>/dev/null || true
ln -sfn "$BACKUP_DIR" "$BACKUP_ROOT/latest" 2>/dev/null || true

if [[ "$SKIP_PULL" -eq 0 ]]; then
  git stash push -m before-token-usage-refresh -- \
    dash/data/openclaw-usage.json \
    dash/data/openclaw-usage.js \
    dash/data/codex-usage.json \
    dash/data/codex-usage.js \
    dash/data/codex-macos-usage.json \
    dash/data/codex-macos-usage.js \
    dash/data/codex-server-usage.json \
    dash/data/codex-server-usage.js \
    dash/data/token-usage.json \
    dash/data/token-usage.js \
    dash/data/project-meta.json \
    dash/data/project-meta.js >/dev/null 2>&1 || true
  pull_origin_main
fi

restore_runtime_pair openclaw-usage
restore_runtime_pair codex-server-usage
refresh_openclaw_if_empty
python3 scripts/update_data.py token-usage
python3 scripts/check.py

if command -v chown >/dev/null 2>&1; then
  sudo -n chown ubuntu:www-data \
    dash/data/openclaw-usage.json \
    dash/data/openclaw-usage.js \
    dash/data/codex-server-usage.json \
    dash/data/codex-server-usage.js \
    dash/data/token-usage.json \
    dash/data/token-usage.js \
    logs/token-usage.log 2>/dev/null || true
fi

log "token usage server refresh ok"
