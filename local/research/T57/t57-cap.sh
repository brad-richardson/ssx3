#!/usr/bin/env bash
# T57 capture: SC-settled statefile boot on dat-t57 (EE+VU0 interp), VU0
# micro-program starts + VIF0 census, first 2000 lines.
# Foreground run (T51 ST51-6: no detached boots on bytesize). One held ssh.
# Free-gate files are touched for the shared T50/T51 gates; the T57 watch
# itself is ungated (statefile boot lands SC-settled).
# Env: TAG=t57a (default).
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
T4=/home/brad/pcsx2-t4
G=/home/brad/pcsx2-g7
BIN=$G/pcsx2/build/bin/pcsx2-qt
DAT=$G/dat-t57
E=$DAT/PCSX2/logs/emulog.txt
REFSC=$T4/t29-ref-sc.ppm
CD=$T4/t44-cropdiff.py
SNAPS=$DAT/PCSX2/snaps
TAG=${TAG:-t57a}
LOG=$T4/$TAG-poll.log
fail() { echo "T57_FAIL:$1"; date -u; exit 1; }
plog() { echo "$@" | tee -a $LOG; }
[ -x $BIN ] || fail NO_BIN
grep -q "^EnableEE = false" $DAT/PCSX2/inis/PCSX2.ini || fail NOT_INTERP
grep -q "^EnableVU0 = false" $DAT/PCSX2/inis/PCSX2.ini || fail NOT_VU0INT
cp $T4/t50-sc-state $G/t50-sc-state || fail STATE_STAGE
: > $LOG
date -u
rm -f /tmp/t48-arm /tmp/t48-dump-now /tmp/t49-arm /tmp/t50-arm /tmp/t50-free /tmp/t51-arm /tmp/t51-free /tmp/t51-watch /tmp/t53-watch /tmp/t54-watch /tmp/t56-watch2
touch /tmp/t48-arm /tmp/t50-arm /tmp/t51-arm
ls -la /tmp/t48-arm /tmp/t50-arm /tmp/t51-arm
pkill Xvfb || true
sleep 2
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-$TAG.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $DAT/PCSX2/logs/emulog-pre-$TAG-$TS.txt
fi
rm -f $T4/pcsx2-$TAG.pid
nohup $BIN -nogui -turbo -datapath $DAT -logfile $T4/logs/boot-$TAG.log -statefile "$G/t50-sc-state" -- "$T4/inputs/SSX 3 (USA).iso" > $T4/logs/boot-$TAG.stdout 2>&1 &
echo $! > $T4/pcsx2-$TAG.pid
sleep 45
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED
touch /tmp/t50-free /tmp/t51-free
plog "FREE_GATE_OPEN_WALL:$(date -u +%s.%N)"
W0=""
for W in $(seq 1 40); do
  sleep 2
  W0=$(grep -o "T51C_WINDOW vsync=[0-9]*" $E 2>/dev/null | head -1 | grep -o "[0-9]*$")
  if [ -n "$W0" ]; then plog "CWINDOW vsync=$W0 at wait$W"; break; fi
done
[ -n "$W0" ] || fail NO_CWINDOW
TARGET=$((W0+6))
plog "TARGET_PATHS vsync=$TARGET"
ENDSEEN=0
for W in $(seq 1 40); do
  sleep 2
  if grep -q "T48_PATHS vsync=$TARGET " $E 2>/dev/null; then
    plog "WINDOW_END vsync=$TARGET seen at wait$W"
    ENDSEEN=1
    break
  fi
done
[ $ENDSEEN -eq 1 ] || fail NO_WINDOW_END
sleep 4
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
xdotool windowfocus --sync $WID || fail FOCUS
xdotool keydown F8; sleep 0.5; xdotool keyup F8
sleep 2
NEW=$(ls -t $SNAPS | head -n 1)
plog "GSHOT newest=$NEW"
cp "$SNAPS/$NEW" $T4/$TAG-shot-sc.png || fail GSHOT_CP
xwd -root -out $T4/$TAG-loaded.xwd || fail SNAP
xwdtopnm $T4/$TAG-loaded.xwd > $T4/$TAG-loaded.ppm || fail SNAP2
rm -f $T4/$TAG-loaded.xwd
read SM SP <<< $(python3 $CD $T4/$TAG-loaded.ppm $REFSC 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}')
plog "LOADED vs-sc mean=$SM p99=$SP"
plog "COUNTS vu0call=$(grep -c 'vu0call vsync=' $E || true) vif0op=$(grep -c 'vif0op vsync=' $E || true) cap=$(grep -c 'T57_CAP' $E || true) ctag=$(grep -c 'ctag ' $E || true) spw=$(grep -c 'spw vsync=' $E || true)"
kill $(cat $T4/pcsx2-$TAG.pid); sleep 5; pgrep -a pcsx2-qt || true
date -u
echo T57_DONE
