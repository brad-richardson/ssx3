#!/usr/bin/env bash
# VK1 Android build: F5 recipe (local/research/F5/build-android.sh) with the
# source root at /home/brad/vk1 (git archive of fork branch vk1-present,
# streamed from the mini) and every other input read-only from /home/brad/f5
# (canonical codegen, paraLLEl-GS 19d93b2 copy, TL1 jniLibs, F5 vu1gen).
set -euo pipefail
root=/home/brad/vk1
inp=/home/brad/f5
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
ls $inp/codegen-ssx3 | wc -l
echo "== vu1gen input count =="
ls $inp/vu1gen-f5 | wc -l
echo "== gradlew argv =="
echo "$ext/gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=$inp/codegen-ssx3 -Pps2xGsShadowParallel=ON -Pps2xParallelGsSourceDir=$inp/parallel-gs -Pps2xJniLibsDir=$inp/jniLibs -Pps2xVu1RecompDir=$inp/vu1gen-f5 --max-workers=2 --console=plain --warning-mode=none"
"$ext/gradlew" assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir=$inp/codegen-ssx3 \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir=$inp/parallel-gs \
  -Pps2xJniLibsDir=$inp/jniLibs \
  -Pps2xVu1RecompDir=$inp/vu1gen-f5 \
  --max-workers=2 --console=plain --warning-mode=none \
  > "$root/assembleRelease.log" 2>&1
echo "EXIT=0"
tail -15 "$root/assembleRelease.log"
