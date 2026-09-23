#!/usr/bin/env bash
# T66 capture: T64's recipe (t63-menu-state, dat-t57 EE+VU0 interp) -> K -> SC settled, on the T66 build.
# t66w/t66chg/t66cen watch the quaternion at 0x00bc5950 from the MENU state; /tmp/t66-dump at settled SC
# dumps object 0x00bc5920 for 3 vsyncs + one RAM scan. Changes vs t64-cap.sh are marked T66.
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
TAG=${TAG:-t66a}
LOG=$T4/$TAG-poll.log
IDENT_MEAN_MAX=4.0
WALL_CAP=590
fail() { echo "T66_FAIL:$1"; date -u; kill $(cat $T4/pcsx2-$TAG.pid) 2>/dev/null; sleep 5; exit 1; }
wallcheck() { [ $(( $(date -u +%s) - T_BOOT )) -lt $WALL_CAP ] || fail WALL_CAP; }
: > $LOG
plog() { echo "$@" | tee -a $LOG; }
snap() {
  local N=$1
  xwd -root -out $T4/$N.xwd || return 1
  xwdtopnm $T4/$N.xwd > $T4/$N.ppm || return 1
  rm -f $T4/$N.xwd
}
score_ref() {
  python3 $CD $1 $2 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
is_num() {
  case "$1" in ''|*[!0-9.]*) return 1;; *) return 0;; esac
}
is_ident() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$IDENT_MEAN_MAX 'BEGIN{exit !(m<mm)}'
}
press() {
  local KEY=$1; local LAB=$2; local HOLD=${3:-0.5}
  wallcheck
  xdotool windowfocus --sync $WID || fail FOCUS_$LAB
  xdotool keydown $KEY || fail KEYDOWN_$LAB
  sleep $HOLD
  xdotool keyup $KEY || fail KEYUP_$LAB
  plog "${LAB}_WALL:$(date -u +%s.%N)"
}
date -u
[ -x $BIN ] || fail NO_BIN
grep -q "^EnableEE = false" $DAT/PCSX2/inis/PCSX2.ini || fail NOT_INTERP
grep -q "^EnableVU0 = false" $DAT/PCSX2/inis/PCSX2.ini || fail NOT_VU0INT
STATEFILE=${STATEFILE:-$G/t63-menu-state}
if [ -f $STATEFILE ]; then plog "STATEFILE=$STATEFILE"; else plog "FALLBACK t58-pre-sc-state (no fresh state)"; STATEFILE=$G/t58-pre-sc-state; fi
[ -f $STATEFILE ] || fail NO_PRESTATE
rm -f /tmp/t48-arm /tmp/t48-dump-now /tmp/t49-arm /tmp/t50-arm /tmp/t50-free /tmp/t51-arm /tmp/t51-free /tmp/t51-watch /tmp/t53-watch /tmp/t54-watch /tmp/t56-watch2 /tmp/t59-dump /tmp/t65-arm /tmp/t65-vu-now /tmp/t66-dump /tmp/t52-mark-* # T66
touch /tmp/t48-arm # T66: only the G13-autodump suppressor; older lanes' log gates stay off
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
T_BOOT=$(date -u +%s)
nohup $BIN -nogui -turbo -datapath $DAT -logfile $T4/logs/boot-$TAG.log -statefile "$STATEFILE" -- "$T4/inputs/SSX 3 (USA).iso" > $T4/logs/boot-$TAG.stdout 2>&1 &
echo $! > $T4/pcsx2-$TAG.pid
sleep 45
wallcheck
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED
P0=$(grep -o "T48_PATHS vsync=[0-9]*" $E 2>/dev/null | tail -1 | grep -o "[0-9]*$")
plog "PATHS_AT_START=${P0:-none}"
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
T_K=$(date -u +%s.%N)
touch /tmp/t52-mark-scentry # T66
press K "MENU_CROSS" 2
plog "K_PRESS_T=$T_K"
SC_OK=0
for TRY in 1 2 3; do
  sleep 15; wallcheck
  snap $TAG-sc-t$TRY || fail SNAP_SC
  read M P <<< $(score_ref $T4/$TAG-sc-t$TRY.ppm $REFSC)
  plog "SC try$TRY ident mean=$M p99=$P"
  if is_ident $M; then SC_OK=1; T_SC1=$(date -u +%s.%N); plog "SC_FIRST_IDENT_T=$T_SC1"; break; fi
done
[ $SC_OK -eq 1 ] || fail NO_SC_IDENT
sleep 15; wallcheck
snap $TAG-sc-settled || fail SNAP_SETTLED
read SM SP <<< $(score_ref $T4/$TAG-sc-settled.ppm $REFSC)
plog "SC_SETTLED ident mean=$SM p99=$SP"
is_ident $SM || fail NO_SC_SETTLED
touch /tmp/t52-mark-scsettled /tmp/t66-dump # T66
plog "DUMP_GATE_WALL:$(date -u +%s.%N)"
DONE=0
for W in $(seq 1 15); do sleep 2; wallcheck; if grep -q "t66obj_done" $E 2>/dev/null; then DONE=1; break; fi; done
plog "T66_OBJ_DONE=$DONE $(grep -a t66obj_done $E | tail -1)"
[ $DONE -eq 1 ] || fail NO_T66_DUMP
WID2=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW2
xdotool windowfocus --sync $WID2 || fail FOCUS
xdotool keydown F8; sleep 0.5; xdotool keyup F8
sleep 2
NEW=$(ls -t $SNAPS | head -n 1)
plog "GSHOT newest=$NEW"
cp "$SNAPS/$NEW" $T4/$TAG-shot-sc.png || fail GSHOT_CP
xwd -root -out $T4/$TAG-loaded.xwd || fail SNAP
xwdtopnm $T4/$TAG-loaded.xwd > $T4/$TAG-loaded.ppm || fail SNAP2
rm -f $T4/$TAG-loaded.xwd
read LM LP <<< $(python3 $CD $T4/$TAG-loaded.ppm $REFSC 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}')
plog "LOADED vs-sc mean=$LM p99=$LP"
P1=$(grep -o "T48_PATHS vsync=[0-9]*" $E 2>/dev/null | tail -1 | grep -o "[0-9]*$")
plog "PATHS_AT_END=${P1:-none}"
plog "COUNTS t66w=$(grep -ac 't66w vsync=' $E) t66chg=$(grep -ac 't66chg vsync=' $E) t66f=$(grep -ac 't66f vsync=' $E) t66v=$(grep -ac 't66v vsync=' $E) t66cen=$(grep -ac 't66cen vsync=' $E) t66obj=$(grep -ac 't66obj vsync=' $E) t66scan=$(grep -ac 't66scan vsync=' $E) marks=$(grep -ac T52_MARK $E) emulog=$(stat -c %s $E)"
kill $(cat $T4/pcsx2-$TAG.pid); sleep 5; pgrep -a pcsx2-qt || true
date -u
rm -f /tmp/t48-arm /tmp/t66-dump
echo T66_DONE
