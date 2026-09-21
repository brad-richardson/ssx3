#!/usr/bin/env bash
# G10: pcsx2-gsrunner build + bounded replay recipe (runs INSIDE WSL as brad).
# Pinned tree: /home/brad/pcsx2-g7/pcsx2 @ 9056c08349 (G8 trigger hunks present,
# dormant under dump replay: no EE, ExecPS2 counter stays 0, trigger inert).
# Renderer is vulkan-on-llvmpipe, NOT sw: the sw GSDevice needs a GL context
# and GL context creation fails headless AND under Xvfb (:99) at this rev
# (verified failure, exit 1, "Failed to create GS device"). Vulkan creates
# its device surfaceless via lavapipe. Geometry is renderer-independent
# (uncorrected = m_real_size from display regs).
set -u
SRC=/home/brad/pcsx2-g7/pcsx2
BUILD=/home/brad/pcsx2-g7/pcsx2/build
BIN=$BUILD/bin/pcsx2-gsrunner
DUMP="/home/brad/pcsx2-g7/dat-g8/PCSX2/snaps/SSX 3_SLUS-20772_20260920212606.gs"
INI=/home/brad/pcsx2-g7/g10-uncorrected.ini   # staged via scp (no wsl redirect)
OUT=/home/brad/pcsx2-g7/g10-frames

# 1. reconfigure (cache reuse: Ninja, Devel, clang, /home/brad/deps)
cmake -S $SRC -B $BUILD -DENABLE_GSRUNNER=ON
# 2. build (119 steps: libzip + Main.cpp + link)
cmake --build $BUILD --target pcsx2-gsrunner -j2
echo "BUILD_EXIT:$?"
stat -c "%s %n" $BIN
# 3. ini: [EmuCore/GS] + ScreenshotSize = 2 (InternalResolutionUncorrected)
cat $INI
mkdir -p $OUT
# 4. bounded replay: existing dump only, 300 s wall cap, loop 2 (project recipe)
timeout 300 $BIN -renderer vulkan -dumpdir $OUT -logfile $OUT/emulog.txt \
  -loop 2 -noshadercache -surfaceless -ini $INI -- "$DUMP"
echo "RUN_EXIT:$?"
ls -la $OUT
# Expect: 7 PNGs {title}_frame00001..00007.png (512x448 uncorrected) + emulog.
# File N names post-dump-vsync#(N-1) state; the final present never snapshots
# (no _frame00000, no _frame00008) at this rev. Loop-1 output is byte-identical
# (verified by md5); retrieve one set via /mnt/c staging + scp (G8 shape).
