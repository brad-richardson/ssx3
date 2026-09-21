#!/usr/bin/env bash
# G8 run: G8 binary (draw-aware trigger, K=500), EE recompiler ON, 150 s wall,
# auto 5-frame dump K transfers after first non-zero-transfer vsync past game
# entry, park shot, post counts. No /mnt/c touches (stage/retrieve after).
# Runs INSIDE WSL as brad.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-g7
B=$D/pcsx2/build/bin/pcsx2-qt
E=$D/dat-g8/PCSX2/logs/emulog.txt
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "G8_FAIL:$1"; stamp; exit 1; }
stamp
pgrep -f pcsx2-qt && fail PCSX2_ALREADY_RUNNING || true
pkill Xvfb || true
sleep 2
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-g8.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
rm -f $D/pcsx2-g8.pid
grep -n EnableEE $D/dat-g8/PCSX2/inis/PCSX2.ini
grep -n "GSDumpCompression\|ScreenshotSize" $D/dat-g8/PCSX2/inis/PCSX2.ini
echo "G_BOOT_WALL:$(date -u +%s) G_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $B -nogui -slowboot -turbo -datapath $D/dat-g8 -logfile $D/logs/boot-g8.log -- "/home/brad/pcsx2-t4/inputs/SSX 3 (USA).iso" > $D/logs/boot-g8.stdout 2>&1 &
echo $! > $D/pcsx2-g8.pid
echo "PID:$!"
sleep 150
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
xwd -root -out $D/g8-park.xwd
xwdtopnm $D/g8-park.xwd | pnmtojpeg -quality=80 > $D/g8-park.jpg
ls -la $D/g8-park.jpg $E
kill $(cat $D/pcsx2-g8.pid); sleep 10; pgrep -a pcsx2-qt || true
pkill Xvfb || true
echo "--- post: newest snaps:"
ls -lat $D/dat-g8/PCSX2/snaps | head -12
echo "--- post: emulog markers:"
grep -c "Bios call: ExecPS2" $E
grep -c "G8_FIRST_NONZERO" $E $D/logs/boot-g8.stdout
grep -c "G8_DUMP_QUEUED" $E $D/logs/boot-g8.stdout
grep -c "G7_DUMP_QUEUED" $E $D/logs/boot-g8.stdout
grep -c "Bios call:" $E
grep -m2 "G8_FIRST_NONZERO" $E
grep -m2 "G8_DUMP_QUEUED" $E
stamp
echo G8_RUN_DONE
