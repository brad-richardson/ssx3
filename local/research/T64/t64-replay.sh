#!/usr/bin/env bash
# T64 preservation proof: G13 replay 7/7 + HWSTAT + zero hook lines.
set -e
G=/home/brad/pcsx2-g7
rm -rf $G/t64-frames
mkdir -p $G/t64-frames
timeout 300 $G/pcsx2/build/bin/pcsx2-gsrunner -renderer vulkan -dumpdir $G/t64-frames -logfile $G/emulog-t64proof.txt -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- '/home/brad/pcsx2-g7/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs'
echo "=== HWSTAT ==="
grep -A8 STATISTICS $G/emulog-t64proof.txt
echo "=== MD5 ==="
md5sum $G/t64-frames/*.png
echo "=== hook line counts (want 0) ==="
grep -c "app vsync=\|appx vsync=\|axfirst vsync=\|v1b0 vsync=\|tw vsync=\|twbase vsync=\|t2 vsync=\|appsum vsync=\|apc vsync=\|tpl vsync=\|tplrearm vsync=\|T6\|ebw vsync=\|ebwlast vsync=\|ebwend vsync=\|T58_CAP\|vu0call vsync=\|vif0op vsync=\|T57_CAP" $G/emulog-t64proof.txt || true
echo T64_REPLAY_DONE
