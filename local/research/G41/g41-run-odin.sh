#!/usr/bin/env bash
# G41: Odin run O1 (G40-O1 shape + PGS_G41_CANARY=1). Staging/verify/push/run/pull.
set -u
export COPYFILE_DISABLE=1
SSD="/Volumes/Extreme SSD"
DEV=622c49b1
G41DIR=/data/local/tmp/g41
BIN="$SSD/parallel-gs-g41-android-build/tools/parallel-gs-replayer"
DUMP="$SSD/ps2x-g13/g13-dump.gs"
OUT="$SSD/ps2x-g41"
adb -s $DEV shell 'ls /data/local/tmp/; ls -lt /data/tombstones/ | head -2'
shasum -a 256 "$BIN" | cut -c1-16
shasum -a 256 "$DUMP" | cut -c1-16
adb -s $DEV shell "rm -rf $G41DIR && mkdir -p $G41DIR"
adb -s $DEV push "$DUMP" $G41DIR/g13-dump.gs
adb -s $DEV push "$BIN" $G41DIR/parallel-gs-replayer
adb -s $DEV shell "cd $G41DIR && sha256sum g13-dump.gs parallel-gs-replayer | cut -c1-16"
adb -s $DEV logcat -c
adb -s $DEV logcat -d -s Granite:V 2>/dev/null | tail -2
adb -s $DEV shell "cd $G41DIR && date +%s; PGS_G40_WALL=1 PGS_G41_CANARY=1 PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G41DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g41-run-stdout.txt 2> g41-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
adb -s $DEV shell "ls -la $G41DIR/ | head -20; ls -lt /data/tombstones/ | head -3"
adb -s $DEV logcat -d -s Granite:V > "$OUT/g41-odin-logcat.txt"
adb -s $DEV shell "sha256sum $G41DIR/parallel-gs-replayer | cut -c1-16"
wc -l "$OUT/g41-odin-logcat.txt"
