#!/usr/bin/env bash
# T58 state run: cold REC boot along T48's route to the main menu, F1-save a
# pre-SC statefile. Emulog is discarded (hooks log noise only); the pinned
# output is $G/t58-pre-sc-state (+ sha in the poll log).
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
T4=/home/brad/pcsx2-t4
G=/home/brad/pcsx2-g7
BIN=$G/pcsx2/build/bin/pcsx2-qt
DAT=$G/dat-t48
E=$DAT/PCSX2/logs/emulog.txt
REF=$T4/t27-ref-title.ppm
REFMENU=$T4/t28-ref-menu.ppm
CD=$T4/t44-cropdiff.py
TAG=t58s
LOG=$T4/$TAG-poll.log
TITLE_MEAN_MAX=2.0
TITLE_P99_MAX=10
IDENT_MEAN_MAX=4.0
WALL_CAP=590
fail() { echo "T58S_FAIL:$1"; date -u; kill $(cat $T4/pcsx2-$TAG.pid) 2>/dev/null; sleep 5; exit 1; }
wallcheck() { [ $(( $(date -u +%s) - T_BOOT )) -lt $WALL_CAP ] || fail WALL_CAP; }
: > $LOG
plog() { echo "$@" | tee -a $LOG; }
snap() {
  local N=$1
  xwd -root -out $T4/$N.xwd || return 1
  xwdtopnm $T4/$N.xwd > $T4/$N.ppm || return 1
  rm -f $T4/$N.xwd
}
score_band() {
  python3 $CD $1 $REF | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
score_ref() {
  python3 $CD $1 $2 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
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
press() {
  local KEY=$1; local LAB=$2; local HOLD=${3:-0.5}
  wallcheck
  xdotool windowfocus --sync $WID || fail FOCUS_$LAB
  xdotool keydown $KEY || fail KEYDOWN_$LAB
  sleep $HOLD
  xdotool keyup $KEY || fail KEYUP_$LAB
  plog "${LAB}_WALL:$(date -u +%s.%N)"
}
leg() {
  local KEY=$1 LAB=$2 EXP=$3 TRY=0 M=99
  while [ $TRY -lt 3 ]; do
    TRY=$((TRY+1))
    press $KEY "${LAB}_t$TRY" 2
    sleep 12; wallcheck; snap t58s-$LAB-t$TRY || fail SNAP_${LAB}
    read M P <<< $(score_ref $T4/t58s-$LAB-t$TRY.ppm $EXP)
    plog "$LAB try$TRY ident mean=$M p99=$P"
    if is_ident $M; then break; fi
  done
  is_ident $M || fail NO_${LAB}_IDENT
}
date -u
[ -x $BIN ] || fail NO_BIN
rm -f /tmp/t48-arm /tmp/t48-dump-now /tmp/t49-arm /tmp/t50-arm /tmp/t50-free /tmp/t51-arm /tmp/t51-free /tmp/t51-watch /tmp/t53-watch /tmp/t54-watch /tmp/t56-watch2
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
nohup $BIN -nogui -slowboot -turbo -datapath $DAT -logfile $T4/logs/boot-$TAG.log -- "$T4/inputs/SSX 3 (USA).iso" > $T4/logs/boot-$TAG.stdout 2>&1 &
echo $! > $T4/pcsx2-$TAG.pid
sleep 70
wallcheck
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_START
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
press K "A1_CROSS"
DETECTED=0
for N in $(seq 1 18); do
  sleep 2; wallcheck
  snap t58s-a1-poll$N || fail SNAP_A1_POLL$N
  read M P <<< $(score_band $T4/t58s-a1-poll$N.ppm)
  plog "A1 poll$N score mean=$M p99=$P"
  if is_title $M $P; then plog "A1 TITLE-DETECTED at poll$N"; DETECTED=1; break; fi
done
[ $DETECTED -eq 1 ] || fail NO_TITLE
leg Return TITLE $REFMENU
snap t58s-menu-pre || fail SNAP_MENU_PRE
read MM MP <<< $(score_ref $T4/t58s-menu-pre.ppm $REFMENU)
plog "MENU-PRE ident mean=$MM p99=$MP"
is_ident $MM || fail NO_MENU_PRE_IDENT
press F1 "STATE_SAVE"
T_SAVE_START=$(date -u +%s)
sleep 5
SSD=$DAT/PCSX2/sstates
ls -lat "$SSD" 2>/dev/null | head -n 8 || plog "no sstates dir yet"
STATE_NEWEST=""
for SPOLL in 1 2 3 4 5 6; do
  STATE_NEWEST=$(ls -t "$SSD" 2>/dev/null | grep -v -i backup | head -n 1)
  [ -n "$STATE_NEWEST" ] && break
  sleep 5
done
[ -n "$STATE_NEWEST" ] || fail NO_STATE_FILE
STATE_MTIME=$(stat -c %Y "$SSD/$STATE_NEWEST")
plog "STATE newest=$STATE_NEWEST size=$(stat -c %s "$SSD/$STATE_NEWEST") mtime=$STATE_MTIME save_start=$T_SAVE_START"
[ $(stat -c %s "$SSD/$STATE_NEWEST") -gt 1000000 ] || fail STATE_TINY
[ $STATE_MTIME -ge $((T_SAVE_START - 10)) ] || fail STATE_STALE
cp "$SSD/$STATE_NEWEST" $G/t58-pre-sc-state || fail STATE_CP
sha256sum $G/t58-pre-sc-state | tee -a $LOG
ls -la $G/t58-pre-sc-state
kill $(cat $T4/pcsx2-$TAG.pid); sleep 10; pgrep -a pcsx2-qt || true
date -u
echo T58S_DONE
