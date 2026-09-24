#!/usr/bin/env bash
# N8D7M12P3 prepare: copy N8D7M1 -> new WSL root, excluding caches and runner.
# Same shape as N8D7M1 prepare.sh, new root. No overlay here (separate step).
set -euo pipefail
root=/home/brad/n8d7m12p3
base=/home/brad/n8d7m1
test ! -e "$root"
mkdir -p "$root/PS2Recomp" "$root/parallel-gs" "$root/jniLibs"
rsync -a --exclude=.cxx --exclude=build --exclude=.gradle \
  --exclude=/ps2xRuntime/src/runner/ \
  "$base/PS2Recomp/" "$root/PS2Recomp/"
rsync -a --exclude=.cxx --exclude=build --exclude=.gradle \
  "$base/parallel-gs/" "$root/parallel-gs/"
rsync -a "$base/jniLibs/" "$root/jniLibs/"
echo "== diff PS2Recomp vs N8D7M1 (expect empty) =="
diff -rq --exclude=.cxx --exclude=build --exclude=.gradle \
  --exclude=runner "$base/PS2Recomp" "$root/PS2Recomp" \
  > "$root/source-diff-pre-candidate.txt" || test -s "$root/source-diff-pre-candidate.txt"
test ! -s "$root/source-diff-pre-candidate.txt"
echo "== diff parallel-gs vs N8D7M1 (expect empty) =="
diff -rq --exclude=.cxx --exclude=build --exclude=.gradle \
  "$base/parallel-gs" "$root/parallel-gs" \
  > "$root/parallel-diff-pre-candidate.txt" || test -s "$root/parallel-diff-pre-candidate.txt"
test ! -s "$root/parallel-diff-pre-candidate.txt"
echo "== diff jniLibs vs N8D7M1 (expect empty) =="
diff -rq "$base/jniLibs" "$root/jniLibs" \
  > "$root/jni-diff-pre-candidate.txt" || test -s "$root/jni-diff-pre-candidate.txt"
test ! -s "$root/jni-diff-pre-candidate.txt"
echo "PRE_CANDIDATE_DIFFS_EMPTY"
echo "== header pin in both roots (expect 9635a40e...) =="
sha256sum "$base/PS2Recomp/ps2xRuntime/include/runtime/gs/ps2_gs_psmct32.h" \
  "$root/PS2Recomp/ps2xRuntime/include/runtime/gs/ps2_gs_psmct32.h"
du -sh "$root"
