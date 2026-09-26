#!/bin/bash
# bytesize_lock.sh claim <LABEL> | release <LABEL> | status | run <LABEL> -- <cmd...>
# One heavy job (Android/gradle, Mesa/meson, big ninja) at a time on bytesize's WSL: 09-26 two
# concurrent builds (VR4's gradle + FS2's Mesa ninja -j20) ate WSL's 12 GB and wedged the VM.
# The lock is an atomic mkdir inside WSL; it holds a HOLDER file with the label and UTC time.
# `run` waits (polling every 30 s) until the lock is free, runs the command locally (it should
# itself ssh to bytesize and hold the ssh open), then releases. Mesa builds: ninja -j8 at most.
set -u
L=/home/brad/.ssx3-heavy.lock
w() { ssh -o ConnectTimeout=10 bytesize "wsl -d Ubuntu -- bash -c \"$1\""; }
cmd=${1:-status}; label=${2:-}
case "$cmd" in
  status) w "cat $L/HOLDER 2>/dev/null || echo FREE" ;;
  claim)
    [ -n "$label" ] || { echo "usage: claim LABEL" >&2; exit 2; }
    # Refuse when Windows C: is low: the WSL disk image lives there (09-26: C: at 4 GB free wedged WSL and
    # then Windows). The image is sparse (fstrim returns freed space); MIN_FREE_GB defaults to 60.
    free=$(ssh -o ConnectTimeout=10 bytesize 'powershell -NoProfile -Command "[int]((Get-PSDrive C).Free/1GB)"' | tr -dc 0-9)
    [ -n "$free" ] && [ "$free" -ge "${MIN_FREE_GB:-60}" ] || { echo "LOWDISK C: free=${free:-?} GB < ${MIN_FREE_GB:-60} GB; clean up (delete finished lane dirs, then wsl -u root fstrim /)"; exit 1; }
    out=$(w "mkdir $L 2>/dev/null && echo '$label '\$(date -u +%FT%TZ) > $L/HOLDER && echo CLAIMED || { echo -n 'HELD '; cat $L/HOLDER; }")
    echo "$out"; [ "$out" = CLAIMED ] ;;
  release)
    [ -n "$label" ] || { echo "usage: release LABEL" >&2; exit 2; }
    out=$(w "grep -q '^$label ' $L/HOLDER 2>/dev/null && rm -rf $L && echo RELEASED || { echo -n 'NOTMINE '; cat $L/HOLDER 2>/dev/null; }")
    echo "$out"; [ "$out" = RELEASED ] ;;
  run)
    [ -n "$label" ] && [ "${3:-}" = "--" ] || { echo "usage: run LABEL -- cmd..." >&2; exit 2; }
    shift 3
    until out=$("$0" claim "$label"); do case "$out" in LOWDISK*) echo "$out" >&2; exit 3;; esac; sleep 30; done
    "$@"; rc=$?
    "$0" release "$label" >/dev/null; exit $rc ;;
  *) echo "usage: $0 claim|release|status|run" >&2; exit 2 ;;
esac
