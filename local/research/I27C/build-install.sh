#!/bin/bash
# I27C: pinned, optimized iphoneos build; stage, sign, and install only.
set -euo pipefail
W=/Users/brad/dev/ssx3-work/I27C
REPO=/Users/brad/dev/ssx3
FORK_WT="$W/PS2Recomp"
RAYLIB="$W/raylib-src"
CODEGEN=/Users/brad/dev/ssx3-work/codegen-ssx3
PW=/Users/brad/dev/ssx3-work/I25
I26="$REPO/local/research/I26"
BUILD="$W/ios-runtime-device-release"
APP="$BUILD/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
STAGE="$W/staged/ps2EntryRunner.app"
LOGS="$W/logs"
ELF=/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72
ISO='/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso'
PROFILE='/Users/brad/Library/Developer/Xcode/UserData/Provisioning Profiles/f0793278-db43-413c-9260-f120dc740845.mobileprovision'
IPHONE=00008140-0002505001F3001C
IDENTITY=295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1
PIN=04f3ace599e3d9d52b94803150688f54dbf330ec
RAYPIN=c1ab645ca298a2801097931d1079b10ff7eb9df8
mkdir -p "$LOGS"

hash_pair() { shasum -a 256 "$1" "$1"; }

preflight() {
  test "$(git -C "$FORK_WT" rev-parse HEAD)" = "$PIN"
  test "$(git -C "$FORK_WT" rev-parse fork/ssx3)" = "$PIN"
  git -C "$FORK_WT" diff --exit-code 14b1e5cb HEAD -- ps2xRuntime/src/runner
  test "$(git -C "$RAYLIB" rev-parse HEAD)" = "$RAYPIN"
  test "$(shasum -a 256 "$RAYLIB/src/platforms/rcore_desktop_sdl.c" | cut -d' ' -f1)" = 30db3e9f5c2d1c2bf656ba06a59b5cf8c740a3024a65134a6d5edf57cc18984d
  hash_pair "$CODEGEN/register_functions.cpp" > "$LOGS/codegen-sha.txt"
  hash_pair "$RAYLIB/src/platforms/rcore_desktop_sdl.c" > "$LOGS/raylib-original-sha.txt"
  hash_pair "$ELF" > "$LOGS/elf-input-sha.txt"
  hash_pair "$ISO" > "$LOGS/iso-input-sha.txt"
  hash_pair "$PROFILE" > "$LOGS/profile-sha.txt"
  hash_pair "$PW/ffmpeg-ios-7.1.1/lib/libavcodec.a" > "$LOGS/ffmpeg-sha.txt"
  hash_pair "$PW/sdl2-ios-device/lib/libSDL2.a" > "$LOGS/sdl2-sha.txt"
  hash_pair "$I26/ios-device.toolchain.cmake" > "$LOGS/toolchain-sha.txt"
  hash_pair "$I26/ps2x.env" > "$LOGS/env-sha.txt"
  hash_pair "$I26/entitlements.plist" > "$LOGS/entitlements-sha.txt"
  python3 - "$PROFILE" "$IPHONE" <<'PY' > "$LOGS/profile-check.txt"
import datetime, plistlib, subprocess, sys
profile, iphone = sys.argv[1:]
r = subprocess.run(['security', 'cms', '-D', '-i', profile], capture_output=True, check=True)
p = plistlib.loads(r.stdout)
assert p['UUID'] == 'f0793278-db43-413c-9260-f120dc740845'
assert 'LQ3V7772Q2' in p['TeamIdentifier']
assert p['Entitlements']['application-identifier'] == 'LQ3V7772Q2.*'
assert iphone in p['ProvisionedDevices']
assert datetime.datetime.now(datetime.timezone.utc) < p['ExpirationDate'].replace(tzinfo=datetime.timezone.utc)
for key in ('UUID', 'Name', 'ExpirationDate'):
    print(key, p[key])
print('TeamIdentifier LQ3V7772Q2')
print('ApplicationIdentifier LQ3V7772Q2.*')
print('iPhoneProvisioned true')
PY
  security find-identity -v -p codesigning | grep -F "$IDENTITY" > "$LOGS/identity-check.txt"
  xcrun devicectl list devices > "$LOGS/devices-before.txt"
  grep -F "$IPHONE" "$LOGS/devices-before.txt" | grep -F connected
}

configure() {
  test ! -e "$BUILD/CMakeCache.txt"
  env -u CC -u CXX cmake -G Xcode \
    -DCMAKE_TOOLCHAIN_FILE="$I26/ios-device.toolchain.cmake" \
    -DCMAKE_C_FLAGS_RELEASE='-O3 -DNDEBUG' \
    -DCMAKE_CXX_FLAGS_RELEASE='-O3 -DNDEBUG' \
    -DCMAKE_CONFIGURATION_TYPES=Release \
    -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
    -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF \
    -DPS2X_ENABLE_SCCACHE=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
    -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF \
    -DPS2X_ENABLE_FFMPEG=ON -DPS2X_FFMPEG_IOS_ROOT="$PW/ffmpeg-ios-7.1.1" \
    -DSDL2_DIR="$PW/sdl2-ios-device/lib/cmake/SDL2" \
    -DFETCHCONTENT_SOURCE_DIR_RAYLIB="$RAYLIB" \
    -DPS2X_GAME_CODEGEN_DIR="$CODEGEN" \
    -S "$FORK_WT" -B "$BUILD" > "$LOGS/device-configure.log" 2>&1
  rg '^CMAKE_(C|CXX)_FLAGS_RELEASE:STRING=-O3 -DNDEBUG$' "$BUILD/CMakeCache.txt" > "$LOGS/release-cache.txt"
  test "$(wc -l < "$LOGS/release-cache.txt" | tr -d ' ')" = 2
  rg 'patched pinned raylib iOS SDL2 DPI path|pinned raylib iOS SDL2 DPI patch already applied' "$LOGS/device-configure.log" > "$LOGS/raylib-patch-result.txt"
  hash_pair "$RAYLIB/src/platforms/rcore_desktop_sdl.c" > "$LOGS/raylib-patched-sha.txt"
}

build() {
  while ps -axo args | rg -q '[c]lang\+\+|[/]clang |[n]inja|[x]codebuild'; do
    echo 'Other clang/ninja/Xcode build active; waiting 60 s'
    sleep 60
  done
  nice -n 10 cmake --build "$BUILD" --config Release --target ps2EntryRunner -- -jobs 8 \
    > "$LOGS/device-build.log" 2>&1
  test -f "$APP/ps2EntryRunner"
  hash_pair "$APP/ps2EntryRunner" > "$LOGS/source-binary-sha.txt"
}

stage() {
  test ! -e "$STAGE"
  mkdir -p "$(dirname "$STAGE")"
  cp -R "$APP" "$STAGE"
  cp "$ELF" "$STAGE/SLUS_207.72"
  cp -c "$ISO" "$STAGE/SSX3.iso"
  cp "$I26/ps2x.env" "$STAGE/ps2x.env"
  cp -R "$FORK_WT/ps2xRuntime/ios/Settings.bundle" "$STAGE/Settings.bundle"
  chmod 0644 "$STAGE/SLUS_207.72" "$STAGE/SSX3.iso" "$STAGE/ps2x.env"
  hash_pair "$STAGE/SLUS_207.72" > "$LOGS/elf-stage-sha.txt"
  hash_pair "$STAGE/SSX3.iso" > "$LOGS/iso-stage-sha.txt"
  hash_pair "$STAGE/ps2EntryRunner" > "$LOGS/stage-unsigned-binary-sha.txt"
  cmp "$LOGS/elf-input-sha.txt" <(sed "s|$STAGE/SLUS_207.72|$ELF|" "$LOGS/elf-stage-sha.txt")
  cmp "$LOGS/iso-input-sha.txt" <(sed "s|$STAGE/SSX3.iso|$ISO|" "$LOGS/iso-stage-sha.txt")
  /usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$STAGE/Info.plist" | grep -Fx org.ps2x.ps2entryrunner
}

sign() {
  test -f "$LOGS/profile-check.txt"
  cp "$PROFILE" "$STAGE/embedded.mobileprovision"
  cp "$I26/entitlements.plist" "$W/staged/entitlements.plist"
  codesign --force --sign "$IDENTITY" --timestamp=none \
    --entitlements "$W/staged/entitlements.plist" "$STAGE" > "$LOGS/codesign.log" 2>&1
  codesign --verify --strict --verbose=2 "$STAGE" > "$LOGS/codesign-verify.log" 2>&1
  codesign -dv "$STAGE" > "$LOGS/codesign-details.txt" 2>&1
  hash_pair "$STAGE/ps2EntryRunner" > "$LOGS/signed-binary-sha.txt"
}

install() {
  xcrun devicectl list devices > "$LOGS/devices-install.txt"
  grep -F "$IPHONE" "$LOGS/devices-install.txt" | grep -F connected
  xcrun devicectl device install app --device "$IPHONE" --timeout 1200 "$STAGE" \
    > "$LOGS/install-iphone.log" 2>&1
  cat "$LOGS/install-iphone.log"
}

for step in "$@"; do "$step"; done
