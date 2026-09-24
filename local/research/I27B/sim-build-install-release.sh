#!/bin/bash
set -euo pipefail
W=/Users/brad/dev/ssx3-work/I27B
FORK_WT="$W/PS2Recomp"
I26=/Users/brad/dev/ssx3/local/research/I26
SIM=7662ACD6-6294-4676-B426-26A3F8C7B258
BUILD="$W/ios-runtime-sim-release"
APP="$BUILD/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app"
STAGE="$W/staged-sim/ps2EntryRunner.app"
CACHE="$BUILD/CMakeCache.txt"
rg -q '^CMAKE_C_FLAGS_RELEASE:STRING=-O3 -DNDEBUG$' "$CACHE"
rg -q '^CMAKE_CXX_FLAGS_RELEASE:STRING=-O3 -DNDEBUG$' "$CACHE"
cmake --build "$BUILD" --config Release --target ps2EntryRunner -- -jobs 8 \
  > "$W/logs/sim-release-build.log" 2>&1

mkdir -p "$(dirname "$STAGE")"
cp -R "$APP" "$STAGE"
ELF=/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72
ISO='/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso'
shasum -a 256 "$ELF" "$ELF" "$ISO" "$ISO" > "$W/logs/sim-input-sha.txt"
cp "$ELF" "$STAGE/SLUS_207.72"
cp -c "$ISO" "$STAGE/SSX3.iso"
cp "$I26/ps2x.env" "$STAGE/ps2x.env"
cp -R "$FORK_WT/ps2xRuntime/ios/Settings.bundle" "$STAGE/Settings.bundle"
chmod 0644 "$STAGE/SLUS_207.72" "$STAGE/SSX3.iso" "$STAGE/ps2x.env"
shasum -a 256 "$STAGE/SLUS_207.72" "$STAGE/SLUS_207.72" \
  "$STAGE/SSX3.iso" "$STAGE/SSX3.iso" > "$W/logs/sim-stage-sha.txt"
codesign --force --sign - --timestamp=none "$STAGE"
shasum -a 256 "$STAGE/ps2EntryRunner" "$STAGE/ps2EntryRunner" \
  > "$W/logs/sim-binary-sha.txt"
xcrun simctl bootstatus "$SIM" -b > "$W/logs/sim-release-bootstatus.log" 2>&1
xcrun simctl install "$SIM" "$STAGE" > "$W/logs/sim-release-install.log" 2>&1
echo 'I27B Simulator build, stage, install completed'
