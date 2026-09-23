#!/bin/bash
# N6 launch 4 (final): per-button/stick mapping proof via [padlog] on the
# padlog build. Stays at the title (fast ticks) for every press except START,
# which goes last and advances to the menu. Ends with a 60 s idle (log must
# stay silent). Cap ~420 s.
set -u
D=622c49b1
OUT=~/dev/ssx3-work/N6/launch4
FILES=/storage/emulated/0/Android/data/com.ps2x.runner/files
DSCRAP=/data/local/tmp/n6
EVPAD=/dev/input/event8
mkdir -p "$OUT"
echo "LAUNCH4_AT=$(date -u +%FT%TZ)"
adb -s $D shell "cat /data/local/tmp/mg/LEASE; dumpsys window policy 2>/dev/null | grep -m1 showing" 2>&1 | tee "$OUT/precheck.txt"

printf '# N6 launch4: pad-log mapping proof, NO pad script\nPS2X_CD_IMAGE=/storage/emulated/0/Android/data/com.ps2x.runner/files/SSX3.iso\nPS2X_SKIP_MOVIE=1\nPS2X_FRAME_DUMP_DIR=/storage/emulated/0/Android/data/com.ps2x.runner/files/frames\nPS2X_PAD_LOG=1\n' > "$OUT/ps2x-launch4.env"
adb -s $D shell "mkdir -p $DSCRAP && rm -rf $FILES/frames && mkdir -p $FILES/frames && rm -f $DSCRAP/sc4-*.png && echo DIRS_OK"
adb -s $D push "$OUT/ps2x-launch4.env" $FILES/ps2x.env 2>&1 | tail -1
adb -s $D shell am force-stop com.ps2x.runner
adb -s $D logcat -c
adb -s $D logcat -b main -b crash -s ps2x raylib > "$OUT/logcat-ps2x-raylib.txt" 2>&1 &
LC1=$!
adb -s $D shell am start -n com.ps2x.runner/android.app.NativeActivity 2>&1 | tee "$OUT/am-start.txt"
sleep 6
adb -s $D shell input keyevent 4
sleep 4
adb -s $D shell "screencap -p $DSCRAP/sc4-focus.png; pidof com.ps2x.runner" 2>&1 | tee "$OUT/focus.txt"

scap() { adb -s $D shell "screencap -p $DSCRAP/sc4-$1.png" 2>&1; }
# Button hold with wall markers in a sidecar (adb clock ~= logcat clock).
press() { # $1=name $2=code $3=hold_s
  echo "PRESS $1 $(date -u +%T)" | tee -a "$OUT/press-marks.txt"
  adb -s $D shell "sendevent $EVPAD 1 $2 1; sendevent $EVPAD 0 0 0; sleep $3; sendevent $EVPAD 1 $2 0; sendevent $EVPAD 0 0 0" 2>&1
  sleep 1
}
# Axis deflect-and-hold with markers.
axis() { # $1=name $2=code $3=value $4=hold_s
  echo "AXIS $1=$3 $(date -u +%T)" | tee -a "$OUT/press-marks.txt"
  adb -s $D shell "sendevent $EVPAD 3 $2 $3; sendevent $EVPAD 0 0 0; sleep $4; sendevent $EVPAD 3 $2 0; sendevent $EVPAD 0 0 0" 2>&1
  sleep 1
}

echo "--- wait for title ---"
sleep 22
scap p0-title
: > "$OUT/press-marks.txt"

# Face + shoulders + sticks-click + select/mode at the title (no screen change).
press A-cross 304 1.5
press B-circle 305 1.5
press X-square 308 1.5
press Y-triangle 307 1.5
press L1 310 1.5
press R1 311 1.5
press L2-digi 312 1.5
press R2-digi 313 1.5
press L3 317 1.5
press R3 318 1.5
press SELECT 314 1.5
press MODE 316 1.5
scap p1-title-still
# Dpad keys + hat axes.
press DPAD-UP 544 1
press DPAD-DOWN 545 1
press DPAD-LEFT 546 1
press DPAD-RIGHT 547 1
axis HAT-X-pos 16 1 1
axis HAT-Y-pos 17 1 1
# Sticks full deflection.
axis ABS-X-max 0 32767 1
axis ABS-X-min 0 -32767 1
axis ABS-Y-max 1 32767 1
axis ABS-Y-min 1 -32767 1
axis ABS-Z-max 2 32767 1
axis ABS-RZ-max 5 32767 1
# Analog triggers (expect: NO pad change; only digital L2/R2 map).
axis ABS-GAS 9 32767 1
axis ABS-BRAKE 10 32767 1
scap p2-before-start
# START last: advances title -> menu.
press START 315 2
sleep 8
scap p3-menu

echo "--- 60 s idle at menu (padlog must stay silent) ---"
echo "IDLE_BEGIN $(date -u +%FT%TZ)" | tee -a "$OUT/press-marks.txt"
sleep 60
echo "IDLE_END $(date -u +%FT%TZ)" | tee -a "$OUT/press-marks.txt"
scap p4-idle
adb -s $D shell "pidof com.ps2x.runner; tail -1 $FILES/frames/upload-latest.txt" 2>&1 | tee "$OUT/idle-end.txt"

for s in focus p0-title p1-title-still p2-before-start p3-menu p4-idle; do
  adb -s $D pull $DSCRAP/sc4-$s.png "$OUT/sc4-$s.png" 2>&1 | tail -1
done
sleep 2
kill $LC1 2>/dev/null
sleep 1
grep -c 'padlog' "$OUT/logcat-ps2x-raylib.txt" | sed 's/^/PADLOG_LINES=/'
grep 'padlog' "$OUT/logcat-ps2x-raylib.txt" | head -60 | tee "$OUT/padlog-lines.txt" | tail -40
sha256sum "$OUT"/sc4-*.png | tee "$OUT/scap-sha.txt"
adb -s $D shell am force-stop com.ps2x.runner
echo "LAUNCH4_END=$(date -u +%FT%TZ)"
