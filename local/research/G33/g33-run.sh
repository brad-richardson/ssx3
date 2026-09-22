#!/bin/sh
# G33: ONE bounded WITH-FLAG H1-vs-H2 write-back-control run on Odin3 (622c49b1).
# Expects the control binary already pushed + on-device sha-matched (see REPORT
# S3d). Same dump/iterations/knobs as G28/G29/G30/G31/G32 (flag SET,
# PGS_SKIP_COMPILATION_TASKS=1 KEPT) — the ONLY delta is the G33 pre-vsync()
# stale write-back hunk (G29 ladder + G30 vpage + G31 state/bytes
# retained for control/verification; G32 pattern block excised).
# Expect exit 0 + 16 G33: writeback lines (temp==stale FNV) + 16 G31: state
# lines + 16 G31: bytes lines (B==stale FNV) + 512 G30: vpage lines
# (==G31) + 10 G29: ladder lines + 1 G29: vram. NOTE (predictor finding):
# stale-correct renders byte-identical to cleared, so ladder/scanouts can
# only score VOID (black) or BOTH-REFUTED (non-black). Pull scanouts by
# EXPLICIT filename list (G31-E1); cleanup is its own verified step.
# Run from macOS with adb on PATH.
set -e
export COPYFILE_DISABLE=1
DEV=622c49b1
RDIR=/data/local/tmp/g33
adb -s $DEV logcat -c
adb -s $DEV shell "cd $RDIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $RDIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g33-run-stdout.txt 2> g33-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
