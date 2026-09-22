#!/bin/sh
# G37: ONE bounded WITH-FLAG minimum-content-threshold-wall run on Odin3 (622c49b1).
# Expects the control binary already pushed + on-device sha-matched (see REPORT
# S3d). Same dump/iterations/knobs as G28/G29/G30/G31/G32/G33/G34/G35/G36 (flag SET,
# PGS_SKIP_COMPILATION_TASKS=1 KEPT) — the ONLY delta is the G37 pre-vsync()
# RAW-ACCESS shrunken-tag (1-word: temp[0] |= 0x00FFFFFF) placement hunk (G29
# ladder + G30 vpage + G31 state/bytes retained for control/verification; G36
# block excised).
# Expect exit 0 + 16 G37: writeback lines (SHRUNKEN-temp FNV) + 16 G31: state
# lines + 16 G31: bytes lines (B==shrunken iff the read leg sees the barrier-less
# stores) + 512 G30: vpage lines + 10 G29: ladder lines + 1 G29: vram.
# ANY-nonzero-RGB predicts ladder == shrunken-model + 1-pixel-exact scanouts
# (white at (0,0)); higher-threshold models predict ladder == cleared + black
# scanouts. Pull scanouts by EXPLICIT filename list (G31-E1); cleanup is its
# own verified step. Run from macOS with adb on PATH.
set -e
export COPYFILE_DISABLE=1
DEV=622c49b1
RDIR=/data/local/tmp/g37
adb -s $DEV logcat -c
adb -s $DEV shell "cd $RDIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $RDIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g37-run-stdout.txt 2> g37-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
