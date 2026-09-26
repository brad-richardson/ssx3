#!/usr/bin/env bash
# FS2 Android build: VR3's build-android-vr3.sh recipe with the source root
# at /home/brad/fs2 (git archive of fork fs2 f6529bf streamed from the mini)
# and PGS at /home/brad/fs2/parallel-gs (PGS fs2 35f4462 + Granite fs2 f0009780 tar from the
# mini). Codegen, VU1 images, VU0 image, jniLibs: VR3/VR2 2D's verified inputs.
set -euo pipefail
root=/home/brad/fs2
ext=/home/brad/n2/PS2Recomp/android
export JAVA_HOME=/home/brad/n2/toolchain/jdk-17
export ANDROID_HOME=/home/brad/n2/toolchain/android-sdk
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export GRADLE_USER_HOME=/home/brad/n2/gradle-home
export PATH="$JAVA_HOME/bin:$PATH"
echo "== versions =="
java -version 2>&1
echo "== pins =="
grep -m1 'FS2' /home/brad/fs2/parallel-gs/gs/gs_renderer.cpp | cut -c1-80
grep -m1 'submit_empty2_ms_per_present' /home/brad/fs2/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp | cut -c1-80
cd "$root/PS2Recomp/android"
"$ext/gradlew" assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir=/home/brad/vr2d/codegen-ssx3 \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir=/home/brad/fs2/parallel-gs \
  -Pps2xJniLibsDir=/home/brad/vr2d/jniLibs \
  -Pps2xVu1RecompDir=/home/brad/vr2d/vu1gen -Pps2xVu0RecompDir=/home/brad/vr3/vu0gen \
  --max-workers=2 --console=plain --warning-mode=none \
  > "$root/assembleRelease.log" 2>&1
echo "EXIT=0"
sha256sum app/build/outputs/apk/release/*.apk app/build/outputs/apk/release/*.apk 2>/dev/null || true
ls -la app/build/outputs/apk/release/ 2>/dev/null || true
tail -5 "$root/assembleRelease.log"
