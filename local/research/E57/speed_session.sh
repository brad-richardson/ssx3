#!/bin/zsh
# E57 speed session: diagnostics-off runners, exclusive mini lease per boot,
# order base c1 c2 c3 c3 c2 c1 base (drift cancels). Labels s<N>-<cand>.
cd ~/dev/ssx3-work/E57
n=0
for c in base c1 c2 c3 c3 c2 c1 base; do
  n=$((n+1))
  python3 ~/dev/ssx3/local/research/E57/e57_boot.py --mode speed --runner bin/runner-$c-speed \
    --label s$n-$c --stop-tick 2400 > boot-s$n-$c.txt 2>&1
  echo "s$n-$c rc=$?"
done
