#!/bin/bash
# FS2 Part 3: build Turnip (libvulkan_freedreno.so) from Mesa at the checked-out HEAD for
# Android arm64 / kgsl, reproducing StevenMXZ Adreno-Tools-Drivers A8xx build_turnip.sh
# (commit 50cbd613e7, the recipe behind Turnip_Gen8_V36 = our shipped 717812c3…): same seds,
# same cross file (NDK r29, android35 since r29 has no android36), same meson options.
# Differences: tools are user-local (venv meson/mako, dpkg -x flex/bison/glslang), and the
# source is upstream Mesa at c501e1d16e (the shipped .so's git id) rather than the script's clone.
# Build 2 on: API 34 (the shipped .so's NT_ANDROID_TYPE_IDENT is 0x22 = 34), prefix
# /tmp/turnip-gen8 and build dir <src>/build-android-aarch64, as in the script.
# usage: mesa-build.sh <mesa-src> <out-dir>   (env CVER, default 34)
set -euo pipefail
SRC=$1; OUT=$2; BD=$SRC/build-android-aarch64; PREFIX=/tmp/turnip-gen8
T=/home/brad/fs2/turnip
ndk=$T/android-ndk-r29/toolchains/llvm/prebuilt/linux-x86_64/bin
export PATH="$T/venv/bin:$T/sysroot/usr/bin:$ndk:$PATH"
export LD_LIBRARY_PATH="$T/sysroot/usr/lib/x86_64-linux-gnu"
export BISON_PKGDATADIR=$T/sysroot/usr/share/bison M4=$T/sysroot/usr/bin/m4
cd "$SRC"
git checkout -q -- . && rm -f src/freedreno/vulkan/tu_version.h android-aarch64.txt native.txt
echo "== src $(git rev-parse HEAD) $(git status --porcelain | wc -l) dirty files before seds"
echo "#define TUGEN8_DRV_VERSION \"\"" > ./src/freedreno/vulkan/tu_version.h
sed -i 's/ (%s)//g' src/freedreno/vulkan/tu_device.cc || true
sed -i '/a7xx_gen1 = GPUProps(/a \        has_early_preamble = False,' src/freedreno/common/freedreno_devices.py || true
sed -i 's/typedef const native_handle_t\* buffer_handle_t;/typedef void\* buffer_handle_t;/g' include/android_stub/cutils/native_handle.h || true
sed -i 's/, hnd->handle/, (void \*)hnd->handle/g' src/util/u_gralloc/u_gralloc_fallback.c || true
sed -i 's/native_buffer->handle->/((const native_handle_t \*)native_buffer->handle)->/g' src/vulkan/runtime/vk_android.c || true
sed -i 's/anb->handle->/((const native_handle_t \*)anb->handle)->/g' src/vulkan/runtime/vk_android.c || true
git diff --stat | tail -1
cver=${CVER:-34}
cat > "$SRC/android-aarch64.txt" <<X
[binaries]
ar = '$ndk/llvm-ar'
c = ['ccache', '$ndk/aarch64-linux-android${cver}-clang']
cpp = ['ccache', '$ndk/aarch64-linux-android${cver}-clang++', '-fno-exceptions', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables', '--start-no-unused-arguments', '-static-libstdc++', '--end-no-unused-arguments']
c_ld = '$ndk/ld.lld'
cpp_ld = '$ndk/ld.lld'
strip = '$ndk/llvm-strip'
pkg-config = ['env', 'PKG_CONFIG_LIBDIR=$ndk/pkg-config', '/usr/bin/pkg-config']

[host_machine]
system = 'android'
cpu_family = 'aarch64'
cpu = 'armv8'
endian = 'little'
X
cat > "$SRC/native.txt" <<X
[build_machine]
c = ['ccache', '$ndk/clang']
cpp = ['ccache', '$ndk/clang++']
ar = '$ndk/llvm-ar'
strip = '$ndk/llvm-strip'
c_ld = '$ndk/ld.lld'
cpp_ld = '$ndk/ld.lld'
system = 'linux'
cpu_family = 'x86_64'
cpu = 'x86_64'
endian = 'little'
X
rm -rf "$BD" "$OUT" "$PREFIX"; mkdir -p "$OUT"
meson setup build-android-aarch64 --cross-file android-aarch64.txt --native-file native.txt --prefix "$PREFIX" \
  -Dbuildtype=release -Dstrip=true -Dplatforms=android -Dvideo-codecs= -Dplatform-sdk-version=36 \
  -Dandroid-stub=true -Dgallium-drivers= -Dvulkan-drivers=freedreno -Dvulkan-beta=true \
  -Dfreedreno-kmds=kgsl -Degl=disabled -Dandroid-libbacktrace=disabled > "$OUT.setup.log" 2>&1 || { tail -30 "$OUT.setup.log"; exit 1; }
ninja -C build-android-aarch64 install > "$OUT.ninja.log" 2>&1 || { grep -m5 -B2 -A8 "error" "$OUT.ninja.log"; exit 1; }
cp $PREFIX/lib/libvulkan_freedreno.so $OUT/ && so=$OUT/libvulkan_freedreno.so
ls -la $so; sha256sum $so
strings -a $so | grep -E "Mesa [0-9]|git-[0-9a-f]{10}|Turnip Adreno" | sort -u
