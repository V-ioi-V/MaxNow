#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-}"
NO_PUSH=0
NO_COMMIT=0
NO_DEPLOY=0
ALLOW_DIRTY=0
LOG_PATH="${MAXNOW_CODEX_REPORT_LOG:-$HOME/Library/Logs/MaxNow/local-codex-usage-report.log}"
LOCK_DIR="${TMPDIR:-/tmp}/maxnow-local-codex-usage-report.lock"

ALLOWED_FILES=(
  "dash/data/codex-macos-usage.json"
  "dash/data/codex-macos-usage.js"
)

usage() {
  cat <<'USAGE'
Usage: scripts/report_codex_usage.sh [options]

Options:
  --repo-root PATH       MaxNow repository root. Defaults to this script's parent.
  --no-push             Commit locally but do not push.
  --no-commit           Refresh data but do not commit.
  --no-deploy           Deprecated no-op; server token merge runs on its own schedule.
  --allow-dirty         Skip unrelated dirty-file guards.
  --remote-host HOST    Deprecated no-op.
  --identity-file PATH  Deprecated no-op.
  --python PATH         Python executable. Defaults to python3, then python.
  -h, --help            Show this help.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      REPO_ROOT="$(cd "$2" && pwd)"
      shift 2
      ;;
    --no-push)
      NO_PUSH=1
      shift
      ;;
    --no-commit)
      NO_COMMIT=1
      shift
      ;;
    --no-deploy)
      NO_DEPLOY=1
      shift
      ;;
    --allow-dirty)
      ALLOW_DIRTY=1
      shift
      ;;
    --remote-host)
      shift 2
      ;;
    --identity-file)
      shift 2
      ;;
    --python)
      PYTHON_BIN="$2"
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

export PATH="/usr/local/bin:/opt/homebrew/bin:/Users/bytedance/.npm-global/bin:$PATH"

log() {
  local stamp
  stamp="$(date '+%Y-%m-%d %H:%M:%S')"
  mkdir -p "$(dirname "$LOG_PATH")"
  printf '[%s] %s\n' "$stamp" "$*" | tee -a "$LOG_PATH"
}

fail() {
  log "local Codex usage report failed: $*"
  exit 1
}

status_path() {
  local line="$1"
  local path
  if [[ ${#line} -lt 4 ]]; then
    return
  fi
  path="${line:3}"
  if [[ "$path" == *" -> "* ]]; then
    path="${path##* -> }"
  fi
  printf '%s\n' "${path//\\//}"
}

is_allowed_path() {
  local path="$1"
  local allowed
  for allowed in "${ALLOWED_FILES[@]}"; do
    if [[ "$path" == "$allowed" ]]; then
      return 0
    fi
  done
  return 1
}

dirty_paths_text() {
  local status="$1"
  local line
  local path
  while IFS= read -r line; do
    path="$(status_path "$line")"
    if [[ -n "$path" ]]; then
      printf '%s\n' "$path"
    fi
  done <<< "$status"
}

assert_clean_worktree() {
  local stage="$1"
  local status
  if [[ "$ALLOW_DIRTY" -eq 1 ]]; then
    return
  fi
  status="$(git status --porcelain)"
  if [[ -n "$status" ]]; then
    fail "$stage requires a clean worktree: $(dirty_paths_text "$status" | paste -sd ', ' -)"
  fi
}

assert_no_blocking_dirty_files() {
  local stage="$1"
  local status
  local line
  local path
  local blocking=""
  if [[ "$ALLOW_DIRTY" -eq 1 ]]; then
    return
  fi
  status="$(git status --porcelain)"
  while IFS= read -r line; do
    path="$(status_path "$line")"
    if [[ -n "$path" ]] && ! is_allowed_path "$path"; then
      if [[ -n "$blocking" ]]; then
        blocking="$blocking, $path"
      else
        blocking="$path"
      fi
    fi
  done <<< "$status"
  if [[ -n "$blocking" ]]; then
    fail "$stage has unrelated dirty files: $blocking"
  fi
}

run_step() {
  local label="$1"
  shift
  log "$label"
  "$@" > >(tee -a "$LOG_PATH") 2>&1
}

find_python() {
  if [[ -n "$PYTHON_BIN" ]]; then
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
    return
  fi
  if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python)"
    return
  fi
  fail "python3 or python not found"
}

refresh_local_usage() {
  "$PYTHON_BIN" scripts/update_data.py codex-macos-usage --source-only
}

acquire_lock() {
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    printf '%s\n' "$$" > "$LOCK_DIR/pid"
    return
  fi

  if [[ -f "$LOCK_DIR/pid" ]]; then
    local old_pid
    old_pid="$(cat "$LOCK_DIR/pid" 2>/dev/null || true)"
    if [[ -n "$old_pid" ]] && ! kill -0 "$old_pid" 2>/dev/null; then
      rm -rf "$LOCK_DIR"
      mkdir "$LOCK_DIR"
      printf '%s\n' "$$" > "$LOCK_DIR/pid"
      return
    fi
  fi

  log "skip local Codex usage report because another run is active"
  exit 0
}

release_lock() {
  if [[ -d "$LOCK_DIR" ]] && [[ "$(cat "$LOCK_DIR/pid" 2>/dev/null || true)" == "$$" ]]; then
    rm -rf "$LOCK_DIR"
  fi
}

trap release_lock EXIT

find_python
acquire_lock

cd "$REPO_ROOT"
log "local Codex usage report start"

branch="$(git branch --show-current)"
if [[ "$branch" != "main" ]]; then
  fail "expected local reporting worktree to be on main, got '$branch'"
fi

assert_clean_worktree "before refresh"

run_step "pull latest origin/main" git pull --ff-only origin main
run_step "refresh local Codex usage ledger" refresh_local_usage
run_step "run consistency check" "$PYTHON_BIN" scripts/check.py

assert_no_blocking_dirty_files "after refresh"

changed_allowed="$(git status --porcelain -- "${ALLOWED_FILES[@]}")"
if [[ -z "$changed_allowed" ]]; then
  log "no Codex usage data changes to report"
  exit 0
fi

if [[ "$NO_COMMIT" -eq 1 ]]; then
  log "skip commit because --no-commit was set; changed files: $(dirty_paths_text "$changed_allowed" | paste -sd ', ' -)"
  exit 0
fi

run_step "stage generated usage ledgers" git add -- "${ALLOWED_FILES[@]}"
log "staged: $(git diff --cached --name-only | paste -sd ', ' -)"
run_step "commit generated usage ledgers" git commit -m "Update macOS Codex token usage"

if [[ "$NO_PUSH" -eq 1 ]]; then
  log "skip push because --no-push was set"
else
  run_step "push generated usage ledgers to origin/main" git push origin HEAD:main
  if [[ "$NO_DEPLOY" -eq 1 ]]; then
    log "--no-deploy is deprecated; server token merge is scheduled independently"
  fi
fi

log "local Codex usage report ok"
