#!/usr/bin/env bash
# T50 preservation proof: replay the G13 rich dump with the patched gsrunner;
# PNG md5s + HWSTAT must match the G13/T48 pins exactly.
set -e
G=/home/brad/pcsx2-g7
rm -rf $G/t50-frames
mkdir -p $G/t50-frames
timeout 300 $G/pcsx2/build/bin/pcsx2-gsrunner -renderer vulkan -dumpdir $G/t50-frames -logfile $G/emulog-t50proof.txt -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- '/home/brad/pcsx2-g7/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs'
echo "=== HWSTAT ==="
grep -A8 STATISTICS $G/emulog-t50proof.txt
echo "=== MD5 ==="
md5sum $G/t50-frames/*.png
echo "=== T50 line counts (want all 0: gsrunner runs no EE) ==="
grep -c "srcread " $G/emulog-t50proof.txt || true
grep -c "T48_VU1" $G/emulog-t50proof.txt || true
echo T50_REPLAY_DONE
