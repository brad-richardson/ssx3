#!/usr/bin/env bash
# T61 kmap: emulog timestamp <-> vsync for appsum lines with n_app>0,
# plus ebwend vsync and duplicate-apc check.
E=/home/brad/pcsx2-g7/dat-t57/PCSX2/logs/emulog.txt
echo "=== appsum n_app>0 : emuts vsync n_app hist ==="
awk '{ if (match($0, /^\[[ 0-9.]*\]/)) ts=substr($0, 2, RLENGTH-2)+0 }
  /appsum vsync=/ && / n_app=[1-9]/ {
    if (match($0, /appsum vsync=[0-9]+ n_app=[0-9]+ n_tpl=[0-9]+ mode_hist=[^ ]*/))
      print ts, substr($0, RSTART, RLENGTH) }' "$E"
echo "=== ebwend ==="
grep -a "ebwend vsync=" "$E" | sed 's/^[^]]*] //'
echo "=== apc duplicate-vsync check ==="
grep -a -o "apc vsync=[0-9]*" "$E" | sort -t= -k2 -n | uniq -d
echo T61_KMAP_DONE
