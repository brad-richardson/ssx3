#!/bin/zsh
# E57 speed session: diagnostics-off runners, exclusive mini lease per boot,
# order from $CANDS (ABBA so drift cancels); labels numbered from $START. Labels s<N>-<cand>.
cd ~/dev/ssx3-work/E57
n=${START:-0}
for c in ${=CANDS}; do
  n=$((n+1))
  python3 ~/dev/ssx3/local/research/E57/e57_boot.py --mode speed --runner bin/runner-$c-speed \
    --label s$n-$c --stop-tick 2400 > boot-s$n-$c.txt 2>&1
  echo "s$n-$c rc=$?"
done
