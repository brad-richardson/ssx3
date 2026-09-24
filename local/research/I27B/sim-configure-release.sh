#!/bin/bash
set -euo pipefail
W=/Users/brad/dev/ssx3-work/I27B
FORK_WT="$W/PS2Recomp"
CODEGEN=/Users/brad/dev/ssx3-work/codegen-ssx3
I26=/Users/brad/dev/ssx3/local/research/I26
PW=/Users/brad/dev/ssx3-work/I25
SIM=7662ACD6-6294-4676-B426-26A3F8C7B258
BUILD="$W/ios-runtime-sim-release"
APP="$BUILD/ps2xRuntime/Release-iphonesimulator/ps2EntryRunner.app"
STAGE="$W/staged-sim/ps2EntryRunner.app"
mkdir -p "$W/logs"

env -u CC -u CXX cmake -G Xcode \
  -DCMAKE_TOOLCHAIN_FILE="$I26/ios-simulator.toolchain.cmake" \
  -DCMAKE_C_FLAGS_RELEASE="-O3 -DNDEBUG" \
  -DCMAKE_CXX_FLAGS_RELEASE="-O3 -DNDEBUG" \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_FFMPEG=ON \
  -DPS2X_FFMPEG_IOS_ROOT="$PW/ffmpeg-ios-sim-7.1.1" \
  -DSDL2_DIR="$PW/sdl2-ios-sim/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB=/Users/brad/dev/ssx3-work/I27B/raylib-src \
  -DPS2X_GAME_CODEGEN_DIR="$CODEGEN" \
  -S "$FORK_WT" -B "$BUILD" > "$W/logs/sim-release-configure.log" 2>&1
echo "fresh Release configure completed"
