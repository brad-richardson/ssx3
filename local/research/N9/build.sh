#!/usr/bin/env bash
# N9 Part 2 THE ONE BUILD: assembleRelease from the pushed fork tips.
# Adapted from N8D7M12P6M6R/build2.sh (root n9). Invokes the EXTERNAL pinned
# wrapper /home/brad/n8d7m12p3/PS2Recomp/android/gradlew as a build tool from
# the new-root android cwd. No file is copied into the four staged source
# roots. Preserves Java/SDK/Gradle locations, -Pps2xGsShadowParallel=ON, the
# new root's parallel-gs/jniLibs/codegen, diagnostics OFF (in-repo defaults
# at fb11e18 incl. the N8B1 repair), arm64-v8a, --max-workers=4, and the
# N8D7M1 memory governor.
set -euo pipefail
root=/home/brad/n9
ext=/home/brad/n8d7m12p3/PS2Recomp/android
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
echo "-- wrapper pins in use (single read; double reads in wrapper-pins.txt) --"
sha256sum "$ext/gradlew" "$ext/gradle/wrapper/gradle-wrapper.jar"
cd "$root/PS2Recomp/android"
echo "-- gradle (external wrapper targeting new-root project) --"
"$ext/gradlew" --version 2>&1 | head -14
echo "== codegen input count =="
ls "$root/codegen-ssx3" | wc -l
ls "$root/codegen-ssx3/"*.cpp 2>/dev/null | wc -l
echo "== gradlew argv =="
echo "$ext/gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=$root/codegen-ssx3 -Pps2xGsShadowParallel=ON -Pps2xParallelGsSourceDir=$root/parallel-gs -Pps2xJniLibsDir=$root/jniLibs --max-workers=4 --console=plain --warning-mode=none"
echo "== cwd =="
pwd
GOV_LOG="$root/governor.log" bash /home/brad/n8b1/mem_governor.sh &
governor=$!
trap 'kill "$governor" 2>/dev/null || true' EXIT
"$ext/gradlew" assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir="$root/codegen-ssx3" \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir="$root/parallel-gs" \
  -Pps2xJniLibsDir="$root/jniLibs" \
  --max-workers=4 --console=plain --warning-mode=none \
  > "$root/assembleRelease.log" 2>&1
echo "EXIT=0"
tail -15 "$root/assembleRelease.log"
