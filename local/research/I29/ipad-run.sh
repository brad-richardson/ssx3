#!/bin/bash
# I29 iPad validation: install the I29 signed app, run I26-FAST with
# PS2X_VSYNC_RATE_LOG=1 + PS2X_SOUND=1, 4 screenshots, terminate.
set -u -o pipefail
IPAD=00008112-001224302184A01E
APPB=/Users/brad/dev/ssx3-work/I29/staged/ps2EntryRunner.app
APP=org.ps2x.ps2entryrunner
OUT=/Users/brad/dev/ssx3-work/I29/run-ipad
mkdir -p "$OUT"
cd "$OUT" || exit 1
shasum -a 256 "$APPB/ps2EntryRunner" "$APPB/ps2EntryRunner"
xcrun devicectl device install app --device "$IPAD" "$APPB" > install.log 2>&1 || { echo "install failed"; tail -5 install.log; exit 1; }
echo "installed"
LP=''
cleanup() {
  PID=$(xcrun devicectl device info processes --device "$IPAD" 2>/dev/null | grep -i ps2EntryRunner | awk '{print $1}' | head -1)
  [ -n "$PID" ] && xcrun devicectl device process terminate --device "$IPAD" --pid "$PID" >/dev/null 2>&1
  [ -n "$LP" ] && { kill "$LP" 2>/dev/null; wait "$LP" 2>/dev/null; }
  echo "cleanup pid=${PID:-none}"
}
trap cleanup EXIT
xcrun devicectl device process launch --device "$IPAD" --terminate-existing --environment-variables '{"PS2X_VSYNC_RATE_LOG":"1","PS2X_SOUND":"1"}' --console "$APP" > console.log 2>&1 &
LP=$!
START=$(date +%s)
for target in 10 35 100 160; do
  while [ $(( $(date +%s) - START )) -lt "$target" ]; do
    kill -0 "$LP" 2>/dev/null || { echo "app exited at $(( $(date +%s) - START ))s"; exit 1; }
    [ "$(wc -c < console.log)" -ge 7500000 ] && { echo "console cap"; exit 1; }
    sleep 1
  done
  el=$(( $(date +%s) - START ))
  f="$OUT/shot-$(printf %04d $el)s.png"
  xcrun devicectl device capture screenshot --device "$IPAD" --timeout 60 --destination "$f" >/dev/null 2>&1 || echo "screenshot failed at ${el}s"
  echo "shot ${el}s tick=$(grep -o 'tick=[0-9]*' console.log | tail -1)"
done
