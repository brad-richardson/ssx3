#!/usr/bin/env bash
# G41: the ONE budgeted Mac run (M1), SAME shape as the Odin leg + wall envs.
# Full G7 recipe env (G7 REPORT §6:255 + G38 §3d0 lesson: VK_ICD_FILENAMES +
# DYLD_LIBRARY_PATH=/opt/homebrew/lib).
set -u
export COPYFILE_DISABLE=1
SSD="/Volumes/Extreme SSD"
BIN="$SSD/parallel-gs-g41-mac-build/tools/parallel-gs-replayer"
D="$SSD/ps2x-g41/g41-dump.gs"
export VK_ICD_FILENAMES=/opt/homebrew/etc/vulkan/icd.d/MoltenVK_icd.json
export DYLD_LIBRARY_PATH=/opt/homebrew/lib
shasum -a 256 "$BIN" | cut -c1-16
shasum -a 256 "$D" | cut -c1-16
date +%s
PGS_G40_WALL=1 PGS_G41_CANARY=1 PGS_SKIP_COMPILATION_TASKS=1 "$BIN" "$D" --iterations 2 --disable-sampler-feedback \
  > "$SSD/ps2x-g41/g41-mac-stdout.txt" 2> "$SSD/ps2x-g41/g41-mac-stderr.txt"
echo "RUN_EXIT:$?"
date +%s
ls -la "$SSD/ps2x-g41/"
