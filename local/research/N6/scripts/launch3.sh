#!/bin/bash
# N6 launch 3: mechanism proofs on the N6 build (input union).
# W1 event5-ENTER hold -> menu (keyboard-path START, single step).
# W2 event8 dpad-DOWN hold -> moves (real dpad; latches gamepad).
# W3 event5-UP hold AFTER latch -> moves (proves union fix; exact rest
#    item irrelevant, any movement post-latch is the proof).
# W4 event8 Y/triangle hold -> title? (triangle mapping).
# W5/W6 injected ENTER/X bursts continue toward SC; 60 s idle closes.
# Cap ~420 s.
set -u
D=622c49b1
OUT=~/dev/ssx3-work/N6/launch3
FILES=/storage/emulated/0/Android/data/com.ps2x.runner/files
DSCRAP=/data/local/tmp/n6
EVPAD=/dev/input/event8
EVKEY=/dev/input/event5
mkdir -p "$OUT"
echo "LAUNCH3_AT=$(date -u +%FT%TZ)"
adb -s $D shell "cat /data/local/tmp/mg/LEASE; dumpsys window policy 2>/dev/null | grep -m1 showing" 2>&1 | tee "$OUT/precheck.txt"

printf '# N6 launch3: clean env, NO pad script\nPS2X_CD_IMAGE=/storage/emulated/0/Android/data/com.ps2x.runner/files/SSX3.iso\nPS2X_SKIP_MOVIE=1\nPS2X_FRAME_DUMP_DIR=/storage/emulated/0/Android/data/com.ps2x.runner/files/frames\n' > "$OUT/ps2x-launch3.env"
adb -s $D shell "mkdir -p $DSCRAP && rm -rf $FILES/frames && mkdir -p $FILES/frames && rm -f $DSCRAP/sc3-*.png && echo DIRS_OK"
adb -s $D push "$OUT/ps2x-launch3.env" $FILES/ps2x.env 2>&1 | tail -1
adb -s $D shell am force-stop com.ps2x.runner
adb -s $D logcat -c
adb -s $D logcat -b main -b crash -s ps2x raylib > "$OUT/logcat-ps2x-raylib.txt" 2>&1 &
LC1=$!
adb -s $D shell am start -n com.ps2x.runner/android.app.NativeActivity 2>&1 | tee "$OUT/am-start.txt"
sleep 6
adb -s $D shell input keyevent 4
sleep 4
adb -s $D shell "screencap -p $DSCRAP/sc3-focus.png; pidof com.ps2x.runner" 2>&1 | tee "$OUT/focus.txt"

scap() { adb -s $D shell "screencap -p $DSCRAP/sc3-$1.png; cat $FILES/frames/upload-latest.txt 2>/dev/null | tail -1" 2>&1 | tee "$OUT/tick-$1.txt"; }
sehold() { # $1=dev $2=code $3=seconds
  adb -s $D shell "sendevent $1 1 $2 1; sendevent $1 0 0 0; sleep $3; sendevent $1 1 $2 0; sendevent $1 0 0 0" 2>&1
}
burst() {
  for _i in $(seq 1 "$2"); do adb -s $D shell input keyevent "$1" >/dev/null 2>&1; sleep 0.3; done
}

echo "--- wait for title ---"
sleep 22
scap w0-title

echo "--- W1: keyboard-path ENTER hold 2s on event5 (expect: main menu) ---"
sehold $EVKEY 28 2
sleep 8
scap w1-after-kbenter

echo "--- W2: REAL dpad-DOWN hold 0.7s on event8/545 (expect: selection moves) ---"
sehold $EVPAD 545 0.7
sleep 6
scap w2-after-realdpad

echo "--- W3: keyboard-path UP hold 0.7s on event5/103 AFTER latch (expect: moves; proves union) ---"
sehold $EVKEY 103 0.7
sleep 6
scap w3-after-kbup

echo "--- W4: REAL triangle/Y hold 2s on event8/307 (expect: Previous/to title?) ---"
sehold $EVPAD 307 2
sleep 8
scap w4-after-realtri

echo "--- W5: injected ENTER x6 (continue route) ---"
burst KEYCODE_ENTER 6
sleep 8
scap w5-after-enter

echo "--- W6: injected X x6 (continue route) ---"
burst KEYCODE_X 6
sleep 25
scap w6-after-x

echo "--- W7: 60 s idle ---"
sleep 30
scap w7-idle0
sleep 60
scap w7-idle1
adb -s $D shell "pidof com.ps2x.runner; ls $FILES/frames | wc -l; tail -1 $FILES/frames/upload-latest.txt" 2>&1 | tee "$OUT/idle-end.txt"

for s in focus w0-title w1-after-kbenter w2-after-realdpad w3-after-kbup w4-after-realtri w5-after-enter w6-after-x w7-idle0 w7-idle1; do
  adb -s $D pull $DSCRAP/sc3-$s.png "$OUT/sc3-$s.png" 2>&1 | tail -1
done
adb -s $D pull $FILES/frames/upload-latest.txt "$OUT/upload-latest.txt" 2>&1 | tail -1
sha256sum "$OUT"/sc3-*.png | tee "$OUT/scap-sha.txt"
ls -l "$OUT" | head -30
kill $LC1 2>/dev/null
adb -s $D shell am force-stop com.ps2x.runner
echo "LAUNCH3_END=$(date -u +%FT%TZ)"
