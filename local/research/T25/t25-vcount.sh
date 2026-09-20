#!/usr/bin/env bash
# T25 Phase 2: robust vblank counts at log-time marks on the two-press emulog.
E=/home/brad/pcsx2-t4/dat/PCSX2/logs/emulog.txt
awk '/WaitVblankStart/ {
  line = $0
  sub(/^\[ */, "", line)
  sub(/\].*$/, "", line)
  t = line + 0
  total++
  if (t <= 90) c90++
  if (t <= 110) c110++
  if (t <= 140) c140++
  if (t <= 350) c350++
}
END { print "TOTAL=" total " LE90=" c90 " LE110=" c110 " LE140=" c140 " LE350=" c350 }' $E
