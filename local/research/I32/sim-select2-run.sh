#!/bin/bash
# I32 run 4: catch Select Character by guest tick (host load varies, so wall
# time is unreliable). Screenshots when tick first reaches >= 780, then ends.
set -u -o pipefail
W=/Users/brad/dev/ssx3-work/I32
SIM=7662ACD6-6294-4676-B426-26A3F8C7B258
APP=org.ps2x.ps2entryrunner
OUT="$W/run-select2"
mkdir -p "$OUT"
cd "$OUT" || exit 1
SLOT=''
LP=''
cleanup() {
  xcrun simctl terminate "$SIM" "$APP" >/dev/null 2>&1 || true
  if [ -n "$LP" ]; then kill "$LP" >/dev/null 2>&1 || true; wait "$LP" 2>/dev/null || true; fi
  if [ -n "$SLOT" ]; then
    python3 /Users/brad/dev/ssx3/local/tooling/p_lane_lease.py release "$SLOT" >> "$OUT/run.txt" 2>&1
  fi
  echo "cleanup slot=$SLOT own_pid=$LP" >> "$OUT/run.txt"
}
trap cleanup EXIT
while [ -z "$SLOT" ]; do
  if ! SLOT=$(python3 /Users/brad/dev/ssx3/local/tooling/p_lane_lease.py claim I32-select2 2>/dev/null); then
    SLOT=''
    echo 'both lease slots busy; polling in 60 s' >> "$OUT/run.txt"
    sleep 60
  fi
done
echo "lease_slot=$SLOT" >> "$OUT/run.txt"
xcrun simctl terminate "$SIM" "$APP" >/dev/null 2>&1 || true
SIMCTL_CHILD_PS2X_VSYNC_RATE_LOG=1 xcrun simctl launch --console-pty "$SIM" "$APP" > "$OUT/console.log" 2>&1 &
LP=$!
echo "own_pid=$LP" >> "$OUT/run.txt"
START=$(date +%s)
while :; do
  elapsed=$(( $(date +%s) - START ))
  if [ "$elapsed" -ge 240 ]; then echo 'wall cap reached' >> "$OUT/run.txt"; exit 1; fi
  if [ "$(wc -c < "$OUT/console.log")" -ge 7500000 ]; then echo 'console cap reached' >> "$OUT/run.txt"; exit 1; fi
  if ! kill -0 "$LP" 2>/dev/null; then echo "launch exited at ${elapsed}s" >> "$OUT/run.txt"; exit 1; fi
  tick=$(rg -o -N 'tick=[0-9]+' "$OUT/console.log" 2>/dev/null | tail -1 | cut -d= -f2)
  if [ -n "${tick:-}" ] && [ "$tick" -ge 780 ]; then
    echo "tick_threshold at elapsed=${elapsed}s tick=$tick" >> "$OUT/run.txt"
    break
  fi
  sleep 2
done
if ! xcrun simctl io "$SIM" screenshot "$OUT/shot-select.png" >> "$OUT/run.txt" 2>&1; then
  echo 'screenshot failed' >> "$OUT/run.txt"; exit 1
fi
echo "elapsed=$(( $(date +%s) - START ))s select_shot=yes" >> "$OUT/run.txt"
