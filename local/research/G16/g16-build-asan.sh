#!/bin/sh
# G16: configure + build ASan+UBSan parallel-gs-replayer for mac host.
# New build dir (G13/G14/G15 dirs untouched). Host build -j2, one target.
# Recipe = G7/G13 mac recipe (VULKAN_SDK=/opt/homebrew, Ninja, no build type)
# + sanitizer flags only. Compiler note: shell env already exports
# CC=/opt/homebrew/opt/llvm/bin/clang (Homebrew LLVM 23.1.1); the G13 mac
# build mixed that C compiler with Apple CXX. ASan needs ONE runtime, so
# CXX is set to the same Homebrew LLVM (tabled delta in REPORT §2b).
# Expected receipts: configure exit 0, build exit 0, __asan symbols present.
set -e
export COPYFILE_DISABLE=1
CLONE="/Volumes/Extreme SSD/parallel-gs-g7"
BUILD="/Volumes/Extreme SSD/parallel-gs-g16-asan-build"
export VULKAN_SDK=/opt/homebrew
export CC=/opt/homebrew/opt/llvm/bin/clang
export CXX=/opt/homebrew/opt/llvm/bin/clang++
cmake -S "$CLONE" -B "$BUILD" -G Ninja \
  "-DCMAKE_C_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer" \
  "-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer" \
  "-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined"
cmake --build "$BUILD" --target parallel-gs-replayer -j2
ls -la "$BUILD/tools/parallel-gs-replayer"
shasum -a 256 "$BUILD/tools/parallel-gs-replayer"
