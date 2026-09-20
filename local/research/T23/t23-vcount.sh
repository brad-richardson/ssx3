#!/usr/bin/env bash
# T23: robust vblank counts at log-time marks on the four-press emulog.
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
  if (t <= 130) c130++
  if (t <= 380) c380++
}
END { print "TOTAL=" total " LE90=" c90 " LE100=" c100 " LE112=" c112 " LE121=" c121 " LE130=" c130 " LE380=" c380 }' $E
