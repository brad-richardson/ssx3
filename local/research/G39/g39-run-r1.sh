#!/bin/sh
# G39 R1: G26 narrow run shape, verbatim (G26 REPORT section 3b).
# cwd on device: /data/local/tmp/g39/ ; host capture to SSD ps2x-g39/.
# Executed via: adb -s 622c49b1 shell <device part>; logcat pulled on host.
# DEVICE PART (one shell invocation):
#   cd /data/local/tmp/g39 && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g39/g13-dump.gs --iterations 2 --disable-sampler-feedback; echo RUN_EXIT=$?; date +%s
# HOST PART:
#   adb -s 622c49b1 logcat -d -s Granite:V > "$SSD/ps2x-g39/g39-r1-logcat.txt"
set -eu
echo "g39-run-r1.sh is a shape mirror; executed step-by-step per REPORT section 6."
