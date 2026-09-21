#!/bin/sh
# G15: configure + build HWASan parallel-gs-replayer for Android arm64.
# Second build dir (G14 dir untouched). Host builds -j2.
# NOTE: static libc++ (G14 default) FAILS at link under -fsanitize=hwaddress
# (R_AARCH64_ADR_PREL_PG_HI21 out of range in libc++_static.a string.cpp.o);
# -DANDROID_STL=c++_shared fixes it (G15 §2f). -mllvm -hwasan-globals=0 keeps
# heap/stack checks, skips global tagging (heap is the target).
# Receipts: configure exit 0, build exit 0 [452/452], binary 289,108,176 B,
# sha b93bb69a..., NEEDED libclang_rt.hwasan-aarch64-android.so + libc++_shared.
set -e
export COPYFILE_DISABLE=1
CLONE="/Volumes/Extreme SSD/parallel-gs-g7"
BUILD="/Volumes/Extreme SSD/parallel-gs-g15-hwasan-build"
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
