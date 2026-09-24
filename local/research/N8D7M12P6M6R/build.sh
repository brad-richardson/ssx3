#!/usr/bin/env bash
# N8D7M12P6M6R build: P3 build.sh with root n8d7m12p6m6 and in-root codegen.
# Preserves Java/SDK/Gradle locations, -Pps2xGsShadowParallel=ON, new root's
# parallel-gs/jniLibs, diagnostic defaults OFF (project defaults, as in P3),
# arm64-v8a, --max-workers=4, and the N8D7M1 memory governor.
# Version prologue records toolchain versions; it does not change the build.
set -euo pipefail
root=/home/brad/n8d7m12p6m6
export JAVA_HOME=/home/brad/n2/toolchain/jdk-17
export ANDROID_HOME=/home/brad/n2/toolchain/android-sdk
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export GRADLE_USER_HOME=/home/brad/n2/gradle-home
export PATH="$JAVA_HOME/bin:$PATH"
echo "== versions =="
java -version 2>&1
echo "-- sdk --"
ls "$ANDROID_HOME/build-tools" "$ANDROID_HOME/platforms" 2>&1
echo "-- ndk --"
cat "$ANDROID_HOME/ndk/28.2.13676358/source.properties" 2>&1
echo "-- cmake --"
ls "$ANDROID_HOME/cmake" 2>&1
"$ANDROID_HOME/cmake/3.22.1/bin/cmake" --version 2>&1 | head -1
echo "-- gradle --"
cd "$root/PS2Recomp/android"
./gradlew --version 2>&1 | head -12
echo "== codegen input count =="
ls "$root/codegen-ssx3" | wc -l
ls "$root/codegen-ssx3/"*.cpp 2>/dev/null | wc -l
echo "== gradlew argv =="
echo "./gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=$root/codegen-ssx3 -Pps2xGsShadowParallel=ON -Pps2xParallelGsSourceDir=$root/parallel-gs -Pps2xJniLibsDir=$root/jniLibs --max-workers=4 --console=plain --warning-mode=none"
GOV_LOG="$root/governor.log" bash /home/brad/n8b1/mem_governor.sh &
governor=$!
trap 'kill "$governor" 2>/dev/null || true' EXIT
./gradlew assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir="$root/codegen-ssx3" \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir="$root/parallel-gs" \
  -Pps2xJniLibsDir="$root/jniLibs" \
  --max-workers=4 --console=plain --warning-mode=none \
  > "$root/assembleRelease.log" 2>&1
echo "EXIT=0"
tail -15 "$root/assembleRelease.log"
