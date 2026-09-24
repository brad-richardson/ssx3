#!/usr/bin/env bash
# N8D7M12P3 build: N8D7M1 build.sh adapted to the new root only.
# Preserves Java/SDK/Gradle locations, external codegen, -Pps2xGsShadowParallel=ON,
# new root's parallel-gs/jniLibs, five diagnostic defaults OFF (via project
# defaults, as in N8D7M1), --max-workers=4, and the N8D7M1 memory governor.
set -euo pipefail
root=/home/brad/n8d7m12p3
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
echo "EXIT=0"
tail -15 "$root/assembleRelease.log"
