#!/bin/bash
# N4 build4: release on rebased n2-android (e57b5f8 + shim + arm64-only + N4 manifest/PNG fix) + bars, foreground
N2=~/n2; LOG=$N2/logs
export JAVA_HOME=$N2/toolchain/jdk-17
export ANDROID_HOME=$N2/toolchain/android-sdk ANDROID_SDK_ROOT=$N2/toolchain/android-sdk
export GRADLE_USER_HOME=$N2/gradle-home
export PATH=$JAVA_HOME/bin:$PATH
cd $N2/PS2Recomp/android
echo "BUILD4_START $(date -u +%FT%TZ) branch=$(git -C $N2/PS2Recomp rev-parse --abbrev-ref HEAD) head=$(git -C $N2/PS2Recomp rev-parse --short HEAD)"
./gradlew assembleRelease -Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72 -Pps2xGameCodegenDir=/home/brad/n2/c17-codegen/codegen-output --max-workers=4 --console=plain >"$LOG/build4-assembleRelease.log" 2>&1
EXIT=$?
echo "$EXIT" > "$LOG/build4-exit.txt"
echo "BUILD4_END $(date -u +%FT%TZ) EXIT=$EXIT"
if [ "$EXIT" != "0" ]; then
  tail -40 "$LOG/build4-assembleRelease.log"
  exit $EXIT
fi
# --- bars ---
SO=$(ls $N2/PS2Recomp/android/app/build/intermediates/cxx/RelWithDebInfo/*/obj/arm64-v8a/libps2EntryRunner.so 2>/dev/null | head -1)
APK=$N2/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk
echo "SO=$SO"
file "$SO"
ls -l "$SO" "$APK"
sha256sum "$SO" "$APK"
NM=$N2/toolchain/android-sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-nm
$NM -D "$SO" | grep -c ' U sub_' | sed 's/^/UNDEF_SUB_STAR=/'
$NM -g "$SO" | grep -c ' T sub_' | sed 's/^/DEFINED_SUB_STAR_RAW=/'
$NM -g "$SO" | grep ' T .*ANativeActivity_onCreate' | head -2
$NM -g "$SO" | grep ' T main$' | head -2
for s in PS2X_SKIP_MOVIE PS2X_PAD_SCRIPT ps2x.env 'ps2x.env: set ' SLUS_207.72 DEINTERLACE; do
  c=$(strings "$SO" | grep -c -F "$s" || true)
  echo "STR[$s]=$c"
done
grep -c "writePngBytes" $N2/PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp | sed 's/^/WRITEPNGBYTES_SRC=/' || true
python3 -c "import zipfile,sys; [print(n) for n in zipfile.ZipFile(sys.argv[1]).namelist()]" "$APK"
echo BUILD4_BARS_DONE
