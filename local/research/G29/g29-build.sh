#!/bin/sh
# G29: configure + build ladder-diagnostic parallel-gs-replayer for Android arm64.
# NEW build dir (all older dirs untouched). Host builds -j2.
# Recipe = G22/G26/G28 recipe (NON-sanitizer: no ANDROID_STL override, no
# sanitizer flags) + G28 Granite writer-fix hunk + G29 ladder hunk in
# tools/gs_dump_replayer.cpp (save_scanout_ppm: P1/P2/P3 checksums + VRAM
# checksum, logcat only; files still carry P1 bytes).
# Receipts: configure exit 0, build exit 0 [458/458], binary size/sha/BuildID
# in REPORT.md, G29: strings x1/x2, G28: x1, G26: x1/x2/x0.
set -e
export COPYFILE_DISABLE=1
CLONE="/Volumes/Extreme SSD/parallel-gs-g7"
BUILD="/Volumes/Extreme SSD/parallel-gs-g29-android-build"
NDK=/opt/homebrew/share/android-ndk
cmake -S "$CLONE" -B "$BUILD" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake \
  -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35
cmake --build "$BUILD" --target parallel-gs-replayer -j2
ls -la "$BUILD/tools/parallel-gs-replayer"
shasum -a 256 "$BUILD/tools/parallel-gs-replayer"
