#!/usr/bin/env bash
# T50 trim dat-t50 to boot essentials (logs/snaps/cache contents only).
G=/home/brad/pcsx2-g7
D=$G/dat-t50/PCSX2
grep -n "^EnableEE" $D/inis/PCSX2.ini
rm -rf $D/logs/* $D/snaps/* $D/cache/*
mkdir -p $D/logs $D/snaps $D/cache
ls -la $D/sstates/
du -sh $G/dat-t50
df -h /home/brad | tail -1
echo T50_TRIM_DONE
