#!/usr/bin/env bash
# T50 setup: dat-t50 = copy of dat-t48 with EE interpreter (EnableEE=false).
# Run AFTER boot1 (so the F1 savestate in dat-t48/sstates rides along).
set -e
G=/home/brad/pcsx2-g7
rm -rf $G/dat-t50
cp -r $G/dat-t48 $G/dat-t50
sed -i 's/^EnableEE = true$/EnableEE = false/' $G/dat-t50/PCSX2/inis/PCSX2.ini
grep -n "^EnableEE" $G/dat-t50/PCSX2/inis/PCSX2.ini
grep -n "^EnableVU0\|^EnableVU1\|^vuThread" $G/dat-t50/PCSX2/inis/PCSX2.ini $G/dat-t50/PCSX2/inis/PCSX2.ini 2>/dev/null || true
grep -n "vuThread" $G/dat-t50/PCSX2/inis/PCSX2.ini
rm -f $G/dat-t50/PCSX2/logs/emulog.txt
ls $G/dat-t50/PCSX2/sstates/ 2>/dev/null || echo "no sstates yet"
du -sh $G/dat-t50
df -h /home/brad | tail -1
echo T50_SETUP_DONE
