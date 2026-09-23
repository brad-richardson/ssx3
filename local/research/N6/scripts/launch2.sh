#!/bin/bash
# N6 launch 2: validate the N6 build (input union). Injected keys drive
# title -> main menu -> Select Character with NO pad script; sendevent covers
# the real dpad + triangle paths. Ends with a 60 s idle check. Cap ~420 s.
set -u
D=622c49b1
OUT=~/dev/ssx3-work/N6/launch2
FILES=/storage/emulated/0/Android/data/com.ps2x.runner/files
DSCRAP=/data/local/tmp/n6
EVDEV=/dev/input/event8
mkdir -p "$OUT"
echo "LAUNCH2_AT=$(date -u +%FT%TZ)"
adb -s $D shell "cat /data/local/tmp/mg/LEASE; dumpsys window policy 2>/dev/null | grep -m1 showing" 2>&1 | tee "$OUT/precheck.txt"

printf '# N6 launch2: clean env, NO pad script\nPS2X_CD_IMAGE=/storage/emulated/0/Android/data/com.ps2x.runner/files/SSX3.iso\nPS2X_SKIP_MOVIE=1\nPS2X_FRAME_DUMP_DIR=/storage/emulated/0/Android/data/com.ps2x.runner/files/frames\n' > "$OUT/ps2x-launch2.env"
adb -s $D shell "mkdir -p $DSCRAP && rm -rf $FILES/frames && mkdir -p $FILES/frames && rm -f $DSCRAP/sc2-*.png && echo DIRS_OK"
adb -s $D push "$OUT/ps2x-launch2.env" $FILES/ps2x.env 2>&1 | tail -1
adb -s $D shell "cat $FILES/ps2x.env"
adb -s $D shell am force-stop com.ps2x.runner
adb -s $D logcat -c
adb -s $D logcat -b main -b crash -s ps2x raylib > "$OUT/logcat-ps2x-raylib.txt" 2>&1 &
LC1=$!
adb -s $D shell am start -n com.ps2x.runner/android.app.NativeActivity 2>&1 | tee "$OUT/am-start.txt"
sleep 6
adb -s $D shell input keyevent 4
sleep 4
adb -s $D shell "screencap -p $DSCRAP/sc2-focus.png; pidof com.ps2x.runner" 2>&1 | tee "$OUT/focus.txt"

scap() { adb -s $D shell "screencap -p $DSCRAP/sc2-$1.png; cat $FILES/frames/upload-latest.txt 2>/dev/null | tail -1" 2>&1 | tee "$OUT/tick-$1.txt"; }
burst() {
  for _i in $(seq 1 "$2"); do adb -s $D shell input keyevent "$1" >/dev/null 2>&1; sleep 0.3; done
}
sebtn() {
  adb -s $D shell "sendevent $EVDEV 1 $1 1; sendevent $EVDEV 0 0 0; sleep 3; sendevent $EVDEV 1 $1 0; sendevent $EVDEV 0 0 0" 2>&1
}

echo "--- wait for title ---"
sleep 22
scap v0-title

echo "--- V1: injected ENTER x8 (expect: main menu) ---"
burst KEYCODE_ENTER 8
sleep 8
scap v1-after-enter

echo "--- V2: REAL dpad-DOWN via sendevent/545 hold 3s (expect: Conquer) ---"
sebtn 545
sleep 6
scap v2-after-realdpad

echo "--- V3: injected DPAD_UP x8 AFTER gamepad latched (expect: Single Event; proves union fix) ---"
burst KEYCODE_DPAD_UP 8
sleep 6
scap v3-after-dpadup

echo "--- V4: REAL triangle/Y via sendevent/307 hold 3s (expect: back to title) ---"
sebtn 307
sleep 8
scap v4-after-realtri

echo "--- V5: injected ENTER x8 (expect: main menu again) ---"
burst KEYCODE_ENTER 8
sleep 8
scap v5-after-enter2

echo "--- V6: injected X x8 (expect: Select Character) ---"
burst KEYCODE_X 8
sleep 25
scap v6-after-x

echo "--- V7: 60 s idle (expect: no phantom transition) ---"
sleep 45
scap v7-idle0
sleep 60
scap v7-idle1
adb -s $D shell "pidof com.ps2x.runner; ls $FILES/frames | wc -l; tail -1 $FILES/frames/upload-latest.txt" 2>&1 | tee "$OUT/idle-end.txt"

for s in focus v0-title v1-after-enter v2-after-realdpad v3-after-dpadup v4-after-realtri v5-after-enter2 v6-after-x v7-idle0 v7-idle1; do
  adb -s $D pull $DSCRAP/sc2-$s.png "$OUT/sc2-$s.png" 2>&1 | tail -1
done
adb -s $D pull $FILES/frames/upload-latest.txt "$OUT/upload-latest.txt" 2>&1 | tail -1
sha256sum "$OUT"/sc2-*.png | tee "$OUT/scap-sha.txt"
ls -l "$OUT" | head -30
kill $LC1 2>/dev/null
adb -s $D shell am force-stop com.ps2x.runner
echo "LAUNCH2_END=$(date -u +%FT%TZ)"
