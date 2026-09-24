#!/bin/bash
# I26 (from I25) Simulator check-in run: lease slot, home-screen launch (bundled
# ps2x.env = E33 auto-route) + PS2X_VSYNC_RATE_LOG=1, a screenshot every
# SHOT_S seconds, hard cap WALL seconds, then terminate + release.
# Usage: LABEL=a WALL=600 sim-run.sh
set -uo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
I25="$REPO/local/research/I26"
W="${W:-$HOME/dev/ssx3-work/I26}"
LABEL="${LABEL:-a}"; WALL="${WALL:-600}"; SHOT_S="${SHOT_S:-20}"
SIM="${SIM:-7662ACD6-6294-4676-B426-26A3F8C7B258}"
OUT="$W/run-$LABEL"; mkdir -p "$OUT"
cd "$REPO/local/tooling"
SLOT=$(python3 -c 'import p_lane_lease as l; s=l.claim("I26-sim-'"$LABEL"'"); print(s if s else "")')
[ -n "$SLOT" ] || { echo "no free lease slot"; exit 2; }
echo "lease slot $SLOT"
trap 'xcrun simctl terminate "$SIM" org.ps2x.ps2entryrunner 2>/dev/null; kill $LP 2>/dev/null; python3 -c "import p_lane_lease as l; l.release('"$SLOT"')"; echo "released slot '"$SLOT"'"' EXIT
xcrun simctl terminate "$SIM" org.ps2x.ps2entryrunner 2>/dev/null || true
# EXTRA_ENV="K=V K2=V2" adds diagnostic env (passed as SIMCTL_CHILD_*).
for kv in ${EXTRA_ENV:-}; do export "SIMCTL_CHILD_$kv"; done
SIMCTL_CHILD_PS2X_VSYNC_RATE_LOG=1 xcrun simctl launch --console-pty "$SIM" org.ps2x.ps2entryrunner \
  > "$OUT/console.log" 2>&1 &
LP=$!
T0=$(date +%s)
while :; do
  sleep "$SHOT_S"
  t=$(( $(date +%s) - T0 ))
  xcrun simctl io "$SIM" screenshot "$OUT/shot-$(printf %04d $t)s.png" > /dev/null 2>&1
  tick=$(grep -o 'tick=[0-9]*' "$OUT/console.log" | tail -1)
  echo "t=${t}s $tick log=$(wc -c < "$OUT/console.log")B"
  [ "$(wc -c < "$OUT/console.log")" -gt 200000000 ] && { echo "console cap hit"; break; }
  kill -0 $LP 2>/dev/null || { echo "app exited"; break; }
  [ -f "$OUT/STOP" ] && { echo "STOP file"; break; }
  [ "$t" -ge "$WALL" ] && { echo "wall cap"; break; }
done
