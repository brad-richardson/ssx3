#!/bin/sh
# G28: ONE bounded WITH-FLAG verification run on Odin3 (622c49b1).
# Expects the fixed binary already pushed + on-device sha-matched (see REPORT
# SS2e). Same dump/iterations as G26/G27, flag SET, PGS_SKIP_... UNSET,
# PGS_SKIP_COMPILATION_TASKS=1 KEPT. Expect exit 0.
# Run from macOS with adb on PATH.
set -e
export COPYFILE_DISABLE=1
DEV=622c49b1
RDIR=/data/local/tmp/g28
adb -s $DEV logcat -c
adb -s $DEV shell "cd $RDIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $RDIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g28-run-stdout.txt 2> g28-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
