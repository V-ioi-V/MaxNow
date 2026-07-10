#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "refresh_token_sources_on_server.sh must run as root" >&2
  exit 1
fi

cd "$REPO_ROOT"
mkdir -p logs
echo "[$(date -Is)] token source refresh start"
python3 scripts/update_data.py openclaw-usage --source-only
python3 scripts/update_data.py codex-server-usage --source-only
python3 scripts/check.py
chown ubuntu:www-data \
  dash/data/openclaw-usage.json \
  dash/data/openclaw-usage.js \
  dash/data/codex-server-usage.json \
  dash/data/codex-server-usage.js \
  logs/openclaw-usage.log \
  logs/codex-server-usage.log 2>/dev/null || true
echo "[$(date -Is)] token source refresh ok"
