#!/usr/bin/env bash
# G13 run: G13 binary (rate-based scene trigger + fallback 5000), EE recompiler
# ON, 280 s wall cap + progress cap (dump-file size stable across 2 polls after
# the queue marker), auto 5-frame dump, park shot, post counts.
# No /mnt/c touches (stage/retrieve after). Runs INSIDE WSL as brad.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-g7
B=$D/pcsx2/build/bin/pcsx2-qt
E=$D/dat-g13/PCSX2/logs/emulog.txt
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "G13_FAIL:$1"; stamp; exit 1; }
stamp
pgrep -f pcsx2-qt && fail PCSX2_ALREADY_RUNNING || true
pkill Xvfb || true
sleep 2
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-g13.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
rm -f $D/pcsx2-g13.pid
grep -n EnableEE $D/dat-g13/PCSX2/inis/PCSX2.ini
grep -n "GSDumpCompression\|ScreenshotSize" $D/dat-g13/PCSX2/inis/PCSX2.ini
echo "G_BOOT_WALL:$(date -u +%s) G_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $B -nogui -slowboot -turbo -datapath $D/dat-g13 -logfile $D/logs/boot-g13.log -- "/home/brad/pcsx2-t4/inputs/SSX 3 (USA).iso" > $D/logs/boot-g13.stdout 2>&1 &
echo $! > $D/pcsx2-g13.pid
echo "PID:$!"
i=0
lastsize=-1
stable=0
while test $i -lt 14; do
  sleep 20
  i=$((i+1))
  pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED
  echo "POLL:$i UPTIME:$(cut -d. -f1 /proc/uptime)"
  grep -m1 -e G13_DUMP_QUEUED -e G13_DUMP_FALLBACK $E || true
  set +x
  gsfile=""
  for f in $D/dat-g13/PCSX2/snaps/*.gs; do test -f "$f" && gsfile="$f"; done
  if test -n "$gsfile"; then
    sz=$(stat -c %s "$gsfile")
    echo "DUMP:$gsfile SIZE:$sz"
    if test "$sz" = "$lastsize"; then stable=$((stable+1)); else stable=0; fi
    lastsize="$sz"
  else
    echo "DUMP:none"
  fi
  set -x
  if grep -m1 -e G13_DUMP_QUEUED -e G13_DUMP_FALLBACK $E >/dev/null 2>&1; then
    if test -n "$gsfile" && test $stable -ge 1; then echo PROGRESS_CAP_HIT; break; fi
  fi
done
echo "WALL_LOOP_DONE polls=$i"
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
xwd -root -out $D/g13-park.xwd
xwdtopnm $D/g13-park.xwd | pnmtojpeg -quality=80 > $D/g13-park.jpg
ls -la $D/g13-park.jpg $E
kill $(cat $D/pcsx2-g13.pid); sleep 10; pgrep -a pcsx2-qt || true
pkill Xvfb || true
echo "--- post: newest snaps:"
ls -lat $D/dat-g13/PCSX2/snaps | head -12
echo "--- post: emulog markers:"
grep -c "Bios call: ExecPS2" $E
grep -c "G8_FIRST_NONZERO" $E $D/logs/boot-g13.stdout
grep -c "G13_SCAN" $E
grep -c "G13_DUMP_QUEUED" $E $D/logs/boot-g13.stdout
grep -c "G13_DUMP_FALLBACK" $E $D/logs/boot-g13.stdout
grep -c "G8_DUMP_QUEUED" $E $D/logs/boot-g13.stdout
grep -c "Bios call:" $E
grep -m2 "G8_FIRST_NONZERO" $E
grep -m2 "G13_DUMP_QUEUED" $E
grep -m2 "G13_DUMP_FALLBACK" $E
grep -m12 "G13_SCAN" $E
grep -c "G12_DRAW" $E
grep -c "G12_RASTER" $E
grep -c "G12_VSYNC" $E
grep -m5 -e Renderer -e Vulkan -e OpenGL $E
stamp
echo G13_RUN_DONE
