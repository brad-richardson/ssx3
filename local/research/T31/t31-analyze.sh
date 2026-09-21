#!/usr/bin/env bash
# T31 trace analysis on the Continue-Cross emulog. Read-only, streaming.
set -x
D=/home/brad/pcsx2-t4
E=$D/dat/PCSX2/logs/emulog.txt
date -u
ls -la $E
sha256sum $E
wc -l $E
echo "--- markers ---"
grep -m1 -n "BIOS Found" $E
grep -m2 -n "ExecPS2" $E
grep -m1 -n "ReBootStart" $E
grep -m1 -n "sceCdInit" $E
grep -m2 -n "LoadStartModule" $E
grep -m1 -n "UpdateVSyncRate" $E
grep -c "UpdateVSyncRate" $E
grep -m1 -n "WaitVblankStart" $E
grep -c "WaitVblankStart" $E
grep -m1 -n "sceSifGetReg" $E
grep -c "ERROR" $E || true
echo "--- tail ---"
tail -n 5 $E
echo "--- census + samples (T4 scripts) ---"
python3 $D/t4-census.py $E $D/t31-census.txt
python3 $D/t4-sample.py $E $D/t31-samples.txt
ls -la $D/t31-census.txt $D/t31-samples.txt
date -u
