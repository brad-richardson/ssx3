#!/bin/bash
# PX1: copy gsrunner frames + log tail to the Windows side for scp retrieval.
# $1 = label, $2.. = frame numbers (dumpdir px1a-*.png) or "log".
set -eu
R=/home/brad/px1
LABEL=$1; shift
D=$R/frames-$LABEL
OUT=/mnt/c/Users/bradr/px1back/$LABEL
mkdir -p $OUT
for f in "$@"; do
  if [ "$f" = log ]; then
    cp $R/gsrunner-$LABEL.log $OUT/
  else
    n=$(printf "%05d" $f)
    cp $D/*_frame$n.png $OUT/ 2>/dev/null || cp $D/*frame$n.png $OUT/
  fi
done
ls $OUT
