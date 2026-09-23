#!/usr/bin/env bash
# T48 preservation proof: replay the G13 rich dump with the patched gsrunner;
# PNG md5s + HWSTAT must match the G13 pins exactly.
set -e
G=/home/brad/pcsx2-g7
rm -rf $G/t48-frames
mkdir -p $G/t48-frames
timeout 300 $G/pcsx2/build/bin/pcsx2-gsrunner -renderer vulkan -dumpdir $G/t48-frames -logfile $G/emulog-t48proof.txt -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- '/home/brad/pcsx2-g7/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs'
echo "=== HWSTAT ==="
grep -A8 STATISTICS $G/emulog-t48proof.txt
echo "=== MD5 ==="
md5sum $G/t48-frames/*.png
echo "=== T48/G12 line counts ==="
grep -c "G12_DRAW" $G/emulog-t48proof.txt || true
grep -c "G12_RASTER" $G/emulog-t48proof.txt || true
grep -c "G12_VSYNC" $G/emulog-t48proof.txt || true
grep -c "T48_PATHS" $G/emulog-t48proof.txt || true
grep -c "T48_VU1" $G/emulog-t48proof.txt || true
echo T48_REPLAY_DONE
