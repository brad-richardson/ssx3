#!/bin/sh
# G14: configure + build parallel-gs-replayer for Android arm64 (NDK r30).
# Preconditions: G14 shims S1-S3 applied to the SSD clone (see g14-shims.diff),
# NDK r30 at /opt/homebrew/share/android-ndk. Host builds -j2.
# Receipts: configure exit 0 (~21 s), build exit 0, binary 265,837,472 B.
set -e
export COPYFILE_DISABLE=1
CLONE="/Volumes/Extreme SSD/parallel-gs-g7"
BUILD="/Volumes/Extreme SSD/parallel-gs-g14-android-build"
NDK=/opt/homebrew/share/android-ndk
cmake -S "$CLONE" -B "$BUILD" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake \
  -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35
cmake --build "$BUILD" --target parallel-gs-replayer -j2
ls -la "$BUILD/tools/parallel-gs-replayer"
shasum -a 256 "$BUILD/tools/parallel-gs-replayer"
