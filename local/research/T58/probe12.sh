#!/usr/bin/env bash
# T58 probe 12: raw timestamps on key ebw lines, patch diff, byte tally.
set -e
E3=/home/brad/pcsx2-g7/dat-t57/PCSX2/logs/emulog.txt
P=/home/brad/pcsx2-g7/pcsx2
S=/mnt/c/Users/bradr/t58stage
echo "===== first ebw raw ====="
grep "ebw vsync=" $E3 | head -2 || true
echo "===== last ebw raw ====="
grep "ebw vsync=" $E3 | tail -2 || true
echo "===== emulog head time + MENU region ====="
head -3 $E3 || true
echo "===== patch diff ====="
git -C $P diff --output=$S/t58-patch.diff -- pcsx2/R5900OpcodeImpl.cpp pcsx2/FPU.cpp pcsx2/VU0.cpp pcsx2/SPR.cpp pcsx2/Sif0.cpp pcsx2/sif2.cpp pcsx2/IPU/IPUdma.cpp
sha256sum $S/t58-patch.diff
wc -c $S/t58-patch.diff
echo "===== byte tally ====="
du -sh /home/brad/pcsx2-g7/dat-t57 /home/brad/pcsx2-g7/dat-t48/PCSX2/logs/emulog.txt $S
echo T58_PROBE12_DONE
