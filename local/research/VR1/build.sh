#!/bin/zsh
# VR1 build: $1 = base|vr1, $2 = hash|speed. Release, homebrew clang, paraLLEl shadow ON
# (F2 recipe), diagnostics off; hash adds only the det-hash tap.
set -euo pipefail
which=$1 kind=$2
src=~/dev/ssx3-work/VR1/PS2Recomp
[[ $which == base ]] && src=~/dev/ssx3-work/VR1/base-src
recomp=""
[[ $which == gen* ]] && recomp=~/dev/ssx3-work/VR1/gen-v2
bld=~/dev/ssx3-work/VR1/build-$which-$kind
tap=OFF; [[ $kind == hash ]] && tap=ON
if [[ ! -f $bld/build.ninja ]]; then
  cmake -S $src -B $bld -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
    -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
    -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
    -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
    -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=$tap \
    -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/F2/parallel-gs \
    -DPS2X_VU1_RECOMP_DIR=$recomp -DCMAKE_EXPORT_COMPILE_COMMANDS=ON > $bld.configure.log 2>&1 || { mkdir -p $bld; cmake -S $src -B $bld -G Ninja 2>&1 | tail -20; exit 1; }
fi
nice -n 10 cmake --build $bld --parallel 12 --target ps2EntryRunner ps2x_tests
