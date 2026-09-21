#!/bin/sh
# G15: ONE bounded HWASan on-device replay (rich dump) + log pull + cleanup.
# Wall cap: device-side `timeout -s KILL 280`. /data/local/tmp/g15/ ONLY
# (never mg/). HWASan needs its two sidecar .so files + LD_LIBRARY_PATH.
# G15 result: exit 139 (O2 again, fault 0xf0), NO sanitizer report, 0 PPMs.
set -e
export COPYFILE_DISABLE=1
DEV=622c49b1
G15DIR=/data/local/tmp/g15
SSD15="/Volumes/Extreme SSD/ps2x-g15"
HWBUILD="/Volumes/Extreme SSD/parallel-gs-g15-hwasan-build"
NDK=/opt/homebrew/share/android-ndk
adb -s $DEV shell "mkdir -p $G15DIR && df -h /data"
adb -s $DEV push "$HWBUILD/tools/parallel-gs-replayer" $G15DIR/hwasan-replayer
adb -s $DEV push "$NDK/toolchains/llvm/prebuilt/darwin-x86_64/sysroot/usr/lib/aarch64-linux-android/libc++_shared.so" $G15DIR/
adb -s $DEV push "$NDK/toolchains/llvm/prebuilt/darwin-x86_64/lib/clang/21/lib/linux/libclang_rt.hwasan-aarch64-android.so" $G15DIR/
adb -s $DEV shell "cd $G15DIR && chmod 755 hwasan-replayer && sha256sum hwasan-replayer libc++_shared.so libclang_rt.hwasan-aarch64-android.so"
adb -s $DEV logcat -d -s Granite:V | tail -3            # before-snapshot
adb -s $DEV shell "cd $G15DIR && date +%s; LD_LIBRARY_PATH=$G15DIR timeout -s KILL 280 ./hwasan-replayer $G15DIR/g13-dump.gs --iterations 2; echo HW_EXIT=\$?; date +%s"
adb -s $DEV logcat -d -s Granite:V > "$SSD15/g15-logcat-hwasan.txt"
adb -s $DEV shell "ls -la $G15DIR/"
adb -s $DEV shell "rm -rf $G15DIR && ls /data/local/tmp/"   # DEVICE_CLEAN (mg/ only)
