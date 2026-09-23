#!/usr/bin/env bash
# T50 Capture C: EE-interp boot into the SC savestate (-statefile), free-gate
# logging (no dump dependency: G13 auto-dump consumes the one-shot under
# statefile), T48_PATHS-gated F8. Dump trigger attempted (non-fatal bonus).
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
T4=/home/brad/pcsx2-t4
G=/home/brad/pcsx2-g7
BIN=$G/pcsx2/build/bin/pcsx2-qt
DAT=$G/dat-t50
E=$DAT/PCSX2/logs/emulog.txt
REFSC=$T4/t29-ref-sc.ppm
CD=$T4/t44-cropdiff.py
SNAPS=$DAT/PCSX2/snaps
TAG=t50c
LOG=$T4/$TAG-poll.log
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T50C_FAIL:$1"; stamp; exit 1; }
: > $LOG
plog() { echo "$@" | tee -a $LOG; }
[ -x $BIN ] || fail NO_BIN
grep -q "^EnableEE = false" $DAT/PCSX2/inis/PCSX2.ini || fail NOT_INTERP
STATE_SRC=$(ls -t $T4/t50-sc-state* 2>/dev/null | head -n 1)
[ -n "$STATE_SRC" ] || fail NO_STATE_SRC
STATE_BN=$(basename "$STATE_SRC")
cp "$STATE_SRC" "$G/$STATE_BN" || fail STATE_STAGE
STATE="$G/$STATE_BN"
ls -la "$STATE"
snap() {
  local N=$1
  date -u
  xwd -root -out $T4/$N.xwd || return 1
  xwdtopnm $T4/$N.xwd > $T4/$N.ppm || return 1
  rm -f $T4/$N.xwd
}
score_sc() {
  python3 $CD $1 $REFSC 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
press() {
  local KEY=$1; local LAB=$2
  plog "${LAB}_KEYDOWN_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
  xdotool windowfocus --sync $WID || fail FOCUS_$LAB
  xdotool keydown $KEY || fail KEYDOWN_$LAB
  sleep 0.5
  xdotool keyup $KEY || fail KEYUP_$LAB
  plog "${LAB}_KEYUP_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
}
gshot() {
  local LAB=$1
  ls -lat $SNAPS | head -n 5
  press F8 "GSHOT_$LAB"
  sleep 2
  local NEW=$(ls -t $SNAPS | head -n 1)
  plog "GSHOT_$LAB newest=$NEW"
  cp "$SNAPS/$NEW" $T4/t50-shot-$LAB.png || fail GSHOT_CP_$LAB
  ls -la $T4/t50-shot-$LAB.png
}
stamp
rm -f /tmp/t48-arm /tmp/t48-dump-now /tmp/t49-arm /tmp/t50-arm /tmp/t50-free
touch /tmp/t48-arm /tmp/t49-arm /tmp/t50-arm
ls -la /tmp/t48-arm /tmp/t49-arm /tmp/t50-arm
pkill Xvfb || true
sleep 2
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-$TAG.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $DAT/PCSX2/logs/emulog-pre-$TAG-$TS.txt
fi
rm -f $T4/pcsx2-t50c.pid
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT STATE:$STATE"
nohup $BIN -nogui -turbo -datapath $DAT -logfile $T4/logs/boot-$TAG.log -statefile "$STATE" -- "$T4/inputs/SSX 3 (USA).iso" > $T4/logs/boot-$TAG.stdout 2>&1 &
echo $! > $T4/pcsx2-t50c.pid
echo "PID:$!"
sleep 60
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
sleep 10
snap t50c-loaded || fail SNAP_LOADED
read SM SP <<< $(score_sc $T4/t50c-loaded.ppm)
plog "LOADED vs-sc mean=$SM p99=$SP"
if ! awk -v m=$SM 'BEGIN{exit !(m<3.0)}'; then
  sleep 20
  snap t50c-loaded2 || fail SNAP_LOADED2
  read SM SP <<< $(score_sc $T4/t50c-loaded2.ppm)
  plog "LOADED2 vs-sc mean=$SM p99=$SP"
  awk -v m=$SM 'BEGIN{exit !(m<3.0)}' || fail NO_SC_STATE
fi
touch /tmp/t50-free
ls -la /tmp/t50-free
plog "FREE_GATE_OPEN_WALL:$(date -u +%s.%N)"
touch /tmp/t48-dump-now
plog "DUMP_TRY_WALL:$(date -u +%s.%N)"
for W in $(seq 1 5); do
  sleep 2
  if grep -q "T48_DUMP_QUEUED" $E 2>/dev/null; then
    plog "T48_DUMP_QUEUED seen at try$W (bonus)"
    break
  fi
done
Q0=$(grep "T48_PATHS" $E 2>/dev/null | tail -1 | grep -o "vsync=[0-9]*" | grep -o "[0-9]*")
[ -n "$Q0" ] || fail NO_PATHS
TARGET=$((Q0+10))
plog "PATHS_NOW=$Q0 TARGET=$TARGET"
ENDSEEN=0
for W in $(seq 1 60); do
  sleep 5
  if grep -q "T48_PATHS vsync=$TARGET " $E 2>/dev/null; then
    plog "WINDOW_END vsync=$TARGET seen at wait$W"
    ENDSEEN=1
    break
  fi
done
[ $ENDSEEN -eq 1 ] || fail NO_WINDOW_END
sleep 6
rm -f /tmp/t48-dump-now
gshot $TAG-sc
grep -m 2 "T48_DUMP_QUEUED" $E || true
grep -c "mpgpay \|dmareg \|srcread " $E || true
ls -la $T4/t50-shot-$TAG-sc.png $E
kill $(cat $T4/pcsx2-t50c.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T50C_DONE
