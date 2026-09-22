#!/bin/sh
# G32: ONE bounded WITH-FLAG sample_quad[0] unit-probe run on Odin3 (622c49b1).
# Expects the probe binary already pushed + on-device sha-matched (see REPORT
# S3d). Same dump/iterations/knobs as G28/G29/G30/G31 (flag SET,
# PGS_SKIP_COMPILATION_TASKS=1 KEPT) — the ONLY delta is the G32 pre-vsync()
# two-zone pattern-injection hunk (G29 ladder + G30 vpage + G31 state/bytes
# retained for control/verification).
# Expect exit 0 + 16 G32: inject lines + 16 G31: state lines + 16 G31: bytes
# lines (B == pattern FNV) + 512 G30: vpage lines + 10 G29: ladder lines + 1
# G29: vram. Pull scanouts by EXPLICIT filename list (G31-E1); cleanup is its
# own verified step.
# Run from macOS with adb on PATH.
set -e
export COPYFILE_DISABLE=1
DEV=622c49b1
RDIR=/data/local/tmp/g32
adb -s $DEV logcat -c
adb -s $DEV shell "cd $RDIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $RDIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g32-run-stdout.txt 2> g32-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
