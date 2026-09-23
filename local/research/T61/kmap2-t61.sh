#!/usr/bin/env bash
# T61 kmap2: T48_PATHS timestamp<->vsync around K (emuts~47.8) and SC-ident (emuts~68.7).
E=/home/brad/pcsx2-g7/dat-t57/PCSX2/logs/emulog.txt
awk '{ if (match($0, /^\[[ 0-9.]*\]/)) ts=substr($0, 2, RLENGTH-2)+0 }
  /^.*T48_PATHS vsync=/ {
    if ((ts > 45 && ts < 51) || (ts > 66 && ts < 72)) {
      if (match($0, /T48_PATHS vsync=[0-9]+/)) print ts, substr($0, RSTART, RLENGTH) } }' "$E"
echo T61_KMAP2_DONE
