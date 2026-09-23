#!/usr/bin/env bash
# T48 Capture B (v3): lean closed-loop. Identity-vs-ref legs (no pre-snaps,
# no depart gates); event verified by orange-bar presence; rules by
# Cross->animated loop; loading-animated gate before pre-race wait.
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
LOG=$T4/t48b-poll.log
SNAPS=$DAT/PCSX2/snaps
TITLE_MEAN_MAX=2.0
TITLE_P99_MAX=10
IDENT_MEAN_MAX=4.0
STATIC_MEAN_MAX=1.0
ANIM_MEAN_MIN=1.0
WALL_CAP=598
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T48B_FAIL:$1"; stamp; kill $(cat $T4/pcsx2-t48.pid) 2>/dev/null; sleep 5; exit 1; }
wallcheck() { [ $(( $(date -u +%s) - T_BOOT )) -lt $WALL_CAP ] || fail WALL_CAP; }
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
  cp "$SNAPS/$NEW" $T4/t48-shot-$LAB.png || fail GSHOT_CP_$LAB
  ls -la $T4/t48-shot-$LAB.png
}
leg() {
  # press -> arrive EXPECTED (identity-vs-ref, retry to 3, 12 s settles).
  local KEY=$1 LAB=$2 EXP=$3 TRY=0 M=99
  while [ $TRY -lt 3 ]; do
    TRY=$((TRY+1))
    press $KEY "${LAB}_t$TRY" 2
    sleep 12; wallcheck; snap t48b-$LAB-t$TRY || fail SNAP_${LAB}
    read M P <<< $(score_ref $T4/t48b-$LAB-t$TRY.ppm $EXP)
    plog "$LAB try$TRY ident mean=$M p99=$P"
    if is_ident $M; then break; fi
  done
  is_ident $M || fail NO_${LAB}_IDENT
}
stamp
rm -f /tmp/t48-arm /tmp/t48-dump-now
touch /tmp/t48-arm; ls -la /tmp/t48-arm
pkill Xvfb || true
sleep 2
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t48b.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $DAT/PCSX2/logs/emulog-pre-t48b-$TS.txt
fi
rm -f $T4/pcsx2-t48.pid
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $BIN -nogui -slowboot -turbo -datapath $DAT -logfile $T4/logs/boot-t48b.log -- "$T4/inputs/SSX 3 (USA).iso" > $T4/logs/boot-t48b.stdout 2>&1 &
echo $! > $T4/pcsx2-t48.pid
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
  snap t48b-a1-poll$N || fail SNAP_A1_POLL$N
  read M P <<< $(score_band $T4/t48b-a1-poll$N.ppm)
  plog "A1 poll$N score mean=$M p99=$P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  if is_title $M $P; then plog "A1 TITLE-DETECTED at poll$N"; DETECTED=1; break; fi
done
[ $DETECTED -eq 1 ] || fail NO_TITLE
leg Return TITLE $REFMENU
leg K MENU $REFSC
leg K SC $REFZC
leg K ZC $REFSP
leg K SP $REFSM
leg K SM $REFSE
for N in 1 2 3 4; do
  press Down "SE_DOWN$N" 2
  sleep 3; snap t48b-se-down$N || fail SNAP_SE_DOWN$N
done
snap t48b-se-walked || fail SNAP_SE_WALKED
read W WP <<< $(score_ref $T4/t48b-se-walked.ppm $T4/t47-se-walked.ppm)
plog "SE-WALKED vs-T47walked(Happiness) mean=$W p99=$WP (want IDENT <4)"
is_ident $W || fail NO_HAPPINESS_IDENT
press K "EVENT_CROSS" 2
sleep 15; wallcheck; snap t48b-ev-15 || fail SNAP_EV_15
sleep 6; snap t48b-ev-21 || fail SNAP_EV_21
HEV=$(score_whole $T4/t48b-ev-15.ppm $T4/t48b-ev-21.ppm)
read HY HN <<< $(hlrow $T4/t48b-ev-21.ppm)
plog "EVENT hop=$HEV hly=$HY hln=$HN"
is_static $HEV || fail NO_EVENT_STATIC
is_num $HN && [ "$HN" -gt 2000 ] || fail NO_RULES_BAR
snap t48b-rules-pre || fail SNAP_RULES_PRE
RULES_OK=0
for R in 1 2 3; do
  if [ $R -gt 1 ]; then
    for U in $(seq 1 11); do press Up "RULESUP${R}_$U" 0.5; sleep 1; done
  fi
  press K "RULES_CROSS_R$R" 2
  sleep 12; wallcheck; snap t48b-loadR$R || fail SNAP_LOADR
  D=$(score_whole $T4/t48b-rules-pre.ppm $T4/t48b-loadR$R.ppm)
  plog "RULES R$R depart=$D"
  if is_anim $D; then
    sleep 8; snap t48b-loadR${R}b || fail SNAP_LOADRB
    A=$(score_whole $T4/t48b-loadR$R.ppm $T4/t48b-loadR${R}b.ppm)
    plog "RULES R$R anim=$A"
    if is_anim $A; then RULES_OK=1; PREVLOAD=$T4/t48b-loadR${R}b.ppm; break; fi
  fi
done
[ $RULES_OK -eq 1 ] || fail NO_LOADING
plog "RACE LAUNCHED (rules exit goes straight to racing)"
gshot t48b-rules
TRY=0; DEP=99
while [ $TRY -lt 3 ]; do
  TRY=$((TRY+1))
  sleep 12; wallcheck; snap t48b-race-t$TRY || fail SNAP_RACE
  DEP=$(score_whole $T4/t48b-rules-pre.ppm $T4/t48b-race-t$TRY.ppm)
  plog "RACE_ENTRY try$TRY depart=$DEP"
  if is_anim $DEP; then break; fi
done
is_anim $DEP || fail NO_RACE_DEPART
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
gshot t48b-race
ls -lat $SNAPS | head -n 8
ls -la $T4/t48-shot-t48b-race.png $E
kill $(cat $T4/pcsx2-t48.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T48B_DONE
