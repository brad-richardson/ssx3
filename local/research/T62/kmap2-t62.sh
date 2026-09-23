#!/usr/bin/env bash
# T62 kmap2: PATHS ts<->vsync around K (emuts~41.6) and SC-ident (emuts~60.4).
E=/home/brad/pcsx2-g7/dat-t57/PCSX2/logs/emulog.txt
awk '{ if (match($0, /^\[[ 0-9.]*\]/)) ts=substr($0, 2, RLENGTH-2)+0 }
  /^.*T48_PATHS vsync=/ {
    if ((ts > 39 && ts < 44) || (ts > 58 && ts < 63)) {
      if (match($0, /T48_PATHS vsync=[0-9]+/)) print ts, substr($0, RSTART, RLENGTH) } }' "$E"
echo T62_KMAP2_DONE
