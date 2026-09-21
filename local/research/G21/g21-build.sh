#!/bin/bash
# g21-build.sh — build the G21 minimal repro for Android arm64 (host-side).
# Writes ONLY to /Volumes/Extreme SSD/ps2x-g21/. No device, no network.
set -euo pipefail
export COPYFILE_DISABLE=1
SSD="/Volumes/Extreme SSD"
OUT="$SSD/ps2x-g21"
NDK=/opt/homebrew/share/android-ndk
CC="$NDK/toolchains/llvm/prebuilt/darwin-x86_64/bin/aarch64-linux-android35-clang"

mkdir -p "$OUT"
cp /Users/bradrichardson/dev/ssx3/local/research/G21/g21-minrepro.c "$OUT/g21-minrepro.c"
cp "$SSD/ps2x-g20/g20-sampler-feedback.spv" "$OUT/g21-sampler-feedback.spv"

"$CC" -O2 -Wall -Wextra -std=c11 -Wl,--build-id \
  --sysroot="$NDK/toolchains/llvm/prebuilt/darwin-x86_64/sysroot" \
  -o "$OUT/g21-minrepro" "$OUT/g21-minrepro.c" -ldl 2>&1 | tee "$OUT/g21-build.log"

echo "--- identity ---" | tee -a "$OUT/g21-build.log"
ls -l "$OUT/g21-minrepro" | tee -a "$OUT/g21-build.log"
shasum -a 256 "$OUT/g21-minrepro" "$OUT/g21-sampler-feedback.spv" | tee -a "$OUT/g21-build.log"
file "$OUT/g21-minrepro" | tee -a "$OUT/g21-build.log"
"$NDK/toolchains/llvm/prebuilt/darwin-x86_64/bin/llvm-readelf" --notes "$OUT/g21-minrepro" 2>&1 | tee -a "$OUT/g21-build.log"
du -sk "$OUT" | tee -a "$OUT/g21-build.log"
