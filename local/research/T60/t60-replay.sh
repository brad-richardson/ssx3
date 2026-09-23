#!/usr/bin/env bash
# T60 preservation proof: G13 replay 7/7 + HWSTAT + zero hook lines.
set -e
G=/home/brad/pcsx2-g7
rm -rf $G/t60-frames
mkdir -p $G/t60-frames
timeout 300 $G/pcsx2/build/bin/pcsx2-gsrunner -renderer vulkan -dumpdir $G/t60-frames -logfile $G/emulog-t60proof.txt -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- '/home/brad/pcsx2-g7/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs'
echo "=== HWSTAT ==="
grep -A8 STATISTICS $G/emulog-t60proof.txt
echo "=== MD5 ==="
md5sum $G/t60-frames/*.png
echo "=== hook line counts (want 0) ==="
grep -c "app vsync=\|tpl vsync=\|tplrearm vsync=\|T60_CAP\|ebw vsync=\|ebwlast vsync=\|ebwend vsync=\|T58_CAP\|vu0call vsync=\|vif0op vsync=\|T57_CAP" $G/emulog-t60proof.txt || true
echo T60_REPLAY_DONE
