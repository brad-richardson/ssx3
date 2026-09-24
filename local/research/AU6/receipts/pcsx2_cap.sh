#!/usr/bin/env bash
# AU4 capture: T65/T48 closed-loop route, AU4 data directory and audio/video recording.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
T4=/home/brad/au6
R=/home/brad/pcsx2-t4
G=/home/brad/pcsx2-g7
BIN=$G/pcsx2/build/bin/pcsx2-qt
DAT=$T4/dat
E=$DAT/PCSX2/logs/emulog.txt
REF=$R/t27-ref-title.ppm
REFMENU=$R/t28-ref-menu.ppm
REFSC=$R/t29-ref-sc.ppm
REFZC=$R/t30-ref-zc.ppm
REFSP=$R/t31-ref-sp.ppm
REFSM=$R/t32-ref-sm.ppm
REFSE=$R/t33-ref-se.ppm
CD=$R/t44-cropdiff.py
HL=$R/t48-hlscan.py
TAG=${TAG:-au6a}
LOG=$T4/$TAG-poll.log
SNAPS=$DAT/PCSX2/snaps
TITLE_MEAN_MAX=2.0
TITLE_P99_MAX=10
IDENT_MEAN_MAX=4.0
STATIC_MEAN_MAX=1.0
ANIM_MEAN_MIN=1.0
WALL_CAP=560
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "AU4_FAIL:$1"; stamp; [ -f $T4/pcsx2-au4.pid ] && kill $(cat $T4/pcsx2-au4.pid) 2>/dev/null; [ -n "$XVFB_PID" ] && kill $XVFB_PID 2>/dev/null; sleep 5; exit 1; }
wallcheck() { [ $(( $(date -u +%s) - T_BOOT )) -lt $WALL_CAP ] || fail WALL_CAP; [ $(stat -c %s $E 2>/dev/null || echo 0) -lt 3500000000 ] || fail EMULOG_CAP; } # T65: +2 GB emulog cap
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
  cp "$SNAPS/$NEW" $T4/au4-shot-$LAB.png || fail GSHOT_CP_$LAB
  ls -la $T4/au4-shot-$LAB.png
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
ps -eo pid,comm,args | awk '$2 ~ /^(ninja|clang|clang\+\+|pcsx2-qt|gradle)$/ {print}' > $T4/precapture-jobs.txt
[ ! -s $T4/precapture-jobs.txt ] || { cat $T4/precapture-jobs.txt; exit 20; }
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >$T4/xvfb.log 2>&1 < /dev/null &
XVFB_PID=$!
sleep 4
kill -0 $XVFB_PID || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $DAT/PCSX2/logs/emulog-pre-$TAG-$TS.txt
fi
rm -f $T4/pcsx2-au4.pid $T4/pcsx2-tag1.bin
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
PCSX2_AU4_CAPTURE=1 PCSX2_AU6_CAPTURE=1 nohup $BIN -nogui -slowboot -turbo -datapath $DAT -logfile $T4/logs/boot-$TAG.log -- "$R/inputs/SSX 3 (USA).iso" > $T4/logs/boot-$TAG.stdout 2>&1 &
echo $! > $T4/pcsx2-au4.pid
echo "PID:$!"
sleep 70
wallcheck
kill -0 $(cat $T4/pcsx2-au4.pid) || fail PCSX2_DIED_PRE_START
DESC=$(grep -m1 'AU4_DESC' $E 2>/dev/null || true)
plog "LIVE_DESCRIPTOR $DESC"
case "$DESC" in *'desc=0050c800 src=00512b80 size=8f0'*) ;; *) fail BAD_SIF_DESCRIPTOR;; esac
[ $(stat -c %s $T4/pcsx2-tag1.bin 2>/dev/null || echo 0) -gt 0 ] || fail NO_TAG_RECORDS
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
press F12 "VIDEO_START"
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
SC_RECORDS=$(( $(stat -c %s $T4/pcsx2-tag1.bin) / 1572 ))
plog "SC_RECORDS=$SC_RECORDS"

# Stay at Select Character for at least 32 s of 36 kHz tag records and
# include AU6's serial-18000 memory snapshot.
for W in $(seq 1 150); do
  wallcheck
  SZ=$(stat -c %s $T4/pcsx2-tag1.bin 2>/dev/null || echo 0)
  N=$((SZ / 1572))
  plog "AU6_RECORDS=$N SC_RECORDS=$SC_RECORDS wall=$(($(date -u +%s)-T_BOOT))"
  [ $N -ge $((SC_RECORDS + 3000)) ] && [ $N -ge 18000 ] && break
  sleep 2
done
[ $N -ge $((SC_RECORDS + 3000)) ] && [ $N -ge 18000 ] || fail TOO_SHORT
[ $(stat -c %s $T4/status.bin 2>/dev/null || echo 0) -ge 1160000 ] || fail NO_STATUS
[ $(stat -c %s $T4/ee-menu.bin 2>/dev/null || echo 0) -eq 33554432 ] || fail NO_SNAPSHOT
plog "AU6_CAPTURE_DONE records=$N status=$(stat -c %s $T4/status.bin) snap=$(stat -c %s $T4/ee-menu.bin)"
kill $(cat $T4/pcsx2-au4.pid); sleep 5
kill $XVFB_PID 2>/dev/null || true
