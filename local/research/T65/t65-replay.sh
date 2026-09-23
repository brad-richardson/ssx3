#!/usr/bin/env bash
# T65 preservation: G13 replay 7/7 + HWSTAT + zero T65 lines (no arm files present).
set -e
G=/home/brad/pcsx2-g7
rm -f /tmp/t65-arm /tmp/t65-vu-now
rm -rf $G/t65-frames; mkdir -p $G/t65-frames
timeout 300 $G/pcsx2/build/bin/pcsx2-gsrunner -renderer vulkan -dumpdir $G/t65-frames -logfile $G/emulog-t65proof.txt -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- '/home/brad/pcsx2-g7/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs' > /dev/null 2>&1 || echo "gsrunner rc=$?"
echo "=== HWSTAT ==="; grep -A8 STATISTICS $G/emulog-t65proof.txt
echo "=== MD5 ==="; md5sum $G/t65-frames/*.png
echo "=== T65 lines (want 0) ==="; grep -c "T65" $G/emulog-t65proof.txt || true
echo T65_REPLAY_DONE
