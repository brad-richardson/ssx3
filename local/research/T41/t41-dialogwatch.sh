#!/usr/bin/env bash
# T41 dialog-watch (environment hygiene, NOT part of the experiment
# script): polls the Xvfb :99 root for the PCSX2 cubeb-failure modal. Host
# WSLg audio is down on H32/H33 (no /mnt/wslg/PulseServer socket, no
# runtime-dir/pulse/ — present on neither VM; host has 6 OK sound devices
# so this is a WSLg defect), so EVERY pcsx2 boot pops "Failed to create or
# configure audio stream ... CUBEB_ERROR (-1)" over the game window,
# occluding the title text-band and forcing NO-PARK (R1+R2, 2/2 runs).
# Any visible top-level window whose name lacks "SSX 3" gets a targeted
# Return (the dialog's OK default button); the game window never receives
# input from this script. Runs from a SECOND ssh session in parallel with
# t41-auto.sh; exits on first dismissal or after ROUNDS*5 s. Logs rounds,
# window names, and the dismissal (or NO-DIALOG-SEEN) to stdout.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
ROUNDS=${1:-34}
for i in $(seq 1 $ROUNDS); do
  echo "ROUND:$i $(date -u +%s.%N)"
  IDS=$(xdotool search --onlyvisible --name '.*' 2>/dev/null || true)
  if [ -z "$IDS" ]; then echo NO-WINDOWS-YET; sleep 5; continue; fi
  for W in $IDS; do
    N=$(xdotool getwindowname "$W" 2>/dev/null || echo UNKNOWN)
    echo "WIN:$W:$N"
    case "$N" in *SSX*) ;; *) echo "DISMISS:$W:$N"; xdotool key --window "$W" Return; echo DISMISSED; exit 0;; esac
  done
  sleep 5
done
echo NO-DIALOG-SEEN
