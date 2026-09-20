#!/usr/bin/env bash
# R1 run (a): pc-tagged binary, EE recompiler ON, 120 s wall, snap, clean kill.
# Unattended (~2.5 min). No /mnt/c touches (stage/retrieve after).
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-r1
B=$D/pcsx2/build/bin/pcsx2-qt
E=$D/dat/PCSX2/logs/emulog.txt
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "R1A_FAIL:$1"; stamp; exit 1; }
stamp
pgrep -f pcsx2-qt && fail PCSX2_ALREADY_RUNNING || true
pkill Xvfb || true
sleep 2
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-r1a.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $D/dat/PCSX2/logs/emulog-pre-r1a-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
grep -n EnableEE $D/dat/PCSX2/inis/PCSX2.ini
echo "A_BOOT_WALL:$(date -u +%s) A_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $B -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-r1a.log -- "/home/brad/pcsx2-t4/inputs/SSX 3 (USA).iso" > $D/logs/boot-r1a.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 120
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
xwd -root -out $D/r1a-park.xwd
xwdtopnm $D/r1a-park.xwd | pnmtojpeg -quality=80 > $D/r1a-park.jpg
ls -la $D/r1a-park.* $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
pkill Xvfb || true
stamp
echo R1A_DONE
