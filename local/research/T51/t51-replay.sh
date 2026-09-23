#!/usr/bin/env bash
# T51 preservation proof: replay the G13 rich dump with the patched gsrunner;
# PNG md5s + HWSTAT must match the T48 pins exactly; zero T51 lines.
set -e
G=/home/brad/pcsx2-g7
rm -rf $G/t51-frames
mkdir -p $G/t51-frames
timeout 300 $G/pcsx2/build/bin/pcsx2-gsrunner -renderer vulkan -dumpdir $G/t51-frames -logfile $G/emulog-t51proof.txt -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- '/home/brad/pcsx2-g7/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs'
echo "=== HWSTAT ==="
grep -A8 STATISTICS $G/emulog-t51proof.txt
echo "=== MD5 ==="
md5sum $G/t51-frames/*.png
echo "=== T51 line counts (want all 0: gsrunner runs no EE) ==="
grep -c "st vsync=\|sema vsync=\|irq vsync=\|gsreg vsync=\|T51_WINDOW" $G/emulog-t51proof.txt || true
grep -c "T48_VU1" $G/emulog-t51proof.txt || true
echo T51_REPLAY_DONE
