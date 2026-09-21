#!/bin/sh
# G27: ONE bounded HWASan on-device replay (rich dump, flag SET) + pulls + cleanup.
# Wall cap: device-side `timeout -s KILL 280`. /data/local/tmp/g27/ ONLY
# (never mg/). HWASan needs its two sidecar .so files + LD_LIBRARY_PATH
# (no wrap.sh: shell-launched binary inherits env directly, G15 precedent).
# Sanitizer options verbatim: HWASAN_OPTIONS=halt_on_error=1.
# G27 result: exit 134, HWASan allocation-tail-overwritten fired (writer
# named), 10 scanouts wrote, Done! printed, death in Device teardown.
set -e
export COPYFILE_DISABLE=1
DEV=622c49b1
G27DIR=/data/local/tmp/g27
SSD27="/Volumes/Extreme SSD/ps2x-g27"
HWBUILD="/Volumes/Extreme SSD/parallel-gs-g27-hwasan-build"
NDK=/opt/homebrew/share/android-ndk
adb -s $DEV shell "rm -rf $G27DIR && mkdir -p $G27DIR"
adb -s $DEV push "/Volumes/Extreme SSD/ps2x-g13/g13-dump.gs" $G27DIR/g13-dump.gs
adb -s $DEV push "$HWBUILD/tools/parallel-gs-replayer" $G27DIR/hwasan-replayer
adb -s $DEV push "$NDK/toolchains/llvm/prebuilt/darwin-x86_64/sysroot/usr/lib/aarch64-linux-android/libc++_shared.so" $G27DIR/
adb -s $DEV push "$NDK/toolchains/llvm/prebuilt/darwin-x86_64/lib/clang/21/lib/linux/libclang_rt.hwasan-aarch64-android.so" $G27DIR/
adb -s $DEV shell "cd $G27DIR && chmod 755 hwasan-replayer && sha256sum g13-dump.gs hwasan-replayer libc++_shared.so libclang_rt.hwasan-aarch64-android.so"
adb -s $DEV logcat -c
adb -s $DEV shell "cd $G27DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 HWASAN_OPTIONS=halt_on_error=1 LD_LIBRARY_PATH=$G27DIR timeout -s KILL 280 ./hwasan-replayer $G27DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g27-run-stdout.txt 2> g27-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
adb -s $DEV logcat -d -s Granite:V > "$SSD27/g27-logcat.txt"
adb -s $DEV pull /data/local/tmp/g27/g27-run-stderr.txt "$SSD27/g27-run-stderr.txt"
adb -s $DEV pull /data/local/tmp/g27/g27-run-stdout.txt "$SSD27/g27-run-stdout.txt"
adb -s $DEV shell "ls -la $G27DIR/ ; ls -lt /data/tombstones/ | head -6"
# (pulled tombstone_23 + 10 PPMs individually; then:)
adb -s $DEV shell "rm -rf $G27DIR && ls /data/local/tmp/"   # DEVICE_CLEAN (mg/ only)
