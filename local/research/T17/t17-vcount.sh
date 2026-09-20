#!/usr/bin/env bash
# T17: robust vblank counts at log-time marks on the t17c emulog.
E=/home/brad/pcsx2-t4/dat/PCSX2/logs/emulog.txt
awk '/WaitVblankStart/ {
  line = $0
  sub(/^\[ */, "", line)
  sub(/\].*$/, "", line)
  t = line + 0
  total++
  if (t <= 90) c90++
  if (t <= 100) c100++
  if (t <= 110) c110++
  if (t <= 340) c340++
}
END { print "TOTAL=" total " LE90=" c90 " LE100=" c100 " LE110=" c110 " LE340=" c340 }' $E
