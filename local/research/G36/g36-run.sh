#!/bin/sh
# G36: ONE bounded WITH-FLAG barrier-vs-content-wall run on Odin3 (622c49b1).
# Expects the control binary already pushed + on-device sha-matched (see REPORT
# S3d). Same dump/iterations/knobs as G28/G29/G30/G31/G32/G33/G34/G35 (flag SET,
# PGS_SKIP_COMPILATION_TASKS=1 KEPT) — the ONLY delta is the G36 pre-vsync()
# RAW-ACCESS tagged placement hunk (G29 ladder + G30 vpage + G31 state/bytes
# retained for control/verification; G35 block excised).
# Expect exit 0 + 16 G36: writeback lines (TAGGED-temp FNV) + 16 G31: state
# lines + 16 G31: bytes lines (B==tagged iff the read leg sees the barrier-less
# stores) + 512 G30: vpage lines + 10 G29: ladder lines + 1 G29: vram.
# H1-as-barrier predicts ladder == cleared + black scanouts; pure-refined-H2
# predicts ladder == tagged-model + tag-exact scanouts. Pull scanouts by EXPLICIT
# filename list (G31-E1); cleanup is its own verified step. Run from macOS
# with adb on PATH.
set -e
export COPYFILE_DISABLE=1
DEV=622c49b1
RDIR=/data/local/tmp/g36
adb -s $DEV logcat -c
adb -s $DEV shell "cd $RDIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $RDIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g36-run-stdout.txt 2> g36-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
