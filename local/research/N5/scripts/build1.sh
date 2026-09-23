#!/bin/bash
# N5 build1: release APK on n5-android (eac6cba + 6 N-local + E45 + vsync-rate), canonical codegen; + bars.
# One APK serves both (a) dumps-off (no PS2X_FRAME_DUMP_DIR) and (b) PNG dumps (env set).
N2=~/n2; OUT=~/n5; LOG=$OUT/logs; mkdir -p $LOG
export JAVA_HOME=$N2/toolchain/jdk-17
export ANDROID_HOME=$N2/toolchain/android-sdk ANDROID_SDK_ROOT=$N2/toolchain/android-sdk
export GRADLE_USER_HOME=$N2/gradle-home
export PATH=$JAVA_HOME/bin:$PATH
echo "PCSX2_PROCS=$(pgrep -f pcsx2 | wc -l)"
cd $N2/PS2Recomp/android
echo "BUILD1_START $(date -u +%FT%TZ) branch=$(git -C $N2/PS2Recomp rev-parse --abbrev-ref HEAD) head=$(git -C $N2/PS2Recomp rev-parse --short HEAD)"
./gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=/home/brad/n5/codegen-ssx3 --max-workers=4 --console=plain >"$LOG/build1-assembleRelease.log" 2>&1
EXIT=$?
echo "BUILD1_END $(date -u +%FT%TZ) EXIT=$EXIT"
if [ "$EXIT" != "0" ]; then tail -40 "$LOG/build1-assembleRelease.log"; exit $EXIT; fi
SO=$(ls $N2/PS2Recomp/android/app/build/intermediates/cxx/RelWithDebInfo/*/obj/arm64-v8a/libps2EntryRunner.so | head -1)
APK=$N2/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk
echo "SO=$SO"; file "$SO"; ls -l "$SO" "$APK"; sha256sum "$SO" "$APK"; sha256sum "$APK"
BIN=$N2/toolchain/android-sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/linux-x86_64/bin
$BIN/llvm-nm -D "$SO" | grep -c ' U sub_' | sed 's/^/UNDEF_SUB_STAR=/'
$BIN/llvm-nm "$SO" | grep -c ' [Tt] sub_' | sed 's/^/DEFINED_SUB_STAR=/'
$BIN/llvm-nm "$SO" | grep -c -E ' [Tt] _Z.*calculateFmacExactResult' | sed 's/^/FMAC_EXACT_SYMS=/'
$BIN/llvm-nm -g "$SO" | grep -E ' T (ANativeActivity_onCreate|main)$'
for s in PS2X_SKIP_MOVIE PS2X_PAD_SCRIPT PS2X_PAD_SCRIPT_CLOCK PS2X_VSYNC_RATE_LOG '[vsync-rate]' PS2X_FRAME_DUMP_DIR ps2x.env SLUS_207.72; do
  echo "STR[$s]=$(strings "$SO" | grep -c -F -- "$s")"
done
python3 -c "import zipfile,sys; [print(n) for n in zipfile.ZipFile(sys.argv[1]).namelist()]" "$APK"
mkdir -p $OUT/apk && cp "$APK" $OUT/apk/app-release.apk && cp "$SO" $OUT/apk/libps2EntryRunner.unstripped.so && sha256sum $OUT/apk/*
echo BUILD1_BARS_DONE
