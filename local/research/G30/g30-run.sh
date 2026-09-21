#!/bin/sh
# G30: ONE bounded WITH-FLAG content-probe run on Odin3 (622c49b1).
# Expects the content binary already pushed + on-device sha-matched (see REPORT
# S2e). Same dump/iterations/knobs as G28/G29 (flag SET,
# PGS_SKIP_COMPILATION_TASKS=1 KEPT) — the ONLY delta is the G30 pre-restart
# VRAM page-dump hunk (G29 ladder retained for control).
# Expect exit 0 + 512 G30: vpage lines + 10 G29: ladder lines + 1 G29: vram.
# Run from macOS with adb on PATH.
set -e
export COPYFILE_DISABLE=1
DEV=622c49b1
RDIR=/data/local/tmp/g30
adb -s $DEV logcat -c
adb -s $DEV shell "cd $RDIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $RDIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g30-run-stdout.txt 2> g30-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
