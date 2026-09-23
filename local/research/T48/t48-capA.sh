#!/usr/bin/env bash
# T48 Capture A: boot -> Select Character (settled, Zoe) -> 8-vsync dump + F8.
# Shape: t47-frontend.sh legs through SC verbatim (gates, sleeps, refs).
# UNPATCHED=1: proof run (pre-T48 binary, no arm file, SC F8 only, no trigger).
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
T4=/home/brad/pcsx2-t4
G=/home/brad/pcsx2-g7
D=$T4
if [ "${UNPATCHED:-0}" = "1" ]; then BIN=$G/pre-t48/pcsx2-qt; TAG=t48proof; else BIN=$G/pcsx2/build/bin/pcsx2-qt; TAG=t48a; fi
DAT=$G/dat-t48
E=$DAT/PCSX2/logs/emulog.txt
REF=$T4/t27-ref-title.ppm
REFMENU=$T4/t28-ref-menu.ppm
REFSC=$T4/t29-ref-sc.ppm
CD=$T4/t44-cropdiff.py
if [ "${UNPATCHED:-0}" = "1" ]; then LOG=$T4/t48proof-poll.log; else LOG=$T4/t48a-poll.log; fi
SNAPS=$DAT/PCSX2/snaps
TITLE_MEAN_MAX=2.0
TITLE_P99_MAX=10
STATIC_MEAN_MAX=1.0
MENU_MEAN_MAX=2.0
NONMENU_MEAN_MIN=5.0
NONSC_MEAN_MIN=5.0
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T48A_FAIL:$1"; stamp; exit 1; }
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
score_menu() {
  python3 $CD $1 $REFMENU 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
score_sc() {
  python3 $CD $1 $REFSC 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
is_num() {
  case "$1" in ''|*[!0-9.]*) return 1;; *) return 0;; esac
}
is_title() {
  is_num "$1" && is_num "$2" || return 1
  awk -v m=$1 -v p=$2 -v mm=$TITLE_MEAN_MAX -v pm=$TITLE_P99_MAX \
    'BEGIN{exit !((m<mm)&&(p<=pm))}'
}
is_static() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$STATIC_MEAN_MAX 'BEGIN{exit !(m<mm)}'
}
is_menu() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$MENU_MEAN_MAX 'BEGIN{exit !(m<mm)}'
}
is_nonmenu() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$NONMENU_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
is_nonsc() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$NONSC_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
press() {
  local KEY=$1; local LAB=$2
  plog "${LAB}_KEYDOWN_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime) MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  xdotool windowfocus --sync $WID || fail FOCUS_$LAB
  xdotool keydown $KEY || fail KEYDOWN_$LAB
  plog "${LAB}_HELD_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
  sleep 0.5
  xdotool keyup $KEY || fail KEYUP_$LAB
  plog "${LAB}_KEYUP_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime) MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
}
gshot() {
  local LAB=$1
  ls -lat $SNAPS | head -n 5
  press F8 "GSHOT_$LAB"
  sleep 2
  local NEW=$(ls -t $SNAPS | head -n 1)
  plog "GSHOT_$LAB newest=$NEW"
  cp "$SNAPS/$NEW" $T4/t48-shot-$LAB.png || fail GSHOT_CP_$LAB
  ls -la $T4/t48-shot-$LAB.png
}
stamp
rm -f /tmp/t48-arm /tmp/t48-dump-now
if [ "${UNPATCHED:-0}" != "1" ]; then touch /tmp/t48-arm; ls -la /tmp/t48-arm; fi
pkill Xvfb || true
sleep 2
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t48a.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
ls -lat $SNAPS | head -n 5
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $DAT/PCSX2/logs/emulog-pre-$TAG-$TS.txt
  ls -la $DAT/PCSX2/logs/
fi
rm -f $T4/pcsx2-t48.pid
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $BIN -nogui -slowboot -turbo -datapath $DAT -logfile $T4/logs/boot-$TAG.log -- "$T4/inputs/SSX 3 (USA).iso" > $T4/logs/boot-$TAG.stdout 2>&1 &
echo $! > $T4/pcsx2-t48.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_START
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
snap t48a-start || fail SNAP_START
read SM SP <<< $(score_band $T4/t48a-start.ppm)
plog "START_SCORE mean=$SM p99=$SP MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
press K "A1_CROSS"
DETECTED=0
for N in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18; do
  sleep 2
  snap t48a-a1-poll$N || fail SNAP_A1_POLL$N
  read M P <<< $(score_band $T4/t48a-a1-poll$N.ppm)
  plog "A1 poll$N score mean=$M p99=$P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  if is_title $M $P; then
    plog "A1 TITLE-DETECTED at poll$N"
    DETECTED=1
    break
  fi
done
[ $DETECTED -eq 1 ] || fail NO_TITLE
gshot $TAG-title
press Return "TITLE_START"
sleep 3; snap t48a-post3 || fail SNAP_POST3
read M3 P3 <<< $(score_band $T4/t48a-post3.ppm)
plog "post+3 titleband mean=$M3 p99=$P3 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
sleep 5; snap t48a-post8 || fail SNAP_POST8
read M8 P8 <<< $(score_band $T4/t48a-post8.ppm)
plog "post+8 titleband mean=$M8 p99=$P8"
sleep 7; snap t48a-post15 || fail SNAP_POST15
read M15 P15 <<< $(score_band $T4/t48a-post15.ppm)
plog "post+15 titleband mean=$M15 p99=$P15"
sleep 10; snap t48a-post25 || fail SNAP_POST25
read M25 P25 <<< $(score_band $T4/t48a-post25.ppm)
plog "post+25 titleband mean=$M25 p99=$P25"
W815=$(score_whole $T4/t48a-post8.ppm $T4/t48a-post15.ppm)
W1525=$(score_whole $T4/t48a-post15.ppm $T4/t48a-post25.ppm)
plog "whole815=$W815 whole1525=$W1525"
read MM25 MP25 <<< $(score_menu $T4/t48a-post25.ppm)
plog "post25-vs-menu mean=$MM25 p99=$MP25"
if ! is_title $M8 $P8 && ! is_title $M15 $P15 && ! is_title $M25 $P25 \
   && is_static $W815 && is_static $W1525; then
  plog "MENU-LIKE -> menu Cross"
else
  fail NO_MENU_PARK
fi
sleep 5
snap t48a-menupre || fail SNAP_MENUPRE
read MMP MMP_P <<< $(score_menu $T4/t48a-menupre.ppm)
plog "MENUPRE vs-menu mean=$MMP p99=$MMP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
gshot $TAG-menu
press K "MENU_CROSS"
sleep 1; snap t48a-mc-post1 || fail SNAP_MC_POST1
read M1 P1 <<< $(score_band $T4/t48a-mc-post1.ppm)
read MM1 MP1 <<< $(score_menu $T4/t48a-mc-post1.ppm)
read MS1 MSP1 <<< $(score_sc $T4/t48a-mc-post1.ppm)
plog "MC post+1 titleband mean=$M1 p99=$P1 vs-menu mean=$MM1 p99=$MP1 vs-sc mean=$MS1 p99=$MSP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
sleep 2; snap t48a-mc-post3 || fail SNAP_MC_POST3
read M3 P3 <<< $(score_band $T4/t48a-mc-post3.ppm)
read MM3 MP3 <<< $(score_menu $T4/t48a-mc-post3.ppm)
read MS3 MSP3 <<< $(score_sc $T4/t48a-mc-post3.ppm)
plog "MC post+3 titleband mean=$M3 p99=$P3 vs-menu mean=$MM3 p99=$MP3 vs-sc mean=$MS3 p99=$MSP3"
sleep 5; snap t48a-mc-post8 || fail SNAP_MC_POST8
read M8 P8 <<< $(score_band $T4/t48a-mc-post8.ppm)
read MM8 MP8 <<< $(score_menu $T4/t48a-mc-post8.ppm)
read MS8 MSP8 <<< $(score_sc $T4/t48a-mc-post8.ppm)
plog "MC post+8 titleband mean=$M8 p99=$P8 vs-menu mean=$MM8 p99=$MP8 vs-sc mean=$MS8 p99=$MSP8"
sleep 7; snap t48a-mc-post15 || fail SNAP_MC_POST15
read M15 P15 <<< $(score_band $T4/t48a-mc-post15.ppm)
read MM15 MP15 <<< $(score_menu $T4/t48a-mc-post15.ppm)
read MS15 MSP15 <<< $(score_sc $T4/t48a-mc-post15.ppm)
plog "MC post+15 titleband mean=$M15 p99=$P15 vs-menu mean=$MM15 p99=$MP15 vs-sc mean=$MS15 p99=$MSP15"
H_PRE1=$(score_whole $T4/t48a-menupre.ppm $T4/t48a-mc-post1.ppm)
H_13=$(score_whole $T4/t48a-mc-post1.ppm $T4/t48a-mc-post3.ppm)
H_38=$(score_whole $T4/t48a-mc-post3.ppm $T4/t48a-mc-post8.ppm)
H_815=$(score_whole $T4/t48a-mc-post8.ppm $T4/t48a-mc-post15.ppm)
plog "MC hops whole: pre-post1=$H_PRE1 p1-p3=$H_13 p3-p8=$H_38 p8-p15=$H_815"
if is_nonmenu $MM15 && is_static $H_38 && is_static $H_815; then
  plog "SC-LIKE -> settled SC captures"
else
  fail NO_SC_PARK
fi
sleep 5
snap t48a-scpre || fail SNAP_SCPRE
read SCP SCP_P <<< $(score_sc $T4/t48a-scpre.ppm)
plog "SCPRE vs-sc mean=$SCP p99=$SCP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
if [ "${UNPATCHED:-0}" = "1" ]; then
  gshot $TAG-sc
  ls -la $T4/t48-shot-$TAG-sc.png $E
  kill $(cat $T4/pcsx2-t48.pid); sleep 10; pgrep -a pcsx2-qt || true
  stamp
  echo T48A_DONE
  exit 0
fi
touch /tmp/t48-dump-now
ls -la /tmp/t48-dump-now
plog "DUMP_TRIGGERED_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
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
sleep 6
rm -f /tmp/t48-dump-now
gshot $TAG-sc
grep -m 2 "T48_DUMP_QUEUED" $E || true
ls -lat $SNAPS | head -n 8
ls -la $T4/t48-shot-$TAG-sc.png $E
kill $(cat $T4/pcsx2-t48.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T48A_DONE
