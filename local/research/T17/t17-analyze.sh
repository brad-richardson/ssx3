#!/usr/bin/env bash
# T17 trace analysis on the t17c (held-press) emulog. Read-only, streaming.
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
grep -m1 -n "WaitVblankStart" $E
grep -c "WaitVblankStart" $E
grep -m1 -n "sceSifGetReg" $E
echo "--- vblank counts at log-time marks ---"
awk '/WaitVblankStart/{t=$2; sub(/\]/,"",t); total++; if (t<=90) c90++; if (t<=100) c100++; if (t<=340) c340++} END{print "LE90="c90" LE100="c100" LE340="c340" TOTAL="total}' $E
echo "--- tail ---"
tail -n 5 $E
echo "--- census + samples (T4 scripts) ---"
python3 $D/t4-census.py $E $D/t17-census.txt
python3 $D/t4-sample.py $E $D/t17-samples.txt
ls -la $D/t17-census.txt $D/t17-samples.txt
date -u
