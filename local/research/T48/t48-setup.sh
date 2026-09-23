#!/usr/bin/env bash
# T48 setup: fresh dat-t48 from T47's dat, flip vuThread + EnableVU1 off, clean logs/snaps.
set -e
T4=/home/brad/pcsx2-t4
G=/home/brad/pcsx2-g7
rm -rf $G/dat-t48
cp -r $T4/dat $G/dat-t48
INI=$G/dat-t48/PCSX2/inis/PCSX2.ini
grep -n "vuThread\|EnableVU1" $INI
sed -i 's/^vuThread = .*/vuThread = false/' $INI
sed -i 's/^EnableVU1 = .*/EnableVU1 = false/' $INI
grep -n "vuThread\|EnableVU1" $INI
rm -f $G/dat-t48/PCSX2/logs/* $G/dat-t48/PCSX2/snaps/*
ls $G/dat-t48/PCSX2/logs/ | head -3 || true
ls $G/dat-t48/PCSX2/snaps/ | head -3 || true
ls -la $T4/inputs/ | head -8
du -s $G/dat-t48
echo T48_SETUP_DONE
