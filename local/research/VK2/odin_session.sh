#!/bin/bash
# VK2 Odin session (09-26 lease protocol): claim the lease once through the atomic
# local/tooling/odin_lease.sh, run every leg (cool-down -> launch.py -> restore Brad's
# play state), release on exit. launch.py and restore-play.sh only check that VK2
# holds the lease; they never write it.
#   odin_session.sh LEG [LEG...]   LEG = "LABEL|launch.py args"
set -uo pipefail
D=$(cd "$(dirname "$0")" && pwd)
LEASE=$HOME/dev/ssx3/local/tooling/odin_lease.sh
until "$LEASE" claim VK2; do sleep 30; done
trap '"$LEASE" release VK2' EXIT
for leg in "$@"; do
  label=${leg%%|*}; args=${leg#*|}
  echo "=== leg $label: $args ($(date +%H:%M:%S))"
  python3 "$D/cooldown.py" --label "$label" || { echo "cooldown failed for $label"; exit 1; }
  # shellcheck disable=SC2086
  python3 "$D/launch.py" --label "$label" $args; rc=$?
  mkdir -p "$D/logs/$label"
  bash "$D/restore-play.sh" > "$D/logs/$label/restore-play.txt" 2>&1; rr=$?
  tail -3 "$D/logs/$label/restore-play.txt"
  [ $rc -eq 0 ] && [ $rr -eq 0 ] || { echo "leg $label failed: launch rc=$rc restore rc=$rr"; exit 1; }
done
echo "=== session done $(date +%H:%M:%S)"
