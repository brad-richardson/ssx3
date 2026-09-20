#!/usr/bin/env bash
# G7 run: G7 binary, EE recompiler ON, 150 s wall, auto 5-frame dump at
# game-entry+60 vsyncs, park shot, post counts. No /mnt/c touches
# (stage/retrieve after). Runs INSIDE WSL as brad.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-g7
B=$D/pcsx2/build/bin/pcsx2-qt
E=$D/dat/PCSX2/logs/emulog.txt
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "G7_FAIL:$1"; stamp; exit 1; }
stamp
pgrep -f pcsx2-qt && fail PCSX2_ALREADY_RUNNING || true
pkill Xvfb || true
sleep 2
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-g7.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
rm -f $D/pcsx2.pid
grep -n EnableEE $D/dat/PCSX2/inis/PCSX2.ini
grep -n "GSDumpCompression\|ScreenshotSize" $D/dat/PCSX2/inis/PCSX2.ini
echo "G_BOOT_WALL:$(date -u +%s) G_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $B -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-g7.log -- "/home/brad/pcsx2-t4/inputs/SSX 3 (USA).iso" > $D/logs/boot-g7.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 150
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
xwd -root -out $D/g7-park.xwd
xwdtopnm $D/g7-park.xwd | pnmtojpeg -quality=80 > $D/g7-park.jpg
ls -la $D/g7-park.jpg $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
pkill Xvfb || true
echo "--- post: newest snaps:"
ls -lat $D/dat/PCSX2/snaps | head -12
echo "--- post: emulog markers:"
grep -c "Bios call: ExecPS2" $E
grep -c "G7_DUMP_QUEUED" $E $D/logs/boot-g7.stdout
grep -c "Bios call:" $E
stamp
echo G7_RUN_DONE
