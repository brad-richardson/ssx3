#!/bin/bash
# VR4: start the fold Android compile only when bytesize is really idle: the
# bytesize lock is free AND no gradle client / ninja / clang / ld job is running
# (09-26: AP1 gradle + a Mesa ninja ran outside the new lock). Poll 30 s, max 3 h.
set -u
cd ~/dev/ssx3
for i in $(seq 1 360); do
  busy=$(printf 'pgrep -fa "GradleWrapperMain|ninja |clang|ld.lld|cc1" | grep -v pgrep | wc -l\n' | ssh -o ConnectTimeout=20 bytesize 'wsl -d Ubuntu -- bash -s' 2>/dev/null | tr -d ' \r' | tail -1)
  lock=$(bash local/tooling/bytesize_lock.sh status 2>/dev/null | grep -v bogus | tail -1)
  if [ "$busy" = 0 ] && [ "${lock%% *}" = FREE ]; then
    echo "[$(date +%H:%M:%S)] bytesize idle, lock free: starting"
    bash local/tooling/bytesize_lock.sh run VR4-fold -- ssh bytesize 'wsl -d Ubuntu -- bash -lc "/home/brad/vr4fold/build.sh"' > ~/dev/ssx3-work/VR4/android-fold2.log 2>&1
    echo "EXIT=$?"; grep -v bogus ~/dev/ssx3-work/VR4/android-fold2.log | tail -8
    exit 0
  fi
  [ $((i % 10)) = 1 ] && echo "[$(date +%H:%M:%S)] waiting: heavy procs=$busy lock=$lock"
  sleep 30
done
echo "gave up after 3 h"; exit 1
