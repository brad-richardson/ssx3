#!/bin/bash
# N5 build2 bars, fixed: probe the 321r613w (n5-android config) .so and the .so packaged in the APK.
N2=~/n2; OUT=~/n5
BIN=$N2/toolchain/android-sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/linux-x86_64/bin
APK=$N2/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk
ls -l --time-style=+%FT%T $N2/PS2Recomp/android/app/build/intermediates/cxx/RelWithDebInfo/*/obj/arm64-v8a/libps2EntryRunner.so
SO=$N2/PS2Recomp/android/app/build/intermediates/cxx/RelWithDebInfo/321r613w/obj/arm64-v8a/libps2EntryRunner.so
file "$SO"; sha256sum "$SO"
rm -rf /tmp/n5apk && mkdir /tmp/n5apk && cd /tmp/n5apk && python3 -c "import zipfile,sys; z=zipfile.ZipFile(sys.argv[1]); [print(i.filename, i.file_size, i.compress_size, i.compress_type) for i in z.infolist() if i.filename.startswith('lib/')]; z.extract('lib/arm64-v8a/libps2EntryRunner.so')" "$APK"
PK=/tmp/n5apk/lib/arm64-v8a/libps2EntryRunner.so
file "$PK"; sha256sum "$PK"
echo "BUILDID_SO=$($BIN/llvm-readelf -n "$SO" | awk '/Build ID/{print $3}') BUILDID_APK=$($BIN/llvm-readelf -n "$PK" | awk '/Build ID/{print $3}')"
for F in "$SO" "$PK"; do
  echo "== $F"
  $BIN/llvm-nm -D "$F" | grep -c ' U sub_' | sed 's/^/UNDEF_SUB_STAR=/'
  $BIN/llvm-nm -D --defined-only "$F" | grep -c ' sub_' | sed 's/^/DYN_DEFINED_SUB_STAR=/'
done
$BIN/llvm-nm "$SO" | grep -c -E ' [Tt] sub_' | sed 's/^/SYMTAB_SUB_STAR=/'
$BIN/llvm-nm "$SO" | grep -E ' [Tt] _Z.*calculateFmacExactResult'
$BIN/llvm-nm "$SO" | grep -c -E '__(addtf3|multf3|extendsftf2)$' | sed 's/^/QUAD_SOFTFLOAT_SYMS=/'
for s in PS2X_SKIP_MOVIE PS2X_PAD_SCRIPT PS2X_PAD_SCRIPT_CLOCK PS2X_VSYNC_RATE_LOG '[vsync-rate]' PS2X_FRAME_DUMP_DIR PS2X_PAD_LOG ps2x.env SLUS_207.72; do
  echo "STR[$s]=$(strings "$PK" | grep -c -F -- "$s")"
done
cp "$SO" $OUT/apk/libps2EntryRunner.unstripped.so; sha256sum $OUT/apk/*
cd ~; rm -rf /tmp/n5apk
