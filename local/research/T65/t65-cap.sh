#!/usr/bin/env bash
# T65 capture: T48 Capture B's route (t48-capB.sh v5, dat-t48: EE rec, VU1 interp, MTVU off) on the T65 build.
# /tmp/t65-arm from boot (T65_BOX every vsync); VU1 dump #1 at settled Select Character, #2 + T48 GS dump in the race;
# F1 race statefile at the end. Changes vs t48-capB.sh are marked T65.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
T4=/home/brad/pcsx2-t4
G=/home/brad/pcsx2-g7
BIN=$G/pcsx2/build/bin/pcsx2-qt
DAT=$G/dat-t48
E=$DAT/PCSX2/logs/emulog.txt
REF=$T4/t27-ref-title.ppm
REFMENU=$T4/t28-ref-menu.ppm
REFSC=$T4/t29-ref-sc.ppm
REFZC=$T4/t30-ref-zc.ppm
REFSP=$T4/t31-ref-sp.ppm
REFSM=$T4/t32-ref-sm.ppm
REFSE=$T4/t33-ref-se.ppm
CD=$T4/t44-cropdiff.py
HL=$T4/t48-hlscan.py
TAG=${TAG:-t65a}
LOG=$T4/$TAG-poll.log
SNAPS=$DAT/PCSX2/snaps
TITLE_MEAN_MAX=2.0
TITLE_P99_MAX=10
IDENT_MEAN_MAX=4.0
STATIC_MEAN_MAX=1.0
ANIM_MEAN_MIN=1.0
WALL_CAP=598
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T65_FAIL:$1"; stamp; kill $(cat $T4/pcsx2-t65.pid) 2>/dev/null; sleep 5; exit 1; }
wallcheck() { [ $(( $(date -u +%s) - T_BOOT )) -lt $WALL_CAP ] || fail WALL_CAP; [ $(stat -c %s $E 2>/dev/null || echo 0) -lt 2000000000 ] || fail EMULOG_CAP; } # T65: +2 GB emulog cap
: > $LOG
plog() { echo "$@" | tee -a $LOG; }
snap() {
  local N=$1
  date -u
  xwd -root -out $T4/$N.xwd || return 1
  xwdtopnm $T4/$N.xwd > $T4/$N.ppm || return 1
  rm -f $T4/$N.xwd
  pnmtojpeg -quality=80 $T4/$N.ppm > $T4/$N.jpg || return 1
  ls -la $T4/$N.ppm $T4/$N.jpg
}
score_band() {
  python3 $CD $1 $REF | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
score_whole() {
  python3 $CD $1 $2 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)}}};END{print m}'
}
score_ref() {
  python3 $CD $1 $2 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
hlrow() {
  python3 $HL $1 0 700 60 950 | awk '{for(i=1;i<=NF;i++){if($i~/^y=/){y=substr($i,3)};if($i~/^n=/){n=substr($i,3)}}};END{print y, n}'
}
is_num() {
  case "$1" in ''|*[!0-9.]*) return 1;; *) return 0;; esac
}
is_title() {
  is_num "$1" && is_num "$2" || return 1
  awk -v m=$1 -v p=$2 -v mm=$TITLE_MEAN_MAX -v pm=$TITLE_P99_MAX \
    'BEGIN{exit !((m<mm)&&(p<=pm))}'
}
is_ident() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$IDENT_MEAN_MAX 'BEGIN{exit !(m<mm)}'
}
is_static() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$STATIC_MEAN_MAX 'BEGIN{exit !(m<mm)}'
}
is_anim() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$ANIM_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
press() {
  local KEY=$1; local LAB=$2; local HOLD=${3:-0.5}
  wallcheck
  plog "${LAB}_KEYDOWN_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime) MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  xdotool windowfocus --sync $WID || fail FOCUS_$LAB
  xdotool keydown $KEY || fail KEYDOWN_$LAB
  sleep $HOLD
  xdotool keyup $KEY || fail KEYUP_$LAB
  plog "${LAB}_KEYUP_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime) MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
}
gshot() {
  local LAB=$1
  press F8 "GSHOT_$LAB"
  sleep 2
  local NEW=$(ls -t $SNAPS | head -n 1)
  plog "GSHOT_$LAB newest=$NEW"
  cp "$SNAPS/$NEW" $T4/t65-shot-$LAB.png || fail GSHOT_CP_$LAB
  ls -la $T4/t65-shot-$LAB.png
}
vudump() { # T65: request one VU1 dump (3 EE vsyncs) and wait for its DONE line.
  local N=$1 LAB=$2
  touch /tmp/t65-vu-now
  plog "VUDUMP_${LAB}_REQ_WALL:$(date -u +%s.%N)"
  for W in $(seq 1 20); do
    sleep 2; wallcheck
    if grep -q "T65_VU_DONE n=$N " $E 2>/dev/null; then plog "VUDUMP_${LAB} done at wait$W: $(grep "T65_VU_DONE n=$N " $E | tail -1)"; return 0; fi
  done
  fail NO_VUDUMP_$LAB
}
leg() {
  # press -> arrive EXPECTED (identity-vs-ref, retry to 3, 12 s settles).
  local KEY=$1 LAB=$2 EXP=$3 TRY=0 M=99
  while [ $TRY -lt 3 ]; do
    TRY=$((TRY+1))
    press $KEY "${LAB}_t$TRY" 2
    sleep 12; wallcheck; snap $TAG-$LAB-t$TRY || fail SNAP_${LAB}
    read M P <<< $(score_ref $T4/$TAG-$LAB-t$TRY.ppm $EXP)
    plog "$LAB try$TRY ident mean=$M p99=$P"
    if is_ident $M; then break; fi
  done
  is_ident $M || fail NO_${LAB}_IDENT
}
stamp
rm -f /tmp/t48-arm /tmp/t48-dump-now /tmp/t49-arm /tmp/t50-arm /tmp/t50-free /tmp/t51-arm /tmp/t51-free /tmp/t51-watch /tmp/t53-watch /tmp/t54-watch /tmp/t56-watch2 /tmp/t59-dump /tmp/t65-arm /tmp/t65-vu-now # T65
rm -f /tmp/t52-mark-* $G/t65-vu1-*.bin # T65
touch /tmp/t48-arm /tmp/t65-arm; ls -la /tmp/t48-arm /tmp/t65-arm # T65: box from boot
pkill Xvfb || true
sleep 2
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-$TAG.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $DAT/PCSX2/logs/emulog-pre-$TAG-$TS.txt
fi
rm -f $T4/pcsx2-t65.pid
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $BIN -nogui -slowboot -turbo -datapath $DAT -logfile $T4/logs/boot-$TAG.log -- "$T4/inputs/SSX 3 (USA).iso" > $T4/logs/boot-$TAG.stdout 2>&1 &
echo $! > $T4/pcsx2-t65.pid
echo "PID:$!"
sleep 70
wallcheck
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_START
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
press K "A1_CROSS"
DETECTED=0
for N in $(seq 1 18); do
  sleep 2; wallcheck
  snap $TAG-a1-poll$N || fail SNAP_A1_POLL$N
  read M P <<< $(score_band $T4/$TAG-a1-poll$N.ppm)
  plog "A1 poll$N score mean=$M p99=$P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  if is_title $M $P; then plog "A1 TITLE-DETECTED at poll$N"; DETECTED=1; break; fi
done
[ $DETECTED -eq 1 ] || fail NO_TITLE
leg Return TITLE $REFMENU
leg K MENU $REFSC
sleep 15; wallcheck # T65: settle Select Character, then the control dump
snap $TAG-sc-settled || fail SNAP_SC_SETTLED
read SM SP <<< $(score_ref $T4/$TAG-sc-settled.ppm $REFSC)
plog "SC_SETTLED ident mean=$SM p99=$SP"
is_ident $SM || fail NO_SC_SETTLED
vudump 1 SC
gshot $TAG-sc
leg K SC $REFZC
leg K ZC $REFSP
leg K SP $REFSM
leg K SM $REFSE
for N in 1 2 3 4; do
  press Down "SE_DOWN$N" 2
  sleep 3; snap $TAG-se-down$N || fail SNAP_SE_DOWN$N
done
snap $TAG-se-walked || fail SNAP_SE_WALKED
read W WP <<< $(score_ref $T4/$TAG-se-walked.ppm $T4/t47-se-walked.ppm)
plog "SE-WALKED vs-T47walked(Happiness) mean=$W p99=$WP (want IDENT <4)"
is_ident $W || fail NO_HAPPINESS_IDENT
press K "EVENT_CROSS" 2
sleep 15; wallcheck; snap $TAG-ev-15 || fail SNAP_EV_15
sleep 6; snap $TAG-ev-21 || fail SNAP_EV_21
HEV=$(score_whole $T4/$TAG-ev-15.ppm $T4/$TAG-ev-21.ppm)
read HY HN <<< $(hlrow $T4/$TAG-ev-21.ppm)
plog "EVENT hop=$HEV hly=$HY hln=$HN"
is_static $HEV || fail NO_EVENT_STATIC
is_num $HN && [ "$HN" -gt 2000 ] || fail NO_RULES_BAR
snap $TAG-rules-pre || fail SNAP_RULES_PRE
RULES_OK=0
for R in 1 2 3; do
  if [ $R -gt 1 ]; then
    for U in $(seq 1 11); do press Up "RULESUP${R}_$U" 0.5; sleep 1; done
  fi
  press K "RULES_CROSS_R$R" 2
  sleep 12; wallcheck; snap $TAG-loadR$R || fail SNAP_LOADR
  D=$(score_whole $T4/$TAG-rules-pre.ppm $T4/$TAG-loadR$R.ppm)
  plog "RULES R$R depart=$D"
  if is_anim $D; then
    sleep 8; snap $TAG-loadR${R}b || fail SNAP_LOADRB
    A=$(score_whole $T4/$TAG-loadR$R.ppm $T4/$TAG-loadR${R}b.ppm)
    plog "RULES R$R anim=$A"
    if is_anim $A; then RULES_OK=1; PREVLOAD=$T4/$TAG-loadR${R}b.ppm; break; fi
  fi
done
[ $RULES_OK -eq 1 ] || fail NO_LOADING
plog "RACE LAUNCHED (rules exit goes straight to racing)"
gshot $TAG-rules
TRY=0; DEP=99
while [ $TRY -lt 3 ]; do
  TRY=$((TRY+1))
  sleep 12; wallcheck; snap $TAG-race-t$TRY || fail SNAP_RACE
  DEP=$(score_whole $T4/$TAG-rules-pre.ppm $T4/$TAG-race-t$TRY.ppm)
  plog "RACE_ENTRY try$TRY depart=$DEP"
  if is_anim $DEP; then break; fi
done
is_anim $DEP || fail NO_RACE_DEPART
sleep 3 # T65
vudump 2 RACE
touch /tmp/t48-dump-now
ls -la /tmp/t48-dump-now
plog "DUMP_TRIGGERED_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
QUEUED=0
for W in $(seq 1 30); do
  sleep 2; wallcheck
  if grep -q "T48_DUMP_QUEUED" $E 2>/dev/null; then
    plog "T48_DUMP_QUEUED seen at wait$W"
    QUEUED=1
    break
  fi
done
[ $QUEUED -eq 1 ] || fail NO_DUMP_QUEUE
sleep 5
rm -f /tmp/t48-dump-now
gshot $TAG-race
snap $TAG-race-live || fail SNAP_RACE_LIVE
press F1 "STATE_SAVE" # T65: race statefile for reuse
T_SAVE_START=$(date -u +%s)
sleep 8
SSD=$DAT/PCSX2/sstates
STATE_NEWEST=$(ls -t "$SSD" 2>/dev/null | grep -v -i backup | head -n 1)
plog "STATE newest=$STATE_NEWEST size=$(stat -c %s "$SSD/$STATE_NEWEST") mtime=$(stat -c %Y "$SSD/$STATE_NEWEST") save_start=$T_SAVE_START"
[ $(stat -c %Y "$SSD/$STATE_NEWEST") -ge $((T_SAVE_START - 10)) ] && cp "$SSD/$STATE_NEWEST" $G/t65-race-state && sha256sum $G/t65-race-state | tee -a $LOG
plog "COUNTS box=$(grep -c 'T65_BOX' $E) vurec=$(grep -c 'T65_VUREC' $E) paths=$(grep -c 'T48_PATHS' $E) draw=$(grep -c 'G12_DRAW' $E) emulog=$(stat -c %s $E)"
ls -la $G/t65-vu1-*.bin
kill $(cat $T4/pcsx2-t65.pid); sleep 10; pgrep -a pcsx2-qt || true
rm -f /tmp/t65-arm /tmp/t48-arm
stamp
echo T65_DONE
