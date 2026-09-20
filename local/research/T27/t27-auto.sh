#!/usr/bin/env bash
# T27 (press-on-title within dwell): fresh boot (NVM skips to attract) +
# detector-driven Start presses ON title, bounded <=3 title attempts.
# Per attempt: snap+score now; if title -> Start immediately; else Cross
# (attract-skip) then poll ~2.5s cadence up to 45s for title -> Start on
# first match. Post-press snaps +3/+8/+15/+25 with scores; menu-like =
# non-title at +8/+15/+25 AND whole-static across them -> stability 6x10s,
# stop. Unattended (~6 min). No /mnt/c touches. Wall + uptime stamps.
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-t4
E=$D/dat/PCSX2/logs/emulog.txt
REF=$D/t27-ref-title.ppm
CD=$D/t27-cropdiff.py
LOG=$D/t27-poll.log
# Thresholds (T27 calibration: title-title mean<=0.10 p99<=1,
# title-attract mean>=20.55 p99>=171; whole static pairs ~0.0-0.04,
# scene changes >=15.6): TITLE iff band mean<2.0 AND p99<=10;
# STATIC iff whole mean<1.0.
TITLE_MEAN_MAX=2.0
TITLE_P99_MAX=10
STATIC_MEAN_MAX=1.0
stamp() { date -u; echo "UPTIME:$(cut -d. -f1 /proc/uptime)"; }
fail() { echo "T27_FAIL:$1"; stamp; exit 1; }
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
is_num() {
  # fail-closed numeric check (R1 fix: empty scores misfired as title)
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
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t27.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $D/dat/PCSX2/logs/emulog-pre-t27-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t27.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t27.stdout 2>&1 &
echo $! > $D/pcsx2.pid
echo "PID:$!"
sleep 90
pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_START
WID=$(xdotool search --onlyvisible --name "SSX 3") || fail NO_WINDOW
echo "WID:$WID"
plog "REF_CHECK:$(python3 $CD $REF $REF)"
# end-to-end self-test through the real scoring path (R1 fix: would have
# caught the maxval-65535 parse failure before any press)
read SELF_M SELF_P <<< $(score_band $REF)
plog "SELF_TEST mean=$SELF_M p99=$SELF_P"
is_title $SELF_M $SELF_P || fail SELF_TEST
SELF_W=$(score_whole $REF $REF)
plog "SELF_WHOLE=$SELF_W"
is_static $SELF_W || fail SELF_WHOLE
snap t27-start || fail SNAP_START
read SM SP <<< $(score_band $D/t27-start.ppm)
plog "START_SCORE mean=$SM p99=$SP MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
MENU_LIKE=0
for A in 1 2 3; do
  plog "ATTEMPT_$A BEGIN MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_A$A
  snap t27-a$A-now || fail SNAP_A${A}_NOW
  read M P <<< $(score_band $D/t27-a$A-now.ppm)
  plog "ATTEMPT_$A now score mean=$M p99=$P"
  if is_title $M $P; then
    plog "ATTEMPT_$A TITLE-ALREADY-DETECTED (no Cross needed)"
    cp $D/t27-a$A-now.ppm $D/t27-a$A-pre.ppm
    cp $D/t27-a$A-now.jpg $D/t27-a$A-pre.jpg
    press Return "A${A}_START"
    DETECTED=1
  else
    plog "ATTEMPT_$A on attract (non-title) -> Cross attract-skip"
    press K "A${A}_CROSS"
    DETECTED=0
    for N in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18; do
      sleep 2
      snap t27-a$A-poll$N || fail SNAP_A${A}_POLL$N
      read M P <<< $(score_band $D/t27-a$A-poll$N.ppm)
      plog "ATTEMPT_$A poll$N score mean=$M p99=$P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
      if is_title $M $P; then
        plog "ATTEMPT_$A TITLE-DETECTED at poll$N"
        cp $D/t27-a$A-poll$N.ppm $D/t27-a$A-pre.ppm
        cp $D/t27-a$A-poll$N.jpg $D/t27-a$A-pre.jpg
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
  # post-press series with scores (pre-press snap = t27-a$A-pre.*)
  sleep 3; snap t27-a$A-post3 || fail SNAP_A${A}_POST3
  read M3 P3 <<< $(score_band $D/t27-a$A-post3.ppm)
  plog "ATTEMPT_$A post+3 score mean=$M3 p99=$P3 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  sleep 5; snap t27-a$A-post8 || fail SNAP_A${A}_POST8
  read M8 P8 <<< $(score_band $D/t27-a$A-post8.ppm)
  plog "ATTEMPT_$A post+8 score mean=$M8 p99=$P8"
  sleep 7; snap t27-a$A-post15 || fail SNAP_A${A}_POST15
  read M15 P15 <<< $(score_band $D/t27-a$A-post15.ppm)
  plog "ATTEMPT_$A post+15 score mean=$M15 p99=$P15"
  sleep 10; snap t27-a$A-post25 || fail SNAP_A${A}_POST25
  read M25 P25 <<< $(score_band $D/t27-a$A-post25.ppm)
  plog "ATTEMPT_$A post+25 score mean=$M25 p99=$P25"
  # menu-like gate: +8/+15/+25 all non-title AND whole-static across them
  W815=$(score_whole $D/t27-a$A-post8.ppm $D/t27-a$A-post15.ppm)
  W1525=$(score_whole $D/t27-a$A-post15.ppm $D/t27-a$A-post25.ppm)
  plog "ATTEMPT_$A whole815=$W815 whole1525=$W1525"
  if ! is_title $M8 $P8 && ! is_title $M15 $P15 && ! is_title $M25 $P25 \
     && is_static $W815 && is_static $W1525; then
    plog "ATTEMPT_$A MENU-LIKE (non-title + static) -> stability series"
    MENU_LIKE=1
    break
  fi
  plog "ATTEMPT_$A outcome: no-menu (title/attract cycling continues)"
done
if [ $MENU_LIKE -eq 1 ]; then
  for N in 1 2 3 4 5 6; do
    sleep 10; snap t27-menu-stab$N || fail SNAP_STAB$N
    read M P <<< $(score_band $D/t27-menu-stab$N.ppm)
    plog "STAB$N score mean=$M p99=$P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  done
fi
ls -la $D/t27-*.jpg $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T27_DONE
