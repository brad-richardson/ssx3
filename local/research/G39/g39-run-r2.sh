#!/bin/sh
# G39 R2: G28 writer run shape, verbatim (G28 REPORT section 3b).
# cwd on device: /data/local/tmp/g39/ ; host capture to SSD ps2x-g39/.
# DEVICE PART (one shell invocation):
#   cd /data/local/tmp/g39 && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g39/g13-dump.gs --iterations 2 --disable-sampler-feedback > g39-r2-run-stdout.txt 2> g39-r2-run-stderr.txt; echo RUN_EXIT=$?; date +%s
# HOST PART:
#   adb -s 622c49b1 logcat -d -s Granite:V > "$SSD/ps2x-g39/g39-r2-logcat.txt"
set -eu
echo "g39-run-r2.sh is a shape mirror; executed step-by-step per REPORT section 6."
