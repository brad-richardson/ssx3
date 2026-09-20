#!/usr/bin/env bash
# T21: robust vblank counts at log-time marks on the three-press emulog.
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
  if (t <= 121) c121++
  if (t <= 362) c362++
}
END { print "TOTAL=" total " LE90=" c90 " LE100=" c100 " LE112=" c112 " LE121=" c121 " LE362=" c362 }' $E
