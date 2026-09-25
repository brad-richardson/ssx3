#!/bin/bash
# I29: rebuild FFmpeg 7.1.1 + SDL2 release-2.32.10 for iphoneos+iphonesimulator
# into the persistent ~/dev/ssx3-work/ios-deps/. No wait-for-idle: UP1 is
# building concurrently, so everything here runs under nice.
set -euo pipefail
D=/Users/brad/dev/ssx3-work/ios-deps
SRC="$D/src"
LOGS="$D/logs"
JOBS="${JOBS:-8}"
NICE="nice -n 10"
mkdir -p "$LOGS"
log() { echo "[i29-deps $(date +%H:%M:%S)] $*"; }

ffmpeg_one() { # $1 = iphoneos|iphonesimulator, $2 = suffix, $3 = minver flag
  local sdk="$1" sfx="$2" minver="$3"
  local out="$D/ffmpeg-ios${sfx}-7.1.1"
  if [ -f "$out/lib/libavcodec.a" ]; then log "ffmpeg $sdk already built"; return 0; fi
  local sd="$SRC/ffmpeg-7.1.1${sfx}"
  rm -rf "$sd" && mkdir "$sd"
  tar -xf "$SRC/ffmpeg-7.1.1.tar.xz" -C "$sd" --strip-components 1
  ( cd "$sd"
    SDK=$(xcrun --sdk "$sdk" --show-sdk-path)
    ./configure --target-os=darwin --arch=aarch64 --cpu=generic --enable-cross-compile \
      --cc="xcrun -sdk $sdk clang" --sysroot="$SDK" \
      --extra-cflags="-arch arm64 $minver -isysroot $SDK -Os" \
      --extra-ldflags="-arch arm64 $minver -isysroot $SDK" \
      --disable-everything --disable-programs --disable-doc --disable-avdevice --disable-avfilter \
      --disable-avformat --disable-swresample --disable-network --disable-iconv --disable-bzlib \
      --disable-lzma --disable-zlib --enable-decoder=mpeg2video --enable-parser=mpegvideo \
      --enable-swscale --disable-asm --enable-static --disable-shared --disable-debug \
      --prefix="$out" > "$LOGS/ffmpeg${sfx}-configure.log" 2>&1
    $NICE make -j"$JOBS" > "$LOGS/ffmpeg${sfx}-build.log" 2>&1 \
      && make install > "$LOGS/ffmpeg${sfx}-install.log" 2>&1
  )
  rm -rf "$sd"
  lipo -info "$out"/lib/*.a
  log "ffmpeg $sdk done"
}

sdl_one() { # $1 = iphoneos|iphonesimulator, $2 = suffix, $3 = toolchain
  local sdk="$1" sfx="$2" tc="$3"
  local out="$D/sdl2-ios${sfx}"
  if [ -f "$out/lib/libSDL2.a" ]; then log "sdl2 $sdk already built"; return 0; fi
  env -u CC -u CXX cmake -S "$SRC/SDL" -B "$D/sdl2-build${sfx}" -G Ninja \
    -DCMAKE_TOOLCHAIN_FILE="$tc" -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$out" \
    -DSDL_SHARED=OFF -DSDL_STATIC=ON -DSDL_TEST=OFF > "$LOGS/sdl2${sfx}-configure.log" 2>&1
  $NICE cmake --build "$D/sdl2-build${sfx}" --parallel "$JOBS" > "$LOGS/sdl2${sfx}-build.log" 2>&1
  cmake --install "$D/sdl2-build${sfx}" > "$LOGS/sdl2${sfx}-install.log" 2>&1
  lipo -info "$out/lib/libSDL2.a" "$out/lib/libSDL2main.a"
  log "sdl2 $sdk done"
}

ffmpeg_one iphoneos "" "-mios-version-min=17.0"
ffmpeg_one iphonesimulator "-sim" "-mios-simulator-version-min=17.0"
sdl_one iphoneos "-device" /Users/brad/dev/ssx3/local/research/I26/ios-device.toolchain.cmake
sdl_one iphonesimulator "-sim" /Users/brad/dev/ssx3/local/research/I26/ios-simulator.toolchain.cmake
log "all deps built"
