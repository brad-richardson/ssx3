#!/usr/bin/env bash
# T37 (dense post-nudge series + rider-pixel tracking): reproduce the T36
# R1 chain (fresh boot, NVM skips to attract, Cross attract-skip,
# detector-driven Start ON title, menu-like gate, Cross on Single Event,
# SC-LIKE gate, Cross on Zoe, ZC-LIKE gate, Cross on Continue, SP-LIKE
# gate, Cross on Peak 1, SM-LIKE gate, Cross on Race, SE-LIKE gate
# (static + non-SP + se-tag<5.0 remote), Cross on Snow Jam, MR-LIKE gate,
# Cross on Continue, PP-LIKE settled-panel gate, Cross on X Continue),
# confirm LIVE gameplay (LIVE-LIKE proxy gate: departed + non-panel +
# motion x2; the true LIVE-RACE criterion — race clock advancing +
# position/progress HUD — is read off viewed snaps post-hoc), then apply
# ONE bounded steering nudge (single D-pad Left tap, Keyboard/Left,
# 300 ms keydown — same input class as T36) with a PRE-nudge pair (noise
# floor) + DENSE post-nudge series (1 s cadence x 10 s).
# Bounded: <=3 park attempts, ONE nudge, no variant in-script (ONE bounded
# variant allowed post-hoc only if the nudge provably never acted on live
# gameplay). Unattended (~10 min; T36 R1 ran 571 s, same shape + dense tail
# — overrun tabled with full dmesg coverage).
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
REFSE=$D/t33-ref-se.ppm
REFMR=$D/t34-ref-mr.ppm
REFPP=$D/t35-ref-panel.ppm
CD=$D/t37-cropdiff.py
LOG=$D/t37-poll.log
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
# (T33 SE calibration, PIL: whole SE-SE 0.0000-0.0633/p99 0-1,
# SM-vs-SE 0.5071-0.5333/p99 8-11, SP-vs-SE 5.31-5.37/121-122,
# ZC-vs-SE 10.22/164-165, SC-vs-SE 11.89-11.93/157-159,
# menu-vs-SE 10.94/177, title-vs-SE 16.25/160, attract-vs-SE 15.94-16.01;
# TAG crop 40,415,330,450 vs SE-ref: SE-SE 0.0000-0.1401/p99 0-4,
# SM-vs-SE 14.1390-14.1405/p99 88, SP 14.00/89, ZC 15.30-15.33/91,
# SC 26.57/90, menu 26.15-26.17/106, title 106.62/205, attract 44.01-84.26;
# LIST crop 110,195,270,270: SE-SE <=0.1488, SM 21.74;
# PTITLE crop 310,110,410,135: SE-SE 0.0000, SM 16.14-16.51;
# HDR crop 40,60,280,110 REJECTED: SE-SE 0-3.55 overlaps SP 4.36-5.15.)
# GATE WARNING (T32 G1): SM->SE whole hop is only ~0.47-0.50, so DEPARTED
# > 5.0 does NOT fire here, and whole-vs-SE < 2.0 does NOT separate SM
# (0.51-0.53). The SE park gate uses the TAG crop instead: SE_TAG iff
# tag-crop-vs-SE-ref mean<5.0. (R1 ran this bar at 2.0 and NO-SE-PARKed on
# a true SE park: remote se-tag 2.6271/p99 11 x3 snaps vs PIL 0.009-0.012
# — the text-dense crop inflates ~290x remote-vs-PIL from JPEG ringing in
# the ref around glyph edges, vs ~9x on whole-frame. SM side PIL 14.14,
# remote expected ~14+ from large-mean mode agreement; receipted in R2 via
# the smpre se-tag line. R2 margins: SE side 2.63 vs 5.0 = 1.9x, SM side
# ~14 vs 5.0 = 2.8x, both tabled.)
# Post-hoc "Cross acted on SE" bar: whole-vs-SE-ref mean<0.2 PIL
# (SE-SE <=0.063, SM >=0.507) + se-tag<2.0 PIL + viewed snap.
# (T34 MR calibration, PIL whole vs t33r2-sj-stab6 MR-ref: MR-MR
# 0.0786-0.1744/p99 0-3, SE 10.59-10.65/144, SM 10.44-10.47/143,
# SP 9.83-9.87/138, ZC 7.04-7.09/103-104, SC 5.61-5.66/117 (nearest
# prior screen), menu 10.08-10.09/96, title 9.77/143, attract 13.19-14.65.
# SE->MR whole hop ~10.58-10.61, so DEPARTED > 5.0 fires normally here.)
# MR iff whole-vs-MR-ref mean<2.0 (post-hoc bar; the Enter Cross press does
# NOT depend on it, T28/T29/T30/T31/T32/T33 precedent — the in-script
# MR-LIKE gate is departed + non-SE + static; the vs-mr line is scored
# in-script as the remote receipt and classified post-hoc, since the
# remote-vs-PIL gap on the ~0.17 MR-side mean has no pre-run remote receipt
# — T33 G12 chicken-and-egg. Margins: MR side 0.1744 vs 2.0 = 11.5x,
# SC side 5.61 vs 2.0 = 2.8x, both tabled.)
# (T37 panel calibration, PIL whole vs t34r1-mr-stab6 panel-ref: panel
# 0.0000-0.3503/p99 0-16, attract-nearest 10.95/141, cinematic 15.02/190,
# attract 15.32/142, SE 16.43/160, SM 16.41/160, SP 16.58/157, menu
# 19.30/178, SC 19.45/172, MR 19.53-19.59/152-153, ZC 20.18/165, black
# 20.45/191, load 21.08-21.12/169, title 22.15/183. Panel-side spread
# <=0.40/p99 <=18 over 98 s in T34 R1 (panel animation).)
# GATE NOTE (T34 G1): the Enter transition is decisive (MR->load whole hop
# ~12.43-12.47, DEPARTED fires), but the load->panel path is multi-stage
# (loading % -> black -> cinematic -> panel over ~30 s). The PP-LIKE gate
# is a SETTLED-PANEL criterion: departed (mrpre->post1) + static x3
# (post25->post40, post40->stab1, stab1->stab2) + non-MR (stab2 vs-mr).
# The black frame at +8 s is a TRANSITION, not an arrival — the 3-hop
# static chain over ~35 s cannot fire on it (post1->post3 2.13, post3->post8
# 39.96, post8->post15 10.19, post15->post25 15.23 in T34 R1; only
# post25->post40 0.25 static). The vs-panel line is scored in-script as the
# remote receipt and classified post-hoc (< 2.0 strict; panel side 0.3503 =
# 5.7x, nearest non-panel 10.95 = 5.5x, both tabled).
# (T37 reuses the T36 LIVE calibration, T35 R1 receipts: panel->countdown departure hop
# 14.18-14.19; X-snaps vs-panel 12.98-21.27; all 66 X-pair hops 7.97-20.23
# live motion, never static. The in-script LIVE-LIKE proxy gate is
# departed (pppre->x-post1) + non-panel (x-post40 vs-pp > 5.0) + motion x2
# (x-post15->x-post25, x-post25->x-post40 hops > 5.0). The true LIVE-RACE
# criterion — race clock advancing + position/progress HUD present — is
# read off viewed snaps post-hoc, not whole-frame scores (T35 G1 gate
# note: gate on the HUD, not the frame). T35 R1 legs: 14.19 / 18.78 /
# 11.52 / 9.51 — every leg 1.9x+ over its bar.)
# NONPP iff whole-vs-panel-ref mean>5.0 (panel side <=1.00 remote, X 12.98+).
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
fail() { echo "T37_FAIL:$1"; stamp; exit 1; }
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
# score_se PPM: prints "<mean> <p99>" of whole-frame compare vs REFSE
score_se() {
  python3 $CD $1 $REFSE 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
# score_setag PPM: prints "<mean> <p99>" of TAG-crop compare vs REFSE
score_setag() {
  python3 $CD $1 $REFSE $SETAG_BOX | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
# score_mr PPM: prints "<mean> <p99>" of whole-frame compare vs REFMR
score_mr() {
  python3 $CD $1 $REFMR 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
}
# score_pp PPM: prints "<mean> <p99>" of whole-frame compare vs REFPP
score_pp() {
  python3 $CD $1 $REFPP 0,0,1280,1024 | awk '{for(i=1;i<=NF;i++){if($i~/^mean=/){m=substr($i,6)};if($i~/^p99=/){p=substr($i,5)}}};END{print m, p}'
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
is_nonse() {
  # $1=whole-vs-SE mean -> exit 0 iff non-SE; non-numeric -> not-nonse
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$NONSE_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
is_nonmr() {
  # $1=whole-vs-MR mean -> exit 0 iff non-MR; non-numeric -> not-nonmr
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$NONMR_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
is_nonpp() {
  # $1=whole-vs-panel mean -> exit 0 iff non-panel; non-numeric -> no
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$NONPP_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
is_departed() {
  # $1=whole hop mean -> exit 0 iff decisively left; non-numeric -> no
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$DEPART_MEAN_MIN 'BEGIN{exit !(m>mm)}'
}
is_setag() {
  # $1=TAG-crop-vs-SE mean -> exit 0 iff Select Event; non-numeric -> no
  is_num "$1" || return 1
  awk -v m=$1 -v mm=$SETAG_MEAN_MAX 'BEGIN{exit !(m<mm)}'
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
press_nudge() {
  # $1=keyname $2=label: single 300ms tap with stamps (T37 steering nudge;
  # NOT a 534ms-class menu hold — different input class, brief-authorized)
  local KEY=$1; local LAB=$2
  plog "${LAB}_KEYDOWN_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime) MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  xdotool windowfocus --sync $WID || fail FOCUS_$LAB
  xdotool keydown $KEY || fail KEYDOWN_$LAB
  plog "${LAB}_HELD_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime)"
  sleep 0.3
  xdotool keyup $KEY || fail KEYUP_$LAB
  plog "${LAB}_KEYUP_WALL:$(date -u +%s.%N) UPTIME:$(cut -d. -f1 /proc/uptime) MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
}
stamp
pkill Xvfb || true
sleep 2
pgrep -a Xvfb || true
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t37.log 2>&1 < /dev/null &
sleep 4
pgrep -a Xvfb || fail NO_XVFB
xdotool getdisplaygeometry || fail NO_DISPLAY
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f $E ]; then
  mv $E $D/dat/PCSX2/logs/emulog-pre-t37-$TS.txt
  ls -la $D/dat/PCSX2/logs/
fi
rm -f $D/pcsx2.pid
T_BOOT=$(date -u +%s)
echo "T_BOOT_WALL:$T_BOOT T_BOOT_UPTIME:$(cut -d. -f1 /proc/uptime)"
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t37.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t37.stdout 2>&1 &
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
plog "REFSE_CHECK:$(python3 $CD $REFSE $REFSE 0,0,1280,1024)"
plog "REFSETAG_CHECK:$(python3 $CD $REFSE $REFSE $SETAG_BOX)"
plog "REFMR_CHECK:$(python3 $CD $REFMR $REFMR 0,0,1280,1024)"
plog "REFPP_CHECK:$(python3 $CD $REFPP $REFPP 0,0,1280,1024)"
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
read SELF_EM SELF_EP <<< $(score_se $REFSE)
plog "SELF_SE mean=$SELF_EM p99=$SELF_EP"
is_menu $SELF_EM || fail SELF_SE
read SELF_TM SELF_TP <<< $(score_setag $REFSE)
plog "SELF_SETAG mean=$SELF_TM p99=$SELF_TP"
is_setag $SELF_TM || fail SELF_SETAG
read SELF_RM SELF_RP <<< $(score_mr $REFMR)
plog "SELF_MR mean=$SELF_RM p99=$SELF_RP"
is_menu $SELF_RM || fail SELF_MR
read SELF_PM SELF_PP <<< $(score_pp $REFPP)
plog "SELF_PP mean=$SELF_PM p99=$SELF_PP"
is_menu $SELF_PM || fail SELF_PP
snap t37-start || fail SNAP_START
read SM SP <<< $(score_band $D/t37-start.ppm)
plog "START_SCORE mean=$SM p99=$SP MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
MENU_LIKE=0
for A in 1 2 3; do
  plog "ATTEMPT_$A BEGIN MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  pgrep -f pcsx2-qt >/dev/null || fail PCSX2_DIED_PRE_A$A
  snap t37-a$A-now || fail SNAP_A${A}_NOW
  read M P <<< $(score_band $D/t37-a$A-now.ppm)
  plog "ATTEMPT_$A now score mean=$M p99=$P"
  if is_title $M $P; then
    plog "ATTEMPT_$A TITLE-ALREADY-DETECTED (no Cross needed)"
    cp $D/t37-a$A-now.ppm $D/t37-a$A-pre.ppm
    cp $D/t37-a$A-now.jpg $D/t37-a$A-pre.jpg
    press Return "A${A}_START"
    DETECTED=1
  else
    plog "ATTEMPT_$A on attract (non-title) -> Cross attract-skip"
    press K "A${A}_CROSS"
    DETECTED=0
    for N in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18; do
      sleep 2
      snap t37-a$A-poll$N || fail SNAP_A${A}_POLL$N
      read M P <<< $(score_band $D/t37-a$A-poll$N.ppm)
      plog "ATTEMPT_$A poll$N score mean=$M p99=$P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
      if is_title $M $P; then
        plog "ATTEMPT_$A TITLE-DETECTED at poll$N"
        cp $D/t37-a$A-poll$N.ppm $D/t37-a$A-pre.ppm
        cp $D/t37-a$A-poll$N.jpg $D/t37-a$A-pre.jpg
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
  # post-press series with scores (pre-press snap = t37-a$A-pre.*)
  sleep 3; snap t37-a$A-post3 || fail SNAP_A${A}_POST3
  read M3 P3 <<< $(score_band $D/t37-a$A-post3.ppm)
  plog "ATTEMPT_$A post+3 score mean=$M3 p99=$P3 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  sleep 5; snap t37-a$A-post8 || fail SNAP_A${A}_POST8
  read M8 P8 <<< $(score_band $D/t37-a$A-post8.ppm)
  plog "ATTEMPT_$A post+8 score mean=$M8 p99=$P8"
  sleep 7; snap t37-a$A-post15 || fail SNAP_A${A}_POST15
  read M15 P15 <<< $(score_band $D/t37-a$A-post15.ppm)
  plog "ATTEMPT_$A post+15 score mean=$M15 p99=$P15"
  sleep 10; snap t37-a$A-post25 || fail SNAP_A${A}_POST25
  read M25 P25 <<< $(score_band $D/t37-a$A-post25.ppm)
  plog "ATTEMPT_$A post+25 score mean=$M25 p99=$P25"
  # menu-like gate: +8/+15/+25 all non-title AND whole-static across them
  W815=$(score_whole $D/t37-a$A-post8.ppm $D/t37-a$A-post15.ppm)
  W1525=$(score_whole $D/t37-a$A-post15.ppm $D/t37-a$A-post25.ppm)
  plog "ATTEMPT_$A whole815=$W815 whole1525=$W1525"
  read MM25 MP25 <<< $(score_menu $D/t37-a$A-post25.ppm)
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
  snap t37-menupre || fail SNAP_MENUPRE
  read MMP MMP_P <<< $(score_menu $D/t37-menupre.ppm)
  plog "MENUPRE vs-menu mean=$MMP p99=$MMP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  read MPT MPT_P <<< $(score_band $D/t37-menupre.ppm)
  plog "MENUPRE vs-title mean=$MPT p99=$MPT_P"
  press K "MENU_CROSS"
  # SC-park confirmation series (short: the menu->SC transition is already
  # mapped by T28; the +40 s tail belongs to the Continue Cross below),
  # each scored vs title-band, menu-ref and SC-ref
  sleep 1; snap t37-mc-post1 || fail SNAP_MC_POST1
  read M1 P1 <<< $(score_band $D/t37-mc-post1.ppm)
  read MM1 MP1 <<< $(score_menu $D/t37-mc-post1.ppm)
  read MS1 MSP1 <<< $(score_sc $D/t37-mc-post1.ppm)
  plog "MC post+1 titleband mean=$M1 p99=$P1 vs-menu mean=$MM1 p99=$MP1 vs-sc mean=$MS1 p99=$MSP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
  sleep 2; snap t37-mc-post3 || fail SNAP_MC_POST3
  read M3 P3 <<< $(score_band $D/t37-mc-post3.ppm)
  read MM3 MP3 <<< $(score_menu $D/t37-mc-post3.ppm)
  read MS3 MSP3 <<< $(score_sc $D/t37-mc-post3.ppm)
  plog "MC post+3 titleband mean=$M3 p99=$P3 vs-menu mean=$MM3 p99=$MP3 vs-sc mean=$MS3 p99=$MSP3"
  sleep 5; snap t37-mc-post8 || fail SNAP_MC_POST8
  read M8 P8 <<< $(score_band $D/t37-mc-post8.ppm)
  read MM8 MP8 <<< $(score_menu $D/t37-mc-post8.ppm)
  read MS8 MSP8 <<< $(score_sc $D/t37-mc-post8.ppm)
  plog "MC post+8 titleband mean=$M8 p99=$P8 vs-menu mean=$MM8 p99=$MP8 vs-sc mean=$MS8 p99=$MSP8"
  sleep 7; snap t37-mc-post15 || fail SNAP_MC_POST15
  read M15 P15 <<< $(score_band $D/t37-mc-post15.ppm)
  read MM15 MP15 <<< $(score_menu $D/t37-mc-post15.ppm)
  read MS15 MSP15 <<< $(score_sc $D/t37-mc-post15.ppm)
  plog "MC post+15 titleband mean=$M15 p99=$P15 vs-menu mean=$MM15 p99=$MP15 vs-sc mean=$MS15 p99=$MSP15"
  # per-hop whole-frame diffs across the menu->SC chain
  H_PRE1=$(score_whole $D/t37-menupre.ppm $D/t37-mc-post1.ppm)
  H_13=$(score_whole $D/t37-mc-post1.ppm $D/t37-mc-post3.ppm)
  H_38=$(score_whole $D/t37-mc-post3.ppm $D/t37-mc-post8.ppm)
  H_815=$(score_whole $D/t37-mc-post8.ppm $D/t37-mc-post15.ppm)
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
    snap t37-scpre || fail SNAP_SCPRE
    read SCP SCP_P <<< $(score_sc $D/t37-scpre.ppm)
    plog "SCPRE vs-sc mean=$SCP p99=$SCP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
    read SMP SMP_P <<< $(score_menu $D/t37-scpre.ppm)
    plog "SCPRE vs-menu mean=$SMP p99=$SMP_P"
    read SPT SPT_P <<< $(score_band $D/t37-scpre.ppm)
    plog "SCPRE vs-title mean=$SPT p99=$SPT_P"
    press K "ZOE_CROSS"
    # ZC-park confirmation series (short: the SC->ZC transition is already
    # mapped by T29; the +40 s tail belongs to the Continue Cross below),
    # each scored vs title-band, SC-ref and ZC-ref (vs-menu post-hoc local)
    sleep 1; snap t37-zc-post1 || fail SNAP_ZC_POST1
    read Z1 ZP1 <<< $(score_band $D/t37-zc-post1.ppm)
    read ZS1 ZSP1 <<< $(score_sc $D/t37-zc-post1.ppm)
    read ZZ1 ZZP1 <<< $(score_zc $D/t37-zc-post1.ppm)
    plog "ZC post+1 titleband mean=$Z1 p99=$ZP1 vs-sc mean=$ZS1 p99=$ZSP1 vs-zc mean=$ZZ1 p99=$ZZP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
    sleep 2; snap t37-zc-post3 || fail SNAP_ZC_POST3
    read Z3 ZP3 <<< $(score_band $D/t37-zc-post3.ppm)
    read ZS3 ZSP3 <<< $(score_sc $D/t37-zc-post3.ppm)
    read ZZ3 ZZP3 <<< $(score_zc $D/t37-zc-post3.ppm)
    plog "ZC post+3 titleband mean=$Z3 p99=$ZP3 vs-sc mean=$ZS3 p99=$ZSP3 vs-zc mean=$ZZ3 p99=$ZZP3"
    sleep 5; snap t37-zc-post8 || fail SNAP_ZC_POST8
    read Z8 ZP8 <<< $(score_band $D/t37-zc-post8.ppm)
    read ZS8 ZSP8 <<< $(score_sc $D/t37-zc-post8.ppm)
    read ZZ8 ZZP8 <<< $(score_zc $D/t37-zc-post8.ppm)
    plog "ZC post+8 titleband mean=$Z8 p99=$ZP8 vs-sc mean=$ZS8 p99=$ZSP8 vs-zc mean=$ZZ8 p99=$ZZP8"
    # per-hop whole-frame diffs across the SC->ZC chain
    ZH_PRE1=$(score_whole $D/t37-scpre.ppm $D/t37-zc-post1.ppm)
    ZH_13=$(score_whole $D/t37-zc-post1.ppm $D/t37-zc-post3.ppm)
    ZH_38=$(score_whole $D/t37-zc-post3.ppm $D/t37-zc-post8.ppm)
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
      snap t37-ccpre || fail SNAP_CCPRE
      read CZP CZP_P <<< $(score_zc $D/t37-ccpre.ppm)
      plog "CCPRE vs-zc mean=$CZP p99=$CZP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
      read CSP CSP_P <<< $(score_sc $D/t37-ccpre.ppm)
      plog "CCPRE vs-sc mean=$CSP p99=$CSP_P"
      read CPT CPT_P <<< $(score_band $D/t37-ccpre.ppm)
      plog "CCPRE vs-title mean=$CPT p99=$CPT_P"
      press K "CONT_CROSS"
      # SP-park confirmation series (short: the ZC->SP transition is already
      # mapped by T30; the +40 s tail belongs to the Peak Cross below),
      # each scored vs title-band, ZC-ref and SP-ref (vs-sc/vs-menu
      # post-hoc local)
      sleep 1; snap t37-sp-post1 || fail SNAP_SP_POST1
      read S1 SP1 <<< $(score_band $D/t37-sp-post1.ppm)
      read SZ1 SZP1 <<< $(score_zc $D/t37-sp-post1.ppm)
      read SS1 SSP1 <<< $(score_sp $D/t37-sp-post1.ppm)
      plog "SP post+1 titleband mean=$S1 p99=$SP1 vs-zc mean=$SZ1 p99=$SZP1 vs-sp mean=$SS1 p99=$SSP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
      sleep 2; snap t37-sp-post3 || fail SNAP_SP_POST3
      read S3 SP3 <<< $(score_band $D/t37-sp-post3.ppm)
      read SZ3 SZP3 <<< $(score_zc $D/t37-sp-post3.ppm)
      read SS3 SSP3 <<< $(score_sp $D/t37-sp-post3.ppm)
      plog "SP post+3 titleband mean=$S3 p99=$SP3 vs-zc mean=$SZ3 p99=$SZP3 vs-sp mean=$SS3 p99=$SSP3"
      sleep 5; snap t37-sp-post8 || fail SNAP_SP_POST8
      read S8 SP8 <<< $(score_band $D/t37-sp-post8.ppm)
      read SZ8 SZP8 <<< $(score_zc $D/t37-sp-post8.ppm)
      read SS8 SSP8 <<< $(score_sp $D/t37-sp-post8.ppm)
      plog "SP post+8 titleband mean=$S8 p99=$SP8 vs-zc mean=$SZ8 p99=$SZP8 vs-sp mean=$SS8 p99=$SSP8"
      # per-hop whole-frame diffs across the ZC->SP chain
      SPH_PRE1=$(score_whole $D/t37-ccpre.ppm $D/t37-sp-post1.ppm)
      SPH_13=$(score_whole $D/t37-sp-post1.ppm $D/t37-sp-post3.ppm)
      SPH_38=$(score_whole $D/t37-sp-post3.ppm $D/t37-sp-post8.ppm)
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
        snap t37-sppre || fail SNAP_SPPRE
        read SPP SPP_P <<< $(score_sp $D/t37-sppre.ppm)
        plog "SPPRE vs-sp mean=$SPP p99=$SPP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
        read SPZ SPZ_P <<< $(score_zc $D/t37-sppre.ppm)
        plog "SPPRE vs-zc mean=$SPZ p99=$SPZ_P"
        read SPT SPT_P <<< $(score_band $D/t37-sppre.ppm)
        plog "SPPRE vs-title mean=$SPT p99=$SPT_P"
        press K "PEAK_CROSS"
        # SM-park confirmation series (short: the SP->SM transition is already
        # mapped by T31; the +40 s tail belongs to the Race Cross below),
        # each scored vs title-band, SP-ref and SM-ref (vs-zc/vs-sc/vs-menu
        # post-hoc local)
        sleep 1; snap t37-pc-post1 || fail SNAP_PC_POST1
        read P1 PP1 <<< $(score_band $D/t37-pc-post1.ppm)
        read PS1 PSP1 <<< $(score_sp $D/t37-pc-post1.ppm)
        read PX1 PXP1 <<< $(score_sm $D/t37-pc-post1.ppm)
        plog "PC post+1 titleband mean=$P1 p99=$PP1 vs-sp mean=$PS1 p99=$PSP1 vs-sm mean=$PX1 p99=$PXP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
        sleep 2; snap t37-pc-post3 || fail SNAP_PC_POST3
        read P3 PP3 <<< $(score_band $D/t37-pc-post3.ppm)
        read PS3 PSP3 <<< $(score_sp $D/t37-pc-post3.ppm)
        read PX3 PXP3 <<< $(score_sm $D/t37-pc-post3.ppm)
        plog "PC post+3 titleband mean=$P3 p99=$PP3 vs-sp mean=$PS3 p99=$PSP3 vs-sm mean=$PX3 p99=$PXP3"
        sleep 5; snap t37-pc-post8 || fail SNAP_PC_POST8
        read P8 PP8 <<< $(score_band $D/t37-pc-post8.ppm)
        read PS8 PSP8 <<< $(score_sp $D/t37-pc-post8.ppm)
        read PX8 PXP8 <<< $(score_sm $D/t37-pc-post8.ppm)
        plog "PC post+8 titleband mean=$P8 p99=$PP8 vs-sp mean=$PS8 p99=$PSP8 vs-sm mean=$PX8 p99=$PXP8"
        # per-hop whole-frame diffs across the SP->SM chain
        PCH_PRE1=$(score_whole $D/t37-sppre.ppm $D/t37-pc-post1.ppm)
        PCH_13=$(score_whole $D/t37-pc-post1.ppm $D/t37-pc-post3.ppm)
        PCH_38=$(score_whole $D/t37-pc-post3.ppm $D/t37-pc-post8.ppm)
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
          # Chain reproduction: ONE Cross (x Select) on the parked Select
          # Mode (Race highlighted per T32 R1); arrival static 133 s, no
          # dwell pressure.
          sleep 5
          snap t37-smpre || fail SNAP_SMPRE
          read SXP SXP_P <<< $(score_sm $D/t37-smpre.ppm)
          plog "SMPRE vs-sm mean=$SXP p99=$SXP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
          read SXST SXST_P <<< $(score_setag $D/t37-smpre.ppm)
          plog "SMPRE se-tag mean=$SXST p99=$SXST_P"
          read SXSP SXSP_P <<< $(score_sp $D/t37-smpre.ppm)
          plog "SMPRE vs-sp mean=$SXSP p99=$SXSP_P"
          read SXPT SXPT_P <<< $(score_band $D/t37-smpre.ppm)
          plog "SMPRE vs-title mean=$SXPT p99=$SXPT_P"
          press K "RACE_CROSS"
          # SE-park confirmation series (short: the SM->SE transition is already
          # mapped by T32; the +40 s tail belongs to the SnowJam Cross below),
          # each scored vs title-band, SM-ref and the SE tagline crop (whole
          # vs-SE + vs-sp/vs-zc/vs-sc/vs-menu post-hoc local; vs-sp on post8
          # only for the non-SP leg)
          sleep 1; snap t37-rc-post1 || fail SNAP_RC_POST1
          read R1 RP1 <<< $(score_band $D/t37-rc-post1.ppm)
          read RX1 RXP1 <<< $(score_sm $D/t37-rc-post1.ppm)
          read RT1 RTP1 <<< $(score_setag $D/t37-rc-post1.ppm)
          plog "RC post+1 titleband mean=$R1 p99=$RP1 vs-sm mean=$RX1 p99=$RXP1 se-tag mean=$RT1 p99=$RTP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
          sleep 2; snap t37-rc-post3 || fail SNAP_RC_POST3
          read R3 RP3 <<< $(score_band $D/t37-rc-post3.ppm)
          read RX3 RXP3 <<< $(score_sm $D/t37-rc-post3.ppm)
          read RT3 RTP3 <<< $(score_setag $D/t37-rc-post3.ppm)
          plog "RC post+3 titleband mean=$R3 p99=$RP3 vs-sm mean=$RX3 p99=$RXP3 se-tag mean=$RT3 p99=$RTP3"
          sleep 5; snap t37-rc-post8 || fail SNAP_RC_POST8
          read R8 RP8 <<< $(score_band $D/t37-rc-post8.ppm)
          read RX8 RXP8 <<< $(score_sm $D/t37-rc-post8.ppm)
          read RT8 RTP8 <<< $(score_setag $D/t37-rc-post8.ppm)
          read RS8 RSP8 <<< $(score_sp $D/t37-rc-post8.ppm)
          read RW8 RWP8 <<< $(score_se $D/t37-rc-post8.ppm)
          plog "RC post+8 titleband mean=$R8 p99=$RP8 vs-sm mean=$RX8 p99=$RXP8 se-tag mean=$RT8 p99=$RTP8 vs-sp mean=$RS8 p99=$RSP8 vs-se mean=$RW8 p99=$RWP8"
          # per-hop whole-frame diffs across the SM->SE chain
          RCH_PRE1=$(score_whole $D/t37-smpre.ppm $D/t37-rc-post1.ppm)
          RCH_13=$(score_whole $D/t37-rc-post1.ppm $D/t37-rc-post3.ppm)
          RCH_38=$(score_whole $D/t37-rc-post3.ppm $D/t37-rc-post8.ppm)
          plog "RC hops whole: pre-post1=$RCH_PRE1 p1-p3=$RCH_13 p3-p8=$RCH_38"
          # SE-park gate: arrival static + non-SP + SE tagline crop small.
          # DEPARTED > 5.0 does NOT fire on the SM->SE hop (~0.47-0.50 whole,
          # T32 G1 gate warning) and whole-vs-SE < 2.0 does NOT separate SM
          # (0.51-0.53 PIL); the TAG crop does (SE-SE <=0.14, SM-vs-SE 14.14).
          # The whole-vs-se line classifies the park post-hoc (< 0.2 PIL).
          SE_LIKE=0
          if is_static $RCH_13 && is_static $RCH_38 && is_nonsp $RS8 && is_setag $RT8; then
            plog "SE-LIKE (static + non-SP + se-tag) -> park for SnowJam Cross"
            SE_LIKE=1
          else
            plog "NO-SE-PARK (SM->SE chain did not park; no SnowJam Cross pressed)"
          fi
          if [ $SE_LIKE -eq 1 ]; then
            # Chain reproduction: ONE Cross (x Select) on the parked Select
            # Event (Snow Jam highlighted per T33 R2); arrival static 128 s,
            # no dwell pressure.
            sleep 5
            snap t37-sepre || fail SNAP_SEPRE
            read STP STP_P <<< $(score_setag $D/t37-sepre.ppm)
            plog "SEPRE se-tag mean=$STP p99=$STP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
            read SWP SWP_P <<< $(score_se $D/t37-sepre.ppm)
            plog "SEPRE vs-se mean=$SWP p99=$SWP_P"
            read SXP SXP_P <<< $(score_sm $D/t37-sepre.ppm)
            plog "SEPRE vs-sm mean=$SXP p99=$SXP_P"
            read SXSP SXSP_P <<< $(score_sp $D/t37-sepre.ppm)
            plog "SEPRE vs-sp mean=$SXSP p99=$SXSP_P"
            read SXPT SXPT_P <<< $(score_band $D/t37-sepre.ppm)
            plog "SEPRE vs-title mean=$SXPT p99=$SXPT_P"
            press K "SNOWJAM_CROSS"
            # MR-park confirmation series (short: the SE->MR transition is
            # already mapped by T33; the +40 s tail belongs to the Enter
            # Cross below), each scored vs title-band, SE whole-ref and MR
            # whole-ref (vs-sm/vs-sp/vs-zc/vs-sc/vs-menu post-hoc local)
            sleep 1; snap t37-sj-post1 || fail SNAP_SJ_POST1
            read J1 JP1 <<< $(score_band $D/t37-sj-post1.ppm)
            read JW1 JWP1 <<< $(score_se $D/t37-sj-post1.ppm)
            read JR1 JRP1 <<< $(score_mr $D/t37-sj-post1.ppm)
            plog "SJ post+1 titleband mean=$J1 p99=$JP1 vs-se mean=$JW1 p99=$JWP1 vs-mr mean=$JR1 p99=$JRP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
            sleep 2; snap t37-sj-post3 || fail SNAP_SJ_POST3
            read J3 JP3 <<< $(score_band $D/t37-sj-post3.ppm)
            read JW3 JWP3 <<< $(score_se $D/t37-sj-post3.ppm)
            read JR3 JRP3 <<< $(score_mr $D/t37-sj-post3.ppm)
            plog "SJ post+3 titleband mean=$J3 p99=$JP3 vs-se mean=$JW3 p99=$JWP3 vs-mr mean=$JR3 p99=$JRP3"
            sleep 5; snap t37-sj-post8 || fail SNAP_SJ_POST8
            read J8 JP8 <<< $(score_band $D/t37-sj-post8.ppm)
            read JW8 JWP8 <<< $(score_se $D/t37-sj-post8.ppm)
            read JR8 JRP8 <<< $(score_mr $D/t37-sj-post8.ppm)
            plog "SJ post+8 titleband mean=$J8 p99=$JP8 vs-se mean=$JW8 p99=$JWP8 vs-mr mean=$JR8 p99=$JRP8"
            # per-hop whole-frame diffs across the SE->MR chain
            SJH_PRE1=$(score_whole $D/t37-sepre.ppm $D/t37-sj-post1.ppm)
            SJH_13=$(score_whole $D/t37-sj-post1.ppm $D/t37-sj-post3.ppm)
            SJH_38=$(score_whole $D/t37-sj-post3.ppm $D/t37-sj-post8.ppm)
            plog "SJ hops whole: pre-post1=$SJH_PRE1 p1-p3=$SJH_13 p3-p8=$SJH_38"
            # MR-park gate: decisively left SE (departure hop ~10.6) + non-SE
            # + arrival static; the vs-mr line is the remote receipt (strict
            # < 2.0 whole-vs-MR bar confirmed post-hoc, T28/T29/T30/T31/T32/
            # T33 precedent — the Enter Cross press does NOT depend on it).
            MR_LIKE=0
            if is_departed $SJH_PRE1 && is_nonse $JW8 && is_static $SJH_13 && is_static $SJH_38; then
              plog "MR-LIKE (departed + non-SE + static) -> park for Enter Cross"
              MR_LIKE=1
            else
              plog "NO-MR-PARK (SE->MR chain did not park; no Enter Cross pressed)"
            fi
            if [ $MR_LIKE -eq 1 ]; then
              # Chain reproduction: ONE Cross (x Enter game) on the parked My
              # Rules (Continue highlighted per T33 R2 / T34 R1); the pre-race
              # panel arrival was static 98 s in T34 R1, no dwell pressure.
              sleep 5
              snap t37-mrpre || fail SNAP_MRPRE
              read RMP RMP_P <<< $(score_mr $D/t37-mrpre.ppm)
              plog "MRPRE vs-mr mean=$RMP p99=$RMP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
              read RMS RMS_P <<< $(score_se $D/t37-mrpre.ppm)
              plog "MRPRE vs-se mean=$RMS p99=$RMS_P"
              read RMPT RMPT_P <<< $(score_band $D/t37-mrpre.ppm)
              plog "MRPRE vs-title mean=$RMPT p99=$RMPT_P"
              press K "ENTER_CROSS"
              # Enter arrival series: fast cadence early (transition hops),
              # slow tail (multi-stage load->panel path), each scored vs
              # title-band, MR whole-ref and panel whole-ref (vs-se/vs-sm/
              # vs-sp/vs-zc/vs-sc/vs-menu post-hoc local)
              sleep 1; snap t37-mr-post1 || fail SNAP_MR_POST1
              read K1 KP1 <<< $(score_band $D/t37-mr-post1.ppm)
              read KR1 KRP1 <<< $(score_mr $D/t37-mr-post1.ppm)
              read KU1 KUP1 <<< $(score_pp $D/t37-mr-post1.ppm)
              plog "MR post+1 titleband mean=$K1 p99=$KP1 vs-mr mean=$KR1 p99=$KRP1 vs-pp mean=$KU1 p99=$KUP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
              sleep 2; snap t37-mr-post3 || fail SNAP_MR_POST3
              read K3 KP3 <<< $(score_band $D/t37-mr-post3.ppm)
              read KR3 KRP3 <<< $(score_mr $D/t37-mr-post3.ppm)
              read KU3 KUP3 <<< $(score_pp $D/t37-mr-post3.ppm)
              plog "MR post+3 titleband mean=$K3 p99=$KP3 vs-mr mean=$KR3 p99=$KRP3 vs-pp mean=$KU3 p99=$KUP3"
              sleep 5; snap t37-mr-post8 || fail SNAP_MR_POST8
              read K8 KP8 <<< $(score_band $D/t37-mr-post8.ppm)
              read KR8 KRP8 <<< $(score_mr $D/t37-mr-post8.ppm)
              read KU8 KUP8 <<< $(score_pp $D/t37-mr-post8.ppm)
              plog "MR post+8 titleband mean=$K8 p99=$KP8 vs-mr mean=$KR8 p99=$KRP8 vs-pp mean=$KU8 p99=$KUP8"
              sleep 7; snap t37-mr-post15 || fail SNAP_MR_POST15
              read K15 KP15 <<< $(score_band $D/t37-mr-post15.ppm)
              read KR15 KRP15 <<< $(score_mr $D/t37-mr-post15.ppm)
              read KU15 KUP15 <<< $(score_pp $D/t37-mr-post15.ppm)
              plog "MR post+15 titleband mean=$K15 p99=$KP15 vs-mr mean=$KR15 p99=$KRP15 vs-pp mean=$KU15 p99=$KUP15"
              sleep 10; snap t37-mr-post25 || fail SNAP_MR_POST25
              read K25 KP25 <<< $(score_band $D/t37-mr-post25.ppm)
              read KR25 KRP25 <<< $(score_mr $D/t37-mr-post25.ppm)
              read KU25 KUP25 <<< $(score_pp $D/t37-mr-post25.ppm)
              plog "MR post+25 titleband mean=$K25 p99=$KP25 vs-mr mean=$KR25 p99=$KRP25 vs-pp mean=$KU25 p99=$KUP25"
              sleep 15; snap t37-mr-post40 || fail SNAP_MR_POST40
              read K40 KP40 <<< $(score_band $D/t37-mr-post40.ppm)
              read KR40 KRP40 <<< $(score_mr $D/t37-mr-post40.ppm)
              read KU40 KUP40 <<< $(score_pp $D/t37-mr-post40.ppm)
              plog "MR post+40 titleband mean=$K40 p99=$KP40 vs-mr mean=$KR40 p99=$KRP40 vs-pp mean=$KU40 p99=$KUP40"
              # per-hop whole-frame diffs across the Enter transition chain
              MRH_PRE1=$(score_whole $D/t37-mrpre.ppm $D/t37-mr-post1.ppm)
              MRH_13=$(score_whole $D/t37-mr-post1.ppm $D/t37-mr-post3.ppm)
              MRH_38=$(score_whole $D/t37-mr-post3.ppm $D/t37-mr-post8.ppm)
              MRH_815=$(score_whole $D/t37-mr-post8.ppm $D/t37-mr-post15.ppm)
              MRH_1525=$(score_whole $D/t37-mr-post15.ppm $D/t37-mr-post25.ppm)
              MRH_2540=$(score_whole $D/t37-mr-post25.ppm $D/t37-mr-post40.ppm)
              plog "MR hops whole: pre-post1=$MRH_PRE1 p1-p3=$MRH_13 p3-p8=$MRH_38 p8-p15=$MRH_815 p15-p25=$MRH_1525 p25-p40=$MRH_2540"
              # panel settling: 2 x 10 s (band + vs-mr + vs-pp in-script;
              # full vs-ref panel post-hoc local — keeps added scoring tight)
              for N in 1 2; do
                sleep 10; snap t37-mr-stab$N || fail SNAP_MR_STAB$N
                read M P <<< $(score_band $D/t37-mr-stab$N.ppm)
                read MT MTP <<< $(score_mr $D/t37-mr-stab$N.ppm)
                read MU MUP <<< $(score_pp $D/t37-mr-stab$N.ppm)
                plog "MR_STAB$N titleband mean=$M p99=$P vs-mr mean=$MT p99=$MTP vs-pp mean=$MU p99=$MUP MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
              done
              MRH_40S1=$(score_whole $D/t37-mr-post40.ppm $D/t37-mr-stab1.ppm)
              MRH_S12=$(score_whole $D/t37-mr-stab1.ppm $D/t37-mr-stab2.ppm)
              plog "MR panel hops whole: post40-stab1=$MRH_40S1 stab1-stab2=$MRH_S12"
              read MS2 MSP2 <<< $(score_mr $D/t37-mr-stab2.ppm)
              # PP-LIKE settled-panel gate: decisively left MR (departure hop
              # ~12.4) + arrival static x3 over ~35 s + non-MR; the vs-pp
              # line is the remote receipt (strict < 2.0 whole-vs-panel bar
              # confirmed post-hoc, T28-T34 precedent — the X-Continue Cross
              # press does NOT depend on it).
              PP_LIKE=0
              if is_departed $MRH_PRE1 && is_static $MRH_2540 && is_static $MRH_40S1 && is_static $MRH_S12 && is_nonmr $MS2; then
                plog "PP-LIKE (departed + static x3 + non-MR) -> park for X-Continue Cross"
                PP_LIKE=1
              else
                plog "NO-PP-PARK (Enter chain did not settle on panel; no X-Continue Cross pressed)"
              fi
              if [ $PP_LIKE -eq 1 ]; then
                # Chain reproduction: ONE Cross (X Continue) on the settled
                # pre-race panel (Snow Jam - Race per T35 R1); panel static
                # 79 s, no dwell pressure.
                sleep 5
                snap t37-pppre || fail SNAP_PPPRE
                read PUP PUP_P <<< $(score_pp $D/t37-pppre.ppm)
                plog "PPPRE vs-pp mean=$PUP p99=$PUP_P MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
                read PMP PMP_P <<< $(score_mr $D/t37-pppre.ppm)
                plog "PPPRE vs-mr mean=$PMP p99=$PMP_P"
                read PPT PPT_P <<< $(score_band $D/t37-pppre.ppm)
                plog "PPPRE vs-title mean=$PPT p99=$PPT_P"
                press K "XCROSS"
                # X arrival series: fast cadence early (transition hops),
                # slow tail (slow next-screen loads), each scored vs
                # title-band and panel whole-ref (vs-mr/vs-se/vs-sm/vs-sp/
                # vs-zc/vs-sc/vs-menu post-hoc local)
                sleep 1; snap t37-x-post1 || fail SNAP_X_POST1
                read X1 XP1 <<< $(score_band $D/t37-x-post1.ppm)
                read XU1 XUP1 <<< $(score_pp $D/t37-x-post1.ppm)
                plog "X post+1 titleband mean=$X1 p99=$XP1 vs-pp mean=$XU1 p99=$XUP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
                sleep 2; snap t37-x-post3 || fail SNAP_X_POST3
                read X3 XP3 <<< $(score_band $D/t37-x-post3.ppm)
                read XU3 XUP3 <<< $(score_pp $D/t37-x-post3.ppm)
                plog "X post+3 titleband mean=$X3 p99=$XP3 vs-pp mean=$XU3 p99=$XUP3"
                sleep 5; snap t37-x-post8 || fail SNAP_X_POST8
                read X8 XP8 <<< $(score_band $D/t37-x-post8.ppm)
                read XU8 XUP8 <<< $(score_pp $D/t37-x-post8.ppm)
                plog "X post+8 titleband mean=$X8 p99=$XP8 vs-pp mean=$XU8 p99=$XUP8"
                sleep 7; snap t37-x-post15 || fail SNAP_X_POST15
                read X15 XP15 <<< $(score_band $D/t37-x-post15.ppm)
                read XU15 XUP15 <<< $(score_pp $D/t37-x-post15.ppm)
                plog "X post+15 titleband mean=$X15 p99=$XP15 vs-pp mean=$XU15 p99=$XUP15"
                sleep 10; snap t37-x-post25 || fail SNAP_X_POST25
                read X25 XP25 <<< $(score_band $D/t37-x-post25.ppm)
                read XU25 XUP25 <<< $(score_pp $D/t37-x-post25.ppm)
                plog "X post+25 titleband mean=$X25 p99=$XP25 vs-pp mean=$XU25 p99=$XUP25"
                sleep 15; snap t37-x-post40 || fail SNAP_X_POST40
                read X40 XP40 <<< $(score_band $D/t37-x-post40.ppm)
                read XU40 XUP40 <<< $(score_pp $D/t37-x-post40.ppm)
                plog "X post+40 titleband mean=$X40 p99=$XP40 vs-pp mean=$XU40 p99=$XUP40"
                # per-hop whole-frame diffs across the X transition chain
                XH_PRE1=$(score_whole $D/t37-pppre.ppm $D/t37-x-post1.ppm)
                XH_13=$(score_whole $D/t37-x-post1.ppm $D/t37-x-post3.ppm)
                XH_38=$(score_whole $D/t37-x-post3.ppm $D/t37-x-post8.ppm)
                XH_815=$(score_whole $D/t37-x-post8.ppm $D/t37-x-post15.ppm)
                XH_1525=$(score_whole $D/t37-x-post15.ppm $D/t37-x-post25.ppm)
                XH_2540=$(score_whole $D/t37-x-post25.ppm $D/t37-x-post40.ppm)
                plog "X hops whole: pre-post1=$XH_PRE1 p1-p3=$XH_13 p3-p8=$XH_38 p8-p15=$XH_815 p15-p25=$XH_1525 p25-p40=$XH_2540"
                # LIVE-LIKE proxy gate: decisively left the panel (XCROSS
                # departure hop) + arrival non-panel (x-post40 vs-pp) +
                # motion across the late tail (last two hops). The true
                # LIVE-RACE criterion (race clock advancing + position/
                # progress HUD) is read off viewed snaps post-hoc (T35 G1
                # gate note: gate on the HUD, not the frame).
                LIVE_LIKE=0
                if is_departed $XH_PRE1 && is_nonpp $XU40 && is_departed $XH_1525 && is_departed $XH_2540; then
                  plog "LIVE-LIKE (departed + non-panel + motion x2) -> pre-nudge snap + ONE steering nudge"
                  LIVE_LIKE=1
                else
                  plog "NO-LIVE-PARK (X chain not live gameplay; no nudge pressed)"
                fi
                if [ $LIVE_LIKE -eq 1 ]; then
                  # T37 nudge: ONE D-pad Left tap (Left = Keyboard/Left,
                  # PCSX2.ini:576; xdotool key Left; 300 ms keydown — SAME
                  # input class as T36, unchanged) on live gameplay, with a
                  # PRE-nudge pair (noise floor, no input between) + DENSE
                  # post-nudge series (1 s cadence x 10 s). HUD + rider
                  # tracking read off viewed snaps post-hoc local.
                  sleep 5
                  snap t37-npre1 || fail SNAP_NPRE1
                  read NUP1 NUP_P1 <<< $(score_pp $D/t37-npre1.ppm)
                  plog "NPRE1 vs-pp mean=$NUP1 p99=$NUP_P1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
                  read NPT1 NPT_P1 <<< $(score_band $D/t37-npre1.ppm)
                  plog "NPRE1 vs-title mean=$NPT1 p99=$NPT_P1"
                  sleep 2
                  snap t37-npre2 || fail SNAP_NPRE2
                  read NUP2 NUP_P2 <<< $(score_pp $D/t37-npre2.ppm)
                  plog "NPRE2 vs-pp mean=$NUP2 p99=$NUP_P2 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
                  read NPT2 NPT_P2 <<< $(score_band $D/t37-npre2.ppm)
                  plog "NPRE2 vs-title mean=$NPT2 p99=$NPT_P2"
                  press_nudge Left "NUDGE_LEFT"
                  # dense post-nudge series: 1 s cadence x 10 s, each scored
                  # vs title-band and panel whole-ref (HUD delta + rider
                  # tracking read off viewed snaps post-hoc local)
                  sleep 1; snap t37-d-post1 || fail SNAP_D_POST1
                  read D1 DP1 <<< $(score_band $D/t37-d-post1.ppm)
                  read DU1 DUP1 <<< $(score_pp $D/t37-d-post1.ppm)
                  plog "D post+1 titleband mean=$D1 p99=$DP1 vs-pp mean=$DU1 p99=$DUP1 MENU_T+:$(( $(date -u +%s) - T_BOOT ))"
                  sleep 1; snap t37-d-post2 || fail SNAP_D_POST2
                  read D2 DP2 <<< $(score_band $D/t37-d-post2.ppm)
                  read DU2 DUP2 <<< $(score_pp $D/t37-d-post2.ppm)
                  plog "D post+2 titleband mean=$D2 p99=$DP2 vs-pp mean=$DU2 p99=$DUP2"
                  sleep 1; snap t37-d-post3 || fail SNAP_D_POST3
                  read D3 DP3 <<< $(score_band $D/t37-d-post3.ppm)
                  read DU3 DUP3 <<< $(score_pp $D/t37-d-post3.ppm)
                  plog "D post+3 titleband mean=$D3 p99=$DP3 vs-pp mean=$DU3 p99=$DUP3"
                  sleep 1; snap t37-d-post4 || fail SNAP_D_POST4
                  read D4 DP4 <<< $(score_band $D/t37-d-post4.ppm)
                  read DU4 DUP4 <<< $(score_pp $D/t37-d-post4.ppm)
                  plog "D post+4 titleband mean=$D4 p99=$DP4 vs-pp mean=$DU4 p99=$DUP4"
                  sleep 1; snap t37-d-post5 || fail SNAP_D_POST5
                  read D5 DP5 <<< $(score_band $D/t37-d-post5.ppm)
                  read DU5 DUP5 <<< $(score_pp $D/t37-d-post5.ppm)
                  plog "D post+5 titleband mean=$D5 p99=$DP5 vs-pp mean=$DU5 p99=$DUP5"
                  sleep 1; snap t37-d-post6 || fail SNAP_D_POST6
                  read D6 DP6 <<< $(score_band $D/t37-d-post6.ppm)
                  read DU6 DUP6 <<< $(score_pp $D/t37-d-post6.ppm)
                  plog "D post+6 titleband mean=$D6 p99=$DP6 vs-pp mean=$DU6 p99=$DUP6"
                  sleep 1; snap t37-d-post7 || fail SNAP_D_POST7
                  read D7 DP7 <<< $(score_band $D/t37-d-post7.ppm)
                  read DU7 DUP7 <<< $(score_pp $D/t37-d-post7.ppm)
                  plog "D post+7 titleband mean=$D7 p99=$DP7 vs-pp mean=$DU7 p99=$DUP7"
                  sleep 1; snap t37-d-post8 || fail SNAP_D_POST8
                  read D8 DP8 <<< $(score_band $D/t37-d-post8.ppm)
                  read DU8 DUP8 <<< $(score_pp $D/t37-d-post8.ppm)
                  plog "D post+8 titleband mean=$D8 p99=$DP8 vs-pp mean=$DU8 p99=$DUP8"
                  sleep 1; snap t37-d-post9 || fail SNAP_D_POST9
                  read D9 DP9 <<< $(score_band $D/t37-d-post9.ppm)
                  read DU9 DUP9 <<< $(score_pp $D/t37-d-post9.ppm)
                  plog "D post+9 titleband mean=$D9 p99=$DP9 vs-pp mean=$DU9 p99=$DUP9"
                  sleep 1; snap t37-d-post10 || fail SNAP_D_POST10
                  read D10 DP10 <<< $(score_band $D/t37-d-post10.ppm)
                  read DU10 DUP10 <<< $(score_pp $D/t37-d-post10.ppm)
                  plog "D post+10 titleband mean=$D10 p99=$DP10 vs-pp mean=$DU10 p99=$DUP10"
                  # per-hop whole-frame diffs across the dense chain
                  DH_PRE=$(score_whole $D/t37-npre1.ppm $D/t37-npre2.ppm)
                  DH_01=$(score_whole $D/t37-npre2.ppm $D/t37-d-post1.ppm)
                  DH_12=$(score_whole $D/t37-d-post1.ppm $D/t37-d-post2.ppm)
                  DH_23=$(score_whole $D/t37-d-post2.ppm $D/t37-d-post3.ppm)
                  DH_34=$(score_whole $D/t37-d-post3.ppm $D/t37-d-post4.ppm)
                  DH_45=$(score_whole $D/t37-d-post4.ppm $D/t37-d-post5.ppm)
                  DH_56=$(score_whole $D/t37-d-post5.ppm $D/t37-d-post6.ppm)
                  DH_67=$(score_whole $D/t37-d-post6.ppm $D/t37-d-post7.ppm)
                  DH_78=$(score_whole $D/t37-d-post7.ppm $D/t37-d-post8.ppm)
                  DH_89=$(score_whole $D/t37-d-post8.ppm $D/t37-d-post9.ppm)
                  DH_910=$(score_whole $D/t37-d-post9.ppm $D/t37-d-post10.ppm)
                  plog "D hops whole: pre1-pre2=$DH_PRE pre2-d1=$DH_01 d1-d2=$DH_12 d2-d3=$DH_23 d3-d4=$DH_34 d4-d5=$DH_45 d5-d6=$DH_56 d6-d7=$DH_67 d7-d8=$DH_78 d8-d9=$DH_89 d9-d10=$DH_910"
                fi
              fi
            fi
          fi
        fi
      fi
    fi
  fi
else
  plog "NO-PARK (menu-like gate never fired in <=3 attempts; no menu Cross pressed)"
fi
ls -la $D/t37-*.jpg $E
kill $(cat $D/pcsx2.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T37_DONE
