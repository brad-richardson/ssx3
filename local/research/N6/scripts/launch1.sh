#!/bin/bash
# N6 launch 1: Step 1 — characterize existing input paths with the N4 APK (no code change).
# Clean env (NO pad script). Tests: injected BUTTON_* (expect: ignored),
# sendevent START on /dev/input/event8 (expect: title->menu via real gamepad path),
# injected DPAD/X/ENTER (expect: work via keyboard fallback).
# Cap ~420 s.
set -u
D=622c49b1
OUT=~/dev/ssx3-work/N6/launch1
FILES=/storage/emulated/0/Android/data/com.ps2x.runner/files
DSCRAP=/data/local/tmp/n6
EVDEV=/dev/input/event8
mkdir -p "$OUT"
echo "LAUNCH1_AT=$(date -u +%FT%TZ)"

printf '# N6 launch1: clean env, NO pad script\nPS2X_CD_IMAGE=/storage/emulated/0/Android/data/com.ps2x.runner/files/SSX3.iso\nPS2X_SKIP_MOVIE=1\nPS2X_FRAME_DUMP_DIR=/storage/emulated/0/Android/data/com.ps2x.runner/files/frames\n' > "$OUT/ps2x-launch1.env"
cat "$OUT/ps2x-launch1.env"

adb -s $D shell "cat /data/local/tmp/mg/LEASE; dumpsys window policy 2>/dev/null | grep -m1 showing" 2>&1 | tee "$OUT/precheck.txt"
adb -s $D shell "mkdir -p $DSCRAP && rm -rf $FILES/frames && mkdir -p $FILES/frames && rm -f $DSCRAP/scap-*.png && echo DIRS_OK"
adb -s $D push "$OUT/ps2x-launch1.env" $FILES/ps2x.env 2>&1 | tail -1
adb -s $D shell "cat $FILES/ps2x.env"
adb -s $D shell am force-stop com.ps2x.runner
adb -s $D logcat -c
adb -s $D logcat -b main -b crash -s ps2x raylib > "$OUT/logcat-ps2x-raylib.txt" 2>&1 &
LC1=$!
adb -s $D shell am start -n com.ps2x.runner/android.app.NativeActivity 2>&1 | tee "$OUT/am-start.txt"
sleep 6
adb -s $D shell input keyevent 4
sleep 4
adb -s $D shell "screencap -p $DSCRAP/scap-focus.png; pidof com.ps2x.runner" 2>&1 | tee "$OUT/focus.txt"

scap() { adb -s $D shell "screencap -p $DSCRAP/scap-$1.png; cat $FILES/frames/upload-latest.txt 2>/dev/null | tail -1" 2>&1 | tee "$OUT/tick-$1.txt"; }
burst() { # $1=keycode $2=count
  for _i in $(seq 1 "$2"); do adb -s $D shell input keyevent "$1" >/dev/null 2>&1; sleep 0.3; done
}
sebtn() { # $1=linux keycode, hold 3 s, one round trip
  adb -s $D shell "sendevent $EVDEV 1 $1 1; sendevent $EVDEV 0 0 0; sleep 3; sendevent $EVDEV 1 $1 0; sendevent $EVDEV 0 0 0" 2>&1
}

echo "--- wait for title (~25 s) ---"
sleep 20
scap t0-title
sleep 5
scap t0b-title

echo "--- T1: injected BUTTON_START x8 (expect: NO change) ---"
burst KEYCODE_BUTTON_START 8
scap t1-after-btnstart

echo "--- T2: injected BUTTON_A x8 (expect: NO change) ---"
burst KEYCODE_BUTTON_A 8
scap t2-after-btna

echo "--- T3: REAL gamepad START via sendevent/315 hold 3s (expect: main menu) ---"
sebtn 315
sleep 8
scap t3-after-realstart

echo "--- T4: injected ENTER x8 fallback (expect: main menu if T3 failed) ---"
burst KEYCODE_ENTER 8
sleep 8
scap t4-after-enter

echo "--- T5: injected DPAD_DOWN x8 (expect: selection moves) ---"
burst KEYCODE_DPAD_DOWN 8
sleep 4
scap t5-after-dpaddown

echo "--- T6: injected DPAD_UP x8 (expect: selection back) ---"
burst KEYCODE_DPAD_UP 8
sleep 4
scap t6-after-dpadup

echo "--- T7: injected X x8 (expect: confirm -> submenu) ---"
burst KEYCODE_X 8
sleep 10
scap t7-after-x

echo "--- T8: REAL gamepad A/304 via sendevent hold 3s ---"
sebtn 304
sleep 10
scap t8-after-reala

echo "--- T9: 60 s idle (expect: no phantom transition) ---"
scap t9-idle0
sleep 60
scap t9-idle1
adb -s $D shell "pidof com.ps2x.runner; ls $FILES/frames | wc -l; tail -2 $FILES/frames/upload-latest.txt" 2>&1 | tee "$OUT/idle-end.txt"

for s in focus t0-title t0b-title t1-after-btnstart t2-after-btna t3-after-realstart t4-after-enter t5-after-dpaddown t6-after-dpadup t7-after-x t8-after-reala t9-idle0 t9-idle1; do
  adb -s $D pull $DSCRAP/scap-$s.png "$OUT/scap-$s.png" 2>&1 | tail -1
done
adb -s $D pull $FILES/frames/upload-latest.txt "$OUT/upload-latest.txt" 2>&1 | tail -1
sha256sum "$OUT"/scap-*.png | tee "$OUT/scap-sha.txt"
ls -l "$OUT"
kill $LC1 2>/dev/null
adb -s $D shell am force-stop com.ps2x.runner
echo "LAUNCH1_END=$(date -u +%FT%TZ)"
