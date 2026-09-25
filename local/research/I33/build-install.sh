#!/bin/bash
# I33 Part 2: iOS builds with paraLLEl-GS as the default backend
# (PS2X_GS_SHADOW_PARALLEL=ON, bundled env selects parallel + embedded
# MoltenVK 1.4.2). Simulator + device. Adapted from
# ~/dev/ssx3-work/F2/ios/build-install.sh (I32 Part 1). Fork worktree at
# 0ed07c4 on local branch i33-pgs-ios; MoltenVK v1.4.2 embedded per target.
set -euo pipefail
W=/Users/brad/dev/ssx3-work/I33/ios
D=/Users/brad/dev/ssx3-work/ios-deps
REPO=/Users/brad/dev/ssx3
FORK_WT=/Users/brad/dev/ssx3-work/I33/PS2Recomp
PGS=/Users/brad/dev/ssx3-work/I33/parallel-gs
RAYLIB="$D/raylib-src"
CODEGEN=/Users/brad/dev/ssx3-work/codegen-ssx3
MVK=/Users/brad/dev/ssx3-work/I33/MoltenVK/MoltenVK/dynamic/MoltenVK.xcframework
I26="$REPO/local/research/I26"
ENVFILE="$REPO/local/research/I33/ps2x.env"
LOGS="$W/logs"
ELF=/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72
ISO='/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso'
PROFILE='/Users/brad/Library/Developer/Xcode/UserData/Provisioning Profiles/f0793278-db43-413c-9260-f120dc740845.mobileprovision'
IPAD=00008112-001224302184A01E
IPHONE=00008140-0002505001F3001C
SIM=7662ACD6-6294-4676-B426-26A3F8C7B258
IDENTITY=295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1
PIN=0ed07c4362b9bd53c09094fd028ee05e8aaf021a
RAYPIN=c1ab645ca298a2801097931d1079b10ff7eb9df8
PGSPIN=19d93b2d0bb0172c2ab4c057de4adbd6ed566eba
GRANITEPIN=166ba21a247a681903cc9d0bb6562fe50a554c85
JOBS="${JOBS:-8}"
mkdir -p "$LOGS"

hash_pair() { shasum -a 256 "$1" "$1"; }

# Per-target paths. $1 = sim|device
t_paths() {
  if [ "$1" = sim ]; then
    TC="$I26/ios-simulator.toolchain.cmake"; SDKNAME=iphonesimulator
    FFMPEG="$D/ffmpeg-ios-sim-7.1.1"; SDL2P="$D/sdl2-ios-sim"
    BUILD="$W/ios-runtime-sim-release"
    APP="$BUILD/ps2xRuntime/Release-$SDKNAME/ps2EntryRunner.app"
    STAGE="$W/staged-sim/ps2EntryRunner.app"
    MVKFW="$MVK/ios-arm64_x86_64-simulator/MoltenVK.framework"
  else
    TC="$I26/ios-device.toolchain.cmake"; SDKNAME=iphoneos
    FFMPEG="$D/ffmpeg-ios-7.1.1"; SDL2P="$D/sdl2-ios-device"
    BUILD="$W/ios-runtime-device-release"
    APP="$BUILD/ps2xRuntime/Release-$SDKNAME/ps2EntryRunner.app"
    STAGE="$W/staged/ps2EntryRunner.app"
    MVKFW="$MVK/ios-arm64/MoltenVK.framework"
  fi
}

preflight() {
  git -C "$FORK_WT" merge-base --is-ancestor "$PIN" HEAD
  git -C "$FORK_WT" rev-parse HEAD > "$LOGS/fork-head.txt"
  git -C "$FORK_WT" log --oneline -2 > "$LOGS/fork-log.txt"
  git -C "$FORK_WT" diff --exit-code 14b1e5cb HEAD -- ps2xRuntime/src/runner
  test "$(git -C "$RAYLIB" rev-parse HEAD)" = "$RAYPIN"
  test "$(git -C "$PGS" rev-parse HEAD)" = "$PGSPIN"
  git -C "$PGS" status --porcelain > "$LOGS/pgs-status.txt"; test ! -s "$LOGS/pgs-status.txt"
  git -C "$PGS/Granite" rev-parse HEAD > "$LOGS/granite-head.txt"
  grep -q "$GRANITEPIN" "$LOGS/granite-head.txt"
  hash_pair "$CODEGEN/register_functions.cpp" > "$LOGS/codegen-sha.txt"
  hash_pair "$ELF" > "$LOGS/elf-input-sha.txt"
  hash_pair "$ISO" > "$LOGS/iso-input-sha.txt"
  hash_pair "$PROFILE" > "$LOGS/profile-sha.txt"
  hash_pair "$MVK/ios-arm64_x86_64-simulator/MoltenVK.framework/MoltenVK" > "$LOGS/moltenvk-sim-sha.txt"
  hash_pair "$MVK/ios-arm64/MoltenVK.framework/MoltenVK" > "$LOGS/moltenvk-device-sha.txt"
  hash_pair "$ENVFILE" > "$LOGS/env-sha.txt"
  security find-identity -v -p codesigning | grep -F "$IDENTITY" > "$LOGS/identity-check.txt"
}

configure_one() { # $1 = sim|device
  t_paths "$1"
  test ! -e "$BUILD/CMakeCache.txt"
  env -u CC -u CXX cmake -G Xcode \
    -DCMAKE_TOOLCHAIN_FILE="$TC" \
    -DCMAKE_C_FLAGS_RELEASE='-O3 -DNDEBUG' \
    -DCMAKE_CXX_FLAGS_RELEASE='-O3 -DNDEBUG' \
    -DCMAKE_CONFIGURATION_TYPES=Release \
    -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
    -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF \
    -DPS2X_ENABLE_SCCACHE=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
    -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF \
    -DPS2X_ENABLE_FFMPEG=ON -DPS2X_FFMPEG_IOS_ROOT="$FFMPEG" \
    -DSDL2_DIR="$SDL2P/lib/cmake/SDL2" \
    -DFETCHCONTENT_SOURCE_DIR_RAYLIB="$RAYLIB" \
    -DPS2X_GAME_CODEGEN_DIR="$CODEGEN" \
    -DPS2X_GS_SHADOW_PARALLEL=ON \
    -DPS2X_PARALLEL_GS_SOURCE_DIR="$PGS" \
    -S "$FORK_WT" -B "$BUILD" > "$LOGS/$1-configure.log" 2>&1
  rg '^CMAKE_(C|CXX)_FLAGS_RELEASE:STRING=-O3 -DNDEBUG$' "$BUILD/CMakeCache.txt" > "$LOGS/$1-release-cache.txt"
  test "$(wc -l < "$LOGS/$1-release-cache.txt" | tr -d ' ')" = 2
  rg 'PS2X: G44 parallel-gs shadow backend ON' "$LOGS/$1-configure.log" > "$LOGS/$1-pgs-on.txt"
}

build_one() { # $1 = sim|device
  t_paths "$1"
  cmake --build "$BUILD" --config Release --target ps2EntryRunner -- -jobs "$JOBS" \
    > "$LOGS/$1-build.log" 2>&1
  test -f "$APP/ps2EntryRunner"
  hash_pair "$APP/ps2EntryRunner" > "$LOGS/$1-source-binary-sha.txt"
}

stage_one() { # $1 = sim|device
  t_paths "$1"
  test ! -e "$STAGE"
  mkdir -p "$(dirname "$STAGE")"
  cp -R "$APP" "$STAGE"
  cp "$ELF" "$STAGE/SLUS_207.72"
  cp -c "$ISO" "$STAGE/SSX3.iso"
  cp "$ENVFILE" "$STAGE/ps2x.env"
  cp -R "$FORK_WT/ps2xRuntime/ios/Settings.bundle" "$STAGE/Settings.bundle"
  mkdir -p "$STAGE/Frameworks"
  cp -R "$MVKFW" "$STAGE/Frameworks/MoltenVK.framework"
  chmod 0644 "$STAGE/SLUS_207.72" "$STAGE/SSX3.iso" "$STAGE/ps2x.env"
  find "$STAGE" -name '._*' -delete || true
  if [ "$1" = sim ]; then
    codesign --force --sign - --timestamp=none "$STAGE/Frameworks/MoltenVK.framework"
    codesign --force --sign - --timestamp=none "$STAGE"
  fi
  hash_pair "$STAGE/SLUS_207.72" > "$LOGS/$1-elf-stage-sha.txt"
  hash_pair "$STAGE/SSX3.iso" > "$LOGS/$1-iso-stage-sha.txt"
  hash_pair "$STAGE/Frameworks/MoltenVK.framework/MoltenVK" > "$LOGS/$1-mvk-stage-sha.txt"
  /usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$STAGE/Info.plist" | grep -Fx org.ps2x.ps2entryrunner
}

configure_sim() { configure_one sim; }
build_sim() { build_one sim; }
stage_sim() { stage_one sim; }
configure_device() { configure_one device; }
build_device() { build_one device; }
stage_device() { stage_one device; }

sim_install() {
  t_paths sim
  xcrun simctl boot "$SIM" 2>/dev/null || true
  xcrun simctl bootstatus "$SIM" -b > /dev/null
  xcrun simctl install "$SIM" "$STAGE" > "$LOGS/sim-install.log" 2>&1
}

sign() {
  t_paths device
  cp "$PROFILE" "$STAGE/embedded.mobileprovision"
  cp "$I26/entitlements.plist" "$W/staged/entitlements.plist"
  codesign --force --sign "$IDENTITY" --timestamp=none \
    "$STAGE/Frameworks/MoltenVK.framework" >> "$LOGS/codesign.log" 2>&1
  codesign --force --sign "$IDENTITY" --timestamp=none \
    --entitlements "$W/staged/entitlements.plist" "$STAGE" >> "$LOGS/codesign.log" 2>&1
  codesign --verify --strict --verbose=2 "$STAGE" > "$LOGS/codesign-verify.log" 2>&1
  hash_pair "$STAGE/ps2EntryRunner" > "$LOGS/signed-binary-sha.txt"
}

install_ipad() {
  t_paths device
  xcrun devicectl device install app --device "$IPAD" --timeout 1200 "$STAGE" \
    > "$LOGS/install-ipad.log" 2>&1
  cat "$LOGS/install-ipad.log"
}

install_iphone() {
  t_paths device
  xcrun devicectl list devices > "$LOGS/devices-install-iphone.txt"
  grep -F "$IPHONE" "$LOGS/devices-install-iphone.txt" | grep -E 'connected|available'
  xcrun devicectl device install app --device "$IPHONE" --timeout 1200 "$STAGE" \
    > "$LOGS/install-iphone.log" 2>&1
  cat "$LOGS/install-iphone.log"
}

for step in "$@"; do echo "[i33 $(date +%H:%M:%S)] stage $step"; "$step"; done
