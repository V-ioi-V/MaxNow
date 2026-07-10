#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LABEL="cn.maxnow.local-codex-usage-report"
REPORT_MINUTE=0
RUN_NOW=0
NO_DEPLOY=0

usage() {
  cat <<'USAGE'
Usage: scripts/install_local_codex_usage_launchd.sh [options]

Options:
  --repo-root PATH      MaxNow repository root. Defaults to this script's parent.
  --label LABEL         launchd label. Defaults to cn.maxnow.local-codex-usage-report.
  --minute N            Fixed minute of every hour. Defaults to 0.
  --no-deploy           Deprecated no-op; server token merge runs on its own schedule.
  --run-now             Kick the launchd job once after installation.
  -h, --help            Show this help.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      REPO_ROOT="$(cd "$2" && pwd)"
      shift 2
      ;;
    --label)
      LABEL="$2"
      shift 2
      ;;
    --minute)
      REPORT_MINUTE="$2"
      shift 2
      ;;
    --no-deploy)
      NO_DEPLOY=1
      shift
      ;;
    --run-now)
      RUN_NOW=1
      shift
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

if ! [[ "$REPORT_MINUTE" =~ ^[0-9]+$ ]] || [[ "$REPORT_MINUTE" -gt 59 ]]; then
  echo "--minute must be an integer from 0 to 59" >&2
  exit 2
fi

REPORT_SCRIPT="$REPO_ROOT/scripts/report_codex_usage.sh"
if [[ ! -f "$REPORT_SCRIPT" ]]; then
  echo "report script not found: $REPORT_SCRIPT" >&2
  exit 1
fi

xml_escape() {
  local value="$1"
  value="${value//&/&amp;}"
  value="${value//</&lt;}"
  value="${value//>/&gt;}"
  value="${value//\"/&quot;}"
  value="${value//\'/&apos;}"
  printf '%s' "$value"
}

PLIST_DIR="$HOME/Library/LaunchAgents"
LOG_DIR="$HOME/Library/Logs/MaxNow"
PLIST_PATH="$PLIST_DIR/$LABEL.plist"
mkdir -p "$PLIST_DIR" "$LOG_DIR"

NO_DEPLOY_ARG=""
if [[ "$NO_DEPLOY" -eq 1 ]]; then
  NO_DEPLOY_ARG="    <string>--no-deploy</string>"
fi

cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$(xml_escape "$LABEL")</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$(xml_escape "$REPORT_SCRIPT")</string>
    <string>--repo-root</string>
    <string>$(xml_escape "$REPO_ROOT")</string>
$NO_DEPLOY_ARG
  </array>
  <key>WorkingDirectory</key>
  <string>$(xml_escape "$REPO_ROOT")</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Minute</key>
    <integer>$REPORT_MINUTE</integer>
  </dict>
  <key>RunAtLoad</key>
  <false/>
  <key>StandardOutPath</key>
  <string>$(xml_escape "$LOG_DIR/local-codex-usage-report.launchd.out.log")</string>
  <key>StandardErrorPath</key>
  <string>$(xml_escape "$LOG_DIR/local-codex-usage-report.launchd.err.log")</string>
</dict>
</plist>
PLIST

chmod 644 "$PLIST_PATH"
chmod +x "$REPORT_SCRIPT"

DOMAIN="gui/$(id -u)"
launchctl bootout "$DOMAIN" "$PLIST_PATH" >/dev/null 2>&1 || true
if launchctl bootstrap "$DOMAIN" "$PLIST_PATH"; then
  launchctl enable "$DOMAIN/$LABEL" >/dev/null 2>&1 || true
else
  launchctl unload "$PLIST_PATH" >/dev/null 2>&1 || true
  launchctl load "$PLIST_PATH"
fi

if [[ "$RUN_NOW" -eq 1 ]]; then
  launchctl kickstart -k "$DOMAIN/$LABEL" >/dev/null 2>&1 || launchctl start "$LABEL"
fi

printf "[ok] installed launchd job '%s' at minute %02d of every hour\n" "$LABEL" "$REPORT_MINUTE"
echo "[ok] plist: $PLIST_PATH"
echo "[ok] log: $LOG_DIR/local-codex-usage-report.log"
