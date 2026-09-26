#!/usr/bin/env bash
# AP1 Android build: VR3's recipe with the source root at /home/brad/ap1
# (git archive of fork branch ap1 at a2e2953 streamed from the mini) and
# paraLLEl-GS 3d72467 (canonical pin for f0d2d3c; cloned on bytesize).
# Codegen (9457), vu1gen-ssx3 (7 files, SHA-verified), jniLibs (Turnip
# 14188488 B) from /home/brad/vr2d; vu0gen-ssx3 (SHA-verified) from /home/brad/vr3.
set -euo pipefail
root=/home/brad/ap1
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
echo "== ap1 source markers =="
grep -c ap1HideSystemBars "$root/PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp"
grep -n "InitWindow(0, 0, title)" "$root/PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp"
echo "== pgs pin =="
git -C "$root/parallel-gs" log --oneline -1
git -C "$root/parallel-gs" submodule status | head -3
grep -rl PARALLEL_GS_HAS_SAVESTATE_V3 "$root/parallel-gs/gs" | head -2
echo "== codegen input count =="
ls /home/brad/vr2d/codegen-ssx3 | wc -l
echo "== vu1gen input =="
sha256sum /home/brad/vr2d/vu1gen/vu1_*.cpp
echo "== vu0gen input =="
sha256sum /home/brad/vr3/vu0gen/vu0_*.cpp
echo "== jnilibs =="
ls -la /home/brad/vr2d/jniLibs/arm64-v8a/
cd "$root/PS2Recomp/android"
"$ext/gradlew" --version 2>&1 | head -6
echo "== gradlew argv =="
echo "$ext/gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=/home/brad/vr2d/codegen-ssx3 -Pps2xGsShadowParallel=ON -Pps2xParallelGsSourceDir=$root/parallel-gs -Pps2xJniLibsDir=/home/brad/vr2d/jniLibs -Pps2xVu1RecompDir=/home/brad/vr2d/vu1gen -Pps2xVu0RecompDir=/home/brad/vr3/vu0gen --max-workers=2 --console=plain --warning-mode=none"
"$ext/gradlew" assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir=/home/brad/vr2d/codegen-ssx3 \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir=$root/parallel-gs \
  -Pps2xJniLibsDir=/home/brad/vr2d/jniLibs \
  -Pps2xVu1RecompDir=/home/brad/vr2d/vu1gen -Pps2xVu0RecompDir=/home/brad/vr3/vu0gen \
  --max-workers=2 --console=plain --warning-mode=none \
  > "$root/assembleRelease.log" 2>&1
echo "EXIT=0"
sha256sum app/build/outputs/apk/release/*.apk app/build/outputs/apk/release/*.apk 2>/dev/null || true
ls -la app/build/outputs/apk/release/ 2>/dev/null || true
tail -15 "$root/assembleRelease.log"
