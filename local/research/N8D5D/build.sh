#!/usr/bin/env bash
set -euo pipefail
root=/home/brad/n8d5d
export JAVA_HOME=/home/brad/n2/toolchain/jdk-17
export ANDROID_HOME=/home/brad/n2/toolchain/android-sdk
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export GRADLE_USER_HOME=/home/brad/n2/gradle-home
export PATH="$JAVA_HOME/bin:$PATH"
cd "$root/PS2Recomp/android"
GOV_LOG="$root/governor.log" bash /home/brad/n8b1/mem_governor.sh &
governor=$!
trap 'kill "$governor" 2>/dev/null || true' EXIT
./gradlew assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir=/home/brad/n8b1/codegen-ssx3 \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir="$root/parallel-gs" \
  -Pps2xJniLibsDir="$root/jniLibs" \
  --max-workers=4 --console=plain --warning-mode=none \
  > "$root/assembleRelease.log" 2>&1
