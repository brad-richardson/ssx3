#!/bin/bash
# N5 build3: n5-android @ tap guard (PS2X_ENABLE_DIAG_TAPS OFF on Android). Regenerate, verify the define,
# ninja -j6 under the memory governor (LOW 3 GB), gradle package, bars on the 321r613w .so + APK member.
N2=~/n2; OUT=~/n5; LOG=$OUT/logs; mkdir -p $LOG
CXX=$N2/PS2Recomp/android/app/.cxx/RelWithDebInfo/321r613w/arm64-v8a
NINJA=$N2/toolchain/android-sdk/cmake/3.22.1/bin/ninja
BIN=$N2/toolchain/android-sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/linux-x86_64/bin
echo "PCSX2_PROCS=$(pgrep -f pcsx2 | wc -l) head=$(git -C $N2/PS2Recomp rev-parse --short HEAD)"
$NINJA -C $CXX build.ninja > $LOG/build3-regen.log 2>&1; echo "REGEN_EXIT=$?"
grep -E '^PS2X_ENABLE_DIAG_TAPS' $CXX/CMakeCache.txt
echo "CC_TAPS0=$(grep -c 'PS2X_ENABLE_DIAG_TAPS=0' $CXX/compile_commands.json) CC_TAPS1=$(grep -c 'PS2X_ENABLE_DIAG_TAPS=1' $CXX/compile_commands.json)"
if ! grep -q '^PS2X_ENABLE_DIAG_TAPS:BOOL=OFF' $CXX/CMakeCache.txt; then echo "TAPS NOT OFF, abort"; exit 4; fi
( peak=0; while true; do u=$(free -m | awk '/^Mem:/{print $3}'); s=$(free -m | awk '/^Swap:/{print $3}'); t=$((u+s)); [ $t -gt $peak ] && peak=$t && echo "$(date -u +%T) mem_used=${u}M swap_used=${s}M peak_total=${peak}M" >> $LOG/build3-mem.txt; sleep 5; done ) &
MON=$!
GOV_LOG=$LOG/build3-governor.txt bash $OUT/mem_governor.sh &
echo "BUILD3_NINJA_START $(date -u +%FT%TZ)"
$NINJA -C $CXX -j6 ps2EntryRunner > $LOG/build3-ninja.log 2>&1
NEXIT=$?
echo "BUILD3_NINJA_END $(date -u +%FT%TZ) EXIT=$NEXIT"
sleep 4
if [ "$NEXIT" != "0" ]; then kill $MON; grep -n -E "FAILED:|error:|Killed" $LOG/build3-ninja.log | head; exit $NEXIT; fi
export JAVA_HOME=$N2/toolchain/jdk-17 ANDROID_HOME=$N2/toolchain/android-sdk ANDROID_SDK_ROOT=$N2/toolchain/android-sdk GRADLE_USER_HOME=$N2/gradle-home
export PATH=$JAVA_HOME/bin:$PATH
cd $N2/PS2Recomp/android
./gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=/home/brad/n5/codegen-ssx3 --max-workers=4 --console=plain >"$LOG/build3-assembleRelease.log" 2>&1
EXIT=$?; kill $MON
echo "BUILD3_GRADLE_END $(date -u +%FT%TZ) EXIT=$EXIT"; tail -1 $LOG/build3-mem.txt
echo "GRADLE_CXX_REBUILT=$(grep -c 'Building CXX' $LOG/build3-assembleRelease.log)"
if [ "$EXIT" != "0" ]; then tail -30 "$LOG/build3-assembleRelease.log"; exit $EXIT; fi
SO=$CXX/../../../../build/intermediates/cxx/RelWithDebInfo/321r613w/obj/arm64-v8a/libps2EntryRunner.so
SO=$N2/PS2Recomp/android/app/build/intermediates/cxx/RelWithDebInfo/321r613w/obj/arm64-v8a/libps2EntryRunner.so
APK=$N2/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk
ls -l --time-style=+%FT%T "$SO" "$APK"; file "$SO"; sha256sum "$SO" "$APK"; sha256sum "$APK"
rm -rf /tmp/n5apk && mkdir /tmp/n5apk && (cd /tmp/n5apk && python3 -c "import zipfile,sys; z=zipfile.ZipFile(sys.argv[1]); [print(i.filename, i.file_size, i.compress_type) for i in z.infolist() if i.filename.startswith('lib/')]; z.extract('lib/arm64-v8a/libps2EntryRunner.so')" "$APK")
PK=/tmp/n5apk/lib/arm64-v8a/libps2EntryRunner.so; sha256sum "$PK"
echo "BUILDID_SO=$($BIN/llvm-readelf -n "$SO" | awk '/Build ID/{print $3}') BUILDID_APK=$($BIN/llvm-readelf -n "$PK" | awk '/Build ID/{print $3}')"
$BIN/llvm-size -A "$SO" | awk '$1==".text"||$1==".data"||$1==".bss"'
$BIN/llvm-nm -S --defined-only "$SO" | grep -E ' [Tt] .*sub_[0-9A-Fa-f]{8}' | awk '{print strtonum("0x"$2)}' | sort -n | awk '{a[NR]=$1; s+=$1} END{print "GUEST n="NR, "median="a[int(NR/2)], "total="s}'
$BIN/llvm-nm -D "$SO" | grep -c ' U .*sub_[0-9A-Fa-f]\{8\}' | sed 's/^/UNDEF_SUB=/'
$BIN/llvm-nm -S --defined-only "$SO" | grep -E 'sub_002127E8|sub_0037E120|sub_001E9A30' | awk '{print $2, $4}'
echo "TAP_SYMS_IN_GUEST_CALLS: noteFast=$($BIN/llvm-nm "$SO" | grep -c 'ps2_e44_trace.*noteFast') e43 noteProdSite=$($BIN/llvm-nm "$SO" | grep -c 'ps2_e43_trace.*noteProdSite') e41 noteFastWriteSite=$($BIN/llvm-nm "$SO" | grep -c 'ps2_e41_trace.*noteFastWriteSite') mpg noteReadCtx=$($BIN/llvm-nm "$SO" | grep -c 'ps2_mpg_src_trace.*noteReadCtx')"
echo "PS2X_TAP_STUB_SYMS=$($BIN/llvm-nm "$SO" | grep -c 'ps2x_tap_')"
$BIN/llvm-nm "$SO" | grep -E ' [Tt] _Z.*calculateFmacExactResult'
for s in PS2X_PAD_SCRIPT_CLOCK PS2X_VSYNC_RATE_LOG '[vsync-rate]' PS2X_FRAME_DUMP_DIR PS2X_SKIP_MOVIE PS2X_E44_TRACE PS2X_E43_TRACE PS2X_MPG_SRC_TRACE PS2X_CD_READ_TRACE; do echo "STR[$s]=$(strings "$PK" | grep -c -F -- "$s")"; done
cp "$APK" $OUT/apk/app-release-notaps.apk; cp "$SO" $OUT/apk/libps2EntryRunner.notaps.unstripped.so; sha256sum $OUT/apk/*notaps*; rm -rf /tmp/n5apk
echo BUILD3_BARS_DONE
