#!/usr/bin/env bash
# F2 Part 2 THE ONE BUILD: assembleRelease from pushed fork ssx3 92f9991
# (F2 fold + ST1 progressive scanout) + promoted canonical codegen +
# paraLLEl-GS 19d93b2 + TL1 jniLibs. Adapted from F1/build.sh (root np1b).
# PS2Recomp = git archive 92f9991; codegen = mini canonical (SBR regen);
# parallel-gs = mini F2 worktree at 19d93b2 (Granite identical to TL1's);
# jniLibs = /home/brad/tl1/jniLibs (byte-verified vs TL1 manifest).
set -euo pipefail
root=/home/brad/np1b
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
ls /home/brad/np1b/codegen-ssx3 | wc -l
echo "== gradlew argv =="
echo "$ext/gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=/home/brad/np1b/codegen-ssx3 -Pps2xGsShadowParallel=ON -Pps2xParallelGsSourceDir=/home/brad/np1b/parallel-gs -Pps2xJniLibsDir=/home/brad/np1b/jniLibs --max-workers=2 --console=plain --warning-mode=none"
"$ext/gradlew" assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir=/home/brad/np1b/codegen-ssx3 \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir=/home/brad/np1b/parallel-gs \
  -Pps2xJniLibsDir=/home/brad/np1b/jniLibs \
  --max-workers=2 --console=plain --warning-mode=none \
  > "$root/assembleRelease.log" 2>&1
echo "EXIT=0"
tail -15 "$root/assembleRelease.log"
