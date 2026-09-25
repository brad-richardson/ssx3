#!/bin/bash
# Canonical Mac runner build (RS1): the F5 recipe of record behind a shared
# ccache, so every lane compiles only what it changed. Every brief that needs
# a Mac runner calls this instead of inlining its own cmake lines.
#
# Usage:
#   mac_build.sh <fork-worktree> <build-dir> [--det] [--no-cache]
#                [--vu1 DIR] [--pgs DIR] [--codegen DIR] [--target T]...
#
#   <fork-worktree>  PS2Recomp fork checkout (e.g. ~/dev/ssx3-work/<ID>/PS2Recomp)
#   <build-dir>      fresh cmake build dir (need not exist)
#   --det            PS2X_ENABLE_DET_HASH_TAP=ON (default OFF)
#   --no-cache       no compiler launcher (control builds; default: ccache)
#   --vu1 DIR        PS2X_VU1_RECOMP_DIR (default: ~/dev/ssx3-work/vu1gen-ssx3)
#   --pgs DIR        PS2X_PARALLEL_GS_SOURCE_DIR (default: ~/dev/ssx3-work/F2/parallel-gs)
#   --codegen DIR    PS2X_GAME_CODEGEN_DIR (default: ~/dev/ssx3-work/codegen-ssx3)
#   --target T       cmake target (repeatable; default: ps2x_tests ps2EntryRunner)
#
# Prints the configure line, `ccache -s` before/after (unless --no-cache),
# and wall time. Always passes -DPS2X_ENABLE_SCCACHE=OFF: the in-tree sccache
# hook would otherwise override the launcher if sccache is ever installed.
set -euo pipefail

if [ $# -lt 2 ]; then sed -n '2,18p' "$0"; exit 2; fi
WT=$1; BD=$2; shift 2
DET=OFF; CACHE=ON
VU1=$HOME/dev/ssx3-work/vu1gen-ssx3
PGS=$HOME/dev/ssx3-work/F2/parallel-gs
CODEGEN=$HOME/dev/ssx3-work/codegen-ssx3
TARGETS=()
while [ $# -gt 0 ]; do
  case $1 in
    --det) DET=ON;;
    --no-cache) CACHE=OFF;;
    --vu1) VU1=$2; shift;;
    --pgs) PGS=$2; shift;;
    --codegen) CODEGEN=$2; shift;;
    --target) TARGETS+=("$2"); shift;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
  shift
done
[ "${#TARGETS[@]}" -eq 0 ] && TARGETS=(ps2x_tests ps2EntryRunner)
for d in "$WT" "$VU1" "$PGS" "$CODEGEN"; do
  [ -d "$d" ] || { echo "missing dir: $d" >&2; exit 2; }
done
if [ "$CACHE" = ON ] && ! command -v ccache >/dev/null; then
  echo "ccache not installed (brew install ccache) or pass --no-cache" >&2; exit 2
fi

if [ "$CACHE" = ON ]; then echo "--- ccache before ---"; ccache -s; fi

CONFIGURE=(cmake -S "$WT" -B "$BD" -G Ninja -DCMAKE_BUILD_TYPE=Release
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++
  -DPS2X_GAME_CODEGEN_DIR="$CODEGEN" -DPS2X_VU1_RECOMP_DIR="$VU1"
  -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP="$DET"
  -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR="$PGS"
  -DPS2X_ENABLE_SCCACHE=OFF -DCMAKE_EXPORT_COMPILE_COMMANDS=ON)
# NB: appended conditionally (not "${EMPTY_ARR[@]}") for macOS bash 3.2 + set -u.
if [ "$CACHE" = ON ]; then
  CONFIGURE+=(-DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache)
fi
echo "--- configure ---"; printf '%q ' "${CONFIGURE[@]}"; echo

START=$SECONDS
"${CONFIGURE[@]}"
cmake --build "$BD" --parallel 8 --target "${TARGETS[@]}"
echo "--- wall: $((SECONDS - START)) s (configure+build) ---"
if [ "$CACHE" = ON ]; then echo "--- ccache after ---"; ccache -s; fi
