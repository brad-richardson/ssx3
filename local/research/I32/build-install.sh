#!/bin/bash
# I32 Part 1: Simulator-only build at i32-controls (fork ssx3 f949ff0 + stick/D-pad commit); deps from persistent ios-deps.
# No wait-for-idle: UP1 builds concurrently, so builds run under nice.
set -euo pipefail
W=/Users/brad/dev/ssx3-work/I32
D=/Users/brad/dev/ssx3-work/ios-deps
REPO=/Users/brad/dev/ssx3
FORK_WT="$W/PS2Recomp"
RAYLIB="$D/raylib-src"
CODEGEN=/Users/brad/dev/ssx3-work/codegen-ssx3
I26="$REPO/local/research/I26"
ENVFILE="$REPO/local/research/I32/ps2x.env"
LOGS="$W/logs"
ELF=/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72
ISO='/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso'
PROFILE='/Users/brad/Library/Developer/Xcode/UserData/Provisioning Profiles/f0793278-db43-413c-9260-f120dc740845.mobileprovision'
IPHONE=00008140-0002505001F3001C
IPAD=00008112-001224302184A01E
SIM=7662ACD6-6294-4676-B426-26A3F8C7B258
IDENTITY=295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1
PIN=f949ff060d9a0c53f3ab47998068b771f20653e3
RAYPIN=c1ab645ca298a2801097931d1079b10ff7eb9df8
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
  else
    TC="$I26/ios-device.toolchain.cmake"; SDKNAME=iphoneos
    FFMPEG="$D/ffmpeg-ios-7.1.1"; SDL2P="$D/sdl2-ios-device"
    BUILD="$W/ios-runtime-device-release"
    APP="$BUILD/ps2xRuntime/Release-$SDKNAME/ps2EntryRunner.app"
    STAGE="$W/staged/ps2EntryRunner.app"
  fi
}

preflight() {
  test "$(git -C "$FORK_WT" rev-parse fork/ssx3)" = "$PIN"
  git -C "$FORK_WT" merge-base --is-ancestor "$PIN" HEAD
  git -C "$FORK_WT" rev-parse HEAD > "$LOGS/fork-head.txt"
  git -C "$FORK_WT" log --oneline -2 > "$LOGS/fork-log.txt"
  git -C "$FORK_WT" diff --exit-code 14b1e5cb HEAD -- ps2xRuntime/src/runner
  test "$(git -C "$RAYLIB" rev-parse HEAD)" = "$RAYPIN"
  hash_pair "$CODEGEN/register_functions.cpp" > "$LOGS/codegen-sha.txt"
  hash_pair "$ELF" > "$LOGS/elf-input-sha.txt"
  hash_pair "$ISO" > "$LOGS/iso-input-sha.txt"
  hash_pair "$PROFILE" > "$LOGS/profile-sha.txt"
  hash_pair "$D/ffmpeg-ios-7.1.1/lib/libavcodec.a" > "$LOGS/ffmpeg-device-sha.txt"
  hash_pair "$D/ffmpeg-ios-sim-7.1.1/lib/libavcodec.a" > "$LOGS/ffmpeg-sim-sha.txt"
  hash_pair "$D/sdl2-ios-device/lib/libSDL2.a" > "$LOGS/sdl2-device-sha.txt"
  hash_pair "$D/sdl2-ios-sim/lib/libSDL2.a" > "$LOGS/sdl2-sim-sha.txt"
  hash_pair "$I26/ios-device.toolchain.cmake" > "$LOGS/toolchain-device-sha.txt"
  hash_pair "$I26/ios-simulator.toolchain.cmake" > "$LOGS/toolchain-sim-sha.txt"
  hash_pair "$ENVFILE" > "$LOGS/env-sha.txt"
  hash_pair "$I26/ps2x.env" > "$LOGS/env-i26-sha.txt"
  hash_pair "$I26/entitlements.plist" > "$LOGS/entitlements-sha.txt"
  hash_pair "$RAYLIB/src/platforms/rcore_desktop_sdl.c" > "$LOGS/raylib-pre-sha.txt"
  python3 - "$PROFILE" "$IPHONE" "$IPAD" <<'PY' > "$LOGS/profile-check.txt"
import datetime, plistlib, subprocess, sys
profile, iphone, ipad = sys.argv[1:]
r = subprocess.run(['security', 'cms', '-D', '-i', profile], capture_output=True, check=True)
p = plistlib.loads(r.stdout)
assert p['UUID'] == 'f0793278-db43-413c-9260-f120dc740845'
assert 'LQ3V7772Q2' in p['TeamIdentifier']
assert p['Entitlements']['application-identifier'] == 'LQ3V7772Q2.*'
assert iphone in p['ProvisionedDevices'], 'iPhone missing from profile'
assert ipad in p['ProvisionedDevices'], 'iPad missing from profile'
assert datetime.datetime.now(datetime.timezone.utc) < p['ExpirationDate'].replace(tzinfo=datetime.timezone.utc)
for key in ('UUID', 'Name', 'ExpirationDate'):
    print(key, p[key])
print('TeamIdentifier LQ3V7772Q2')
print('ApplicationIdentifier LQ3V7772Q2.*')
print('iPhoneProvisioned true')
print('iPadProvisioned true')
PY
  security find-identity -v -p codesigning | grep -F "$IDENTITY" > "$LOGS/identity-check.txt"
  xcrun devicectl list devices > "$LOGS/devices-before.txt"
  grep -F "$IPHONE" "$LOGS/devices-before.txt" | grep -E 'connected|available'
  grep -F "$IPAD" "$LOGS/devices-before.txt" | grep -E 'connected|available'
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
    -S "$FORK_WT" -B "$BUILD" > "$LOGS/$1-configure.log" 2>&1
  rg '^CMAKE_(C|CXX)_FLAGS_RELEASE:STRING=-O3 -DNDEBUG$' "$BUILD/CMakeCache.txt" > "$LOGS/$1-release-cache.txt"
  test "$(wc -l < "$LOGS/$1-release-cache.txt" | tr -d ' ')" = 2
  rg 'patched pinned raylib iOS SDL2 DPI path|pinned raylib iOS SDL2 DPI patch already applied' "$LOGS/$1-configure.log" > "$LOGS/$1-raylib-patch-result.txt"
  hash_pair "$RAYLIB/src/platforms/rcore_desktop_sdl.c" > "$LOGS/$1-raylib-post-sha.txt"
}

build_one() { # $1 = sim|device (nice'd; UP1 builds concurrently)
  t_paths "$1"
  nice -n 10 cmake --build "$BUILD" --config Release --target ps2EntryRunner -- -jobs "$JOBS" \
    > "$LOGS/$1-build.log" 2>&1
  test -f "$APP/ps2EntryRunner"
  hash_pair "$APP/ps2EntryRunner" > "$LOGS/$1-source-binary-sha.txt"
  xcodebuild -project "$BUILD/PS2RetroX.xcodeproj" -target ps2_game_objects -configuration Release \
    -showBuildSettings > "$LOGS/$1-game-buildsettings.log" 2>&1
  xcodebuild -project "$BUILD/PS2RetroX.xcodeproj" -target raylib -configuration Release \
    -showBuildSettings > "$LOGS/$1-raylib-buildsettings.log" 2>&1
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
  chmod 0644 "$STAGE/SLUS_207.72" "$STAGE/SSX3.iso" "$STAGE/ps2x.env"
  find "$STAGE" -name '._*' -delete || true
  if [ "$1" = sim ]; then codesign --force --sign - --timestamp=none "$STAGE"; fi
  hash_pair "$STAGE/SLUS_207.72" > "$LOGS/$1-elf-stage-sha.txt"
  hash_pair "$STAGE/SSX3.iso" > "$LOGS/$1-iso-stage-sha.txt"
  cmp "$LOGS/elf-input-sha.txt" <(sed "s|$STAGE/SLUS_207.72|$ELF|" "$LOGS/$1-elf-stage-sha.txt")
  cmp "$LOGS/iso-input-sha.txt" <(sed "s|$STAGE/SSX3.iso|$ISO|" "$LOGS/$1-iso-stage-sha.txt")
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
  test -f "$LOGS/profile-check.txt"
  cp "$PROFILE" "$STAGE/embedded.mobileprovision"
  cp "$I26/entitlements.plist" "$W/staged/entitlements.plist"
  codesign --force --sign "$IDENTITY" --timestamp=none \
    --entitlements "$W/staged/entitlements.plist" "$STAGE" > "$LOGS/codesign.log" 2>&1
  codesign --verify --strict --verbose=2 "$STAGE" > "$LOGS/codesign-verify.log" 2>&1
  codesign -dv "$STAGE" > "$LOGS/codesign-details.txt" 2>&1
  hash_pair "$STAGE/ps2EntryRunner" > "$LOGS/signed-binary-sha.txt"
}

install_iphone() {
  t_paths device
  xcrun devicectl list devices > "$LOGS/devices-install-iphone.txt"
  grep -F "$IPHONE" "$LOGS/devices-install-iphone.txt" | grep -E 'connected|available'
  xcrun devicectl device install app --device "$IPHONE" --timeout 1200 "$STAGE" \
    > "$LOGS/install-iphone.log" 2>&1
  cat "$LOGS/install-iphone.log"
}

install_ipad() {
  t_paths device
  xcrun devicectl device install app --device "$IPAD" --timeout 1200 "$STAGE" \
    > "$LOGS/install-ipad.log" 2>&1
  cat "$LOGS/install-ipad.log"
}

for step in "$@"; do echo "[i32 $(date +%H:%M:%S)] stage $step"; "$step"; done
