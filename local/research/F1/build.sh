#!/usr/bin/env bash
# F1 Part 2 THE ONE BUILD: assembleRelease from pushed fork ssx3 56a5e8a + TL1-verified inputs.
# Adapted from N11/build.sh (root f1). PS2Recomp = git archive 56a5e8a;
# codegen/parallel-gs/jniLibs = /home/brad/tl1/* (byte-verified vs TL1 manifest).
set -euo pipefail
root=/home/brad/f1
ext=/home/brad/n2/PS2Recomp/android
export JAVA_HOME=/home/brad/n2/toolchain/jdk-17
export ANDROID_HOME=/home/brad/n2/toolchain/android-sdk
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export GRADLE_USER_HOME=/home/brad/n2/gradle-home
export PATH="$JAVA_HOME/bin:$PATH"
echo "== versions =="
java -version 2>&1
echo "-- wrapper pins --"
sha256sum "$ext/gradlew" "$ext/gradle/wrapper/gradle-wrapper.jar"
cd "$root/PS2Recomp/android"
"$ext/gradlew" --version 2>&1 | head -6
echo "== codegen input count =="
ls /home/brad/f1/codegen-ssx3 | wc -l
echo "== gradlew argv =="
echo "$ext/gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=/home/brad/f1/codegen-ssx3 -Pps2xGsShadowParallel=ON -Pps2xParallelGsSourceDir=/home/brad/f1/parallel-gs -Pps2xJniLibsDir=/home/brad/f1/jniLibs --max-workers=2 --console=plain --warning-mode=none"
"$ext/gradlew" assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir=/home/brad/f1/codegen-ssx3 \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir=/home/brad/f1/parallel-gs \
  -Pps2xJniLibsDir=/home/brad/f1/jniLibs \
  --max-workers=2 --console=plain --warning-mode=none \
  > "$root/assembleRelease.log" 2>&1
echo "EXIT=0"
tail -15 "$root/assembleRelease.log"
