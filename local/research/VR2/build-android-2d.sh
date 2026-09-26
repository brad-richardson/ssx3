#!/usr/bin/env bash
# VR2 2D Android compile (F6 recipe, root /home/brad/vr2d): vr2-fold2 d585e5c (rebased on a523700) (git archive
# streamed from the mini) + canonical codegen (symlink to /home/brad/f5's
# verified copy) + vu1gen-ssx3 content (symlink to /home/brad/f5/vu1gen-f5,
# proven byte-identical on the mini) + paraLLEl-GS fork ssx3 1b3a294 (real
# copy, tar-streamed from the mini) + TL1 jniLibs (symlinked from
# /home/brad/f5, verified). Rest is the F5 recipe verbatim (root f6).
set -euo pipefail
root=/home/brad/vr2d
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
echo "== parallel-gs knob =="
grep -m1 'PGS_HIER_BINNING' /home/brad/vr2d/parallel-gs/gs/gs_renderer.cpp | cut -c1-80
echo "== gradlew argv =="
echo "$ext/gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=/home/brad/vr2d/codegen-ssx3 -Pps2xGsShadowParallel=ON -Pps2xParallelGsSourceDir=/home/brad/vr2d/parallel-gs -Pps2xJniLibsDir=/home/brad/vr2d/jniLibs -Pps2xVu1RecompDir=/home/brad/vr2d/vu1gen --max-workers=2 --console=plain --warning-mode=none"
"$ext/gradlew" assembleRelease \
  -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 \
  -Pps2xGameCodegenDir=/home/brad/vr2d/codegen-ssx3 \
  -Pps2xGsShadowParallel=ON \
  -Pps2xParallelGsSourceDir=/home/brad/vr2d/parallel-gs \
  -Pps2xJniLibsDir=/home/brad/vr2d/jniLibs \
  -Pps2xVu1RecompDir=/home/brad/vr2d/vu1gen \
  --max-workers=2 --console=plain --warning-mode=none \
  > "$root/assembleRelease.log" 2>&1
echo "EXIT=0"
tail -15 "$root/assembleRelease.log"
