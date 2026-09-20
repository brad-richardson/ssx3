#!/usr/bin/env bash
# T17b single-shot positive control: does an XTEST key reach PCSX2-Qt?
# SPACE = TogglePause -> emulog byte-growth must flatline, then resume.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-t4
E=$D/dat/PCSX2/logs/emulog.txt
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
sz() { echo "SIZE@$1:$(stat -c %s $E) WALL:$(date -u +%s) UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T17_FAIL:$1"; stamp; exit 1; }
stamp
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t17b.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $D/dat/PCSX2/logs/emulog-pre-t17b-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
echo "T_BOOT_WALL:$(date -u +%s) T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t17b.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t17b.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_PARK
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
bash $D/t17-snap.sh t17b-park || fail SNAP_PARK
sleep 25; sz T115
sleep 5
echo "PAUSE_PRESS_WALL:$(date -u +%s.%N)"
xdotool windowfocus --sync $WID || fail FOCUS1
xdotool key space || fail KEY1
echo "PAUSED_WALL:$(date -u +%s.%N)"
sleep 5; sz T125
sleep 25; sz T150
bash $D/t17-snap.sh t17b-paused || fail SNAP_PAUSED
sleep 5
echo "RESUME_PRESS_WALL:$(date -u +%s.%N)"
xdotool windowfocus --sync $WID || fail FOCUS2
xdotool key space || fail KEY2
echo "RESUMED_WALL:$(date -u +%s.%N)"
sleep 5; sz T160
sleep 35; sz T195
bash $D/t17-snap.sh t17b-resumed || fail SNAP_RESUMED
ls -la $D/t17b-*.jpg $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T17B_DONE
