#!/usr/bin/env bash
# T57 preservation proof: replay the G13 rich dump with the patched gsrunner;
# PNG md5s + HWSTAT must match the T48 pins exactly; zero T57 lines.
# Pins (T51 S51-3): md5s b7a3e8db a7929218 bb8b1d85 817e934f x2 85cf3599 x2,
# HWSTAT 791/37/0/14/320/6.
set -e
G=/home/brad/pcsx2-g7
rm -rf $G/t57-frames
mkdir -p $G/t57-frames
timeout 300 $G/pcsx2/build/bin/pcsx2-gsrunner -renderer vulkan -dumpdir $G/t57-frames -logfile $G/emulog-t57proof.txt -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- '/home/brad/pcsx2-g7/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs'
echo "=== HWSTAT ==="
grep -A8 STATISTICS $G/emulog-t57proof.txt
echo "=== MD5 ==="
md5sum $G/t57-frames/*.png
echo "=== T57 line counts (want all 0: gsrunner runs no EE/VIF) ==="
grep -c "vu0call vsync=\|vif0op vsync=\|T57_CAP" $G/emulog-t57proof.txt || true
grep -c "T48_VU1" $G/emulog-t57proof.txt || true
echo T57_REPLAY_DONE
