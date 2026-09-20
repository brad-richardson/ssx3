#!/usr/bin/env bash
# T17c single-shot: single Cross press with 500 ms hold + post-press capture.
# One press (one down-edge, one up-edge), recorded timing. Unattended (~4 min).
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-t4
E=$D/dat/PCSX2/logs/emulog.txt
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T17_FAIL:$1"; stamp; exit 1; }
stamp
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t17c.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $D/dat/PCSX2/logs/emulog-pre-t17c-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
echo "T_BOOT_WALL:$(date -u +%s) T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t17c.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t17c.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_PARK
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
bash $D/t17-snap.sh t17c-park || fail SNAP_PARK
sleep 10
echo "KEYDOWN_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
xdotool windowfocus --sync $WID || fail FOCUS
xdotool keydown K || fail KEYDOWN
echo "HELD_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
sleep 0.5
xdotool keyup K || fail KEYUP
echo "KEYUP_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
sleep 5; bash $D/t17-snap.sh t17c-post5 || fail SNAP5
sleep 10; bash $D/t17-snap.sh t17c-post15 || fail SNAP15
sleep 15; bash $D/t17-snap.sh t17c-post30 || fail SNAP30
sleep 30; bash $D/t17-snap.sh t17c-post60 || fail SNAP60
sleep 60; bash $D/t17-snap.sh t17c-post120 || fail SNAP120
sleep 120; bash $D/t17-snap.sh t17c-post240 || fail SNAP240
ls -la $D/t17c-*.jpg $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T17C_DONE
