#!/usr/bin/env bash
# T32 (Cross on Race from the Select Mode park): reproduce the T31 R1
# chain (fresh boot, NVM skips to attract, Cross attract-skip,
# detector-driven Start ON title, menu-like gate, Cross on Single Event,
# SC-LIKE gate, Cross on Zoe, ZC-LIKE gate, Cross on Continue, SP-LIKE
# gate, Cross on Peak 1), confirm the Select Mode park (Race highlighted),
# then press ONE Cross (x Select) on Race and map what comes next.
# Bounded: <=3 park attempts, ONE Race Cross (plus script-captured
# arrival series + stability). Unattended (~6 min).
# No /mnt/c touches. Wall + uptime stamps.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-t4
E=$D/dat/PCSX2/logs/emulog.txt
REF=$D/t27-ref-title.ppm
REFMENU=$D/t28-ref-menu.ppm
REFSC=$D/t29-ref-sc.ppm
REFZC=$D/t30-ref-zc.ppm
REFSP=$D/t31-ref-sp.ppm
REFSM=$D/t32-ref-sm.ppm
CD=$D/t32-cropdiff.py
LOG=$D/t32-poll.log
# Thresholds (T27/T28/T29/T30 calibration + T31 SP calibration: SP-SP whole
# 0.0046-0.0832/p99 0 PIL, ZC-vs-SP 9.35-9.38/153, SC-vs-SP 11.35/158-159,
# menu-vs-SP 10.39/170, title-vs-SP 15.37/156, attract-vs-SP 15.70/172;
# remote T30 sp arrival vs-zc 9.37-9.47/p99 153):
# TITLE iff band mean<2.0 AND p99<=10; STATIC iff whole mean<1.0;
# MENU iff whole-vs-menu-ref mean<2.0 (remote-lossless gap headroom);
# NONMENU iff whole-vs-menu-ref mean>5.0 (menu side 0.29, arrival 10.19+).
# SC iff whole-vs-SC-ref mean<2.0 (post-hoc bar; the Zoe Cross press does
# NOT depend on it, T28 MENU-gate precedent).
# NONSC iff whole-vs-SC-ref mean>5.0 (SC side <=0.59 remote, ZC 7.14+).
# DEPARTED iff whole hop mean>5.0 (left the previous screen decisively).
# ZC iff whole-vs-ZC-ref mean<2.0 (post-hoc bar; the Continue Cross press
# does NOT depend on it, T28/T29 precedent).
# NONZC iff whole-vs-ZC-ref mean>5.0 (ZC side <=0.52 remote, SP 9.37+).
# SP iff whole-vs-SP-ref mean<2.0 (post-hoc bar; the Peak Cross press does
# NOT depend on it, T28/T29/T30 precedent).
# NONSP iff whole-vs-SP-ref mean>5.0 (SP side <=0.42 remote, SM 5.37+).
# (T32 SM calibration, PIL whole: SM-SM 0.0356-0.0678/p99 0-1,
# SP-vs-SM 5.21-5.28/121, ZC-vs-SM 10.10-10.13/164, SC-vs-SM 11.81-11.83/157,
# menu-vs-SM 10.92/177, title-vs-SM 16.15/158, attract-vs-SM 14.25/147;
# remote T31 SM arrival vs-sp 5.37-5.38, sppre->pc-post1 hop 5.2452.)
# SM iff whole-vs-SM-ref mean<2.0 (post-hoc bar; the Race Cross press does
# NOT depend on it, T28/T29/T30/T31 precedent).
TITLE_MEAN_MAX=2.0
TITLE_P99_MAX=10
STATIC_MEAN_MAX=1.0
MENU_MEAN_MAX=2.0
NONMENU_MEAN_MIN=5.0
NONSC_MEAN_MIN=5.0
NONZC_MEAN_MIN=5.0
NONSP_MEAN_MIN=5.0
DEPART_MEAN_MIN=5.0
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T32_FAIL:$1"; stamp; exit 1; }
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
# score_zc PPM: prints "<mean> <p99>" of whole-frame compare vs REFZC
score_zc() {
  python3 $CD $1 $REFZC 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
# score_sp PPM: prints "<mean> <p99>" of whole-frame compare vs REFSP
score_sp() {
  python3 $CD $1 $REFSP 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
# score_sm PPM: prints "<mean> <p99>" of whole-frame compare vs REFSM
score_sm() {
  python3 $CD $1 $REFSM 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
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
is_nonsc() {
  # $1=whole-vs-SC mean -> exit 0 iff non-SC; non-numeric -> not-nonsc
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$NONSC_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
is_nonzc() {
  # $1=whole-vs-ZC mean -> exit 0 iff non-ZC; non-numeric -> not-nonzc
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$NONZC_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
is_nonsp() {
  # $1=whole-vs-SP mean -> exit 0 iff non-SP; non-numeric -> not-nonsp
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$NONSP_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
is_departed() {
  # $1=whole hop mean -> exit 0 iff decisively left; non-numeric -> no
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$DEPART_MEAN_MIN 'BEGIN{exit !(m>mm)}'
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
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t32.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $D/dat/PCSX2/logs/emulog-pre-t32-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t32.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t32.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_START
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
plog "REF_CHECK:$(python3 $CD $REF $REF)"
plog "REFMENU_CHECK:$(python3 $CD $REFMENU $REFMENU 0,0,1280,1024)"
plog "REFSC_CHECK:$(python3 $CD $REFSC $REFSC 0,0,1280,1024)"
plog "REFZC_CHECK:$(python3 $CD $REFZC $REFZC 0,0,1280,1024)"
plog "REFSP_CHECK:$(python3 $CD $REFSP $REFSP 0,0,1280,1024)"
plog "REFSM_CHECK:$(python3 $CD $REFSM $REFSM 0,0,1280,1024)"
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
read SELF_ZM SELF_ZP <<< $(score_zc $REFZC)
plog "SELF_ZC mean=$SELF_ZM p99=$SELF_ZP"
is_menu $SELF_ZM || fail SELF_ZC
read SELF_PM SELF_PP <<< $(score_sp $REFSP)
plog "SELF_SP mean=$SELF_PM p99=$SELF_PP"
is_menu $SELF_PM || fail SELF_SP
read SELF_XM SELF_XP <<< $(score_sm $REFSM)
plog "SELF_SM mean=$SELF_XM p99=$SELF_XP"
is_menu $SELF_XM || fail SELF_SM
snap t32-start || fail SNAP_START
read SM SP <<< $(score_band $D/t32-start.ppm)
plog "START_SCORE mean=$SM p99=$SP MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
MENU_LIKE=0
for A in 1 2 3; do
  plog "ATTEMPT_$A BEGIN MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_A$A
  snap t32-a$A-now || fail SNAP_A${A}_NOW
  read M P <<< $(score_band $D/t32-a$A-now.ppm)
  plog "ATTEMPT_$A now score mean=$M p99=$P"
  if is_title $M $P; then
    plog "ATTEMPT_$A TITLE-ALREADY-DETECTED (no Cross needed)"
    cp $D/t32-a$A-now.ppm $D/t32-a$A-pre.ppm
    cp $D/t32-a$A-now.jpg $D/t32-a$A-pre.jpg
    press Return "A${A}_START"
    DETECTED=1
  else
    plog "ATTEMPT_$A on attract (non-title) -> Cross attract-skip"
    press K "A${A}_CROSS"
    DETECTED=0
    for N in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18; do
      sleep 2
      snap t32-a$A-poll$N || fail SNAP_A${A}_POLL$N
      read M P <<< $(score_band $D/t32-a$A-poll$N.ppm)
      plog "ATTEMPT_$A poll$N score mean=$M p99=$P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
      if is_title $M $P; then
        plog "ATTEMPT_$A TITLE-DETECTED at poll$N"
        cp $D/t32-a$A-poll$N.ppm $D/t32-a$A-pre.ppm
        cp $D/t32-a$A-poll$N.jpg $D/t32-a$A-pre.jpg
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
  # post-press series with scores (pre-press snap = t32-a$A-pre.*)
  sleep 3; snap t32-a$A-post3 || fail SNAP_A${A}_POST3
  read M3 P3 <<< $(score_band $D/t32-a$A-post3.ppm)
  plog "ATTEMPT_$A post+3 score mean=$M3 p99=$P3 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  sleep 5; snap t32-a$A-post8 || fail SNAP_A${A}_POST8
  read M8 P8 <<< $(score_band $D/t32-a$A-post8.ppm)
  plog "ATTEMPT_$A post+8 score mean=$M8 p99=$P8"
  sleep 7; snap t32-a$A-post15 || fail SNAP_A${A}_POST15
  read M15 P15 <<< $(score_band $D/t32-a$A-post15.ppm)
  plog "ATTEMPT_$A post+15 score mean=$M15 p99=$P15"
  sleep 10; snap t32-a$A-post25 || fail SNAP_A${A}_POST25
  read M25 P25 <<< $(score_band $D/t32-a$A-post25.ppm)
  plog "ATTEMPT_$A post+25 score mean=$M25 p99=$P25"
  # menu-like gate: +8/+15/+25 all non-title AND whole-static across them
  W815=$(score_whole $D/t32-a$A-post8.ppm $D/t32-a$A-post15.ppm)
  W1525=$(score_whole $D/t32-a$A-post15.ppm $D/t32-a$A-post25.ppm)
  plog "ATTEMPT_$A whole815=$W815 whole1525=$W1525"
  read MM25 MP25 <<< $(score_menu $D/t32-a$A-post25.ppm)
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
  snap t32-menupre || fail SNAP_MENUPRE
  read MMP MMP_P <<< $(score_menu $D/t32-menupre.ppm)
  plog "MENUPRE vs-menu mean=$MMP p99=$MMP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  read MPT MPT_P <<< $(score_band $D/t32-menupre.ppm)
  plog "MENUPRE vs-title mean=$MPT p99=$MPT_P"
  press K "MENU_CROSS"
  # SC-park confirmation series (short: the menu->SC transition is already
  # mapped by T28; the +40 s tail belongs to the Continue Cross below),
  # each scored vs title-band, menu-ref and SC-ref
  sleep 1; snap t32-mc-post1 || fail SNAP_MC_POST1
  read M1 P1 <<< $(score_band $D/t32-mc-post1.ppm)
  read MM1 MP1 <<< $(score_menu $D/t32-mc-post1.ppm)
  read MS1 MSP1 <<< $(score_sc $D/t32-mc-post1.ppm)
  plog "MC post+1 titleband mean=$M1 p99=$P1 vs-menu mean=$MM1 p99=$MP1 vs-sc mean=$MS1 p99=$MSP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  sleep 2; snap t32-mc-post3 || fail SNAP_MC_POST3
  read M3 P3 <<< $(score_band $D/t32-mc-post3.ppm)
  read MM3 MP3 <<< $(score_menu $D/t32-mc-post3.ppm)
  read MS3 MSP3 <<< $(score_sc $D/t32-mc-post3.ppm)
  plog "MC post+3 titleband mean=$M3 p99=$P3 vs-menu mean=$MM3 p99=$MP3 vs-sc mean=$MS3 p99=$MSP3"
  sleep 5; snap t32-mc-post8 || fail SNAP_MC_POST8
  read M8 P8 <<< $(score_band $D/t32-mc-post8.ppm)
  read MM8 MP8 <<< $(score_menu $D/t32-mc-post8.ppm)
  read MS8 MSP8 <<< $(score_sc $D/t32-mc-post8.ppm)
  plog "MC post+8 titleband mean=$M8 p99=$P8 vs-menu mean=$MM8 p99=$MP8 vs-sc mean=$MS8 p99=$MSP8"
  sleep 7; snap t32-mc-post15 || fail SNAP_MC_POST15
  read M15 P15 <<< $(score_band $D/t32-mc-post15.ppm)
  read MM15 MP15 <<< $(score_menu $D/t32-mc-post15.ppm)
  read MS15 MSP15 <<< $(score_sc $D/t32-mc-post15.ppm)
  plog "MC post+15 titleband mean=$M15 p99=$P15 vs-menu mean=$MM15 p99=$MP15 vs-sc mean=$MS15 p99=$MSP15"
  # per-hop whole-frame diffs across the menu->SC chain
  H_PRE1=$(score_whole $D/t32-menupre.ppm $D/t32-mc-post1.ppm)
  H_13=$(score_whole $D/t32-mc-post1.ppm $D/t32-mc-post3.ppm)
  H_38=$(score_whole $D/t32-mc-post3.ppm $D/t32-mc-post8.ppm)
  H_815=$(score_whole $D/t32-mc-post8.ppm $D/t32-mc-post15.ppm)
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
    # Chain reproduction: ONE Cross (x Select) on the parked Select
    # Character (Zoe selected per T28/T29 R1); arrival static 132 s, no
    # dwell pressure.
    sleep 5
    snap t32-scpre || fail SNAP_SCPRE
    read SCP SCP_P <<< $(score_sc $D/t32-scpre.ppm)
    plog "SCPRE vs-sc mean=$SCP p99=$SCP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
    read SMP SMP_P <<< $(score_menu $D/t32-scpre.ppm)
    plog "SCPRE vs-menu mean=$SMP p99=$SMP_P"
    read SPT SPT_P <<< $(score_band $D/t32-scpre.ppm)
    plog "SCPRE vs-title mean=$SPT p99=$SPT_P"
    press K "ZOE_CROSS"
    # ZC-park confirmation series (short: the SC->ZC transition is already
    # mapped by T29; the +40 s tail belongs to the Continue Cross below),
    # each scored vs title-band, SC-ref and ZC-ref (vs-menu post-hoc local)
    sleep 1; snap t32-zc-post1 || fail SNAP_ZC_POST1
    read Z1 ZP1 <<< $(score_band $D/t32-zc-post1.ppm)
    read ZS1 ZSP1 <<< $(score_sc $D/t32-zc-post1.ppm)
    read ZZ1 ZZP1 <<< $(score_zc $D/t32-zc-post1.ppm)
    plog "ZC post+1 titleband mean=$Z1 p99=$ZP1 vs-sc mean=$ZS1 p99=$ZSP1 vs-zc mean=$ZZ1 p99=$ZZP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
    sleep 2; snap t32-zc-post3 || fail SNAP_ZC_POST3
    read Z3 ZP3 <<< $(score_band $D/t32-zc-post3.ppm)
    read ZS3 ZSP3 <<< $(score_sc $D/t32-zc-post3.ppm)
    read ZZ3 ZZP3 <<< $(score_zc $D/t32-zc-post3.ppm)
    plog "ZC post+3 titleband mean=$Z3 p99=$ZP3 vs-sc mean=$ZS3 p99=$ZSP3 vs-zc mean=$ZZ3 p99=$ZZP3"
    sleep 5; snap t32-zc-post8 || fail SNAP_ZC_POST8
    read Z8 ZP8 <<< $(score_band $D/t32-zc-post8.ppm)
    read ZS8 ZSP8 <<< $(score_sc $D/t32-zc-post8.ppm)
    read ZZ8 ZZP8 <<< $(score_zc $D/t32-zc-post8.ppm)
    plog "ZC post+8 titleband mean=$Z8 p99=$ZP8 vs-sc mean=$ZS8 p99=$ZSP8 vs-zc mean=$ZZ8 p99=$ZZP8"
    # per-hop whole-frame diffs across the SC->ZC chain
    ZH_PRE1=$(score_whole $D/t32-scpre.ppm $D/t32-zc-post1.ppm)
    ZH_13=$(score_whole $D/t32-zc-post1.ppm $D/t32-zc-post3.ppm)
    ZH_38=$(score_whole $D/t32-zc-post3.ppm $D/t32-zc-post8.ppm)
    plog "ZC hops whole: pre-post1=$ZH_PRE1 p1-p3=$ZH_13 p3-p8=$ZH_38"
    # ZC-park gate: decisively left SC (departure hop) + non-SC + arrival
    # static; the vs-zc line classifies the park (strict ZC bar confirmed
    # post-hoc).
    ZC_LIKE=0
    if is_departed $ZH_PRE1 && is_nonsc $ZS8 && is_static $ZH_13 && is_static $ZH_38; then
      plog "ZC-LIKE (departed + non-SC + static) -> park for Continue Cross"
      ZC_LIKE=1
    else
      plog "NO-ZC-PARK (SC->ZC chain did not park; no Continue Cross pressed)"
    fi
    if [ $ZC_LIKE -eq 1 ]; then
      # Chain reproduction: ONE Cross (x Select) on the parked Setup
      # Character (Zoe + Continue highlighted per T29/T30 R1); arrival
      # static 131 s, no dwell pressure.
      sleep 5
      snap t32-ccpre || fail SNAP_CCPRE
      read CZP CZP_P <<< $(score_zc $D/t32-ccpre.ppm)
      plog "CCPRE vs-zc mean=$CZP p99=$CZP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
      read CSP CSP_P <<< $(score_sc $D/t32-ccpre.ppm)
      plog "CCPRE vs-sc mean=$CSP p99=$CSP_P"
      read CPT CPT_P <<< $(score_band $D/t32-ccpre.ppm)
      plog "CCPRE vs-title mean=$CPT p99=$CPT_P"
      press K "CONT_CROSS"
      # SP-park confirmation series (short: the ZC->SP transition is already
      # mapped by T30; the +40 s tail belongs to the Peak Cross below),
      # each scored vs title-band, ZC-ref and SP-ref (vs-sc/vs-menu
      # post-hoc local)
      sleep 1; snap t32-sp-post1 || fail SNAP_SP_POST1
      read S1 SP1 <<< $(score_band $D/t32-sp-post1.ppm)
      read SZ1 SZP1 <<< $(score_zc $D/t32-sp-post1.ppm)
      read SS1 SSP1 <<< $(score_sp $D/t32-sp-post1.ppm)
      plog "SP post+1 titleband mean=$S1 p99=$SP1 vs-zc mean=$SZ1 p99=$SZP1 vs-sp mean=$SS1 p99=$SSP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
      sleep 2; snap t32-sp-post3 || fail SNAP_SP_POST3
      read S3 SP3 <<< $(score_band $D/t32-sp-post3.ppm)
      read SZ3 SZP3 <<< $(score_zc $D/t32-sp-post3.ppm)
      read SS3 SSP3 <<< $(score_sp $D/t32-sp-post3.ppm)
      plog "SP post+3 titleband mean=$S3 p99=$SP3 vs-zc mean=$SZ3 p99=$SZP3 vs-sp mean=$SS3 p99=$SSP3"
      sleep 5; snap t32-sp-post8 || fail SNAP_SP_POST8
      read S8 SP8 <<< $(score_band $D/t32-sp-post8.ppm)
      read SZ8 SZP8 <<< $(score_zc $D/t32-sp-post8.ppm)
      read SS8 SSP8 <<< $(score_sp $D/t32-sp-post8.ppm)
      plog "SP post+8 titleband mean=$S8 p99=$SP8 vs-zc mean=$SZ8 p99=$SZP8 vs-sp mean=$SS8 p99=$SSP8"
      # per-hop whole-frame diffs across the ZC->SP chain
      SPH_PRE1=$(score_whole $D/t32-ccpre.ppm $D/t32-sp-post1.ppm)
      SPH_13=$(score_whole $D/t32-sp-post1.ppm $D/t32-sp-post3.ppm)
      SPH_38=$(score_whole $D/t32-sp-post3.ppm $D/t32-sp-post8.ppm)
      plog "SP hops whole: pre-post1=$SPH_PRE1 p1-p3=$SPH_13 p3-p8=$SPH_38"
      # SP-park gate: decisively left ZC (departure hop) + non-ZC + arrival
      # static; the vs-sp line classifies the park (strict SP bar confirmed
      # post-hoc).
      SP_LIKE=0
      if is_departed $SPH_PRE1 && is_nonzc $SZ8 && is_static $SPH_13 && is_static $SPH_38; then
        plog "SP-LIKE (departed + non-ZC + static) -> park for Peak Cross"
        SP_LIKE=1
      else
        plog "NO-SP-PARK (ZC->SP chain did not park; no Peak Cross pressed)"
      fi
      if [ $SP_LIKE -eq 1 ]; then
        # Chain reproduction: ONE Cross (x Select) on the parked Select
        # Peak (Peak 1 highlighted per T31 R1); arrival static 132 s, no
        # dwell pressure.
        sleep 5
        snap t32-sppre || fail SNAP_SPPRE
        read SPP SPP_P <<< $(score_sp $D/t32-sppre.ppm)
        plog "SPPRE vs-sp mean=$SPP p99=$SPP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
        read SPZ SPZ_P <<< $(score_zc $D/t32-sppre.ppm)
        plog "SPPRE vs-zc mean=$SPZ p99=$SPZ_P"
        read SPT SPT_P <<< $(score_band $D/t32-sppre.ppm)
        plog "SPPRE vs-title mean=$SPT p99=$SPT_P"
        press K "PEAK_CROSS"
        # SM-park confirmation series (short: the SP->SM transition is already
        # mapped by T31; the +40 s tail belongs to the Race Cross below),
        # each scored vs title-band, SP-ref and SM-ref (vs-zc/vs-sc/vs-menu
        # post-hoc local)
        sleep 1; snap t32-pc-post1 || fail SNAP_PC_POST1
        read P1 PP1 <<< $(score_band $D/t32-pc-post1.ppm)
        read PS1 PSP1 <<< $(score_sp $D/t32-pc-post1.ppm)
        read PX1 PXP1 <<< $(score_sm $D/t32-pc-post1.ppm)
        plog "PC post+1 titleband mean=$P1 p99=$PP1 vs-sp mean=$PS1 p99=$PSP1 vs-sm mean=$PX1 p99=$PXP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
        sleep 2; snap t32-pc-post3 || fail SNAP_PC_POST3
        read P3 PP3 <<< $(score_band $D/t32-pc-post3.ppm)
        read PS3 PSP3 <<< $(score_sp $D/t32-pc-post3.ppm)
        read PX3 PXP3 <<< $(score_sm $D/t32-pc-post3.ppm)
        plog "PC post+3 titleband mean=$P3 p99=$PP3 vs-sp mean=$PS3 p99=$PSP3 vs-sm mean=$PX3 p99=$PXP3"
        sleep 5; snap t32-pc-post8 || fail SNAP_PC_POST8
        read P8 PP8 <<< $(score_band $D/t32-pc-post8.ppm)
        read PS8 PSP8 <<< $(score_sp $D/t32-pc-post8.ppm)
        read PX8 PXP8 <<< $(score_sm $D/t32-pc-post8.ppm)
        plog "PC post+8 titleband mean=$P8 p99=$PP8 vs-sp mean=$PS8 p99=$PSP8 vs-sm mean=$PX8 p99=$PXP8"
        # per-hop whole-frame diffs across the SP->SM chain
        PCH_PRE1=$(score_whole $D/t32-sppre.ppm $D/t32-pc-post1.ppm)
        PCH_13=$(score_whole $D/t32-pc-post1.ppm $D/t32-pc-post3.ppm)
        PCH_38=$(score_whole $D/t32-pc-post3.ppm $D/t32-pc-post8.ppm)
        plog "PC hops whole: pre-post1=$PCH_PRE1 p1-p3=$PCH_13 p3-p8=$PCH_38"
        # SM-park gate: decisively left SP (departure hop) + non-SP + arrival
        # static; the vs-sm line classifies the park (strict SM bar confirmed
        # post-hoc).
        SM_LIKE=0
        if is_departed $PCH_PRE1 && is_nonsp $PS8 && is_static $PCH_13 && is_static $PCH_38; then
          plog "SM-LIKE (departed + non-SP + static) -> park for Race Cross"
          SM_LIKE=1
        else
          plog "NO-SM-PARK (SP->SM chain did not park; no Race Cross pressed)"
        fi
        if [ $SM_LIKE -eq 1 ]; then
          # T32 press: ONE Cross (x Select) on the parked Select Mode
          # (Race highlighted per T31 R1); arrival static 132 s, no
          # dwell pressure.
          sleep 5
          snap t32-smpre || fail SNAP_SMPRE
          read SXP SXP_P <<< $(score_sm $D/t32-smpre.ppm)
          plog "SMPRE vs-sm mean=$SXP p99=$SXP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
          read SXSP SXSP_P <<< $(score_sp $D/t32-smpre.ppm)
          plog "SMPRE vs-sp mean=$SXSP p99=$SXSP_P"
          read SXPT SXPT_P <<< $(score_band $D/t32-smpre.ppm)
          plog "SMPRE vs-title mean=$SXPT p99=$SXPT_P"
          press K "RACE_CROSS"
          # arrival series: fast cadence early (transition hops), slow tail
          # (slow next-screen loads), each scored vs title-band, SM-ref and
          # SP-ref (vs-zc/vs-sc/vs-menu post-hoc local)
          sleep 1; snap t32-rc-post1 || fail SNAP_RC_POST1
          read R1 RP1 <<< $(score_band $D/t32-rc-post1.ppm)
          read RX1 RXP1 <<< $(score_sm $D/t32-rc-post1.ppm)
          read RS1 RSP1 <<< $(score_sp $D/t32-rc-post1.ppm)
          plog "RC post+1 titleband mean=$R1 p99=$RP1 vs-sm mean=$RX1 p99=$RXP1 vs-sp mean=$RS1 p99=$RSP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
          sleep 2; snap t32-rc-post3 || fail SNAP_RC_POST3
          read R3 RP3 <<< $(score_band $D/t32-rc-post3.ppm)
          read RX3 RXP3 <<< $(score_sm $D/t32-rc-post3.ppm)
          read RS3 RSP3 <<< $(score_sp $D/t32-rc-post3.ppm)
          plog "RC post+3 titleband mean=$R3 p99=$RP3 vs-sm mean=$RX3 p99=$RXP3 vs-sp mean=$RS3 p99=$RSP3"
          sleep 5; snap t32-rc-post8 || fail SNAP_RC_POST8
          read R8 RP8 <<< $(score_band $D/t32-rc-post8.ppm)
          read RX8 RXP8 <<< $(score_sm $D/t32-rc-post8.ppm)
          read RS8 RSP8 <<< $(score_sp $D/t32-rc-post8.ppm)
          plog "RC post+8 titleband mean=$R8 p99=$RP8 vs-sm mean=$RX8 p99=$RXP8 vs-sp mean=$RS8 p99=$RSP8"
          sleep 7; snap t32-rc-post15 || fail SNAP_RC_POST15
          read R15 RP15 <<< $(score_band $D/t32-rc-post15.ppm)
          read RX15 RXP15 <<< $(score_sm $D/t32-rc-post15.ppm)
          read RS15 RSP15 <<< $(score_sp $D/t32-rc-post15.ppm)
          plog "RC post+15 titleband mean=$R15 p99=$RP15 vs-sm mean=$RX15 p99=$RXP15 vs-sp mean=$RS15 p99=$RSP15"
          sleep 10; snap t32-rc-post25 || fail SNAP_RC_POST25
          read R25 RP25 <<< $(score_band $D/t32-rc-post25.ppm)
          read RX25 RXP25 <<< $(score_sm $D/t32-rc-post25.ppm)
          read RS25 RSP25 <<< $(score_sp $D/t32-rc-post25.ppm)
          plog "RC post+25 titleband mean=$R25 p99=$RP25 vs-sm mean=$RX25 p99=$RXP25 vs-sp mean=$RS25 p99=$RSP25"
          sleep 15; snap t32-rc-post40 || fail SNAP_RC_POST40
          read R40 RP40 <<< $(score_band $D/t32-rc-post40.ppm)
          read RX40 RXP40 <<< $(score_sm $D/t32-rc-post40.ppm)
          read RS40 RSP40 <<< $(score_sp $D/t32-rc-post40.ppm)
          plog "RC post+40 titleband mean=$R40 p99=$RP40 vs-sm mean=$RX40 p99=$RXP40 vs-sp mean=$RS40 p99=$RSP40"
          # per-hop whole-frame diffs across the Race transition chain
          RCH_PRE1=$(score_whole $D/t32-smpre.ppm $D/t32-rc-post1.ppm)
          RCH_13=$(score_whole $D/t32-rc-post1.ppm $D/t32-rc-post3.ppm)
          RCH_38=$(score_whole $D/t32-rc-post3.ppm $D/t32-rc-post8.ppm)
          RCH_815=$(score_whole $D/t32-rc-post8.ppm $D/t32-rc-post15.ppm)
          RCH_1525=$(score_whole $D/t32-rc-post15.ppm $D/t32-rc-post25.ppm)
          RCH_2540=$(score_whole $D/t32-rc-post25.ppm $D/t32-rc-post40.ppm)
          plog "RC hops whole: pre-post1=$RCH_PRE1 p1-p3=$RCH_13 p3-p8=$RCH_38 p8-p15=$RCH_815 p15-p25=$RCH_1525 p25-p40=$RCH_2540"
          # arrival stability: 6 x 10 s
          for N in 1 2 3 4 5 6; do
            sleep 10; snap t32-rc-stab$N || fail SNAP_RC_STAB$N
            read M P <<< $(score_band $D/t32-rc-stab$N.ppm)
            read MS MSP <<< $(score_sm $D/t32-rc-stab$N.ppm)
            plog "RC_STAB$N titleband mean=$M p99=$P vs-sm mean=$MS p99=$MSP MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
          done
        fi
      fi
    fi
  fi
else
  plog "NO-PARK (menu-like gate never fired in <=3 attempts; no menu Cross pressed)"
fi
ls -la $D/t32-*.jpg $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T32_DONE
