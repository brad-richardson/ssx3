#!/bin/sh
# G34: ONE bounded WITH-FLAG H1-vs-H2 TAGGED write-back run on Odin3 (622c49b1).
# Expects the control binary already pushed + on-device sha-matched (see REPORT
# S3d). Same dump/iterations/knobs as G28/G29/G30/G31/G32/G33 (flag SET,
# PGS_SKIP_COMPILATION_TASKS=1 KEPT) — the ONLY delta is the G34 pre-vsync()
# TAGGED write-back hunk (G29 ladder + G30 vpage + G31 state/bytes
# retained for control/verification; G33 block excised).
# Expect exit 0 + 16 G34: writeback lines (TAGGED-temp FNV) + 16 G31: state
# lines + 16 G31: bytes lines (B==tagged FNV) + 512 G30: vpage lines
# (112 tagged pages == oracle, 400 == G31) + 10 G29: ladder lines + 1 G29: vram.
# H1 predicts ladder == tagged-model FNV + 112-white scanouts; H2 predicts
# cleared. Pull scanouts by EXPLICIT filename list (G31-E1); cleanup is its
# own verified step. Run from macOS with adb on PATH.
set -e
export COPYFILE_DISABLE=1
DEV=622c49b1
RDIR=/data/local/tmp/g34
adb -s $DEV logcat -c
adb -s $DEV shell "cd $RDIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $RDIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g34-run-stdout.txt 2> g34-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
