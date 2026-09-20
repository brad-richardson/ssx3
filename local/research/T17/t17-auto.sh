#!/usr/bin/env bash
# T17 single-shot: Xvfb + fresh boot + park-snap + ONE X press + capture series.
# Unattended (~6 min). No /mnt/c touches (stage/retrieve after). Every event
# stamped with wall clock AND kernel uptime (WSL wall clock suspected +4h).
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-t4
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T17_FAIL:$1"; stamp; exit 1; }
stamp
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t17a.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $D/dat/PCSX2/logs/emulog.txt ]; then
  mv $D/dat/PCSX2/logs/emulog.txt $D/dat/PCSX2/logs/emulog-pre-t17auto-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
echo "T_BOOT_WALL:$(date -u +%s) T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t17auto.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t17auto.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_PARK
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
bash $D/t17-snap.sh t17a-park || fail SNAP_PARK
sleep 10
echo "PRESS_T_MINUS_0_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
xdotool windowfocus --sync $WID || fail FOCUS
echo "FOCUSED_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
xdotool key K || fail KEY
echo "PRESS_DONE_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
sleep 10; bash $D/t17-snap.sh t17a-post10 || fail SNAP10
sleep 20; bash $D/t17-snap.sh t17a-post30 || fail SNAP30
sleep 30; bash $D/t17-snap.sh t17a-post60 || fail SNAP60
sleep 60; bash $D/t17-snap.sh t17a-post120 || fail SNAP120
sleep 120; bash $D/t17-snap.sh t17a-post240 || fail SNAP240
ls -la $D/t17a-*.jpg $D/dat/PCSX2/logs/emulog.txt
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T17_AUTO_DONE
