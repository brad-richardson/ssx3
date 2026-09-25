#!/bin/zsh
# VR1 speed session (E57 recipe): diagnostics-off runners, exclusive mini lease per boot,
# order from $CANDS (ABBA so drift cancels); labels s<N>-<cand> numbered from $START.
cd ~/dev/ssx3-work/VR1
n=${START:-0}
for c in ${=CANDS}; do
  n=$((n+1))
  python3 ~/dev/ssx3/local/research/VR1/vr1_boot.py --mode speed --runner bin/runner-$c-speed \
    --label s$n-$c --stop-tick 2400 > boot-s$n-$c.txt 2>&1
  echo "s$n-$c rc=$? $(date +%H:%M:%S) load=$(sysctl -n vm.loadavg)"
done
