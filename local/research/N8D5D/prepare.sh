#!/usr/bin/env bash
set -euo pipefail
root=/home/brad/n8d5d
mkdir -p "$root/PS2Recomp" "$root/parallel-gs" "$root/jniLibs"
rsync -a --exclude=.cxx --exclude=build --exclude=.gradle \
  --exclude=/ps2xRuntime/src/runner/ \
  /home/brad/n8b1/PS2Recomp/ "$root/PS2Recomp/"
rsync -a --exclude=.cxx --exclude=build --exclude=.gradle \
  /home/brad/n8b1/parallel-gs/ "$root/parallel-gs/"
rsync -a /home/brad/n8d3/jniLibs/ "$root/jniLibs/"
diff -rq --exclude=.cxx --exclude=build --exclude=.gradle \
  --exclude=runner /home/brad/n8b1/PS2Recomp "$root/PS2Recomp" \
  > "$root/source-diff-pre-candidate.txt"
test ! -s "$root/source-diff-pre-candidate.txt"
diff -rq --exclude=.cxx --exclude=build --exclude=.gradle \
  /home/brad/n8b1/parallel-gs "$root/parallel-gs" \
  > "$root/parallel-diff-pre-candidate.txt"
test ! -s "$root/parallel-diff-pre-candidate.txt"
diff -rq /home/brad/n8d3/jniLibs "$root/jniLibs" \
  > "$root/jni-diff-pre-candidate.txt"
test ! -s "$root/jni-diff-pre-candidate.txt"
du -sh "$root" "$root/PS2Recomp" "$root/parallel-gs" "$root/jniLibs"
