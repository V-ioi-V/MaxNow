#!/bin/sh
set -eu

if [ "${1:-}" != "status" ] || [ "$#" -ne 1 ]; then
  echo '{"status":"configuration_error"}' >&2
  exit 4
fi

exec sudo -n systemd-run \
  --quiet \
  --wait \
  --pipe \
  --collect \
  --property=Type=oneshot \
  --property=User=root \
  --property=Group=www-data \
  --property=WorkingDirectory=/var/www/maxnow-dashboard \
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
  --property=RestrictAddressFamilies=AF_UNIX \
  --property=IPAddressDeny=any \
  --property=CapabilityBoundingSet= \
  --property=SystemCallArchitectures=native \
  --property=RuntimeMaxSec=20 \
  /usr/bin/python3 -B scripts/book_ballet_fast.py status
