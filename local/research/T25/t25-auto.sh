#!/usr/bin/env bash
# T25 Phase 2 (scripted path): fresh boot (NVM carries -> attract loop) + TWO single 534 ms holds.
# P1 @T+100 K (Cross): attract skip -> title expect. P2 @T+130 Return (Start): title -> first menu expect.
# Snaps after each transition + epoch series. Unattended (~6 min). No /mnt/c touches. Wall + uptime stamps.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-t4
E=$D/dat/PCSX2/logs/emulog.txt
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T25_FAIL:$1"; stamp; exit 1; }
stamp
pkill Xvfb || true
sleep 2
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t25.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $D/dat/PCSX2/logs/emulog-pre-t25-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
echo "T_BOOT_WALL:$(date -u +%s) T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t25.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t25.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_START
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
bash $D/t17-snap.sh t25-start || fail SNAP_START
sleep 10
echo "P1_KEYDOWN_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
xdotool windowfocus --sync $WID || fail FOCUS1
xdotool keydown K || fail KEYDOWN1
echo "P1_HELD_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
sleep 0.5
xdotool keyup K || fail KEYUP1
echo "P1_KEYUP_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
sleep 10; bash $D/t17-snap.sh t25-post-p1a || fail SNAP_P1A
sleep 10; bash $D/t17-snap.sh t25-post-p1b || fail SNAP_P1B
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_P2
echo "P2_KEYDOWN_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
xdotool windowfocus --sync $WID || fail FOCUS2
xdotool keydown Return || fail KEYDOWN2
echo "P2_HELD_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
sleep 0.5
xdotool keyup Return || fail KEYUP2
echo "P2_KEYUP_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
sleep 10; bash $D/t17-snap.sh t25-post-p2a || fail SNAP_P2A
sleep 20; bash $D/t17-snap.sh t25-post-p2b || fail SNAP_P2B
sleep 40; bash $D/t17-snap.sh t25-post-p2c || fail SNAP_P2C
sleep 60; bash $D/t17-snap.sh t25-post-p2d || fail SNAP_P2D
sleep 80; bash $D/t17-snap.sh t25-post-p2e || fail SNAP_P2E
ls -la $D/t25-*.jpg $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T25_DONE
