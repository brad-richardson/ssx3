#!/usr/bin/env bash
# T50 Capture B: EE-interp boot straight into the SC savestate (-statefile),
# then dump trigger + T48_PATHS-gated F8 at window end.
# Arms /tmp/t48-arm always (window+dumptrigger); /tmp/t49-arm + /tmp/t50-arm
# unless UNARMED=1 (proof: T48 traffic + F8 only, same guest endpoint).
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
if [ "${UNARMED:-0}" = "1" ]; then TAG=t50b-proof; else TAG=t50b; fi
LOG=$T4/$TAG-poll.log
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T50B_FAIL:$1"; stamp; exit 1; }
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
rm -f /tmp/t48-arm /tmp/t48-dump-now /tmp/t49-arm /tmp/t50-arm
touch /tmp/t48-arm
if [ "${UNARMED:-0}" != "1" ]; then touch /tmp/t49-arm /tmp/t50-arm; fi
ls -la /tmp/t48-arm /tmp/t49-arm /tmp/t50-arm 2>/dev/null || true
pkill Xvfb || true
sleep 2
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-$TAG.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $DAT/PCSX2/logs/emulog-pre-$TAG-$TS.txt
fi
rm -f $T4/pcsx2-t50b.pid
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT STATE:$STATE"
nohup $BIN -nogui -turbo -datapath $DAT -logfile $T4/logs/boot-$TAG.log -statefile "$STATE" -- "$T4/inputs/SSX 3 (USA).iso" > $T4/logs/boot-$TAG.stdout 2>&1 &
echo $! > $T4/pcsx2-t50b.pid
echo "PID:$!"
sleep 60
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
sleep 10
snap t50b-loaded || fail SNAP_LOADED
read SM SP <<< $(score_sc $T4/t50b-loaded.ppm)
plog "LOADED vs-sc mean=$SM p99=$SP"
if ! awk -v m=$SM 'BEGIN{exit !(m<3.0)}'; then
  sleep 20
  snap t50b-loaded2 || fail SNAP_LOADED2
  read SM SP <<< $(score_sc $T4/t50b-loaded2.ppm)
  plog "LOADED2 vs-sc mean=$SM p99=$SP"
  awk -v m=$SM 'BEGIN{exit !(m<3.0)}' || fail NO_SC_STATE
fi
touch /tmp/t48-dump-now
ls -la /tmp/t48-dump-now
plog "DUMP_TRIGGERED_WALL:$(date -u +%s.%N)"
QUEUED=0
for W in $(seq 1 30); do
  sleep 2
  if grep -q "T48_DUMP_QUEUED" $E 2>/dev/null; then
    plog "T48_DUMP_QUEUED seen at wait$W"
    QUEUED=1
    break
  fi
done
[ $QUEUED -eq 1 ] || fail NO_DUMP_QUEUE
Q=$(grep -m1 -o "T48_DUMP_QUEUED vsync=[0-9]*" $E | grep -o "[0-9]*")
WINSTART=$((Q+1))
TARGET=$((WINSTART+7))
plog "QUEUED_VSYNC=$Q WINSTART=$WINSTART TARGET=$TARGET"
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
ls -la $T4/t50-shot-$TAG-sc.png $E
kill $(cat $T4/pcsx2-t50b.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T50B_DONE
