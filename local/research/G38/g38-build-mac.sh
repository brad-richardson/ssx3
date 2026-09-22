#!/usr/bin/env bash
# G38: ONE Mac build of the excised (G31-equivalent) tree. Recipe: G7 §2a
# (VULKAN_SDK=/opt/homebrew + Ninja + -j2), new SSD build dir.
set -u
export COPYFILE_DISABLE=1
SSD="/Volumes/Extreme SSD"
CLONE="$SSD/parallel-gs-g7"
BUILD="$SSD/parallel-gs-g38-mac-build"
export VULKAN_SDK=/opt/homebrew
cmake -S "$CLONE" -B "$BUILD" -G Ninja 2>&1 | tail -5
echo "CONFIG_EXIT:${PIPESTATUS[0]}"
cmake --build "$BUILD" --target parallel-gs-replayer -j2 2>&1 | tail -8
echo "BUILD_EXIT:${PIPESTATUS[0]}"
ls -la "$BUILD/tools/parallel-gs-replayer"
shasum -a 256 "$BUILD/tools/parallel-gs-replayer"
