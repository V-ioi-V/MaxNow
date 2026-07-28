#!/bin/sh
set -eu

case "${1:-}" in
  dry-run|execute) ;;
  *)
    echo '{"source":"wenda-live","status":"configuration_error","live":false}' >&2
    exit 4
    ;;
esac

if [ "$#" -ne 1 ]; then
  echo '{"source":"wenda-live","status":"configuration_error","live":false}' >&2
  exit 4
fi

PROJECT_DIR=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
REQUEST_JSON=$(dd bs=20001 count=1 2>/dev/null)

if [ -z "$REQUEST_JSON" ] || [ "${#REQUEST_JSON}" -gt 20000 ]; then
  echo '{"source":"wenda-live","status":"configuration_error","live":false}' >&2
  exit 4
fi

exec sudo -n systemd-run \
  --quiet \
  --wait \
  --pipe \
  --collect \
  --property=Type=oneshot \
  --property=DynamicUser=yes \
  --property=WorkingDirectory="$PROJECT_DIR" \
  --property=LoadCredentialEncrypted=wenda-session.json:/etc/credstore.encrypted/maxnow-ballet-wenda.cred \
  --property=NoNewPrivileges=yes \
  --property=PrivateTmp=yes \
  --property=PrivateDevices=yes \
  --property=ProtectHome=yes \
  --property=ProtectSystem=strict \
  --property=ProtectProc=invisible \
  --property=ProcSubset=pid \
  --property=ProtectKernelTunables=yes \
  --property=ProtectKernelModules=yes \
  --property=ProtectKernelLogs=yes \
  --property=ProtectControlGroups=yes \
  --property=ProtectClock=yes \
  --property=ProtectHostname=yes \
  --property=LockPersonality=yes \
  --property=MemoryDenyWriteExecute=yes \
  --property=RestrictRealtime=yes \
  --property=RestrictSUIDSGID=yes \
  --property=RestrictAddressFamilies='AF_UNIX AF_INET AF_INET6' \
  --property=CapabilityBoundingSet= \
  --property=SystemCallArchitectures=native \
  --property=RuntimeMaxSec=180 \
  /usr/bin/python3 -B scripts/book_ballet.py "$1" --request-json "$REQUEST_JSON"
