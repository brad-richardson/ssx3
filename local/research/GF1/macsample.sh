#!/bin/bash
# GF1 stage 1: one diagnostic Mac boot (one lease slot), `sample` the runner over race ticks ~1900+.
set -u
T=/Users/brad/dev/ssx3/local/tooling
W=/Users/brad/dev/ssx3-work/GF1
R=/Users/brad/dev/ssx3-work/VR4/bin/runner-d1-clean
L=gf1-macsample
slot=$(python3 -c "import sys; sys.path.insert(0,'$T'); import p_lane_lease as L; print(L.claim('gf1-macsample') or '')")
[ -n "$slot" ] || { echo "no slot"; exit 1; }
echo "slot=$slot"
SSX3_HELD_SLOT=$slot python3 $T/boot/ssx3_boot.py --mode speed --backend parallel --runner $R --label $L --out $W/run/$L \
  --route fr1r1 --stop-tick 2400 --env PS2X_MTVU=1 --env PS2X_MTVU_LAG=1 --env PS2X_VU1_BLOCKS=1 > $W/run/$L.boot.log 2>&1 &
bp=$!
pid=""
for i in $(seq 1 600); do
  pid=$(grep -o '"pid": [0-9]*' $W/run/$L.boot.log 2>/dev/null | head -1 | grep -o '[0-9]*$')
  tick=$(tail -1 $W/run/$L/trace.jsonl 2>/dev/null | grep -o '"tick": [0-9]*' | grep -o '[0-9]*$')
  if [ -n "$pid" ] && [ -n "$tick" ] && [ "$tick" -ge 1900 ]; then break; fi
  sleep 1
done
echo "pid=$pid tick=$tick"
sample "$pid" 8 1 -mayDie -file $W/prof/mac-sample.txt > /dev/null 2>&1
tail -1 $W/run/$L/trace.jsonl
wait $bp; echo "boot rc=$?"
python3 -c "import sys; sys.path.insert(0,'$T'); import p_lane_lease as L; L.release(int('$slot'))"
echo released
