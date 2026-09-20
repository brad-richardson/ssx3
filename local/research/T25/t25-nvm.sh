#!/usr/bin/env bash
# T25 Phase 1 (NVM verify): ONE fresh boot, ZERO inputs, two snaps + clean shutdown.
# Unattended (~2.5 min). No /mnt/c touches (stage/retrieve after). Wall clock AND kernel uptime stamps.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-t4
E=$D/dat/PCSX2/logs/emulog.txt
N=$D/dat/PCSX2/bios/ps2-bios-0200a-20040614-100909.nvm
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T25NVM_FAIL:$1"; stamp; exit 1; }
stamp
sha256sum $N
ls -la $N
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t25nvm.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $D/dat/PCSX2/logs/emulog-pre-t25nvm-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
echo "T_BOOT_WALL:$(date -u +%s) T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t25nvm.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t25nvm.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_PARK
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
bash $D/t17-snap.sh t25-nvm-park || fail SNAP_PARK
sleep 30; bash $D/t17-snap.sh t25-nvm-park2 || fail SNAP_PARK2
ls -la $D/t25-nvm-*.jpg $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
sha256sum $N
ls -la $N
stamp
echo T25NVM_DONE
