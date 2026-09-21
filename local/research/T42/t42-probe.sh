#!/usr/bin/env bash
# T42 modal probe (forensics/hygiene, NOT the experiment run): boots the
# T4 build with the run's flags on the audio-down VM, snaps at T+25
# (modal expected: T41 R1/R2 signature), applies ONE v2-order dismissal
# (first visible non-root non-SSX window gets Return), snaps at T+30,
# then kills pcsx2. Decides: (a) modal present? (b) does the v2-order
# first-hit land on the modal or (inertly) on the main window?
# No game inputs. Emulog preserved before boot (rotation-style).
set -x
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
D=/home/brad/pcsx2-t4
E=$D/dat/PCSX2/logs/emulog.txt
cp $E $D/dat/PCSX2/logs/emulog-pre-t42-probe.txt
ls -la $D/dat/PCSX2/logs/emulog-pre-t42-probe.txt
pkill Xvfb || true
sleep 2
setsid nohup Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb-t42probe.log 2>&1 < /dev/null &
sleep 2
pgrep -a Xvfb || true
date -u
nohup $D/pcsx2/build/bin/pcsx2-qt -nogui -slowboot -turbo -datapath $D/dat -logfile $D/logs/boot-t42probe.log -- "$D/inputs/SSX 3 (USA).iso" > $D/logs/boot-t42probe.stdout 2>&1 &
echo PCBOOT:$!
sleep 25
date -u
xwd -root -out $D/t42probe1.xwd
xwdtopnm $D/t42probe1.xwd > $D/t42probe1.ppm
rm -f $D/t42probe1.xwd
pnmtojpeg -quality=80 $D/t42probe1.ppm > $D/t42probe1.jpg
ls -la $D/t42probe1.ppm $D/t42probe1.jpg
IDS=$(xdotool search --onlyvisible --name '.*' 2>/dev/null || true)
echo "PROBE_IDS:$IDS"
for W in $IDS; do
  N=$(xdotool getwindowname "$W" 2>/dev/null || echo UNKNOWN)
  eval "$(xdotool getwindowgeometry --shell "$W" 2>/dev/null | grep -E '^(WIDTH|HEIGHT)=')"
  echo "PROBE_WIN:$W:$N:${WIDTH}x${HEIGHT}"
  case "$N" in *SSX*) echo "PROBE_SKIP_GAME:$W"; continue;; esac
  if [ "${WIDTH}x${HEIGHT}" = "1280x1024" ]; then echo "PROBE_SKIP_ROOT:$W"; continue; fi
  echo "PROBE_DISMISS:$W:$N"
  xdotool windowfocus --sync "$W" || echo PROBE_FOCUS_FAILED
  xdotool key --window "$W" Return || echo PROBE_KEY_FAILED
  echo PROBE_DISMISSED_ONE
  break
done
sleep 3
xwd -root -out $D/t42probe2.xwd
xwdtopnm $D/t42probe2.xwd > $D/t42probe2.ppm
rm -f $D/t42probe2.xwd
pnmtojpeg -quality=80 $D/t42probe2.ppm > $D/t42probe2.jpg
ls -la $D/t42probe2.ppm $D/t42probe2.jpg
pkill -f pcsx2-qt || true
sleep 5
pgrep -a pcsx2-qt || echo PROBE_PCSX2_DEAD
echo T42_PROBE_DONE
