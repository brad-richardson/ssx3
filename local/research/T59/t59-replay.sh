#!/usr/bin/env bash
# T59 preservation proof: replay the G13 rich dump with the patched gsrunner;
# PNG md5s + HWSTAT must match the T48 pins exactly; zero T59/T58/T57 lines.
# Pins: md5s b7a3e8db a7929218 bb8b1d85 817e934f x2 85cf3599 x2,
# HWSTAT 791/37/0/14/320/6.
set -e
G=/home/brad/pcsx2-g7
rm -rf $G/t59-frames
mkdir -p $G/t59-frames
timeout 300 $G/pcsx2/build/bin/pcsx2-gsrunner -renderer vulkan -dumpdir $G/t59-frames -logfile $G/emulog-t59proof.txt -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- '/home/brad/pcsx2-g7/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs'
echo "=== HWSTAT ==="
grep -A8 STATISTICS $G/emulog-t59proof.txt
echo "=== MD5 ==="
md5sum $G/t59-frames/*.png
echo "=== hook line counts (want 0) ==="
grep -c "ebw vsync=\|ebwlast vsync=\|ebwend vsync=\|T58_CAP\|vu0call vsync=\|vif0op vsync=\|T57_CAP" $G/emulog-t59proof.txt || true
echo T59_REPLAY_DONE
