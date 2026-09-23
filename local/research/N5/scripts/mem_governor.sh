#!/bin/bash
# N5 build2: keep bytesize WSL out of OOM without killing compiles. Pauses the
# youngest running clang++ when MemAvailable < 2 GB; resumes the oldest paused
# one when MemAvailable > 4 GB (or nothing else is running). Exits with ninja.
LOG=~/n5/logs/build2-governor.txt
echo "$(date -u +%T) governor start" >> $LOG
while pgrep -x ninja >/dev/null; do
  avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  running=$(ps -eo pid,etimes,stat,comm --sort=etimes | awk '$4=="clang++" && $3!~/T/{print $1}')
  stopped=$(ps -eo pid,etimes,stat,comm --sort=-etimes | awk '$4=="clang++" && $3~/T/{print $1}')
  nrun=$(echo "$running" | grep -c .)
  if [ "$avail" -lt 2048 ] && [ "$nrun" -gt 1 ]; then
    p=$(echo "$running" | head -1); kill -STOP "$p" && echo "$(date -u +%T) avail=${avail}M STOP $p (running=$nrun)" >> $LOG
  elif [ -n "$stopped" ] && { [ "$avail" -gt 4096 ] || [ "$nrun" -eq 0 ]; }; then
    p=$(echo "$stopped" | head -1); kill -CONT "$p" && echo "$(date -u +%T) avail=${avail}M CONT $p" >> $LOG
  fi
  sleep 3
done
for p in $(ps -eo pid,stat,comm | awk '$3=="clang++" && $2~/T/{print $1}'); do kill -CONT $p; done
echo "$(date -u +%T) governor end" >> $LOG
