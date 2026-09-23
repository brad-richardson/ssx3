#!/usr/bin/env bash
# T47 Mission 1: front-end reference captures (title, menu, SC, ZC, SP, SM,
# SE-default, SE Happiness/Rival walk) + F8 native-res shots + F9 SW toggle.
# Shape: t44-auto.sh (sha a3acb2d6) front-end legs verbatim (same gates,
# same sleeps, same refs); outputs t47-* (no t44-* overwrite). One input
# class beyond t44: Down/Right/Left menu-walk on SE + F8/F9 GS keys.
# Bounded: ~7 min wall. Unattended.
# SW_FIRST=1: press F9 right after WID detect (whole run SW-rendered).
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
REFSE=$D/t33-ref-se.ppm
REFMR=$D/t34-ref-mr.ppm
REFPP=$D/t35-ref-panel.ppm
CD=$D/t44-cropdiff.py
LOG=$D/t47-poll.log
SNAPS=$D/dat/PCSX2/snaps
TITLE_MEAN_MAX=2.0
TITLE_P99_MAX=10
STATIC_MEAN_MAX=1.0
MENU_MEAN_MAX=2.0
NONMENU_MEAN_MIN=5.0
NONSC_MEAN_MIN=5.0
NONZC_MEAN_MIN=5.0
NONSP_MEAN_MIN=5.0
NONSE_MEAN_MIN=5.0
NONMR_MEAN_MIN=5.0
NONPP_MEAN_MIN=5.0
DEPART_MEAN_MIN=5.0
SETAG_MEAN_MAX=5.0
SETAG_BOX=40,415,330,450
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T47_FAIL:$1"; stamp; exit 1; }
: > $LOG
plog() { echo "$@" | tee -a $LOG; }
snap() {
  local N=$1
  date -u
  xwd -root -out $D/$N.xwd || return 1
  xwdtopnm $D/$N.xwd > $D/$N.ppm || return 1
  rm -f $D/$N.xwd
  pnmtojpeg -quality=80 $D/$N.ppm > $D/$N.jpg || return 1
  ls -la $D/$N.ppm $D/$N.jpg
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
score_zc() {
  python3 $CD $1 $REFZC 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
score_sp() {
  python3 $CD $1 $REFSP 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
score_sm() {
  python3 $CD $1 $REFSM 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
score_se() {
  python3 $CD $1 $REFSE 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
score_setag() {
  python3 $CD $1 $REFSE $SETAG_BOX | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
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
is_nonzc() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$NONZC_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
is_nonsp() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$NONSP_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
is_departed() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$DEPART_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
is_setag() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$SETAG_MEAN_MAX 'BEGIN{exit !(m<mm)}'
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
  # $1=label: PCSX2 F8 native-res screenshot; adopts newest snaps/ file
  local LAB=$1
  ls -lat $SNAPS | head -n 5
  press F8 "GSHOT_$LAB"
  sleep 2
  local NEW=$(ls -t $SNAPS | head -n 1)
  plog "GSHOT_$LAB newest=$NEW"
  cp "$SNAPS/$NEW" $D/t47-shot-$LAB.png || fail GSHOT_CP_$LAB
  ls -la $D/t47-shot-$LAB.png
}
stamp
pkill Xvfb || true
sleep 2
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t47.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
ls -lat $SNAPS | head -n 5
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $D/dat/PCSX2/logs/emulog-pre-t47-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t47.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t47.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_START
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
if [ "${SW_FIRST:-0}" = "1" ]; then
  plog "SW_FIRST: F9 toggle before attract-skip"
  press F9 "SW_FIRST_TOGGLE"
  sleep 5
  snap t47-swcheck || fail SNAP_SWCHECK
fi
plog "REF_CHECK:$(python3 $CD $REF $REF)"
plog "REFMENU_CHECK:$(python3 $CD $REFMENU $REFMENU 0,0,1280,1024)"
plog "REFSC_CHECK:$(python3 $CD $REFSC $REFSC 0,0,1280,1024)"
plog "REFZC_CHECK:$(python3 $CD $REFZC $REFZC 0,0,1280,1024)"
plog "REFSP_CHECK:$(python3 $CD $REFSP $REFSP 0,0,1280,1024)"
plog "REFSM_CHECK:$(python3 $CD $REFSM $REFSM 0,0,1280,1024)"
plog "REFSE_CHECK:$(python3 $CD $REFSE $REFSE 0,0,1280,1024)"
plog "REFSETAG_CHECK:$(python3 $CD $REFSE $REFSE $SETAG_BOX)"
snap t47-start || fail SNAP_START
read SM SP <<< $(score_band $D/t47-start.ppm)
plog "START_SCORE mean=$SM p99=$SP MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
# Attract-skip: ONE Cross then title poll (t44 attempt-1 shape, no re-attempts:
# front-end reference run, fail fast and loud)
press K "A1_CROSS"
DETECTED=0
for N in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18; do
  sleep 2
  snap t47-a1-poll$N || fail SNAP_A1_POLL$N
  read M P <<< $(score_band $D/t47-a1-poll$N.ppm)
  plog "A1 poll$N score mean=$M p99=$P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  if is_title $M $P; then
    plog "A1 TITLE-DETECTED at poll$N"
    cp $D/t47-a1-poll$N.ppm $D/t47-title.ppm
    cp $D/t47-a1-poll$N.jpg $D/t47-title.jpg
    DETECTED=1
    break
  fi
done
[ $DETECTED -eq 1 ] || fail NO_TITLE
gshot title
press Return "TITLE_START"
sleep 3; snap t47-post3 || fail SNAP_POST3
read M3 P3 <<< $(score_band $D/t47-post3.ppm)
plog "post+3 titleband mean=$M3 p99=$P3 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
sleep 5; snap t47-post8 || fail SNAP_POST8
read M8 P8 <<< $(score_band $D/t47-post8.ppm)
plog "post+8 titleband mean=$M8 p99=$P8"
sleep 7; snap t47-post15 || fail SNAP_POST15
read M15 P15 <<< $(score_band $D/t47-post15.ppm)
plog "post+15 titleband mean=$M15 p99=$P15"
sleep 10; snap t47-post25 || fail SNAP_POST25
read M25 P25 <<< $(score_band $D/t47-post25.ppm)
plog "post+25 titleband mean=$M25 p99=$P25"
W815=$(score_whole $D/t47-post8.ppm $D/t47-post15.ppm)
W1525=$(score_whole $D/t47-post15.ppm $D/t47-post25.ppm)
plog "whole815=$W815 whole1525=$W1525"
read MM25 MP25 <<< $(score_menu $D/t47-post25.ppm)
plog "post25-vs-menu mean=$MM25 p99=$MP25"
if ! is_title $M8 $P8 && ! is_title $M15 $P15 && ! is_title $M25 $P25 \
   && is_static $W815 && is_static $W1525; then
  plog "MENU-LIKE -> menu Cross"
else
  fail NO_MENU_PARK
fi
sleep 5
snap t47-menupre || fail SNAP_MENUPRE
read MMP MMP_P <<< $(score_menu $D/t47-menupre.ppm)
plog "MENUPRE vs-menu mean=$MMP p99=$MMP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
gshot menu
press K "MENU_CROSS"
sleep 1; snap t47-mc-post1 || fail SNAP_MC_POST1
read M1 P1 <<< $(score_band $D/t47-mc-post1.ppm)
read MM1 MP1 <<< $(score_menu $D/t47-mc-post1.ppm)
read MS1 MSP1 <<< $(score_sc $D/t47-mc-post1.ppm)
plog "MC post+1 titleband mean=$M1 p99=$P1 vs-menu mean=$MM1 p99=$MP1 vs-sc mean=$MS1 p99=$MSP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
sleep 2; snap t47-mc-post3 || fail SNAP_MC_POST3
read M3 P3 <<< $(score_band $D/t47-mc-post3.ppm)
read MM3 MP3 <<< $(score_menu $D/t47-mc-post3.ppm)
read MS3 MSP3 <<< $(score_sc $D/t47-mc-post3.ppm)
plog "MC post+3 titleband mean=$M3 p99=$P3 vs-menu mean=$MM3 p99=$MP3 vs-sc mean=$MS3 p99=$MSP3"
sleep 5; snap t47-mc-post8 || fail SNAP_MC_POST8
read M8 P8 <<< $(score_band $D/t47-mc-post8.ppm)
read MM8 MP8 <<< $(score_menu $D/t47-mc-post8.ppm)
read MS8 MSP8 <<< $(score_sc $D/t47-mc-post8.ppm)
plog "MC post+8 titleband mean=$M8 p99=$P8 vs-menu mean=$MM8 p99=$MP8 vs-sc mean=$MS8 p99=$MSP8"
sleep 7; snap t47-mc-post15 || fail SNAP_MC_POST15
read M15 P15 <<< $(score_band $D/t47-mc-post15.ppm)
read MM15 MP15 <<< $(score_menu $D/t47-mc-post15.ppm)
read MS15 MSP15 <<< $(score_sc $D/t47-mc-post15.ppm)
plog "MC post+15 titleband mean=$M15 p99=$P15 vs-menu mean=$MM15 p99=$MP15 vs-sc mean=$MS15 p99=$MSP15"
H_PRE1=$(score_whole $D/t47-menupre.ppm $D/t47-mc-post1.ppm)
H_13=$(score_whole $D/t47-mc-post1.ppm $D/t47-mc-post3.ppm)
H_38=$(score_whole $D/t47-mc-post3.ppm $D/t47-mc-post8.ppm)
H_815=$(score_whole $D/t47-mc-post8.ppm $D/t47-mc-post15.ppm)
plog "MC hops whole: pre-post1=$H_PRE1 p1-p3=$H_13 p3-p8=$H_38 p8-p15=$H_815"
if is_nonmenu $MM15 && is_static $H_38 && is_static $H_815; then
  plog "SC-LIKE -> Zoe Cross"
else
  fail NO_SC_PARK
fi
sleep 5
snap t47-scpre || fail SNAP_SCPRE
read SCP SCP_P <<< $(score_sc $D/t47-scpre.ppm)
plog "SCPRE vs-sc mean=$SCP p99=$SCP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
gshot sc
press K "ZOE_CROSS"
sleep 1; snap t47-zc-post1 || fail SNAP_ZC_POST1
read Z1 ZP1 <<< $(score_band $D/t47-zc-post1.ppm)
read ZS1 ZSP1 <<< $(score_sc $D/t47-zc-post1.ppm)
read ZZ1 ZZP1 <<< $(score_zc $D/t47-zc-post1.ppm)
plog "ZC post+1 titleband mean=$Z1 p99=$ZP1 vs-sc mean=$ZS1 p99=$ZSP1 vs-zc mean=$ZZ1 p99=$ZZP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
sleep 2; snap t47-zc-post3 || fail SNAP_ZC_POST3
read Z3 ZP3 <<< $(score_band $D/t47-zc-post3.ppm)
read ZS3 ZSP3 <<< $(score_sc $D/t47-zc-post3.ppm)
read ZZ3 ZZP3 <<< $(score_zc $D/t47-zc-post3.ppm)
plog "ZC post+3 titleband mean=$Z3 p99=$ZP3 vs-sc mean=$ZS3 p99=$ZSP3 vs-zc mean=$ZZ3 p99=$ZZP3"
sleep 5; snap t47-zc-post8 || fail SNAP_ZC_POST8
read Z8 ZP8 <<< $(score_band $D/t47-zc-post8.ppm)
read ZS8 ZSP8 <<< $(score_sc $D/t47-zc-post8.ppm)
read ZZ8 ZZP8 <<< $(score_zc $D/t47-zc-post8.ppm)
plog "ZC post+8 titleband mean=$Z8 p99=$ZP8 vs-sc mean=$ZS8 p99=$ZSP8 vs-zc mean=$ZZ8 p99=$ZZP8"
ZH_PRE1=$(score_whole $D/t47-scpre.ppm $D/t47-zc-post1.ppm)
ZH_13=$(score_whole $D/t47-zc-post1.ppm $D/t47-zc-post3.ppm)
ZH_38=$(score_whole $D/t47-zc-post3.ppm $D/t47-zc-post8.ppm)
plog "ZC hops whole: pre-post1=$ZH_PRE1 p1-p3=$ZH_13 p3-p8=$ZH_38"
if is_departed $ZH_PRE1 && is_nonsc $ZS8 && is_static $ZH_13 && is_static $ZH_38; then
  plog "ZC-LIKE -> Continue Cross"
else
  fail NO_ZC_PARK
fi
sleep 5
snap t47-ccpre || fail SNAP_CCPRE
read CZP CZP_P <<< $(score_zc $D/t47-ccpre.ppm)
plog "CCPRE vs-zc mean=$CZP p99=$CZP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
gshot zc
press K "CONT_CROSS"
sleep 1; snap t47-sp-post1 || fail SNAP_SP_POST1
read S1 SP1 <<< $(score_band $D/t47-sp-post1.ppm)
read SZ1 SZP1 <<< $(score_zc $D/t47-sp-post1.ppm)
read SS1 SSP1 <<< $(score_sp $D/t47-sp-post1.ppm)
plog "SP post+1 titleband mean=$S1 p99=$SP1 vs-zc mean=$SZ1 p99=$SZP1 vs-sp mean=$SS1 p99=$SSP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
sleep 2; snap t47-sp-post3 || fail SNAP_SP_POST3
read S3 SP3 <<< $(score_band $D/t47-sp-post3.ppm)
read SZ3 SZP3 <<< $(score_zc $D/t47-sp-post3.ppm)
read SS3 SSP3 <<< $(score_sp $D/t47-sp-post3.ppm)
plog "SP post+3 titleband mean=$S3 p99=$SP3 vs-zc mean=$SZ3 p99=$SZP3 vs-sp mean=$SS3 p99=$SSP3"
sleep 5; snap t47-sp-post8 || fail SNAP_SP_POST8
read S8 SP8 <<< $(score_band $D/t47-sp-post8.ppm)
read SZ8 SZP8 <<< $(score_zc $D/t47-sp-post8.ppm)
read SS8 SSP8 <<< $(score_sp $D/t47-sp-post8.ppm)
plog "SP post+8 titleband mean=$S8 p99=$SP8 vs-zc mean=$SZ8 p99=$SZP8 vs-sp mean=$SS8 p99=$SSP8"
SPH_PRE1=$(score_whole $D/t47-ccpre.ppm $D/t47-sp-post1.ppm)
SPH_13=$(score_whole $D/t47-sp-post1.ppm $D/t47-sp-post3.ppm)
SPH_38=$(score_whole $D/t47-sp-post3.ppm $D/t47-sp-post8.ppm)
plog "SP hops whole: pre-post1=$SPH_PRE1 p1-p3=$SPH_13 p3-p8=$SPH_38"
if is_departed $SPH_PRE1 && is_nonzc $SZ8 && is_static $SPH_13 && is_static $SPH_38; then
  plog "SP-LIKE -> Peak Cross"
else
  fail NO_SP_PARK
fi
sleep 5
snap t47-sppre || fail SNAP_SPPRE
read SPP SPP_P <<< $(score_sp $D/t47-sppre.ppm)
plog "SPPRE vs-sp mean=$SPP p99=$SPP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
gshot sp
press K "PEAK_CROSS"
sleep 1; snap t47-pc-post1 || fail SNAP_PC_POST1
read P1 PP1 <<< $(score_band $D/t47-pc-post1.ppm)
read PS1 PSP1 <<< $(score_sp $D/t47-pc-post1.ppm)
read PX1 PXP1 <<< $(score_sm $D/t47-pc-post1.ppm)
plog "PC post+1 titleband mean=$P1 p99=$PP1 vs-sp mean=$PS1 p99=$PSP1 vs-sm mean=$PX1 p99=$PXP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
sleep 2; snap t47-pc-post3 || fail SNAP_PC_POST3
read P3 PP3 <<< $(score_band $D/t47-pc-post3.ppm)
read PS3 PSP3 <<< $(score_sp $D/t47-pc-post3.ppm)
read PX3 PXP3 <<< $(score_sm $D/t47-pc-post3.ppm)
plog "PC post+3 titleband mean=$P3 p99=$PP3 vs-sp mean=$PS3 p99=$PSP3 vs-sm mean=$PX3 p99=$PXP3"
sleep 5; snap t47-pc-post8 || fail SNAP_PC_POST8
read P8 PP8 <<< $(score_band $D/t47-pc-post8.ppm)
read PS8 PSP8 <<< $(score_sp $D/t47-pc-post8.ppm)
read PX8 PXP8 <<< $(score_sm $D/t47-pc-post8.ppm)
plog "PC post+8 titleband mean=$P8 p99=$PP8 vs-sp mean=$PS8 p99=$PSP8 vs-sm mean=$PX8 p99=$PXP8"
PCH_PRE1=$(score_whole $D/t47-sppre.ppm $D/t47-pc-post1.ppm)
PCH_13=$(score_whole $D/t47-pc-post1.ppm $D/t47-pc-post3.ppm)
PCH_38=$(score_whole $D/t47-pc-post3.ppm $D/t47-pc-post8.ppm)
plog "PC hops whole: pre-post1=$PCH_PRE1 p1-p3=$PCH_13 p3-p8=$PCH_38"
if is_departed $PCH_PRE1 && is_nonsp $PS8 && is_static $PCH_13 && is_static $PCH_38; then
  plog "SM-LIKE -> Race Cross"
else
  fail NO_SM_PARK
fi
sleep 5
snap t47-smpre || fail SNAP_SMPRE
read SXP SXP_P <<< $(score_sm $D/t47-smpre.ppm)
plog "SMPRE vs-sm mean=$SXP p99=$SXP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
gshot sm
press K "RACE_CROSS"
sleep 1; snap t47-rc-post1 || fail SNAP_RC_POST1
read R1 RP1 <<< $(score_band $D/t47-rc-post1.ppm)
read RX1 RXP1 <<< $(score_sm $D/t47-rc-post1.ppm)
read RT1 RTP1 <<< $(score_setag $D/t47-rc-post1.ppm)
plog "RC post+1 titleband mean=$R1 p99=$RP1 vs-sm mean=$RX1 p99=$RXP1 se-tag mean=$RT1 p99=$RTP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
sleep 2; snap t47-rc-post3 || fail SNAP_RC_POST3
read R3 RP3 <<< $(score_band $D/t47-rc-post3.ppm)
read RX3 RXP3 <<< $(score_sm $D/t47-rc-post3.ppm)
read RT3 RTP3 <<< $(score_setag $D/t47-rc-post3.ppm)
plog "RC post+3 titleband mean=$R3 p99=$RP3 vs-sm mean=$RX3 p99=$RXP3 se-tag mean=$RT3 p99=$RTP3"
sleep 5; snap t47-rc-post8 || fail SNAP_RC_POST8
read R8 RP8 <<< $(score_band $D/t47-rc-post8.ppm)
read RX8 RXP8 <<< $(score_sm $D/t47-rc-post8.ppm)
read RT8 RTP8 <<< $(score_setag $D/t47-rc-post8.ppm)
read RS8 RSP8 <<< $(score_sp $D/t47-rc-post8.ppm)
read RW8 RWP8 <<< $(score_se $D/t47-rc-post8.ppm)
plog "RC post+8 titleband mean=$R8 p99=$RP8 vs-sm mean=$RX8 p99=$RXP8 se-tag mean=$RT8 p99=$RTP8 vs-sp mean=$RS8 p99=$RSP8 vs-se mean=$RW8 p99=$RWP8"
RCH_PRE1=$(score_whole $D/t47-smpre.ppm $D/t47-rc-post1.ppm)
RCH_13=$(score_whole $D/t47-rc-post1.ppm $D/t47-rc-post3.ppm)
RCH_38=$(score_whole $D/t47-rc-post3.ppm $D/t47-rc-post8.ppm)
plog "RC hops whole: pre-post1=$RCH_PRE1 p1-p3=$RCH_13 p3-p8=$RCH_38"
if is_static $RCH_13 && is_static $RCH_38 && is_nonsp $RS8 && is_setag $RT8; then
  plog "SE-LIKE -> SE default captures + Down-walk"
else
  fail NO_SE_PARK
fi
sleep 5
snap t47-sepre || fail SNAP_SEPRE
read STP STP_P <<< $(score_setag $D/t47-sepre.ppm)
plog "SEPRE se-tag mean=$STP p99=$STP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
gshot se-default
# Down-walk to Happiness/Rival (recomp e31d end-state): 4x Down +3s snaps,
# then Right/Left mode-tab probe +2s snaps. Bounded: 7 inputs, 7 snaps.
for N in 1 2 3 4; do
  press Down "SE_DOWN$N"
  sleep 3; snap t47-se-down$N || fail SNAP_SE_DOWN$N
  read W WP <<< $(score_se $D/t47-se-down$N.ppm)
  read T TP <<< $(score_setag $D/t47-se-down$N.ppm)
  plog "SE_DOWN$N vs-se mean=$W p99=$WP se-tag mean=$T p99=$TP"
done
snap t47-se-walked || fail SNAP_SE_WALKED
gshot se-walked
press Right "SE_RIGHT1"
sleep 2; snap t47-se-right1 || fail SNAP_SE_RIGHT1
press Left "SE_LEFT1"
sleep 2; snap t47-se-left1 || fail SNAP_SE_LEFT1
press Left "SE_LEFT2"
sleep 2; snap t47-se-left2 || fail SNAP_SE_LEFT2
gshot se-final
if [ "${SW_FIRST:-0}" = "1" ]; then
  plog "SW_FIRST run: no F9 toggle-back (whole run SW)"
else
  plog "F9 SW toggle + SW re-capture of final SE state"
  press F9 "SW_TOGGLE"
  sleep 5
  snap t47-se-sw || fail SNAP_SE_SW
  gshot se-sw
fi
ls -la $D/t47-*.jpg $D/t47-shot-*.png $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T47_DONE
