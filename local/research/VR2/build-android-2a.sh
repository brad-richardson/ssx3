#!/usr/bin/env bash
# VR2 2A Android compile: F5 recipe (build-android.sh) with root /home/brad/vr2fold:
# streamed from the mini) + PROMOTED canonical codegen (real copy) +
# private F5 vu1gen copy + paraLLEl-GS (f2, 19d93b2 fingerprint) + TL1
# jniLibs (symlinked from /home/brad/f2, verified). Rest is the F4
# recipe verbatim (root f5) plus -Pps2xVu1RecompDir (VR1 6c2de6f).
set -euo pipefail
root=/home/brad/vr2fold
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
ls /home/brad/vr2fold/codegen-ssx3 | wc -l
echo "== vu1gen input count =="
ls /home/brad/vr2fold/vu1gen | wc -l
echo "== gradlew argv =="
echo "$ext/gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=/home/brad/vr2fold/codegen-ssx3 -Pps2xGsShadowParallel=ON -Pps2xParallelGsSourceDir=/home/brad/vr2fold/parallel-gs -Pps2xJniLibsDir=/home/brad/vr2fold/jniLibs -Pps2xVu1RecompDir=/home/brad/vr2fold/vu1gen --max-workers=2 --console=plain --warning-mode=none"
"$ext/gradlew" assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir=/home/brad/vr2fold/codegen-ssx3 \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir=/home/brad/vr2fold/parallel-gs \
  -Pps2xJniLibsDir=/home/brad/vr2fold/jniLibs \
  -Pps2xVu1RecompDir=/home/brad/vr2fold/vu1gen \
  --max-workers=2 --console=plain --warning-mode=none \
  > "$root/assembleRelease.log" 2>&1
echo "EXIT=0"
tail -15 "$root/assembleRelease.log"
