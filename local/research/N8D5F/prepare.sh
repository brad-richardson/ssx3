#!/usr/bin/env bash
set -euo pipefail
root=/home/brad/n8d5f
test ! -e "$root"
mkdir -p "$root/PS2Recomp" "$root/parallel-gs" "$root/jniLibs"
rsync -a --exclude=.cxx --exclude=build --exclude=.gradle \
  --exclude=/ps2xRuntime/src/runner/ \
  /home/brad/n8d5d/PS2Recomp/ "$root/PS2Recomp/"
rsync -a --exclude=.cxx --exclude=build --exclude=.gradle \
  /home/brad/n8d5d/parallel-gs/ "$root/parallel-gs/"
rsync -a /home/brad/n8d5d/jniLibs/ "$root/jniLibs/"
diff -rq --exclude=.cxx --exclude=build --exclude=.gradle \
  --exclude=runner /home/brad/n8d5d/PS2Recomp "$root/PS2Recomp" \
  > "$root/source-diff-pre-candidate.txt"
test ! -s "$root/source-diff-pre-candidate.txt"
diff -rq --exclude=.cxx --exclude=build --exclude=.gradle \
  /home/brad/n8d5d/parallel-gs "$root/parallel-gs" \
  > "$root/parallel-diff-pre-candidate.txt"
test ! -s "$root/parallel-diff-pre-candidate.txt"
diff -rq /home/brad/n8d5d/jniLibs "$root/jniLibs" \
  > "$root/jni-diff-pre-candidate.txt"
test ! -s "$root/jni-diff-pre-candidate.txt"
du -sh "$root" "$root/PS2Recomp" "$root/parallel-gs" "$root/jniLibs"
