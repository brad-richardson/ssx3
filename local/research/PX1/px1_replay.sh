#!/bin/bash
# PX1: replay our converted GS stream through the T48-pinned (G13) gsrunner.
# Runs inside bytesize WSL. $1 = input .gs.zst basename (staged at
# /mnt/c/Users/bradr/), $2 = out label. Frames land in ~/px1/frames-<label>/.
set -eu
G=/home/brad/pcsx2-g7
R=/home/brad/px1
IN_ZST=$1
LABEL=$2
PROBE=${3:-none}
RANGE=${4:-0,4}
case $PROBE in
  none) EXTRA_ARGS="" ;;
  dumps) EXTRA_ARGS="-dump tex,tr,rt,f -dumprangef $RANGE -dumprange 0,-1,1 -dumpdirhw $R/hw-$LABEL" ;;
  dpi) EXTRA_ARGS="-renderhacks dpi" ;;
  af) EXTRA_ARGS="-renderhacks af" ;;
  tinrt) EXTRA_ARGS="-renderhacks tinrt" ;;
  dsf) EXTRA_ARGS="-renderhacks dsf" ;;
  *) echo "unknown probe $PROBE"; exit 2 ;;
esac
mkdir -p $R $R/run
# Stage the pinned gsrunner once (T48 pre-patch pin 8e446ff1...).
if [ ! -x $R/run/pcsx2-gsrunner ]; then
  cp $G/pre-t48/pcsx2-gsrunner $R/run/
  ln -sfn $G/pre-t48/resources $R/run/resources
  ln -sfn $G/pre-t48/translations $R/run/translations
fi
sha256sum $R/run/pcsx2-gsrunner
cp /mnt/c/Users/bradr/$IN_ZST $R/
cd $R
gunzip -f $IN_ZST
IN=${IN_ZST%.gz}
OUT=$R/frames-$LABEL
mkdir -p $OUT
rm -f $OUT/*.png
Xvfb :98 -screen 0 1280x1024x24 >/dev/null 2>&1 & XP=$!
export DISPLAY=:98
cd $R/run
timeout 1500 ./pcsx2-gsrunner -renderer ${REN:-vulkan} -dumpdir $OUT -logfile $R/gsrunner-$LABEL.log \
  -loop 1 -noshadercache -surfaceless -ini $G/g10-uncorrected.ini $EXTRA_ARGS -- $R/$IN || echo "gsrunner rc=$?"
kill $XP 2>/dev/null || true
ls $OUT | wc -l
ls $OUT | head -3; ls $OUT | tail -3
tail -5 $R/gsrunner-$LABEL.log
