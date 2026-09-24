#!/bin/bash
# I26: build + stage + install the SSX 3 PS2 recomp for iOS (I25's script,
# pointed at the I26 worktree/branch; FFmpeg + SDL2 prefixes reused from I25).
#
#   TARGET=device build-install.sh            # iPhone: prefixes configure build stage sign install
#   TARGET=sim    build-install.sh            # Simulator: prefixes configure build stage sim_install
#   TARGET=sim    build-install.sh sim_launch sim_shot   # test run (LABEL=<name> for the shot)
#   TARGET=device build-install.sh ipad_install ipad_launch ipad_shot   # iPad fallback test
#
# Brad's rule (09-23): the iPhone is BUILD + INSTALL ONLY. No launch, test,
# screenshot or devicectl process command on it; guard_not_iphone enforces it.
# Every stage is idempotent; rerun from any point. Env overrides: W, CODEGEN,
# FORK_WT, IPHONE, IPAD, SIM, JOBS, ISO, ELF, WALL (launch cap, s).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
I25="$REPO/local/research/I26"   # (variable name kept from I25)
TARGET="${TARGET:-device}"
case "$TARGET" in device) SDKNAME=iphoneos ;; sim) SDKNAME=iphonesimulator ;; *) echo "TARGET=device|sim"; exit 1 ;; esac
W="${W:-$HOME/dev/ssx3-work/I26}"
PW="${PW:-$HOME/dev/ssx3-work/I25}"               # prefixes (FFmpeg, SDL2) built by I25
FORK_WT="${FORK_WT:-$W/PS2Recomp}"                 # worktree on local branch i26-qol
CODEGEN="${CODEGEN:-$HOME/dev/ssx3-work/codegen-ssx3}"
ISO="${ISO:-$HOME/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso}"
ELF="${ELF:-$HOME/dev/ssx3-work/E32-inputs/cd/SLUS_207.72}"
ISO_SHA=3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5
IPHONE="${IPHONE:-00008140-0002505001F3001C}"      # Brad's iPhone 16 Pro Max: install only
IPAD="${IPAD:-00008112-001224302184A01E}"          # Brad's iPad Air 11" (M2): test fallback
SIM="${SIM:-7662ACD6-6294-4676-B426-26A3F8C7B258}" # iPhone 18 Pro simulator, iOS 27.0
BUNDLE_ID=org.ps2x.ps2entryrunner
IDENTITY=295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1  # Apple Development: Brad Richardson (E4R78PLLKY)
JOBS="${JOBS:-8}"
WALL="${WALL:-600}"
if [ "$TARGET" = sim ]; then
  TC="$I25/ios-simulator.toolchain.cmake"          # = local/research/I1/logs/ios-simulator.toolchain.v2.cmake
  SFX=-sim; MINVER="-mios-simulator-version-min=17.0"
else
  TC="$I25/ios-device.toolchain.cmake"             # = local/research/I9/logs/ios-device.toolchain.cmake
  SFX=; MINVER="-mios-version-min=17.0"
fi
FFMPEG="$PW/ffmpeg-ios${SFX}-7.1.1"
SDL2="$PW/sdl2-ios${SFX:--device}"
RAYLIB_SRC="${RAYLIB_SRC:-$HOME/dev/ssx3-work/E46-build/_deps/raylib-src}"  # raylib 5.5 (c1ab645c)
BUILD="$W/ios-runtime${SFX:--device}"
APP="$BUILD/ps2xRuntime/Release-$SDKNAME/ps2EntryRunner.app"
SAPP="$W/staged${SFX}/ps2EntryRunner.app"
LOGS="$W/logs"; mkdir -p "$LOGS" "$W/src"
NICE="nice -n 10"
log() { echo "[i26 $(date +%H:%M:%S) $TARGET] $*"; }

wait_idle() {  # don't compete with another lane's build (E50 etc.)
  while pgrep -q -f 'clang\+\+|ninja' ; do log "another build is running; waiting 60 s"; sleep 60; done
}
guard_not_iphone() {
  if [ "$1" = "$IPHONE" ]; then echo "REFUSED: iPhone is build+install only (Brad, 09-23)"; exit 3; fi
}

stage_prefixes() {
  cd "$W/src"
  [ -f ffmpeg-7.1.1.tar.xz ] || curl -fsSL -o ffmpeg-7.1.1.tar.xz https://ffmpeg.org/releases/ffmpeg-7.1.1.tar.xz
  echo "733984395e0dbbe5c046abda2dc49a5544e7e0e1e2366bba849222ae9e3a03b1  ffmpeg-7.1.1.tar.xz" | shasum -a 256 -c
  if [ ! -f "$FFMPEG/lib/libavcodec.a" ]; then
    local sd="ffmpeg-7.1.1$SFX"; rm -rf "$sd" && mkdir "$sd" && tar -xf ffmpeg-7.1.1.tar.xz -C "$sd" --strip-components 1 && cd "$sd"
    SDK=$(xcrun --sdk $SDKNAME --show-sdk-path)
    # Recipe: ps2xRuntime/cmake/iOS-FFmpeg-7.1.1.md (sim: same flags, simulator SDK + min-version flag).
    ./configure --target-os=darwin --arch=aarch64 --cpu=generic --enable-cross-compile \
      --cc="xcrun -sdk $SDKNAME clang" --sysroot="$SDK" \
      --extra-cflags="-arch arm64 $MINVER -isysroot $SDK -Os" \
      --extra-ldflags="-arch arm64 $MINVER -isysroot $SDK" \
      --disable-everything --disable-programs --disable-doc --disable-avdevice --disable-avfilter \
      --disable-avformat --disable-swresample --disable-network --disable-iconv --disable-bzlib \
      --disable-lzma --disable-zlib --enable-decoder=mpeg2video --enable-parser=mpegvideo \
      --enable-swscale --disable-asm --enable-static --disable-shared --disable-debug \
      --prefix="$FFMPEG" > "$LOGS/ffmpeg$SFX-configure.log" 2>&1
    $NICE make -j"$JOBS" > "$LOGS/ffmpeg$SFX-build.log" 2>&1 && make install > "$LOGS/ffmpeg$SFX-install.log" 2>&1
    cd "$W/src" && rm -rf "$sd"
  fi
  lipo -info "$FFMPEG"/lib/*.a
  [ -d SDL ] || git clone -q --depth 1 --branch release-2.32.10 https://github.com/libsdl-org/SDL.git SDL
  test "$(git -C SDL rev-parse --short HEAD)" = 5d24957
  if [ ! -f "$SDL2/lib/libSDL2.a" ]; then
    # Recipe: local/research/I8/REPORT.md Task 1 (Ninja, static only; I4 for the sim).
    env -u CC -u CXX cmake -S SDL -B "$W/sdl2-build$SFX" -G Ninja \
      -DCMAKE_TOOLCHAIN_FILE="$TC" -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY \
      -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$SDL2" \
      -DSDL_SHARED=OFF -DSDL_STATIC=ON -DSDL_TEST=OFF > "$LOGS/sdl2$SFX-configure.log" 2>&1
    $NICE cmake --build "$W/sdl2-build$SFX" --parallel "$JOBS" > "$LOGS/sdl2$SFX-build.log" 2>&1
    cmake --install "$W/sdl2-build$SFX" > "$LOGS/sdl2$SFX-install.log" 2>&1
  fi
  lipo -info "$SDL2/lib/libSDL2.a" "$SDL2/lib/libSDL2main.a"
}

stage_configure() {
  test "$(git -C "$FORK_WT" rev-parse --abbrev-ref HEAD)" = i26-qol
  test -d "$CODEGEN"
  env -u CC -u CXX cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE="$TC" \
    -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
    -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
    -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF \
    -DPS2X_ENABLE_FFMPEG=ON -DPS2X_FFMPEG_IOS_ROOT="$FFMPEG" \
    -DSDL2_DIR="$SDL2/lib/cmake/SDL2" \
    -DFETCHCONTENT_SOURCE_DIR_RAYLIB="$RAYLIB_SRC" \
    -DPS2X_GAME_CODEGEN_DIR="$CODEGEN" \
    -S "$FORK_WT" -B "$BUILD" > "$LOGS/runtime$SFX-configure.log" 2>&1
  grep -E 'game objects|dropped' "$LOGS/runtime$SFX-configure.log" || true
}

stage_build() {
  wait_idle
  $NICE cmake --build "$BUILD" --config Release --target ps2EntryRunner -- -jobs "$JOBS" \
    > "$LOGS/runtime$SFX-build.log" 2>&1 || { grep -E ' error:' "$LOGS/runtime$SFX-build.log" | head -20; exit 1; }
  tail -3 "$LOGS/runtime$SFX-build.log"
  stat -f "%z %N" "$APP/ps2EntryRunner"; shasum -a 256 "$APP/ps2EntryRunner"
}

stage_stage() {
  rm -rf "$(dirname "$SAPP")"; mkdir -p "$(dirname "$SAPP")"
  cp -R "$APP" "$SAPP"
  cp "$ELF" "$SAPP/SLUS_207.72"
  # The 3 GB ISO: APFS clone (no extra bytes), then two sha reads.
  cp -c "$ISO" "$SAPP/SSX3.iso" 2>/dev/null || cp "$ISO" "$SAPP/SSX3.iso"
  for i in 1 2; do test "$(shasum -a 256 "$SAPP/SSX3.iso" | cut -d' ' -f1)" = "$ISO_SHA"; done
  cp "$I25/ps2x.env" "$SAPP/ps2x.env"
  cp -R "$FORK_WT/ps2xRuntime/ios/Settings.bundle" "$SAPP/Settings.bundle"
  chmod 0644 "$SAPP/SLUS_207.72" "$SAPP/SSX3.iso" "$SAPP/ps2x.env"   # sources are 0700
  find "$SAPP" -name "._*" -delete
  if [ "$TARGET" = sim ]; then codesign --force --sign - --timestamp=none "$SAPP"; fi  # sim: ad-hoc
  ls -la "$SAPP" | head -20
}

find_profile() {  # newest dev profile whose app id matches the bundle id (or the team wildcard)
  local d="$HOME/Library/Developer/Xcode/UserData/Provisioning Profiles" f p best=""
  for f in "$d"/*.mobileprovision "$HOME/Library/MobileDevice/Provisioning Profiles"/*.mobileprovision; do
    [ -f "$f" ] || continue
    p=$(mktemp); security cms -D -i "$f" > "$p" 2>/dev/null || { rm -f "$p"; continue; }
    local appid; appid=$(/usr/libexec/PlistBuddy -c 'Print :Entitlements:application-identifier' "$p" 2>/dev/null || true)
    if { [ "$appid" = "LQ3V7772Q2.$BUNDLE_ID" ] || [ "$appid" = "LQ3V7772Q2.*" ]; } \
       && /usr/libexec/PlistBuddy -c 'Print :ProvisionedDevices' "$p" 2>/dev/null | grep -q "$IPHONE"; then
      best="$f"
    fi
    rm -f "$p"
  done
  [ -n "$best" ] && echo "$best"
}

stage_sign() {  # device only; I23 mechanism: embed profile + codesign with I9's entitlements
  local prof; prof=$(find_profile) || { echo "NO PROFILE for $BUNDLE_ID + $IPHONE"; exit 2; }
  log "profile: $prof"
  cp "$prof" "$SAPP/embedded.mobileprovision"
  cp "$I25/entitlements.plist" "$W/staged/entitlements.plist"   # = local/research/I9/logs/entitlements.plist
  codesign --force --sign "$IDENTITY" --timestamp=none \
    --entitlements "$W/staged/entitlements.plist" "$SAPP"
  codesign --verify --strict "$SAPP" && log "signed + verified"
}

# --- iPhone: install only ---
stage_install() {
  xcrun devicectl device install app --device "$IPHONE" --timeout 1200 "$SAPP" 2>&1 | tee "$LOGS/install-iphone.log"
}

# --- Simulator (preferred test target) ---
stage_sim_install() {
  xcrun simctl boot "$SIM" 2>/dev/null || true
  xcrun simctl bootstatus "$SIM" -b > /dev/null
  xcrun simctl install "$SIM" "$SAPP"
  log "installed on simulator $SIM"
}
stage_sim_launch() {  # home-screen equivalent (bundled ps2x.env) + the diagnostic rate line; capped at WALL s
  xcrun simctl terminate "$SIM" "$BUNDLE_ID" 2>/dev/null || true
  SIMCTL_CHILD_PS2X_VSYNC_RATE_LOG=1 xcrun simctl launch --console-pty "$SIM" "$BUNDLE_ID" \
    > "$LOGS/sim-console-${LABEL:-run}.log" 2>&1 &
  echo $! > "$W/sim-launch.pid"
  log "launched; console -> $LOGS/sim-console-${LABEL:-run}.log (pid $(cat "$W/sim-launch.pid"))"
}
stage_sim_shot() {
  local out="$LOGS/sim-shot-${LABEL:-$(date +%H%M%S)}.png"
  xcrun simctl io "$SIM" screenshot "$out" > /dev/null 2>&1 && shasum -a 256 "$out"
}
stage_sim_stop() {
  xcrun simctl terminate "$SIM" "$BUNDLE_ID" 2>/dev/null || true
  [ -f "$W/sim-launch.pid" ] && kill "$(cat "$W/sim-launch.pid")" 2>/dev/null || true
}

# --- iPad (fallback test target; same recipe as I23) ---
stage_ipad_install() {
  guard_not_iphone "$IPAD"
  xcrun devicectl device install app --device "$IPAD" --timeout 1200 "$SAPP" 2>&1 | tee "$LOGS/install-ipad.log"
}
stage_ipad_launch() {
  guard_not_iphone "$IPAD"
  xcrun devicectl device process launch --device "$IPAD" --timeout "$WALL" --console --terminate-existing \
    -e '{"PS2X_VSYNC_RATE_LOG":"1"}' "$BUNDLE_ID" > "$LOGS/ipad-console-${LABEL:-run}.log" 2>&1 &
  echo $! > "$W/ipad-launch.pid"
}
stage_ipad_shot() {
  guard_not_iphone "$IPAD"
  local out="$LOGS/ipad-shot-${LABEL:-$(date +%H%M%S)}.png"
  xcrun devicectl device capture screenshot --device "$IPAD" --timeout 60 --destination "$out" > /dev/null && shasum -a 256 "$out"
}

if [ $# -eq 0 ]; then
  if [ "$TARGET" = sim ]; then set -- prefixes configure build stage sim_install
  else set -- prefixes configure build stage sign install; fi
fi
for s in "$@"; do log "stage $s"; "stage_$s"; done
