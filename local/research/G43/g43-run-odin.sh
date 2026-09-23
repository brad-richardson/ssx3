#!/usr/bin/env bash
# G43 Mission 1: same binary, two Odin runs in one session —
#   (T) Turnip via PGS_G42_TURNIP, (S) system-driver control (= C1 repeat).
# G41-O1 shape + wall envs; per-run logcat + tagged pulls. No cleanup here
# (cleanup is a separate OWN step at brief end). Adapted from G42 to the
# internal G43 tree: build, inputs and outputs all on the mini's internal disk.
set -u
export COPYFILE_DISABLE=1
WORK="$HOME/dev/ssx3-work/G43"
DEV=622c49b1
G43DIR=/data/local/tmp/g43
BIN="$WORK/android-build/tools/parallel-gs-replayer"
DUMP="$WORK/inputs/g13-dump.gs"
TURNIP="$WORK/inputs/libvulkan_freedreno.so"
OUT="$WORK/odin-run"
WHICH="${1:-both}"  # turnip | sys | both
mkdir -p "$OUT"

echo "== pre-check =="
adb -s $DEV shell 'ls /data/local/tmp/; cat /data/local/tmp/mg/LEASE 2>&1; ls -lt /data/tombstones/ | head -2'
echo "== host shas (pre-push read 1) =="
shasum -a 256 "$BIN" | cut -c1-16
shasum -a 256 "$DUMP" | cut -c1-16
shasum -a 256 "$TURNIP" | cut -c1-16
adb -s $DEV shell "rm -rf $G43DIR && mkdir -p $G43DIR"
adb -s $DEV push "$DUMP" $G43DIR/g13-dump.gs
adb -s $DEV push "$BIN" $G43DIR/parallel-gs-replayer
adb -s $DEV push "$TURNIP" $G43DIR/libvulkan_freedreno.so
echo "== on-device shas =="
adb -s $DEV shell "cd $G43DIR && sha256sum g13-dump.gs parallel-gs-replayer libvulkan_freedreno.so | cut -c1-16"

run_leg() {
  TAG="$1"      # turnip | sys
  EXTRA="$2"    # extra env prefix or empty
  adb -s $DEV logcat -c
  adb -s $DEV logcat -d -s Granite:V 2>/dev/null | tail -1
  # shellcheck disable=SC2086
  adb -s $DEV shell "cd $G43DIR && date +%s; $EXTRA PGS_G40_WALL=1 PGS_G41_CANARY=1 PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G43DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > ${TAG}-run-stdout.txt 2> ${TAG}-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
  adb -s $DEV logcat -d -s Granite:V > "$OUT/g43-${TAG}-logcat.txt"
  adb -s $DEV pull $G43DIR/${TAG}-run-stdout.txt "$OUT/g43-${TAG}-run-stdout.txt"
  adb -s $DEV pull $G43DIR/${TAG}-run-stderr.txt "$OUT/g43-${TAG}-run-stderr.txt"
  for p in g8-first g8-last g10-vsync0 g10-vsync1 g10-vsync2 g10-vsync3 g10-vsync4 g10-vsync5 g10-vsync6 g10-vsync7; do
    adb -s $DEV pull $G43DIR/g13-dump.gs.${p}.ppm "$OUT/g43-${TAG}-g13-dump.gs.${p}.ppm"
  done
  wc -l "$OUT/g43-${TAG}-logcat.txt"
  adb -s $DEV shell "ls -lt /data/tombstones/ | head -2"
}

if [ "$WHICH" = "turnip" ] || [ "$WHICH" = "both" ]; then
  echo "== run T (Turnip) =="
  run_leg turnip "PGS_G42_TURNIP=$G43DIR/libvulkan_freedreno.so"
fi
if [ "$WHICH" = "sys" ] || [ "$WHICH" = "both" ]; then
  echo "== run S (system control) =="
  run_leg sys ""
fi
echo "== post-run binary sha =="
adb -s $DEV shell "sha256sum $G43DIR/parallel-gs-replayer | cut -c1-16"
