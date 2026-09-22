#!/usr/bin/env bash
# G42 Mission 1: same binary, two Odin runs in one session —
#   (T) Turnip via PGS_G42_TURNIP, (S) system-driver control.
# G41-O1 shape + wall envs; per-run logcat + tagged pulls. No cleanup here
# (cleanup is a separate OWN step at brief end).
set -u
export COPYFILE_DISABLE=1
SSD="/Volumes/Extreme SSD"
DEV=622c49b1
G42DIR=/data/local/tmp/g42
BIN="$SSD/parallel-gs-g42-android-build/tools/parallel-gs-replayer"
DUMP="$SSD/ps2x-g13/g13-dump.gs"
TURNIP="$SSD/ps2x-g42/libvulkan_freedreno.so"
OUT="$SSD/ps2x-g42"
WHICH="${1:-both}"  # turnip | sys | both

echo "== pre-check =="
adb -s $DEV shell 'ls /data/local/tmp/; cat /data/local/tmp/mg/LEASE 2>&1; ls -lt /data/tombstones/ | head -2'
echo "== host shas (pre-push read 1) =="
shasum -a 256 "$BIN" | cut -c1-16
shasum -a 256 "$DUMP" | cut -c1-16
shasum -a 256 "$TURNIP" | cut -c1-16
adb -s $DEV shell "rm -rf $G42DIR && mkdir -p $G42DIR"
adb -s $DEV push "$DUMP" $G42DIR/g13-dump.gs
adb -s $DEV push "$BIN" $G42DIR/parallel-gs-replayer
adb -s $DEV push "$TURNIP" $G42DIR/libvulkan_freedreno.so
echo "== on-device shas =="
adb -s $DEV shell "cd $G42DIR && sha256sum g13-dump.gs parallel-gs-replayer libvulkan_freedreno.so | cut -c1-16"

run_leg() {
  TAG="$1"      # turnip | sys
  EXTRA="$2"    # extra env prefix or empty
  adb -s $DEV logcat -c
  adb -s $DEV logcat -d -s Granite:V 2>/dev/null | tail -1
  # shellcheck disable=SC2086
  adb -s $DEV shell "cd $G42DIR && date +%s; $EXTRA PGS_G40_WALL=1 PGS_G41_CANARY=1 PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G42DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > ${TAG}-run-stdout.txt 2> ${TAG}-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
  adb -s $DEV logcat -d -s Granite:V > "$OUT/g42-${TAG}-logcat.txt"
  adb -s $DEV pull $G42DIR/${TAG}-run-stdout.txt "$OUT/g42-${TAG}-run-stdout.txt"
  adb -s $DEV pull $G42DIR/${TAG}-run-stderr.txt "$OUT/g42-${TAG}-run-stderr.txt"
  for p in g8-first g8-last g10-vsync0 g10-vsync1 g10-vsync2 g10-vsync3 g10-vsync4 g10-vsync5 g10-vsync6 g10-vsync7; do
    adb -s $DEV pull $G42DIR/g13-dump.gs.${p}.ppm "$OUT/g42-${TAG}-g13-dump.gs.${p}.ppm"
  done
  wc -l "$OUT/g42-${TAG}-logcat.txt"
  adb -s $DEV shell "ls -lt /data/tombstones/ | head -2"
}

if [ "$WHICH" = "turnip" ] || [ "$WHICH" = "both" ]; then
  echo "== run T (Turnip) =="
  run_leg turnip "PGS_G42_TURNIP=$G42DIR/libvulkan_freedreno.so"
fi
if [ "$WHICH" = "sys" ] || [ "$WHICH" = "both" ]; then
  echo "== run S (system control) =="
  run_leg sys ""
fi
echo "== post-run binary sha =="
adb -s $DEV shell "sha256sum $G42DIR/parallel-gs-replayer | cut -c1-16"
