#!/usr/bin/env bash
# T56 diff: patch of the 4 T56-touched files vs HEAD (stacks on the T55 tree).
set -e
cd /home/brad/pcsx2-g7/pcsx2
git diff --output=/mnt/c/Users/bradr/t56stage/t56-patch.diff -- pcsx2/R5900OpcodeImpl.cpp pcsx2/FPU.cpp pcsx2/VU0.cpp pcsx2/SPR.cpp
wc -c /mnt/c/Users/bradr/t56stage/t56-patch.diff
sha256sum /mnt/c/Users/bradr/t56stage/t56-patch.diff
grep -c "T56\|t56" /mnt/c/Users/bradr/t56stage/t56-patch.diff
echo T56_DIFF_DONE
