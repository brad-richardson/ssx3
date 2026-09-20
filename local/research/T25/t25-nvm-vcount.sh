#!/usr/bin/env bash
# T25 Phase 1: robust vblank counts at log-time marks on the no-input emulog.
E=/home/brad/pcsx2-t4/dat/PCSX2/logs/emulog.txt
awk '/WaitVblankStart/ {
  line = $0
  sub(/^\[ */, "", line)
  sub(/\].*$/, "", line)
  t = line + 0
  total++
  if (t <= 90) c90++
  if (t <= 120) c120++
  if (t <= 135) c135++
}
END { print "TOTAL=" total " LE90=" c90 " LE120=" c120 " LE135=" c135 }' $E
