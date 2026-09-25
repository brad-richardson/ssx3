#!/bin/bash
# I32 iPad test: ONE launch. Route re-armed per launch (-e wins over the
# manual-play Documents env), stick injected, D-pad checks via test touches.
# Tick-triggered screenshots, terminate after. ENV_JSON decided by the
# sim save-route tests (see REPORT).
set -u -o pipefail
IPAD=00008112-001224302184A01E
APP=org.ps2x.ps2entryrunner
OUT=/Users/brad/dev/ssx3-work/I32/run-ipad
ENV_JSON="$1"
THRESHOLDS="$2" # space-separated ticks, one screenshot each
mkdir -p "$OUT"
cd "$OUT" || exit 1
LP=''
cleanup() {
  PID=$(xcrun devicectl device info processes --device "$IPAD" 2>/dev/null | grep -i ps2EntryRunner | awk '{print $1}' | head -1)
  [ -n "${PID:-}" ] && xcrun devicectl device process terminate --device "$IPAD" --pid "$PID" >/dev/null 2>&1
  [ -n "$LP" ] && { kill "$LP" 2>/dev/null; wait "$LP" 2>/dev/null; }
  echo "cleanup pid=${PID:-none}"
}
trap cleanup EXIT
xcrun devicectl device process launch --device "$IPAD" --terminate-existing \
  --environment-variables "$ENV_JSON" --console "$APP" > console.log 2>&1 &
LP=$!
START=$(date +%s)
for need in $THRESHOLDS; do
  while :; do
    el=$(( $(date +%s) - START ))
    if [ "$el" -ge 420 ]; then echo 'wall cap reached' >> run.txt; exit 1; fi
    if [ "$(wc -c < console.log)" -ge 7500000 ]; then echo 'console cap reached' >> run.txt; exit 1; fi
    if ! kill -0 "$LP" 2>/dev/null; then echo "app exited at ${el}s" >> run.txt; exit 1; fi
    tick=$(rg -o -N 'tick=[0-9]+' console.log 2>/dev/null | tail -1 | cut -d= -f2)
    if [ -n "${tick:-}" ] && [ "$tick" -ge "$need" ]; then
      echo "threshold need=$need at elapsed=${el}s tick=$tick" >> run.txt
      break
    fi
    sleep 2
  done
  f="$OUT/shot-t$need.png"
  xcrun devicectl device capture screenshot --device "$IPAD" --timeout 60 --destination "$f" >/dev/null 2>&1 \
    || { echo "screenshot failed at $need" >> run.txt; exit 1; }
  echo "shot t$need at ${el}s" >> run.txt
done
echo "elapsed=$(( $(date +%s) - START ))s ipad_done=yes" >> run.txt
