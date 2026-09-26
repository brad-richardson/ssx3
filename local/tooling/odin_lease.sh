#!/bin/bash
# odin_lease.sh claim <LABEL> | release <LABEL> | status | run <LABEL> -- <cmd...>
# Atomic Odin lease. The claim is one shell on the device that checks and writes in the same
# command, guarded by an on-device mkdir lock, so two lanes can't both see LEASE_FREE and both
# write (09-26: BA1 installed an APK during VK2's stress run with no lease check).
# The LEASE file keeps its old format ("LEASE_FREE …" or "<LABEL> <utc> …"), so older launchers that
# read it still see the right holder. Any adb install/launch/force-stop must hold the lease:
# use `run` for one-off commands (claims, runs, releases).
set -u
S=${ODIN_SERIAL:-$(cat "$HOME/dev/ssx3/local/odin-serial")}
L=/data/local/tmp/mg/LEASE
LOCK=/data/local/tmp/mg/lease.lock.d
cmd=${1:-status}; label=${2:-}
case "$cmd" in
  status) adb -s "$S" shell "cat $L" ;;
  claim)
    [ -n "$label" ] || { echo "usage: claim LABEL" >&2; exit 2; }
    out=$(adb -s "$S" shell "mkdir $LOCK 2>/dev/null || { echo BUSYLOCK; exit 0; }; \
      cur=\$(cat $L 2>/dev/null); case \"\$cur\" in LEASE_FREE*|'$label '*) \
      echo '$label '\$(date -u +%FT%TZ) > $L; echo CLAIMED;; *) echo \"HELD \$cur\";; esac; rmdir $LOCK")
    echo "$out"; [ "$out" = CLAIMED ] ;;
  release)
    [ -n "$label" ] || { echo "usage: release LABEL" >&2; exit 2; }
    out=$(adb -s "$S" shell "mkdir $LOCK 2>/dev/null || { echo BUSYLOCK; exit 0; }; \
      cur=\$(cat $L 2>/dev/null); case \"\$cur\" in '$label '*) echo 'LEASE_FREE $label done' > $L; echo RELEASED;; \
      *) echo \"NOTMINE \$cur\";; esac; rmdir $LOCK")
    echo "$out"; [ "$out" = RELEASED ] ;;
  run)
    [ -n "$label" ] && [ "${3:-}" = "--" ] || { echo "usage: run LABEL -- cmd..." >&2; exit 2; }
    shift 3
    until "$0" claim "$label" >/dev/null; do sleep 20; done
    "$@"; rc=$?
    "$0" release "$label" >/dev/null; exit $rc ;;
  *) echo "usage: $0 claim|release|status|run" >&2; exit 2 ;;
esac
