#!/bin/sh
# G29: ONE bounded WITH-FLAG ladder run on Odin3 (622c49b1).
# Expects the ladder binary already pushed + on-device sha-matched (see REPORT
# S2e). Same dump/iterations/knobs as G28 (flag SET,
# PGS_SKIP_COMPILATION_TASKS=1 KEPT) — the ONLY delta is the G29 ladder hunk.
# Expect exit 0 + 10 G29: ladder lines + 1 G29: vram line in logcat.
# Run from macOS with adb on PATH.
set -e
export COPYFILE_DISABLE=1
DEV=622c49b1
RDIR=/data/local/tmp/g29
adb -s $DEV logcat -c
adb -s $DEV shell "cd $RDIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $RDIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g29-run-stdout.txt 2> g29-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
