#!/bin/bash
# RR1: replay our converted GS stream through PCSX2 gsrunner (T48 pin build,
# G46 invocation), keep frames for the ticks named in $KEEP (vsync index = tick-1).
set -eu
G=/home/brad/pcsx2-g7
R=/home/brad/rr1
IN=$1; OUT=$R/$2; KEEP=${3:-}
mkdir -p $OUT
cd $G/pcsx2/build/bin
Xvfb :98 -screen 0 1280x1024x24 >/dev/null 2>&1 & XP=$!
export DISPLAY=:98
timeout 1500 ./pcsx2-gsrunner -renderer ${REN:-vulkan} -dumpdir $OUT -logfile $R/gsrunner-$2.log \
  -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- $R/$IN || echo "gsrunner rc=$?"
kill $XP 2>/dev/null || true
ls $OUT | wc -l
ls $OUT | head -3; ls $OUT | tail -3
