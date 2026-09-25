#!/usr/bin/env bash
# RP1: PCSX2 own run from T65's race statefile (00:00:18), no inputs, F8 GS shot every PERIOD s. Wall cap 400 s.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
G=/home/brad/pcsx2-g7
BIN=$G/pcsx2/build/bin/pcsx2-qt
SRC=$G/dat-t48/PCSX2
W=/home/brad/rp1
DAT=$W/dat-rp1
TAG=${TAG:-rp1a}
PERIOD=${PERIOD:-20}
N=${N:-14}
mkdir -p $W/$TAG $DAT/PCSX2
for d in inis bios memcards gamesettings; do [ -e $DAT/PCSX2/$d ] || cp -r $SRC/$d $DAT/PCSX2/; done
mkdir -p $DAT/PCSX2/snaps $DAT/PCSX2/sstates $DAT/PCSX2/logs
sha256sum $G/t65-race-state
pkill -f pcsx2-qt; pkill Xvfb; sleep 2
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-$TAG.log 2>&1 < /dev/null &
sleep 4
T0=$(date +%s)
nohup $BIN -nogui -datapath $DAT -statefile $G/t65-race-state -- "/home/brad/pcsx2-t4/inputs/SSX 3 (USA).iso" > $W/$TAG/stdout.txt 2>&1 &
PID=$!; echo PID=$PID
for i in $(seq 1 30); do sleep 2; WID=$(xdotool search --onlyvisible --name "SSX 3" 2>/dev/null | head -1); [ -n "$WID" ] && break; done
echo WID=$WID at $(( $(date +%s) - T0 ))s
[ -n "$WID" ] || { kill $PID; exit 1; }
for k in $(seq 1 $N); do
  [ $(( $(date +%s) - T0 )) -gt ${CAP:-400} ] && break
  kill -0 $PID || { echo DIED; break; }
  xdotool windowfocus --sync $WID; xdotool key F8
  sleep 1.5
  NEW=$(ls -t $DAT/PCSX2/snaps | head -1)
  EL=$(( $(date +%s) - T0 ))
  cp "$DAT/PCSX2/snaps/$NEW" $W/$TAG/shot-$(printf %02d $k)-${EL}s.png && echo SHOT $k $EL $NEW
  sleep $(( PERIOD - 2 ))
done
kill $PID; sleep 3; kill -9 $PID 2>/dev/null; pkill Xvfb
ls -la $W/$TAG | head -40
