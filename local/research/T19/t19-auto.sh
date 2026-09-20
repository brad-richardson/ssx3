#!/usr/bin/env bash
# T19 single-shot: fresh boot + TWO single 534 ms K holds (User Prefs, then confirm English) + capture.
# Press1 @T+100 -> User Prefs snap @T+110; press2 right after (~T+112) -> +5/+15/+30/+60/+120/+240 series.
# Unattended (~6 min). No /mnt/c touches (stage/retrieve after). Wall clock AND kernel uptime stamps.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-t4
E=$D/dat/PCSX2/logs/emulog.txt
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T19_FAIL:$1"; stamp; exit 1; }
stamp
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t19.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $D/dat/PCSX2/logs/emulog-pre-t19-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
echo "T_BOOT_WALL:$(date -u +%s) T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t19.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t19.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_PARK
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
bash $D/t17-snap.sh t19-park || fail SNAP_PARK
sleep 10
echo "PRESS1_KEYDOWN_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
xdotool windowfocus --sync $WID || fail FOCUS1
xdotool keydown K || fail KEYDOWN1
echo "PRESS1_HELD_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
sleep 0.5
xdotool keyup K || fail KEYUP1
echo "PRESS1_KEYUP_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
sleep 10; bash $D/t17-snap.sh t19-prefs || fail SNAP_PREFS
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_PRESS2
echo "PRESS2_KEYDOWN_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
xdotool windowfocus --sync $WID || fail FOCUS2
xdotool keydown K || fail KEYDOWN2
echo "PRESS2_HELD_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
sleep 0.5
xdotool keyup K || fail KEYUP2
echo "PRESS2_KEYUP_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
sleep 5; bash $D/t17-snap.sh t19-post5 || fail SNAP5
sleep 10; bash $D/t17-snap.sh t19-post15 || fail SNAP15
sleep 15; bash $D/t17-snap.sh t19-post30 || fail SNAP30
sleep 30; bash $D/t17-snap.sh t19-post60 || fail SNAP60
sleep 60; bash $D/t17-snap.sh t19-post120 || fail SNAP120
sleep 120; bash $D/t17-snap.sh t19-post240 || fail SNAP240
ls -la $D/t19-*.jpg $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T19_DONE
