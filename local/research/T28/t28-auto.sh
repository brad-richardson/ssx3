#!/usr/bin/env bash
# T28 (Single Event Cross from the menu park): reproduce the T27 R3 menu
# park (fresh boot, NVM skips to attract, Cross attract-skip, detector-
# driven Start ON title, menu-like gate), then press Cross with Single
# Event highlighted and map what comes next. Bounded: <=3 park attempts,
# ONE menu Cross (plus script-captured arrival series + stability).
# Unattended (~6 min). No /mnt/c touches. Wall + uptime stamps.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-t4
E=$D/dat/PCSX2/logs/emulog.txt
REF=$D/t27-ref-title.ppm
REFMENU=$D/t28-ref-menu.ppm
CD=$D/t28-cropdiff.py
LOG=$D/t28-poll.log
# Thresholds (T27 calibration + T28 §menu calibration: menu-menu whole
# 0.05-0.08/p99 0-1 PIL, title-vs-menu 14.13/151, attract-vs-menu 18.70/164):
# TITLE iff band mean<2.0 AND p99<=10; STATIC iff whole mean<1.0;
# MENU iff whole-vs-menu-ref mean<2.0 (remote-lossless gap headroom).
TITLE_MEAN_MAX=2.0
TITLE_P99_MAX=10
STATIC_MEAN_MAX=1.0
MENU_MEAN_MAX=2.0
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T28_FAIL:$1"; stamp; exit 1; }
: > $LOG
plog() { echo "$@" | tee -a $LOG; }
# snap NAME: xwd -> ppm + jpg, rm xwd; echoes "SNAP <name> <wall> <uptime>"
snap() {
  local N=$1
  date -u
  xwd -root -out $D/$N.xwd || return 1
  xwdtopnm $D/$N.xwd > $D/$N.ppm || return 1
  rm -f $D/$N.xwd
  pnmtojpeg -quality=80 $D/$N.ppm > $D/$N.jpg || return 1
  ls -la $D/$N.ppm $D/$N.jpg
}
# score_band PPM: prints "<mean> <p99>" from text-band compare vs REF
score_band() {
  python3 $CD $1 $REF | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
# score_whole A B: prints "<mean>" of whole-frame compare
score_whole() {
  python3 $CD $1 $2 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)}}};END{print m}'
}
# score_menu PPM: prints "<mean> <p99>" of whole-frame compare vs REFMENU
score_menu() {
  python3 $CD $1 $REFMENU 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
is_num() {
  # fail-closed numeric check (T27 R1 fix: empty scores misfired as title)
  case "$1" in ''|*[!0-9.]*) return 1;; *) return 0;; esac
}
is_title() {
  # $1=mean $2=p99 -> exit 0 iff title; non-numeric -> not-title
  is_num "$1" && is_num "$2" || return 1
  awk -v m=$1 -v p=$2 -v mm=$TITLE_MEAN_MAX -v pm=$TITLE_P99_MAX \
    'BEGIN{exit !((m<mm)&&(p<=pm))}'
}
is_static() {
  # $1=whole mean -> exit 0 iff static; non-numeric -> not-static
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$STATIC_MEAN_MAX 'BEGIN{exit !(m<mm)}'
}
is_menu() {
  # $1=whole-vs-menu mean -> exit 0 iff menu; non-numeric -> not-menu
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$MENU_MEAN_MAX 'BEGIN{exit !(m<mm)}'
}
press() {
  # $1=keyname $2=label: single 534ms-class hold with stamps
  local KEY=$1; local LAB=$2
  plog "${LAB}_KEYDOWN_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime) MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  xdotool windowfocus --sync $WID || fail FOCUS_$LAB
  xdotool keydown $KEY || fail KEYDOWN_$LAB
  plog "${LAB}_HELD_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
  sleep 0.5
  xdotool keyup $KEY || fail KEYUP_$LAB
  plog "${LAB}_KEYUP_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime) MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
}
stamp
pkill Xvfb || true
sleep 2
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t28.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $D/dat/PCSX2/logs/emulog-pre-t28-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t28.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t28.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_START
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
plog "REF_CHECK:$(python3 $CD $REF $REF)"
plog "REFMENU_CHECK:$(python3 $CD $REFMENU $REFMENU 0,0,1280,1024)"
# end-to-end self-tests through the real scoring paths (T27 G9 lesson)
read SELF_M SELF_P <<< $(score_band $REF)
plog "SELF_TEST mean=$SELF_M p99=$SELF_P"
is_title $SELF_M $SELF_P || fail SELF_TEST
SELF_W=$(score_whole $REF $REF)
plog "SELF_WHOLE=$SELF_W"
is_static $SELF_W || fail SELF_WHOLE
read SELF_MM SELF_MP <<< $(score_menu $REFMENU)
plog "SELF_MENU mean=$SELF_MM p99=$SELF_MP"
is_menu $SELF_MM || fail SELF_MENU
snap t28-start || fail SNAP_START
read SM SP <<< $(score_band $D/t28-start.ppm)
plog "START_SCORE mean=$SM p99=$SP MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
MENU_LIKE=0
for A in 1 2 3; do
  plog "ATTEMPT_$A BEGIN MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_A$A
  snap t28-a$A-now || fail SNAP_A${A}_NOW
  read M P <<< $(score_band $D/t28-a$A-now.ppm)
  plog "ATTEMPT_$A now score mean=$M p99=$P"
  if is_title $M $P; then
    plog "ATTEMPT_$A TITLE-ALREADY-DETECTED (no Cross needed)"
    cp $D/t28-a$A-now.ppm $D/t28-a$A-pre.ppm
    cp $D/t28-a$A-now.jpg $D/t28-a$A-pre.jpg
    press Return "A${A}_START"
    DETECTED=1
  else
    plog "ATTEMPT_$A on attract (non-title) -> Cross attract-skip"
    press K "A${A}_CROSS"
    DETECTED=0
    for N in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18; do
      sleep 2
      snap t28-a$A-poll$N || fail SNAP_A${A}_POLL$N
      read M P <<< $(score_band $D/t28-a$A-poll$N.ppm)
      plog "ATTEMPT_$A poll$N score mean=$M p99=$P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
      if is_title $M $P; then
        plog "ATTEMPT_$A TITLE-DETECTED at poll$N"
        cp $D/t28-a$A-poll$N.ppm $D/t28-a$A-pre.ppm
        cp $D/t28-a$A-poll$N.jpg $D/t28-a$A-pre.jpg
        press Return "A${A}_START"
        DETECTED=1
        break
      fi
    done
    if [ $DETECTED -eq 0 ]; then
      plog "ATTEMPT_$A NO-TITLE-IN-WINDOW (outcome: no-title)"
      continue
    fi
  fi
  # post-press series with scores (pre-press snap = t28-a$A-pre.*)
  sleep 3; snap t28-a$A-post3 || fail SNAP_A${A}_POST3
  read M3 P3 <<< $(score_band $D/t28-a$A-post3.ppm)
  plog "ATTEMPT_$A post+3 score mean=$M3 p99=$P3 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  sleep 5; snap t28-a$A-post8 || fail SNAP_A${A}_POST8
  read M8 P8 <<< $(score_band $D/t28-a$A-post8.ppm)
  plog "ATTEMPT_$A post+8 score mean=$M8 p99=$P8"
  sleep 7; snap t28-a$A-post15 || fail SNAP_A${A}_POST15
  read M15 P15 <<< $(score_band $D/t28-a$A-post15.ppm)
  plog "ATTEMPT_$A post+15 score mean=$M15 p99=$P15"
  sleep 10; snap t28-a$A-post25 || fail SNAP_A${A}_POST25
  read M25 P25 <<< $(score_band $D/t28-a$A-post25.ppm)
  plog "ATTEMPT_$A post+25 score mean=$M25 p99=$P25"
  # menu-like gate: +8/+15/+25 all non-title AND whole-static across them
  W815=$(score_whole $D/t28-a$A-post8.ppm $D/t28-a$A-post15.ppm)
  W1525=$(score_whole $D/t28-a$A-post15.ppm $D/t28-a$A-post25.ppm)
  plog "ATTEMPT_$A whole815=$W815 whole1525=$W1525"
  read MM25 MP25 <<< $(score_menu $D/t28-a$A-post25.ppm)
  plog "ATTEMPT_$A post25-vs-menu mean=$MM25 p99=$MP25"
  if ! is_title $M8 $P8 && ! is_title $M15 $P15 && ! is_title $M25 $P25 \
     && is_static $W815 && is_static $W1525; then
    plog "ATTEMPT_$A MENU-LIKE (non-title + static) -> park for menu Cross"
    MENU_LIKE=1
    break
  fi
  plog "ATTEMPT_$A outcome: no-menu (title/attract cycling continues)"
done
if [ $MENU_LIKE -eq 1 ]; then
  # T28 press: Cross on the parked menu (Single Event highlighted per T27
  # R3); the menu is static with no reclaim in 91 s, so no dwell pressure.
  sleep 5
  snap t28-menupre || fail SNAP_MENUPRE
  read MMP MMP_P <<< $(score_menu $D/t28-menupre.ppm)
  plog "MENUPRE vs-menu mean=$MMP p99=$MMP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  read MPT MPT_P <<< $(score_band $D/t28-menupre.ppm)
  plog "MENUPRE vs-title mean=$MPT p99=$MPT_P"
  press K "MENU_CROSS"
  # arrival series: fast cadence early (transition hops), slow tail (slow
  # submenu loads), each scored vs menu-ref and title-ref
  sleep 1; snap t28-mc-post1 || fail SNAP_MC_POST1
  read M1 P1 <<< $(score_band $D/t28-mc-post1.ppm)
  read MM1 MP1 <<< $(score_menu $D/t28-mc-post1.ppm)
  plog "MC post+1 titleband mean=$M1 p99=$P1 vs-menu mean=$MM1 p99=$MP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  sleep 2; snap t28-mc-post3 || fail SNAP_MC_POST3
  read M3 P3 <<< $(score_band $D/t28-mc-post3.ppm)
  read MM3 MP3 <<< $(score_menu $D/t28-mc-post3.ppm)
  plog "MC post+3 titleband mean=$M3 p99=$P3 vs-menu mean=$MM3 p99=$MP3"
  sleep 5; snap t28-mc-post8 || fail SNAP_MC_POST8
  read M8 P8 <<< $(score_band $D/t28-mc-post8.ppm)
  read MM8 MP8 <<< $(score_menu $D/t28-mc-post8.ppm)
  plog "MC post+8 titleband mean=$M8 p99=$P8 vs-menu mean=$MM8 p99=$MP8"
  sleep 7; snap t28-mc-post15 || fail SNAP_MC_POST15
  read M15 P15 <<< $(score_band $D/t28-mc-post15.ppm)
  read MM15 MP15 <<< $(score_menu $D/t28-mc-post15.ppm)
  plog "MC post+15 titleband mean=$M15 p99=$P15 vs-menu mean=$MM15 p99=$MP15"
  sleep 10; snap t28-mc-post25 || fail SNAP_MC_POST25
  read M25 P25 <<< $(score_band $D/t28-mc-post25.ppm)
  read MM25 MP25 <<< $(score_menu $D/t28-mc-post25.ppm)
  plog "MC post+25 titleband mean=$M25 p99=$P25 vs-menu mean=$MM25 p99=$MP25"
  sleep 15; snap t28-mc-post40 || fail SNAP_MC_POST40
  read M40 P40 <<< $(score_band $D/t28-mc-post40.ppm)
  read MM40 MP40 <<< $(score_menu $D/t28-mc-post40.ppm)
  plog "MC post+40 titleband mean=$M40 p99=$P40 vs-menu mean=$MM40 p99=$MP40"
  # per-hop whole-frame diffs across the transition chain
  H_PRE1=$(score_whole $D/t28-menupre.ppm $D/t28-mc-post1.ppm)
  H_13=$(score_whole $D/t28-mc-post1.ppm $D/t28-mc-post3.ppm)
  H_38=$(score_whole $D/t28-mc-post3.ppm $D/t28-mc-post8.ppm)
  H_815=$(score_whole $D/t28-mc-post8.ppm $D/t28-mc-post15.ppm)
  H_1525=$(score_whole $D/t28-mc-post15.ppm $D/t28-mc-post25.ppm)
  H_2540=$(score_whole $D/t28-mc-post25.ppm $D/t28-mc-post40.ppm)
  plog "MC hops whole: pre-post1=$H_PRE1 p1-p3=$H_13 p3-p8=$H_38 p8-p15=$H_815 p15-p25=$H_1525 p25-p40=$H_2540"
  # arrival stability: 6 x 10 s
  for N in 1 2 3 4 5 6; do
    sleep 10; snap t28-mc-stab$N || fail SNAP_MC_STAB$N
    read M P <<< $(score_band $D/t28-mc-stab$N.ppm)
    read MM MP <<< $(score_menu $D/t28-mc-stab$N.ppm)
    plog "MC_STAB$N titleband mean=$M p99=$P vs-menu mean=$MM p99=$MP MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  done
else
  plog "NO-PARK (menu-like gate never fired in <=3 attempts; no menu Cross pressed)"
fi
ls -la $D/t28-*.jpg $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T28_DONE
