#!/bin/sh
# G31: ONE bounded WITH-FLAG (b1)/(b2) state-probe run on Odin3 (622c49b1).
# Expects the state binary already pushed + on-device sha-matched (see REPORT
# S3d). Same dump/iterations/knobs as G28/G29/G30 (flag SET,
# PGS_SKIP_COMPILATION_TASKS=1 KEPT) — the ONLY delta is the G31 in-vsync()
# state-dump hunk (G29 ladder + G30 vpage retained for control).
# Expect exit 0 + 16 G31: state lines + 16 G31: bytes lines + 512 G30: vpage
# lines + 10 G29: ladder lines + 1 G29: vram.
# Run from macOS with adb on PATH.
set -e
export COPYFILE_DISABLE=1
DEV=622c49b1
RDIR=/data/local/tmp/g31
adb -s $DEV logcat -c
adb -s $DEV shell "cd $RDIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $RDIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g31-run-stdout.txt 2> g31-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
