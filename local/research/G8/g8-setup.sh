#!/usr/bin/env bash
# G8: datapath copy (G7 dat -> dat-g8) + clean snaps/logs + ini verification.
# G7 dat/ untouched (still holds the G7 run state). Runs INSIDE WSL as brad.
set -x
D=/home/brad/pcsx2-g7
rm -rf $D/dat-g8
cp -a $D/dat $D/dat-g8
rm -rf $D/dat-g8/PCSX2/logs/* $D/dat-g8/PCSX2/snaps/*
grep -n "GSDumpCompression\|ScreenshotSize\|ScreenshotFormat\|EnableEE" $D/dat-g8/PCSX2/inis/PCSX2.ini
ls -la $D/dat-g8/PCSX2/snaps
du -sb $D/dat-g8
du -sb $D/dat
echo G8_SETUP_DONE
