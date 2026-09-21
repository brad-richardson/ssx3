#!/usr/bin/env bash
# G13: datapath copy (G7 dat -> dat-g13, same lineage as G8) + clean snaps/logs
# + ini verification. dat/ and dat-g8/ untouched (G8 receipt chain pristine).
# Runs INSIDE WSL as brad.
set -x
D=/home/brad/pcsx2-g7
rm -rf $D/dat-g13
cp -a $D/dat $D/dat-g13
rm -rf $D/dat-g13/PCSX2/logs/* $D/dat-g13/PCSX2/snaps/*
grep -n "GSDumpCompression\|ScreenshotSize\|ScreenshotFormat\|EnableEE" $D/dat-g13/PCSX2/inis/PCSX2.ini
ls -la $D/dat-g13/PCSX2/snaps
du -sb $D/dat-g13
du -sb $D/dat
echo G13_SETUP_DONE
