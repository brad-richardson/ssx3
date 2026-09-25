#!/bin/zsh
# VB1 build: $1 = candidate label (bin name), $2 = hash|speed. Source = the VB1 worktree
# at its current state; generated VU1 images = ~/dev/ssx3-work/vu1gen-ssx3 (unchanged from
# VR1 gen-v2). Release, homebrew clang, paraLLEl shadow ON (F2 recipe), diagnostics off;
# hash adds only the det-hash tap. Binaries are copied to bin/<kind>-<label>.
set -euo pipefail
label=$1 kind=$2
src=~/dev/ssx3-work/VB1/PS2Recomp
recomp=~/dev/ssx3-work/vu1gen-ssx3
bld=~/dev/ssx3-work/VB1/build-$kind
tap=OFF; [[ $kind == hash ]] && tap=ON
if [[ ! -f $bld/build.ninja ]]; then
  cmake -S $src -B $bld -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
    -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
    -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
    -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
    -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=$tap \
    -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/F2/parallel-gs \
    -DPS2X_VU1_RECOMP_DIR=$recomp -DCMAKE_EXPORT_COMPILE_COMMANDS=ON > $bld.configure.log 2>&1
fi
nice -n 10 cmake --build $bld --parallel 12 --target ps2EntryRunner ps2x_tests > $bld.log 2>&1 || { grep -E "error|Error" -A3 $bld.log | head -40; exit 1; }
runner=$(find $bld -name ps2EntryRunner -type f -perm +111 | head -1)
tests=$(find $bld -name ps2x_tests -type f -perm +111 | head -1)
cp $runner bin/runner-$label-$kind; cp $tests bin/tests-$label-$kind
shasum -a 256 bin/runner-$label-$kind bin/tests-$label-$kind
