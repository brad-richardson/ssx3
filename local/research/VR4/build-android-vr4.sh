#!/usr/bin/env bash
# VR4 D1 Android compile (VR3 recipe; source = git archive of beff31f = 5d5c382 + D1, -Pps2xVu1FmacSimd=ON; all other inputs identical to VR3)
# VR3 stage 4 Android compile: VR2 2D's recipe with the source root at
# /home/brad/vr3 (git archive of vr3-fold 5d5c382 streamed from the mini) and
# the VU0 image (-Pps2xVu0RecompDir=/home/brad/vr3/vu0gen, vu0gen-ssx3 copy,
# SHA-verified). Codegen, VU1 images (set d28e3fc6 = vu1gen-ssx3), paraLLEl-GS
# 1b3a294 and jniLibs are VR2 2D's verified inputs under /home/brad/vr2d.
set -euo pipefail
root=/home/brad/vr4
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
ls /home/brad/vr2d/codegen-ssx3 | wc -l
echo "== vu1gen input count =="
ls /home/brad/vr2d/vu1gen | wc -l
echo "== vu0gen input =="
sha256sum /home/brad/vr3/vu0gen/vu0_*.cpp
echo "== parallel-gs knob =="
grep -m1 'PGS_HIER_BINNING' /home/brad/vr2d/parallel-gs/gs/gs_renderer.cpp | cut -c1-80
echo "== gradlew argv =="
echo "$ext/gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=/home/brad/vr2d/codegen-ssx3 -Pps2xGsShadowParallel=ON -Pps2xParallelGsSourceDir=/home/brad/vr2d/parallel-gs -Pps2xJniLibsDir=/home/brad/vr2d/jniLibs -Pps2xVu1RecompDir=/home/brad/vr2d/vu1gen -Pps2xVu0RecompDir=/home/brad/vr3/vu0gen -Pps2xVu1FmacSimd=ON --max-workers=2 --console=plain --warning-mode=none"
"$ext/gradlew" assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir=/home/brad/vr2d/codegen-ssx3 \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir=/home/brad/vr2d/parallel-gs \
  -Pps2xJniLibsDir=/home/brad/vr2d/jniLibs \
  -Pps2xVu1RecompDir=/home/brad/vr2d/vu1gen -Pps2xVu0RecompDir=/home/brad/vr3/vu0gen -Pps2xVu1FmacSimd=ON \
  --max-workers=2 --console=plain --warning-mode=none \
  > "$root/assembleRelease.log" 2>&1
echo "EXIT=0"
sha256sum app/build/outputs/apk/release/*.apk app/build/outputs/apk/release/*.apk 2>/dev/null || true
ls -la app/build/outputs/apk/release/ 2>/dev/null || true
grep -c "vu0_40829a098c260b4f" "$root/assembleRelease.log" || true
find app/.cxx -name "vu0_*.o" 2>/dev/null | head
tail -15 "$root/assembleRelease.log"
