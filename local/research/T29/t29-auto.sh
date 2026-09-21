#!/usr/bin/env bash
# T29 (Cross on Zoe from the Select Character park): reproduce the T28 R1
# chain (fresh boot, NVM skips to attract, Cross attract-skip, detector-
# driven Start ON title, menu-like gate, Cross on Single Event), confirm
# the Select Character park, then press ONE Cross (x Select) on Zoe and
# map what comes next. Bounded: <=3 park attempts, ONE Zoe Cross (plus
# script-captured arrival series + stability). Unattended (~6 min).
# No /mnt/c touches. Wall + uptime stamps.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-t4
E=$D/dat/PCSX2/logs/emulog.txt
REF=$D/t27-ref-title.ppm
REFMENU=$D/t28-ref-menu.ppm
REFSC=$D/t29-ref-sc.ppm
CD=$D/t29-cropdiff.py
LOG=$D/t29-poll.log
# Thresholds (T27/T28 calibration + T29 SC calibration: SC-SC whole
# 0.07-0.30/p99 1-6 PIL, menu-vs-SC 10.11/105, title-vs-SC 11.31/152;
# remote T28 arrival vs-menu 10.19-10.25/p99 105-107):
# TITLE iff band mean<2.0 AND p99<=10; STATIC iff whole mean<1.0;
# MENU iff whole-vs-menu-ref mean<2.0 (remote-lossless gap headroom);
# NONMENU iff whole-vs-menu-ref mean>5.0 (menu side 0.29, arrival 10.19+).
# SC iff whole-vs-SC-ref mean<2.0 (post-hoc bar; the Zoe Cross press does
# NOT depend on it, T28 MENU-gate precedent).
TITLE_MEAN_MAX=2.0
TITLE_P99_MAX=10
STATIC_MEAN_MAX=1.0
MENU_MEAN_MAX=2.0
NONMENU_MEAN_MIN=5.0
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T29_FAIL:$1"; stamp; exit 1; }
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
# score_sc PPM: prints "<mean> <p99>" of whole-frame compare vs REFSC
score_sc() {
  python3 $CD $1 $REFSC 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
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
is_nonmenu() {
  # $1=whole-vs-menu mean -> exit 0 iff non-menu; non-numeric -> not-nonmenu
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$NONMENU_MEAN_MIN 'BEGIN{exit !(m>mm)}'
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
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t29.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $D/dat/PCSX2/logs/emulog-pre-t29-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t29.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t29.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_START
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
plog "REF_CHECK:$(python3 $CD $REF $REF)"
plog "REFMENU_CHECK:$(python3 $CD $REFMENU $REFMENU 0,0,1280,1024)"
plog "REFSC_CHECK:$(python3 $CD $REFSC $REFSC 0,0,1280,1024)"
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
read SELF_SM SELF_SP <<< $(score_sc $REFSC)
plog "SELF_SC mean=$SELF_SM p99=$SELF_SP"
is_menu $SELF_SM || fail SELF_SC
snap t29-start || fail SNAP_START
read SM SP <<< $(score_band $D/t29-start.ppm)
plog "START_SCORE mean=$SM p99=$SP MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
MENU_LIKE=0
for A in 1 2 3; do
  plog "ATTEMPT_$A BEGIN MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_A$A
  snap t29-a$A-now || fail SNAP_A${A}_NOW
  read M P <<< $(score_band $D/t29-a$A-now.ppm)
  plog "ATTEMPT_$A now score mean=$M p99=$P"
  if is_title $M $P; then
    plog "ATTEMPT_$A TITLE-ALREADY-DETECTED (no Cross needed)"
    cp $D/t29-a$A-now.ppm $D/t29-a$A-pre.ppm
    cp $D/t29-a$A-now.jpg $D/t29-a$A-pre.jpg
    press Return "A${A}_START"
    DETECTED=1
  else
    plog "ATTEMPT_$A on attract (non-title) -> Cross attract-skip"
    press K "A${A}_CROSS"
    DETECTED=0
    for N in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18; do
      sleep 2
      snap t29-a$A-poll$N || fail SNAP_A${A}_POLL$N
      read M P <<< $(score_band $D/t29-a$A-poll$N.ppm)
      plog "ATTEMPT_$A poll$N score mean=$M p99=$P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
      if is_title $M $P; then
        plog "ATTEMPT_$A TITLE-DETECTED at poll$N"
        cp $D/t29-a$A-poll$N.ppm $D/t29-a$A-pre.ppm
        cp $D/t29-a$A-poll$N.jpg $D/t29-a$A-pre.jpg
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
  # post-press series with scores (pre-press snap = t29-a$A-pre.*)
  sleep 3; snap t29-a$A-post3 || fail SNAP_A${A}_POST3
  read M3 P3 <<< $(score_band $D/t29-a$A-post3.ppm)
  plog "ATTEMPT_$A post+3 score mean=$M3 p99=$P3 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  sleep 5; snap t29-a$A-post8 || fail SNAP_A${A}_POST8
  read M8 P8 <<< $(score_band $D/t29-a$A-post8.ppm)
  plog "ATTEMPT_$A post+8 score mean=$M8 p99=$P8"
  sleep 7; snap t29-a$A-post15 || fail SNAP_A${A}_POST15
  read M15 P15 <<< $(score_band $D/t29-a$A-post15.ppm)
  plog "ATTEMPT_$A post+15 score mean=$M15 p99=$P15"
  sleep 10; snap t29-a$A-post25 || fail SNAP_A${A}_POST25
  read M25 P25 <<< $(score_band $D/t29-a$A-post25.ppm)
  plog "ATTEMPT_$A post+25 score mean=$M25 p99=$P25"
  # menu-like gate: +8/+15/+25 all non-title AND whole-static across them
  W815=$(score_whole $D/t29-a$A-post8.ppm $D/t29-a$A-post15.ppm)
  W1525=$(score_whole $D/t29-a$A-post15.ppm $D/t29-a$A-post25.ppm)
  plog "ATTEMPT_$A whole815=$W815 whole1525=$W1525"
  read MM25 MP25 <<< $(score_menu $D/t29-a$A-post25.ppm)
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
  # Chain reproduction: Cross on the parked menu (Single Event highlighted
  # per T27 R3); the menu is static with no reclaim, so no dwell pressure.
  sleep 5
  snap t29-menupre || fail SNAP_MENUPRE
  read MMP MMP_P <<< $(score_menu $D/t29-menupre.ppm)
  plog "MENUPRE vs-menu mean=$MMP p99=$MMP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  read MPT MPT_P <<< $(score_band $D/t29-menupre.ppm)
  plog "MENUPRE vs-title mean=$MPT p99=$MPT_P"
  press K "MENU_CROSS"
  # SC-park confirmation series (short: the menu->SC transition is already
  # mapped by T28; the +40 s tail belongs to the Zoe Cross below), each
  # scored vs title-band, menu-ref and SC-ref
  sleep 1; snap t29-mc-post1 || fail SNAP_MC_POST1
  read M1 P1 <<< $(score_band $D/t29-mc-post1.ppm)
  read MM1 MP1 <<< $(score_menu $D/t29-mc-post1.ppm)
  read MS1 MSP1 <<< $(score_sc $D/t29-mc-post1.ppm)
  plog "MC post+1 titleband mean=$M1 p99=$P1 vs-menu mean=$MM1 p99=$MP1 vs-sc mean=$MS1 p99=$MSP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  sleep 2; snap t29-mc-post3 || fail SNAP_MC_POST3
  read M3 P3 <<< $(score_band $D/t29-mc-post3.ppm)
  read MM3 MP3 <<< $(score_menu $D/t29-mc-post3.ppm)
  read MS3 MSP3 <<< $(score_sc $D/t29-mc-post3.ppm)
  plog "MC post+3 titleband mean=$M3 p99=$P3 vs-menu mean=$MM3 p99=$MP3 vs-sc mean=$MS3 p99=$MSP3"
  sleep 5; snap t29-mc-post8 || fail SNAP_MC_POST8
  read M8 P8 <<< $(score_band $D/t29-mc-post8.ppm)
  read MM8 MP8 <<< $(score_menu $D/t29-mc-post8.ppm)
  read MS8 MSP8 <<< $(score_sc $D/t29-mc-post8.ppm)
  plog "MC post+8 titleband mean=$M8 p99=$P8 vs-menu mean=$MM8 p99=$MP8 vs-sc mean=$MS8 p99=$MSP8"
  sleep 7; snap t29-mc-post15 || fail SNAP_MC_POST15
  read M15 P15 <<< $(score_band $D/t29-mc-post15.ppm)
  read MM15 MP15 <<< $(score_menu $D/t29-mc-post15.ppm)
  read MS15 MSP15 <<< $(score_sc $D/t29-mc-post15.ppm)
  plog "MC post+15 titleband mean=$M15 p99=$P15 vs-menu mean=$MM15 p99=$MP15 vs-sc mean=$MS15 p99=$MSP15"
  # per-hop whole-frame diffs across the menu->SC chain
  H_PRE1=$(score_whole $D/t29-menupre.ppm $D/t29-mc-post1.ppm)
  H_13=$(score_whole $D/t29-mc-post1.ppm $D/t29-mc-post3.ppm)
  H_38=$(score_whole $D/t29-mc-post3.ppm $D/t29-mc-post8.ppm)
  H_815=$(score_whole $D/t29-mc-post8.ppm $D/t29-mc-post15.ppm)
  plog "MC hops whole: pre-post1=$H_PRE1 p1-p3=$H_13 p3-p8=$H_38 p8-p15=$H_815"
  # SC-park gate: left the menu (vs-menu>5) + arrival static (last hops);
  # the vs-sc line classifies the park (strict SC bar confirmed post-hoc).
  SC_LIKE=0
  if is_nonmenu $MM15 && is_static $H_38 && is_static $H_815; then
    plog "SC-LIKE (non-menu + static) -> park for Zoe Cross"
    SC_LIKE=1
  else
    plog "NO-SC-PARK (menu->SC chain did not park; no Zoe Cross pressed)"
  fi
  if [ $SC_LIKE -eq 1 ]; then
    # T29 press: ONE Cross (x Select) on the parked Select Character (Zoe
    # selected per T28 R1); arrival static 127 s, no dwell pressure.
    sleep 5
    snap t29-scpre || fail SNAP_SCPRE
    read SCP SCP_P <<< $(score_sc $D/t29-scpre.ppm)
    plog "SCPRE vs-sc mean=$SCP p99=$SCP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
    read SMP SMP_P <<< $(score_menu $D/t29-scpre.ppm)
    plog "SCPRE vs-menu mean=$SMP p99=$SMP_P"
    read SPT SPT_P <<< $(score_band $D/t29-scpre.ppm)
    plog "SCPRE vs-title mean=$SPT p99=$SPT_P"
    press K "ZOE_CROSS"
    # arrival series: fast cadence early (transition hops), slow tail (slow
    # next-screen loads), each scored vs title-band, SC-ref and menu-ref
    sleep 1; snap t29-zc-post1 || fail SNAP_ZC_POST1
    read Z1 ZP1 <<< $(score_band $D/t29-zc-post1.ppm)
    read ZS1 ZSP1 <<< $(score_sc $D/t29-zc-post1.ppm)
    read ZM1 ZMP1 <<< $(score_menu $D/t29-zc-post1.ppm)
    plog "ZC post+1 titleband mean=$Z1 p99=$ZP1 vs-sc mean=$ZS1 p99=$ZSP1 vs-menu mean=$ZM1 p99=$ZMP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
    sleep 2; snap t29-zc-post3 || fail SNAP_ZC_POST3
    read Z3 ZP3 <<< $(score_band $D/t29-zc-post3.ppm)
    read ZS3 ZSP3 <<< $(score_sc $D/t29-zc-post3.ppm)
    read ZM3 ZMP3 <<< $(score_menu $D/t29-zc-post3.ppm)
    plog "ZC post+3 titleband mean=$Z3 p99=$ZP3 vs-sc mean=$ZS3 p99=$ZSP3 vs-menu mean=$ZM3 p99=$ZMP3"
    sleep 5; snap t29-zc-post8 || fail SNAP_ZC_POST8
    read Z8 ZP8 <<< $(score_band $D/t29-zc-post8.ppm)
    read ZS8 ZSP8 <<< $(score_sc $D/t29-zc-post8.ppm)
    read ZM8 ZMP8 <<< $(score_menu $D/t29-zc-post8.ppm)
    plog "ZC post+8 titleband mean=$Z8 p99=$ZP8 vs-sc mean=$ZS8 p99=$ZSP8 vs-menu mean=$ZM8 p99=$ZMP8"
    sleep 7; snap t29-zc-post15 || fail SNAP_ZC_POST15
    read Z15 ZP15 <<< $(score_band $D/t29-zc-post15.ppm)
    read ZS15 ZSP15 <<< $(score_sc $D/t29-zc-post15.ppm)
    read ZM15 ZMP15 <<< $(score_menu $D/t29-zc-post15.ppm)
    plog "ZC post+15 titleband mean=$Z15 p99=$ZP15 vs-sc mean=$ZS15 p99=$ZSP15 vs-menu mean=$ZM15 p99=$ZMP15"
    sleep 10; snap t29-zc-post25 || fail SNAP_ZC_POST25
    read Z25 ZP25 <<< $(score_band $D/t29-zc-post25.ppm)
    read ZS25 ZSP25 <<< $(score_sc $D/t29-zc-post25.ppm)
    read ZM25 ZMP25 <<< $(score_menu $D/t29-zc-post25.ppm)
    plog "ZC post+25 titleband mean=$Z25 p99=$ZP25 vs-sc mean=$ZS25 p99=$ZSP25 vs-menu mean=$ZM25 p99=$ZMP25"
    sleep 15; snap t29-zc-post40 || fail SNAP_ZC_POST40
    read Z40 ZP40 <<< $(score_band $D/t29-zc-post40.ppm)
    read ZS40 ZSP40 <<< $(score_sc $D/t29-zc-post40.ppm)
    read ZM40 ZMP40 <<< $(score_menu $D/t29-zc-post40.ppm)
    plog "ZC post+40 titleband mean=$Z40 p99=$ZP40 vs-sc mean=$ZS40 p99=$ZSP40 vs-menu mean=$ZM40 p99=$ZMP40"
    # per-hop whole-frame diffs across the Zoe transition chain
    ZH_PRE1=$(score_whole $D/t29-scpre.ppm $D/t29-zc-post1.ppm)
    ZH_13=$(score_whole $D/t29-zc-post1.ppm $D/t29-zc-post3.ppm)
    ZH_38=$(score_whole $D/t29-zc-post3.ppm $D/t29-zc-post8.ppm)
    ZH_815=$(score_whole $D/t29-zc-post8.ppm $D/t29-zc-post15.ppm)
    ZH_1525=$(score_whole $D/t29-zc-post15.ppm $D/t29-zc-post25.ppm)
    ZH_2540=$(score_whole $D/t29-zc-post25.ppm $D/t29-zc-post40.ppm)
    plog "ZC hops whole: pre-post1=$ZH_PRE1 p1-p3=$ZH_13 p3-p8=$ZH_38 p8-p15=$ZH_815 p15-p25=$ZH_1525 p25-p40=$ZH_2540"
    # arrival stability: 6 x 10 s
    for N in 1 2 3 4 5 6; do
      sleep 10; snap t29-zc-stab$N || fail SNAP_ZC_STAB$N
      read M P <<< $(score_band $D/t29-zc-stab$N.ppm)
      read MS MSP <<< $(score_sc $D/t29-zc-stab$N.ppm)
      plog "ZC_STAB$N titleband mean=$M p99=$P vs-sc mean=$MS p99=$MSP MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
    done
  fi
else
  plog "NO-PARK (menu-like gate never fired in <=3 attempts; no menu Cross pressed)"
fi
ls -la $D/t29-*.jpg $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T29_DONE
