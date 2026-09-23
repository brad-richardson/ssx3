#!/usr/bin/env bash
# T66 preservation: G13 replay 7/7 + HWSTAT + zero T66 lines (no arm files present).
set -e
G=/home/brad/pcsx2-g7
rm -f /tmp/t66-arm /tmp/t66-vu-now
rm -rf $G/t66-frames; mkdir -p $G/t66-frames
timeout 300 $G/pcsx2/build/bin/pcsx2-gsrunner -renderer vulkan -dumpdir $G/t66-frames -logfile $G/emulog-t66proof.txt -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- '/home/brad/pcsx2-g7/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs' > /dev/null 2>&1 || echo "gsrunner rc=$?"
echo "=== HWSTAT ==="; grep -A8 STATISTICS $G/emulog-t66proof.txt
echo "=== MD5 ==="; md5sum $G/t66-frames/*.png
echo "=== T66 lines (want 0) ==="; grep -c "t66" $G/emulog-t66proof.txt || true
echo T66_REPLAY_DONE
