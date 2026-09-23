#!/usr/bin/env bash
# T61 preservation proof: G13 replay 7/7 + HWSTAT + zero hook lines.
set -e
G=/home/brad/pcsx2-g7
rm -rf $G/t61-frames
mkdir -p $G/t61-frames
timeout 300 $G/pcsx2/build/bin/pcsx2-gsrunner -renderer vulkan -dumpdir $G/t61-frames -logfile $G/emulog-t61proof.txt -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- '/home/brad/pcsx2-g7/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs'
echo "=== HWSTAT ==="
grep -A8 STATISTICS $G/emulog-t61proof.txt
echo "=== MD5 ==="
md5sum $G/t61-frames/*.png
echo "=== hook line counts (want 0) ==="
grep -c "app vsync=\|appsum vsync=\|apc vsync=\|tpl vsync=\|tplrearm vsync=\|T6\|ebw vsync=\|ebwlast vsync=\|ebwend vsync=\|T58_CAP\|vu0call vsync=\|vif0op vsync=\|T57_CAP" $G/emulog-t61proof.txt || true
echo T61_REPLAY_DONE
