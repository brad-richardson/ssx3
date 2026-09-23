#!/usr/bin/env bash
# T57 probe 10: build dat-t57 (dat-t50 + EnableVU0=false) and load-check the
# SC statefile with the EXISTING T56 binary (no T57 hooks yet). Short gate
# check only: CWINDOW -> PATHS -> kill. Proves state-load under VU0 interp.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
G=/home/brad/pcsx2-g7
T4=/home/brad/pcsx2-t4
BIN=$G/pcsx2/build/bin/pcsx2-qt
E=/home/brad/pcsx2-g7/dat-t57/PCSX2/logs/emulog.txt
LOG=$T4/t57probe-poll.log
fail() { echo "T57PROBE_FAIL:$1"; date -u; exit 1; }
plog() { echo "$@" | tee -a $LOG; }
[ -x $BIN ] || fail NO_BIN
echo "=== contenders (must be empty) ==="
pgrep -af "pcsx2-qt|pcsx2-gsrunner|cmake --build|ninja" || true
if pgrep -f "pcsx2-qt" > /dev/null; then fail OTHER_PCSX2_RUNNING; fi
if [ ! -d $G/dat-t57 ]; then
  cp -r $G/dat-t50 $G/dat-t57 || fail DAT_CP
fi
grep -q "^EnableVU0 = true" $G/dat-t57/PCSX2/inis/PCSX2.ini || fail NOT_VU0REC_BASE
grep -q "^EnableEE = false" $G/dat-t57/PCSX2/inis/PCSX2.ini || fail NOT_INTERP
sed -i 's/^EnableVU0 = true/EnableVU0 = false/' $G/dat-t57/PCSX2/inis/PCSX2.ini || fail SED
grep -n "^EnableVU0\|^EnableEE\|^EnableVU1" $G/dat-t57/PCSX2/inis/PCSX2.ini | tee -a $LOG
du -sh $G/dat-t57 | tee -a $LOG
cp $T4/t50-sc-state $G/t50-sc-state || fail STATE_STAGE
: > $LOG
date -u
rm -f /tmp/t48-arm /tmp/t48-dump-now /tmp/t49-arm /tmp/t50-arm /tmp/t50-free /tmp/t51-arm /tmp/t51-free /tmp/t51-watch /tmp/t53-watch /tmp/t54-watch /tmp/t56-watch2
touch /tmp/t48-arm /tmp/t50-arm /tmp/t51-arm
pkill Xvfb || true
sleep 2
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t57probe.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
TS=$(date -u +%Y%m%dT%H%M%SZ)
DAT=$G/dat-t57
E=$DAT/PCSX2/logs/emulog.txt
if [ -f $E ]; then
  mv $E $DAT/PCSX2/logs/emulog-pre-t57probe-$TS.txt
fi
rm -f $T4/pcsx2-t57probe.pid
nohup $BIN -nogui -turbo -datapath $DAT -logfile $T4/logs/boot-t57probe.log -statefile "$G/t50-sc-state" -- "$T4/inputs/SSX 3 (USA).iso" > $T4/logs/boot-t57probe.stdout 2>&1 &
echo $! > $T4/pcsx2-t57probe.pid
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
plog "MODELINES:"
grep -h "T48_MODE" $E 2>/dev/null | head -3 | tee -a $LOG
plog "COUNTS spw=$(grep -c 'spw vsync=' $E || true) ctag=$(grep -c 'ctag ' $E || true)"
kill $(cat $T4/pcsx2-t57probe.pid); sleep 5; pgrep -a pcsx2-qt || true
date -u
echo T57PROBE_DONE
