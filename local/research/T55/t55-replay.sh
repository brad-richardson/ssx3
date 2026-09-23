#!/usr/bin/env bash
# T55 preservation proof: replay the G13 rich dump with the patched gsrunner;
# PNG md5s + HWSTAT must match the T48 pins exactly; zero T55 lines.
# Pins (T51 §T51-3): md5s b7a3e8db a7929218 bb8b1d85 817e934f x2 85cf3599 x2,
# HWSTAT 791/37/0/14/320/6.
set -e
G=/home/brad/pcsx2-g7
rm -rf $G/t55-frames
mkdir -p $G/t55-frames
timeout 300 $G/pcsx2/build/bin/pcsx2-gsrunner -renderer vulkan -dumpdir $G/t55-frames -logfile $G/emulog-t55proof.txt -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- '/home/brad/pcsx2-g7/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs'
echo "=== HWSTAT ==="
grep -A8 STATISTICS $G/emulog-t55proof.txt
echo "=== MD5 ==="
md5sum $G/t55-frames/*.png
echo "=== T55 line counts (want all 0: gsrunner runs no EE) ==="
grep -c "h394 vsync=\|T55_CAP" $G/emulog-t55proof.txt || true
grep -c "T48_VU1" $G/emulog-t55proof.txt || true
echo T55_REPLAY_DONE
