#!/usr/bin/env bash
# T63 run 2: fresh MENU state under EE+VU0 interp, K to SC settled.
# Window covers the MENU->SC scene build plus a settled tail. Proves SC via
# F8 + LOADED band; the ebw/ebwlast tail proves the buffers' end state.
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
TAG=${TAG:-t63r2}
LOG=$T4/$TAG-poll.log
IDENT_MEAN_MAX=4.0
WALL_CAP=590
fail() { echo "T58_FAIL:$1"; date -u; kill $(cat $T4/pcsx2-$TAG.pid) 2>/dev/null; sleep 5; exit 1; }
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
rm -f /tmp/t48-arm /tmp/t48-dump-now /tmp/t49-arm /tmp/t50-arm /tmp/t50-free /tmp/t51-arm /tmp/t51-free /tmp/t51-watch /tmp/t53-watch /tmp/t54-watch /tmp/t56-watch2 /tmp/t59-dump
touch /tmp/t48-arm /tmp/t50-arm /tmp/t51-arm
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
touch /tmp/t50-free /tmp/t51-free
plog "FREE_GATE_OPEN_WALL:$(date -u +%s.%N)"
P0=$(grep -o "T48_PATHS vsync=[0-9]*" $E 2>/dev/null | tail -1 | grep -o "[0-9]*$")
plog "PATHS_AT_START=${P0:-none}"
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
T_K=$(date -u +%s.%N)
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
touch /tmp/t59-dump
plog "DUMP_GATE_WALL:$(date -u +%s.%N)"
sleep 5
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
plog "COUNTS app=$(grep -c 'app vsync=' $E || true) appx=$(grep -c 'appx vsync=' $E || true) axfirst=$(grep -c 'axfirst vsync=' $E || true) v1b0=$(grep -c 'v1b0 vsync=' $E || true) tw=$(grep -c 'tw vsync=' $E || true) twbase=$(grep -c 'twbase vsync=' $E || true) t63cap=$(grep -c 'T63_CAP' $E || true) t62cap=$(grep -c 'T62_CAP' $E || true) appsum=$(grep -c 'appsum vsync=' $E || true) apc=$(grep -c 'apc vsync=' $E || true) tpl=$(grep -c 'tpl vsync=' $E || true) t60cap=$(grep -c 'T60_CAP' $E || true) capsum=$(grep -c 'T61_CAPSUM' $E || true) tplrearm=$(grep -c 'tplrearm vsync=' $E || true) ebw=$(grep -c 'ebw vsync=' $E || true) ebwend=$(grep -c 'ebwend vsync=' $E || true) ebwlast=$(grep -c 'ebwlast vsync=' $E || true) cap=$(grep -c 'T58_CAP' $E || true) caplast=$(grep -c 'T58_CAPLAST' $E || true) vu0call=$(grep -c 'vu0call vsync=' $E || true) vif0op=$(grep -c 'vif0op vsync=' $E || true) t57cap=$(grep -c 'T57_CAP' $E || true) ctag=$(grep -c 'ctag ' $E || true) spw=$(grep -c 'spw vsync=' $E || true)"
kill $(cat $T4/pcsx2-$TAG.pid); sleep 5; pgrep -a pcsx2-qt || true
date -u
echo T63R2_DONE
