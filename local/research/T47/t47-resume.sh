#!/usr/bin/env bash
# T47 resume: continue F1 from parked ZC (pcsx2 PID in pcsx2.pid, Xvfb :99
# already up). $1 = T_BOOT wall. Legs: ZC shot -> CONT -> SP -> SM -> SE
# -> Down-walk -> mode probe -> F9 SW -> kill. Settle-robust: +1/+3/+8/+15
# series per leg, static gate on the LAST TWO hops only (p1-p3 catches
# fades: F1 zc p1-p3 was 1.36 on a true ZC park). Thresholds = t44.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-t4
E=$D/dat/PCSX2/logs/emulog.txt
REFZC=$D/t30-ref-zc.ppm
REFSP=$D/t31-ref-sp.ppm
REFSM=$D/t32-ref-sm.ppm
REFSE=$D/t33-ref-se.ppm
REFSC=$D/t29-ref-sc.ppm
CD=$D/t44-cropdiff.py
LOG=$D/t47-poll.log
SNAPS=$D/dat/PCSX2/snaps
STATIC_MEAN_MAX=1.0
NONSC_MEAN_MIN=5.0
NONZC_MEAN_MIN=5.0
NONSP_MEAN_MIN=5.0
DEPART_MEAN_MIN=5.0
SETAG_MEAN_MAX=5.0
SETAG_BOX=40,415,330,450
T_BOOT=${1:?usage: t47-resume.sh T_BOOT}
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T47_FAIL:$1"; stamp; exit 1; }
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
score_whole() {
  python3 $CD $1 $2 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)}}};END{print m}'
}
score_band() {
  python3 $CD $1 $D/t27-ref-title.ppm | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
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
is_static() {
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$STATIC_MEAN_MAX 'BEGIN{exit !(m<mm)}'
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
cat $D/pcsx2.pid
kill -0 $(cat $D/pcsx2.pid) || fail PCSX2_GONE
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID RESUME_T_BOOT:$T_BOOT"
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
sleep 7; snap t47-sp-post15 || fail SNAP_SP_POST15
read S15 SP15 <<< $(score_band $D/t47-sp-post15.ppm)
read SZ15 SZP15 <<< $(score_zc $D/t47-sp-post15.ppm)
read SS15 SSP15 <<< $(score_sp $D/t47-sp-post15.ppm)
plog "SP post+15 titleband mean=$S15 p99=$SP15 vs-zc mean=$SZ15 p99=$SZP15 vs-sp mean=$SS15 p99=$SSP15"
SPH_PRE1=$(score_whole $D/t47-ccpre.ppm $D/t47-sp-post1.ppm)
SPH_38=$(score_whole $D/t47-sp-post3.ppm $D/t47-sp-post8.ppm)
SPH_815=$(score_whole $D/t47-sp-post8.ppm $D/t47-sp-post15.ppm)
plog "SP hops whole: pre-post1=$SPH_PRE1 p3-p8=$SPH_38 p8-p15=$SPH_815"
if is_departed $SPH_PRE1 && is_nonzc $SZ15 && is_static $SPH_38 && is_static $SPH_815; then
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
sleep 7; snap t47-pc-post15 || fail SNAP_PC_POST15
read P15 PP15 <<< $(score_band $D/t47-pc-post15.ppm)
read PS15 PSP15 <<< $(score_sp $D/t47-pc-post15.ppm)
read PX15 PXP15 <<< $(score_sm $D/t47-pc-post15.ppm)
plog "PC post+15 titleband mean=$P15 p99=$PP15 vs-sp mean=$PS15 p99=$PSP15 vs-sm mean=$PX15 p99=$PXP15"
PCH_PRE1=$(score_whole $D/t47-ccpre.ppm $D/t47-pc-post1.ppm)
PCH_PRE1=$(score_whole $D/t47-sppre.ppm $D/t47-pc-post1.ppm)
PCH_38=$(score_whole $D/t47-pc-post3.ppm $D/t47-pc-post8.ppm)
PCH_815=$(score_whole $D/t47-pc-post8.ppm $D/t47-pc-post15.ppm)
plog "PC hops whole: pre-post1=$PCH_PRE1 p3-p8=$PCH_38 p8-p15=$PCH_815"
if is_departed $PCH_PRE1 && is_nonsp $PS15 && is_static $PCH_38 && is_static $PCH_815; then
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
sleep 7; snap t47-rc-post15 || fail SNAP_RC_POST15
read R15 RP15 <<< $(score_band $D/t47-rc-post15.ppm)
read RX15 RXP15 <<< $(score_sm $D/t47-rc-post15.ppm)
read RT15 RTP15 <<< $(score_setag $D/t47-rc-post15.ppm)
read RS15 RSP15 <<< $(score_sp $D/t47-rc-post15.ppm)
read RW15 RWP15 <<< $(score_se $D/t47-rc-post15.ppm)
plog "RC post+15 titleband mean=$R15 p99=$RP15 vs-sm mean=$RX15 p99=$RXP15 se-tag mean=$RT15 p99=$RTP15 vs-sp mean=$RS15 p99=$RSP15 vs-se mean=$RW15 p99=$RWP15"
RCH_38=$(score_whole $D/t47-rc-post3.ppm $D/t47-rc-post8.ppm)
RCH_815=$(score_whole $D/t47-rc-post8.ppm $D/t47-rc-post15.ppm)
plog "RC hops whole: p3-p8=$RCH_38 p8-p15=$RCH_815"
if is_static $RCH_38 && is_static $RCH_815 && is_nonsp $RS15 && is_setag $RT15; then
  plog "SE-LIKE -> SE default captures + Down-walk"
else
  fail NO_SE_PARK
fi
sleep 5
snap t47-sepre || fail SNAP_SEPRE
read STP STP_P <<< $(score_setag $D/t47-sepre.ppm)
plog "SEPRE se-tag mean=$STP p99=$STP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
gshot se-default
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
plog "F9 SW toggle + SW re-capture of final SE state"
press F9 "SW_TOGGLE"
sleep 5
snap t47-se-sw || fail SNAP_SE_SW
gshot se-sw
ls -la $D/t47-*.jpg $D/t47-shot-*.png $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T47_DONE
