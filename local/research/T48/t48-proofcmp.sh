#!/usr/bin/env bash
# T48 proof compare (fixed): PNG->PPM then cropdiff.
set -e
T4=/home/brad/pcsx2-t4
cp $T4/t48-shot-t48proof-sc.png /mnt/c/Users/bradr/pcsx2-t4/t48-shot-t48proof-sc.png
pngtopnm $T4/t48-shot-t48proof-sc.png > $T4/t48proof-sc.ppm
pngtopnm $T4/t48-shot-t48a-sc.png > $T4/t48a-sc.ppm
ls -la $T4/t48proof-sc.ppm $T4/t48a-sc.ppm
BOX=0,0,640,480
echo "=== patched-vs-unpatched whole ==="
python3 $T4/t44-cropdiff.py $T4/t48a-sc.ppm $T4/t48proof-sc.ppm $BOX || true
ls $T4/t47-shot-sc.png 2>/dev/null || echo NO_T47_SHOT_ON_BOX
if [ -f $T4/t47-shot-sc.png ]; then
pngtopnm $T4/t47-shot-sc.png > $T4/t47-sc.ppm 2>/dev/null || true
echo "=== unpatched vs T47 F8 SC ==="
python3 $T4/t44-cropdiff.py $T4/t48proof-sc.ppm $T4/t47-sc.ppm $BOX || true
echo "=== patched vs T47 F8 SC ==="
python3 $T4/t44-cropdiff.py $T4/t48a-sc.ppm $T4/t47-sc.ppm $BOX || true
fi
echo T48_PROOFCMP_DONE
