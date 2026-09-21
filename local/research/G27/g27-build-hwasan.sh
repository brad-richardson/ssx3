#!/bin/sh
# G27: configure + build HWASan parallel-gs-replayer for Android arm64.
# NEW build dir (all older dirs untouched). Host builds -j2.
# Recipe = G22/G26 recipe + G15 HWASan flags (-DANDROID_STL=c++_shared +
# -fsanitize=hwaddress -fno-omit-frame-pointer -mllvm -hwasan-globals=0).
# ZERO source edits (build flags only; G26 narrower hunk stays in tree).
# Receipts: configure exit 0, build exit 0 [458/458], binary 289,112,232 B,
# sha 6387d2f3..., BuildID 52977886..., 164 __hwasan symbols,
# NEEDED libclang_rt.hwasan + libc++_shared.
set -e
export COPYFILE_DISABLE=1
CLONE="/Volumes/Extreme SSD/parallel-gs-g7"
BUILD="/Volumes/Extreme SSD/parallel-gs-g27-hwasan-build"
NDK=/opt/homebrew/share/android-ndk
cmake -S "$CLONE" -B "$BUILD" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake \
  -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35 \
  -DANDROID_STL=c++_shared \
  "-DCMAKE_C_FLAGS=-fsanitize=hwaddress -fno-omit-frame-pointer -mllvm -hwasan-globals=0" \
  "-DCMAKE_CXX_FLAGS=-fsanitize=hwaddress -fno-omit-frame-pointer -mllvm -hwasan-globals=0" \
  -DCMAKE_EXE_LINKER_FLAGS="-fsanitize=hwaddress"
cmake --build "$BUILD" --target parallel-gs-replayer -j2
ls -la "$BUILD/tools/parallel-gs-replayer"
shasum -a 256 "$BUILD/tools/parallel-gs-replayer"
