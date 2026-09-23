#!/usr/bin/env bash
# T52 preservation proof: replay the G13 rich dump with the patched gsrunner;
# PNG md5s + HWSTAT must match the T48 pins exactly; zero T52 lines
# (gsrunner replay performs no disc reads).
set -e
G=/home/brad/pcsx2-g7
rm -rf $G/t52-frames
mkdir -p $G/t52-frames
timeout 300 $G/pcsx2/build/bin/pcsx2-gsrunner -renderer vulkan -dumpdir $G/t52-frames -logfile $G/emulog-t52proof.txt -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- '/home/brad/pcsx2-g7/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs'
echo "=== HWSTAT ==="
grep -A8 STATISTICS $G/emulog-t52proof.txt
echo "=== MD5 ==="
md5sum $G/t52-frames/*.png
echo "=== T52 line counts (want 0) ==="
grep -c "T52_CDREAD\|T52_MARK" $G/emulog-t52proof.txt || true
echo T52_REPLAY_DONE
