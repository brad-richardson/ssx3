#!/usr/bin/env bash
set -euo pipefail
root=/home/brad/n8d7h
base=/home/brad/n8d6b
test ! -e "$root"
mkdir -p "$root/PS2Recomp" "$root/parallel-gs" "$root/jniLibs"
rsync -a --exclude=.cxx --exclude=build --exclude=.gradle \
  --exclude=/ps2xRuntime/src/runner/ \
  "$base/PS2Recomp/" "$root/PS2Recomp/"
rsync -a --exclude=.cxx --exclude=build --exclude=.gradle \
  "$base/parallel-gs/" "$root/parallel-gs/"
rsync -a "$base/jniLibs/" "$root/jniLibs/"
echo "== diff PS2Recomp vs N8D6B (expect empty) =="
diff -rq --exclude=.cxx --exclude=build --exclude=.gradle \
  --exclude=runner "$base/PS2Recomp" "$root/PS2Recomp" \
  > "$root/source-diff-pre-candidate.txt" || test -s "$root/source-diff-pre-candidate.txt"
test ! -s "$root/source-diff-pre-candidate.txt"
echo "== diff parallel-gs vs N8D6B (expect empty) =="
diff -rq --exclude=.cxx --exclude=build --exclude=.gradle \
  "$base/parallel-gs" "$root/parallel-gs" \
  > "$root/parallel-diff-pre-candidate.txt" || test -s "$root/parallel-diff-pre-candidate.txt"
test ! -s "$root/parallel-diff-pre-candidate.txt"
echo "== diff jniLibs vs N8D6B (expect empty) =="
diff -rq "$base/jniLibs" "$root/jniLibs" \
  > "$root/jni-diff-pre-candidate.txt" || test -s "$root/jni-diff-pre-candidate.txt"
test ! -s "$root/jni-diff-pre-candidate.txt"
echo "PRE_CANDIDATE_DIFFS_EMPTY"
du -sh "$root"
