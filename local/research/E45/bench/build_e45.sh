#!/bin/bash
# E45: build the VU1 bench for Odin (arm64 Android) with NDK clang.
# Runs inside bytesize WSL. Expects the e45 pkg dir at ~/e45.
set -u
cd ~/e45 || exit 1
BIN=~/n2/toolchain/android-sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/linux-x86_64/bin
ls "$BIN"/aarch64-linux-android*-clang++ | head -8
CXX=""
for api in 21 24 26; do
  if [ -x "$BIN/aarch64-linux-android${api}-clang++" ]; then CXX="$BIN/aarch64-linux-android${api}-clang++"; break; fi
done
[ -n "$CXX" ] || { echo E45_NO_NDK_CXX; exit 1; }
echo "E45_CXX=$CXX"
"$CXX" --version | head -2

MARCH="-march=armv8-a+fp+simd"
if "$CXX" -march=armv8-a+fp+simd+crypto+crc -x c++ -E /dev/null -o /dev/null 2>/dev/null; then
  MARCH="-march=armv8-a+fp+simd+crypto+crc"
fi
echo "E45_MARCH=$MARCH"

COMMON=(-std=c++20 -O3 -DNDEBUG -DUSE_SSE2NEON "$MARCH" -static-libstdc++ -Iinclude -Ivudetail -I.)
SRCS=(vu/ps2_vu1_core.cpp vu/ps2_vu1_lower.cpp vu/ps2_vu1_upper.cpp bench/e45_stubs.cpp bench/e45_bench.cpp)

echo "== double =="
"$CXX" "${COMMON[@]}" "${SRCS[@]}" -o e45_odin_double 2>&1 | head -20
echo "== quad =="
"$CXX" "${COMMON[@]}" -DPS2X_VU_WIDE_QUAD=1 "${SRCS[@]}" -o e45_odin_quad 2>&1 | head -20

file e45_odin_double e45_odin_quad
sha256sum e45_odin_double e45_odin_quad
ls -l e45_odin_double e45_odin_quad
echo "== soft-float refs (quad must have them, double must not) =="
for b in e45_odin_double e45_odin_quad; do
  echo "-- $b"
  "$BIN"/llvm-nm "$b" 2>/dev/null | grep -c -E "__addtf3|__extendsftf2|__multf3|__eqtf2|__subtf3|__letf2|__getf2" | sed 's/^/TF_REFS=/'
  strings "$b" | grep -c -E "__addtf3|__extendsftf2" | sed 's/^/TF_STRS=/'
done
mkdir -p /mnt/c/Users/bradr/e45out
cp e45_odin_double e45_odin_quad /mnt/c/Users/bradr/e45out/
sha256sum /mnt/c/Users/bradr/e45out/e45_odin_double /mnt/c/Users/bradr/e45out/e45_odin_quad
echo E45_BUILD_DONE
