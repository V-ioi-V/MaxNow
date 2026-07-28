#!/bin/sh
set -eu

case "${1:-}" in
  timetable|bookings|attendance|membership) ;;
  *)
    echo '{"source":"wenda-live","status":"configuration_error","live":false}' >&2
    exit 4
    ;;
esac

for argument in "$@"; do
  case "$argument" in
    timetable|bookings|attendance|membership|--from-date|--through-date) ;;
    20[0-9][0-9]-[01][0-9]-[0-3][0-9]) ;;
    *)
      echo '{"source":"wenda-live","status":"configuration_error","live":false}' >&2
      exit 4
      ;;
  esac
done

exec sudo -n systemd-run \
  --quiet \
  --wait \
  --pipe \
  --collect \
  --property=Type=oneshot \
  --property=DynamicUser=yes \
  --property=WorkingDirectory=/var/www/maxnow-dashboard \
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
  --property=RuntimeMaxSec=120 \
  /usr/bin/python3 -B scripts/query_ballet_live.py "$@" \
  --credential-file=%d/wenda-session.json
