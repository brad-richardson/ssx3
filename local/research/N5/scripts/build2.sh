#!/bin/bash
# N5 build2: resume build1's tree with ninja -j6 (build1 OOM'd at ninja's default -j20), then gradle packages + bars.
N2=~/n2; OUT=~/n5; LOG=$OUT/logs; mkdir -p $LOG
CXX=$N2/PS2Recomp/android/app/.cxx/RelWithDebInfo/321r613w/arm64-v8a
NINJA=$N2/toolchain/android-sdk/cmake/3.22.1/bin/ninja
echo "PCSX2_PROCS=$(pgrep -f pcsx2 | wc -l)"
( peak=0; while true; do u=$(free -m | awk '/^Mem:/{print $3}'); s=$(free -m | awk '/^Swap:/{print $3}'); t=$((u+s)); [ $t -gt $peak ] && peak=$t && echo "$(date -u +%T) mem_used=${u}M swap_used=${s}M peak_total=${peak}M" >> $LOG/build2-mem.txt; sleep 5; done ) &
MON=$!
echo "BUILD2_NINJA_START $(date -u +%FT%TZ) head=$(git -C $N2/PS2Recomp rev-parse --short HEAD)"
$NINJA -C $CXX -j6 ps2EntryRunner > $LOG/build2-ninja.log 2>&1
NEXIT=$?
echo "BUILD2_NINJA_END $(date -u +%FT%TZ) EXIT=$NEXIT"
if [ "$NEXIT" != "0" ]; then kill $MON; grep -n -E "FAILED:|error:|Killed" $LOG/build2-ninja.log | head; tail -5 $LOG/build2-mem.txt; exit $NEXIT; fi
export JAVA_HOME=$N2/toolchain/jdk-17
export ANDROID_HOME=$N2/toolchain/android-sdk ANDROID_SDK_ROOT=$N2/toolchain/android-sdk
export GRADLE_USER_HOME=$N2/gradle-home
export PATH=$JAVA_HOME/bin:$PATH
cd $N2/PS2Recomp/android
./gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=/home/brad/n5/codegen-ssx3 --max-workers=4 --console=plain >"$LOG/build2-assembleRelease.log" 2>&1
EXIT=$?
kill $MON
echo "BUILD2_GRADLE_END $(date -u +%FT%TZ) EXIT=$EXIT"; tail -1 $LOG/build2-mem.txt
grep -c 'Building CXX' "$LOG/build2-assembleRelease.log" | sed 's/^/GRADLE_CXX_REBUILT=/'
if [ "$EXIT" != "0" ]; then tail -40 "$LOG/build2-assembleRelease.log"; exit $EXIT; fi
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
python3 -c "import zipfile,sys; [print(n) for n in zipfile.ZipFile(sys.argv[1]).namelist() if not n.startswith(('res/','META-INF/'))]" "$APK"
mkdir -p $OUT/apk && cp "$APK" $OUT/apk/app-release.apk && cp "$SO" $OUT/apk/libps2EntryRunner.unstripped.so && sha256sum $OUT/apk/*
echo BUILD2_BARS_DONE
