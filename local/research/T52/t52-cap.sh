#!/usr/bin/env bash
# T52 capture: FRESH rec boot through T47's route to Select Character settled,
# with T52_CDREAD (every N-data-read + vsync) + T52_MARK transition anchors.
# Shape: t47-frontend.sh legs verbatim through the SC park (same gates, same
# sleeps, same refs); stops after SC settle (no ZC onward). Foreground run.
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
CD=$T4/t44-cropdiff.py
LOG=$T4/t52-poll.log
SNAPS=$DAT/PCSX2/snaps
TITLE_MEAN_MAX=2.0
TITLE_P99_MAX=10
STATIC_MEAN_MAX=1.0
MENU_MEAN_MAX=2.0
NONMENU_MEAN_MIN=5.0
DEPART_MEAN_MIN=5.0
SC_MEAN_MAX=2.0
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T52_FAIL:$1"; stamp; exit 1; }
: > $LOG
plog() { echo "$@" | tee -a $LOG; }
[ -x $BIN ] || fail NO_BIN
grep -q "^EnableEE = true" $DAT/PCSX2/inis/PCSX2.ini || fail NOT_REC
for R in $REF $REFMENU $REFSC $CD; do [ -f $R ] || fail NO_REF_$R; done
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
is_departed() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$DEPART_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
is_sc() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$SC_MEAN_MAX 'BEGIN{exit !(m<mm)}'
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
  cp "$SNAPS/$NEW" $T4/t52-shot-$LAB.png || fail GSHOT_CP_$LAB
  ls -la $T4/t52-shot-$LAB.png
}
mark() {
  touch /tmp/t52-mark-$1
  plog "MARK_$1 touched at MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  sleep 2
}
stamp
rm -f /tmp/t52-mark-title /tmp/t52-mark-menu /tmp/t52-mark-scentry /tmp/t52-mark-scsettled
pkill Xvfb || true
sleep 2
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t52.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
ls -lat $SNAPS | head -n 5
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $DAT/PCSX2/logs/emulog-pre-t52-$TS.txt
  ls -la $DAT/PCSX2/logs/
fi
rm -f $T4/pcsx2-t52.pid
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $BIN -nogui -slowboot -turbo -datapath $DAT -logfile $T4/logs/boot-t52.log -- "$T4/inputs/SSX 3 (USA).iso" > $T4/logs/boot-t52.stdout 2>&1 &
echo $! > $T4/pcsx2-t52.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_START
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
snap t52-start || fail SNAP_START
read SM SP <<< $(score_band $T4/t52-start.ppm)
plog "START_SCORE mean=$SM p99=$SP MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
press K "A1_CROSS"
DETECTED=0
for N in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18; do
  sleep 2
  snap t52-a1-poll$N || fail SNAP_A1_POLL$N
  read M P <<< $(score_band $T4/t52-a1-poll$N.ppm)
  plog "A1 poll$N score mean=$M p99=$P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  if is_title $M $P; then
    plog "A1 TITLE-DETECTED at poll$N"
    cp $T4/t52-a1-poll$N.ppm $T4/t52-title.ppm
    cp $T4/t52-a1-poll$N.jpg $T4/t52-title.jpg
    DETECTED=1
    break
  fi
done
[ $DETECTED -eq 1 ] || fail NO_TITLE
mark title
gshot title
press Return "TITLE_START"
sleep 3; snap t52-post3 || fail SNAP_POST3
read M3 P3 <<< $(score_band $T4/t52-post3.ppm)
plog "post+3 titleband mean=$M3 p99=$P3 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
sleep 5; snap t52-post8 || fail SNAP_POST8
read M8 P8 <<< $(score_band $T4/t52-post8.ppm)
plog "post+8 titleband mean=$M8 p99=$P8"
sleep 7; snap t52-post15 || fail SNAP_POST15
read M15 P15 <<< $(score_band $T4/t52-post15.ppm)
plog "post+15 titleband mean=$M15 p99=$P15"
sleep 10; snap t52-post25 || fail SNAP_POST25
read M25 P25 <<< $(score_band $T4/t52-post25.ppm)
plog "post+25 titleband mean=$M25 p99=$P25"
W815=$(score_whole $T4/t52-post8.ppm $T4/t52-post15.ppm)
W1525=$(score_whole $T4/t52-post15.ppm $T4/t52-post25.ppm)
plog "whole815=$W815 whole1525=$W1525"
read MM25 MP25 <<< $(score_menu $T4/t52-post25.ppm)
plog "post25-vs-menu mean=$MM25 p99=$MP25"
if ! is_title $M8 $P8 && ! is_title $M15 $P15 && ! is_title $M25 $P25 \
   && is_static $W815 && is_static $W1525; then
  plog "MENU-LIKE -> menu Cross"
else
  fail NO_MENU_PARK
fi
sleep 5
snap t52-menupre || fail SNAP_MENUPRE
read MMP MMP_P <<< $(score_menu $T4/t52-menupre.ppm)
plog "MENUPRE vs-menu mean=$MMP p99=$MMP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
mark menu
gshot menu
press K "MENU_CROSS"
sleep 1; snap t52-mc-post1 || fail SNAP_MC_POST1
H_PRE1=$(score_whole $T4/t52-menupre.ppm $T4/t52-mc-post1.ppm)
plog "MC hops pre-post1=$H_PRE1"
ENTRY_MARKED=0
if is_departed $H_PRE1; then mark scentry; ENTRY_MARKED=1; fi
read M1 P1 <<< $(score_band $T4/t52-mc-post1.ppm)
read MM1 MP1 <<< $(score_menu $T4/t52-mc-post1.ppm)
read MS1 MSP1 <<< $(score_sc $T4/t52-mc-post1.ppm)
plog "MC post+1 titleband mean=$M1 p99=$P1 vs-menu mean=$MM1 p99=$MP1 vs-sc mean=$MS1 p99=$MSP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
sleep 2; snap t52-mc-post3 || fail SNAP_MC_POST3
H_13=$(score_whole $T4/t52-mc-post1.ppm $T4/t52-mc-post3.ppm)
if [ $ENTRY_MARKED -eq 0 ] && is_departed $H_13; then mark scentry; ENTRY_MARKED=1; fi
read M3 P3 <<< $(score_band $T4/t52-mc-post3.ppm)
read MM3 MP3 <<< $(score_menu $T4/t52-mc-post3.ppm)
read MS3 MSP3 <<< $(score_sc $T4/t52-mc-post3.ppm)
plog "MC post+3 titleband mean=$M3 p99=$P3 vs-menu mean=$MM3 p99=$MP3 vs-sc mean=$MS3 p99=$MSP3 hops p1-p3=$H_13"
sleep 5; snap t52-mc-post8 || fail SNAP_MC_POST8
H_38=$(score_whole $T4/t52-mc-post3.ppm $T4/t52-mc-post8.ppm)
if [ $ENTRY_MARKED -eq 0 ] && is_departed $H_38; then mark scentry; ENTRY_MARKED=1; fi
read M8 P8 <<< $(score_band $T4/t52-mc-post8.ppm)
read MM8 MP8 <<< $(score_menu $T4/t52-mc-post8.ppm)
read MS8 MSP8 <<< $(score_sc $T4/t52-mc-post8.ppm)
plog "MC post+8 titleband mean=$M8 p99=$P8 vs-menu mean=$MM8 p99=$MP8 vs-sc mean=$MS8 p99=$MSP8 hops p3-p8=$H_38"
sleep 7; snap t52-mc-post15 || fail SNAP_MC_POST15
read M15 P15 <<< $(score_band $T4/t52-mc-post15.ppm)
read MM15 MP15 <<< $(score_menu $T4/t52-mc-post15.ppm)
read MS15 MSP15 <<< $(score_sc $T4/t52-mc-post15.ppm)
plog "MC post+15 titleband mean=$M15 p99=$P15 vs-menu mean=$MM15 p99=$MP15 vs-sc mean=$MS15 p99=$MSP15"
H_815=$(score_whole $T4/t52-mc-post8.ppm $T4/t52-mc-post15.ppm)
plog "MC hops p8-p15=$H_815"
if is_nonmenu $MM15 && is_static $H_38 && is_static $H_815; then
  plog "SC-LIKE -> settle"
else
  fail NO_SC_PARK
fi
[ $ENTRY_MARKED -eq 1 ] || fail NO_SC_ENTRY_MARK
sleep 5
snap t52-scpre || fail SNAP_SCPRE
read SCP SCP_P <<< $(score_sc $T4/t52-scpre.ppm)
plog "SCPRE vs-sc mean=$SCP p99=$SCP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
is_sc $SCP || fail NO_SC_CONFIRM
mark scsettled
gshot sc
sleep 8
snap t52-scfinal || fail SNAP_SCFINAL
read SCF SCF_P <<< $(score_sc $T4/t52-scfinal.ppm)
H_SETTLE=$(score_whole $T4/t52-scpre.ppm $T4/t52-scfinal.ppm)
plog "SCFINAL vs-sc mean=$SCF p99=$SCF_P settle-hop scpre-scfinal=$H_SETTLE"
plog "COUNTS cdread=$(grep -c 'T52_CDREAD' $E || true) marks=$(grep -c 'T52_MARK' $E || true)"
grep "T52_MARK" $E || true
ls -la $T4/t52-*.jpg $T4/t52-shot-*.png $E
kill $(cat $T4/pcsx2-t52.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T52_DONE
