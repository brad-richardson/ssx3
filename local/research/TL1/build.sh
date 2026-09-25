#!/usr/bin/env bash
# TL1 Part 2 THE ONE BUILD: assembleRelease from the pushed fork tips.
# Adapted from N9/build.sh (root tl1). Differences from N9, all recorded:
#  - external wrapper is /home/brad/n2/PS2Recomp/android (gradle-8.9, jar
#    present, dist cached): the N9 wrapper root n8d7m12p3 was cleaned up.
#  - --max-workers=2 (N9 used 4 with the n8b1 memory governor, also cleaned
#    up); worker count is not baked into the artifact. Same 9 GB box.
#  - fork root is PS2Recomp ssx3 f949ff0 (N9: fb11e18); parallel-gs/codegen/
#    jniLibs are byte-identical to N9's verified manifest (see REPORT).
set -euo pipefail
root=/home/brad/tl1
ext=/home/brad/n2/PS2Recomp/android
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
echo "-- wrapper pins in use (single read; double reads in REPORT) --"
sha256sum "$ext/gradlew" "$ext/gradle/wrapper/gradle-wrapper.jar"
cd "$root/PS2Recomp/android"
echo "-- gradle (external wrapper targeting new-root project) --"
"$ext/gradlew" --version 2>&1 | head -14
echo "== codegen input count =="
ls "$root/codegen-ssx3" | wc -l
ls "$root/codegen-ssx3/"*.cpp 2>/dev/null | wc -l
echo "== gradlew argv =="
echo "$ext/gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=$root/codegen-ssx3 -Pps2xGsShadowParallel=ON -Pps2xParallelGsSourceDir=$root/parallel-gs -Pps2xJniLibsDir=$root/jniLibs --max-workers=2 --console=plain --warning-mode=none"
echo "== cwd =="
pwd
"$ext/gradlew" assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir="$root/codegen-ssx3" \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir="$root/parallel-gs" \
  -Pps2xJniLibsDir="$root/jniLibs" \
  --max-workers=2 --console=plain --warning-mode=none \
  > "$root/assembleRelease.log" 2>&1
echo "EXIT=0"
tail -15 "$root/assembleRelease.log"
