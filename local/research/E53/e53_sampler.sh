#!/bin/zsh
# E53 Part 2: take `sample <pid> 10` when the boot's latest snapshot tick
# crosses each threshold. Usage: e53_sampler.sh <label> <boot.out> <tick1> <tick2>
set -u
label=$1 out=$2 t1=$3 t2=$4
RUN=$HOME/dev/ssx3-work/E53/run
pid=""
while [ -z "$pid" ]; do
  pid=$(grep -o '"event": "boot", "pid": [0-9]*' $out 2>/dev/null | grep -o '[0-9]*$' | head -1)
  sleep 1
done
echo "runner pid $pid"
n=1
for t in $t1 $t2; do
  while kill -0 $pid 2>/dev/null; do
    f=$(ls -t $RUN/frames-$label-1/snap/*.txt 2>/dev/null | head -1)
    tick=$( [ -n "$f" ] && head -1 $f | sed -E 's/.*tick=([0-9]+).*/\1/' )
    [ -n "$tick" ] && [ "$tick" -ge $t ] && break
    sleep 2
  done
  kill -0 $pid 2>/dev/null || { echo "runner exited before tick $t"; exit 1; }
  echo "sample $n at tick $tick $(date +%T)"
  sample $pid 10 -file $RUN/sample$n-$label-tick$tick.txt > /dev/null 2>&1
  echo "sample $n done rc=$?"
  n=$((n+1))
done
