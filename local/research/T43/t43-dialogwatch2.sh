#!/usr/bin/env bash
# T41 dialog-watch v2 (environment hygiene, NOT part of the experiment
# script). v1 bug (found on R3): `xdotool search --onlyvisible --name '.*'`
# ALSO matches the root window (ID 511, empty name, 1280x1024), and v1
# dismissed the FIRST non-SSX window = root, then exited — never reaching
# a real dialog. v2 enumerates ALL visible windows every round, SKIPS root
# by fullscreen geometry (1280x1024) and the game by name (*SSX*), and
# dismisses every other visible top-level with windowfocus + Return,
# exiting after the first real dismissal. If the dialog resists keys it
# stays visible and the run log shows PERSISTS (escalation: measured mouse
# click). Same parallel-session role as v1; logs rounds + geometries.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
ROUNDS=${1:-40}
for i in $(seq 1 $ROUNDS); do
  echo "ROUND:$i $(date -u +%s.%N)"
  IDS=$(xdotool search --onlyvisible --name '.*' 2>/dev/null || true)
  if [ -z "$IDS" ]; then echo NO-WINDOWS-YET; sleep 5; continue; fi
  for W in $IDS; do
    N=$(xdotool getwindowname "$W" 2>/dev/null || echo UNKNOWN)
    eval "$(xdotool getwindowgeometry --shell "$W" 2>/dev/null | grep -E '^(WIDTH|HEIGHT)=')"
    echo "WIN:$W:$N:${WIDTH}x${HEIGHT}"
    case "$N" in *SSX*) echo "SKIP-GAME:$W"; continue;; esac
    if [ "${WIDTH}x${HEIGHT}" = "1280x1024" ]; then echo "SKIP-ROOT:$W"; continue; fi
    echo "DISMISS:$W:$N"
    xdotool windowfocus --sync "$W" || echo FOCUS-FAILED
    xdotool key --window "$W" Return || echo KEY-FAILED
    echo DISMISSED-EXIT
    exit 0
  done
  sleep 5
done
echo NO-DIALOG-SEEN
