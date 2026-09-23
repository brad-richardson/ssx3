#!/usr/bin/env bash
# T58 probe 13: spw via-breakdown in run2 emulog (store-hook liveness).
set -e
E=/home/brad/pcsx2-g7/dat-t57/PCSX2/logs/emulog-pre-t58i-20260923T154058Z.txt
echo "===== spw total ====="
grep -c "spw vsync=" $E || true
echo "===== spw by via ====="
grep "spw vsync=" $E | grep -o "via=[a-z0-9-]*" | sort | uniq -c || true
echo "===== T56_CAP count ====="
grep -c "T56_CAP" $E || true
echo T58_PROBE13_DONE
