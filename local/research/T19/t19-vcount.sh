#!/usr/bin/env bash
# T19: robust vblank counts at log-time marks on the two-press emulog.
E=/home/brad/pcsx2-t4/dat/PCSX2/logs/emulog.txt
awk '/WaitVblankStart/ {
  line = $0
  sub(/^\[ */, "", line)
  sub(/\].*$/, "", line)
  t = line + 0
  total++
  if (t <= 90) c90++
  if (t <= 100) c100++
  if (t <= 112) c112++
  if (t <= 120) c120++
  if (t <= 352) c352++
}
END { print "TOTAL=" total " LE90=" c90 " LE100=" c100 " LE112=" c112 " LE120=" c120 " LE352=" c352 }' $E
