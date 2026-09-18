#!/bin/sh
# Poll until the Odin is usable: lease absent, no moderngekko, battery >= 20%
# and status 2 (charging) or 5 (full). Logs every 5 min. Exit 0 = usable.
LOG=~/dev/ssx3/local/research/S2/waits.log
S=$(cat ~/dev/ssx3/local/odin-serial 2>/dev/null || echo <odin-serial>)
adb connect "$S" >/dev/null 2>&1
n=0
while [ $n -lt 150 ]; do
  L=$(adb -s $S shell "cat /data/local/tmp/mg/LEASE 2>/dev/null || echo ABSENT" 2>/dev/null | tr -d '\r')
  P=$(adb -s $S shell "ps -A | grep moderngekko | grep -v grep | wc -l" 2>/dev/null | tr -d '\r ')
  B=$(adb -s $S shell "dumpsys battery | grep -E '^  (level|status):'" 2>/dev/null | tr -d '\r' | awk -F': ' '{printf "%s=%s ",$1,$2}' | tr -d ' ' )
  LV=$(adb -s $S shell "dumpsys battery | awk -F': ' '/^  level:/{print \$2}'" 2>/dev/null | tr -d '\r ')
  ST=$(adb -s $S shell "dumpsys battery | awk -F': ' '/^  status:/{print \$2}'" 2>/dev/null | tr -d '\r ')
  [ -z "$L" ] && L=ADB_DOWN
  [ -z "$LV" ] && LV=-1
  [ -z "$ST" ] && ST=-1
  if [ "$L" = "ABSENT" ] && [ "$P" = "0" ] && [ "$LV" -ge 20 ] 2>/dev/null && { [ "$ST" = "2" ] || [ "$ST" = "5" ]; }; then
    printf '%s device USABLE: lease ABSENT, no procs, battery %s%% status %s\n' "$(date -u +%H:%M:%SZ)" "$LV" "$ST" >> $LOG
    exit 0
  fi
  if [ $((n % 5)) -eq 0 ]; then
    printf '%s waiting: lease=%s procs=%s battery=%s%% status=%s\n' "$(date -u +%H:%M:%SZ)" "$L" "$P" "$LV" "$ST" >> $LOG
  fi
  n=$((n+1))
  sleep 60
done
printf '%s device wait timed out (150 polls)\n' "$(date -u +%H:%M:%SZ)" >> $LOG
exit 2
