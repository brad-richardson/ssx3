#!/bin/bash
# G46: replay the recomp's recorded GS stream (g46a.gs.zst, converted by
# g46_rec2gs.py) through PCSX2 gsrunner (T48 pin 9056c083, post-patch
# gsrunner) and keep only the frames that match the shadow pair ticks.
# Run inside bytesize WSL. One PNG per vsync; frame N = the Nth vsync = the
# Nth line of g46a.gs.ticks (tick column).
set -eu
G=/home/brad/pcsx2-g7
OUT=$G/g46/frames
mkdir -p $OUT
cd $G/pcsx2/build/bin
timeout 1800 ./pcsx2-gsrunner -renderer ${REN:-vulkan} -dumpdir $OUT -logfile $G/g46/gsrunner.log \
  -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini -- $G/g46/g46a.gs.zst
ls $OUT | wc -l
