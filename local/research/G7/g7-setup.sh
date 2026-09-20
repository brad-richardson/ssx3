#!/usr/bin/env bash
# G7: datapath snapshot + ini flips (uncompressed dump, internal-res PNG).
# R1 dat/ untouched: G7 runs on its own copy. Runs INSIDE WSL as brad.
set -x
D=/home/brad/pcsx2-g7
rm -rf $D/dat $D/logs
mkdir -p $D/logs
cp -a /home/brad/pcsx2-r1/dat $D/dat
cp $D/dat/PCSX2/inis/PCSX2.ini $D/dat/PCSX2/inis/PCSX2.ini.pre-g7
sed -i 's/^GSDumpCompression = .*/GSDumpCompression = 0/' $D/dat/PCSX2/inis/PCSX2.ini
sed -i 's/^ScreenshotSize = .*/ScreenshotSize = 1/' $D/dat/PCSX2/inis/PCSX2.ini
grep -n "GSDumpCompression\|ScreenshotSize\|ScreenshotFormat\|EnableEE" $D/dat/PCSX2/inis/PCSX2.ini
ls $D/dat/PCSX2/snaps | head -5
echo G7_SETUP_DONE
