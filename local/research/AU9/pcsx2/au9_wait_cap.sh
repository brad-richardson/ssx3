#!/usr/bin/env bash
# AU9: wait (<= 45 min) until bytesize has no build/PCSX2 job, then run the race capture once.
for i in $(seq 1 90); do
  J=$(pgrep -af 'GradleWrapperMain|ninja|clang|pcsx2-qt|cc1plus' | grep -v pgrep)
  if [ -z "$J" ]; then echo "IDLE at $(date) after $i polls"; cd ~/au9 && bash ~/au9/au9_race_cap.sh > ~/au9/au9r-run.log 2>&1; echo rc=$?; tail -4 ~/au9/au9r-poll.log; exit 0; fi
  sleep 30
done
echo "STILL_BUSY $(date)"; echo "$J" | cut -c1-200 | head -5
