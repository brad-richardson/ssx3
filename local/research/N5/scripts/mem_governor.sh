#!/bin/bash
# N5: keep bytesize WSL out of OOM without killing compiles. Pauses the youngest
# running clang++ when MemAvailable < LOW MB; resumes the oldest paused one when
# MemAvailable > HIGH MB (or nothing else runs). Exits when ninja exits.
LOW=${LOW:-3072}; HIGH=${HIGH:-5120}; LOG=${GOV_LOG:-~/n5/logs/governor.txt}
echo "$(date -u +%T) governor start LOW=$LOW HIGH=$HIGH" >> $LOG
for _ in $(seq 1 30); do pgrep -x ninja >/dev/null && break; sleep 1; done
while pgrep -x ninja >/dev/null; do
  avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  running=$(ps -eo pid,etimes,stat,comm --sort=etimes | awk '$4=="clang++" && $3!~/T/{print $1}')
  stopped=$(ps -eo pid,etimes,stat,comm --sort=-etimes | awk '$4=="clang++" && $3~/T/{print $1}')
  nrun=$(echo "$running" | grep -c .)
  if [ "$avail" -lt "$LOW" ] && [ "$nrun" -gt 1 ]; then
    p=$(echo "$running" | head -1); kill -STOP "$p" && echo "$(date -u +%T) avail=${avail}M STOP $p (running=$nrun)" >> $LOG
  elif [ -n "$stopped" ] && { [ "$avail" -gt "$HIGH" ] || [ "$nrun" -eq 0 ]; }; then
    p=$(echo "$stopped" | head -1); kill -CONT "$p" && echo "$(date -u +%T) avail=${avail}M CONT $p" >> $LOG
  fi
  sleep 3
done
for p in $(ps -eo pid,stat,comm | awk '$3=="clang++" && $2~/T/{print $1}'); do kill -CONT $p; done
echo "$(date -u +%T) governor end" >> $LOG
