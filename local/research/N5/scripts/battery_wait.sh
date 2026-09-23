#!/bin/bash
# N5: poll the Odin battery every 5 min for up to 2 h; exit 0 when status=2 (charging) and level>=20, else exit 1.
D=622c49b1; LOG=~/dev/ssx3-work/N5/battery-poll.txt
for i in $(seq 0 24); do
  b=$(adb -s $D shell 'dumpsys battery; cat /sys/class/power_supply/battery/current_now' 2>&1)
  lvl=$(echo "$b" | awk '/  level:/{print $2}'); st=$(echo "$b" | awk '/  status:/{print $2}'); cur=$(echo "$b" | tail -1 | tr -d '\r')
  ac=$(echo "$b" | awk '/AC powered:/{print $3}')
  echo "$(date '+%F %T %Z') poll=$i level=$lvl status=$st current_uA=$cur ac=$ac" | tee -a $LOG
  if [ "$st" = "2" ] && [ -n "$lvl" ] && [ "$lvl" -ge 20 ]; then echo READY; exit 0; fi
  [ $i -lt 24 ] && sleep 300
done
echo NEVER_READY; exit 1
