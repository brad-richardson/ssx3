#!/bin/bash
# N4 launch 2: pad script to menus + 30s simpleperf on settled screen. Cap ~300 s.
set -u
D=622c49b1
OUT=~/dev/ssx3-work/N4/launch2
FILES=/storage/emulated/0/Android/data/com.ps2x.runner/files
DSCRAP=/data/local/tmp/n4
mkdir -p "$OUT"
printf '# N4 launch2: pad script to menus\nPS2X_CD_IMAGE=/storage/emulated/0/Android/data/com.ps2x.runner/files/SSX3.iso\nPS2X_SKIP_MOVIE=1\nPS2X_FRAME_DUMP_DIR=/storage/emulated/0/Android/data/com.ps2x.runner/files/frames\nPS2X_PAD_SCRIPT=25000:start:5000,90000:cross:5000\n' > "$OUT/ps2x-launch2.env"
cat "$OUT/ps2x-launch2.env"
echo "LAUNCH2_AT=$(date -u +%FT%TZ)"
adb -s $D shell "rm -rf $FILES/frames && mkdir -p $FILES/frames && rm -f $DSCRAP/scap2-*.png $DSCRAP/perf-menu.data && echo DIRS_OK"
adb -s $D push "$OUT/ps2x-launch2.env" $FILES/ps2x.env 2>&1 | tail -1
adb -s $D shell am force-stop com.ps2x.runner
adb -s $D logcat -c
adb -s $D logcat -b main -b crash -s ps2x raylib > "$OUT/logcat-ps2x-raylib.txt" 2>&1 &
LC1=$!
adb -s $D shell am start -n com.ps2x.runner/android.app.NativeActivity 2>&1 | tee "$OUT/am-start.txt"
sleep 6
adb -s $D shell input keyevent 4
sleep 6
adb -s $D shell "screencap -p $DSCRAP/scap2-focus.png; pidof com.ps2x.runner" 2>&1 | tee "$OUT/focus.txt"
T0=$(date +%s)
sleep 88
EL=$(( $(date +%s) - T0 )); echo "EL=${EL}s post-start-inputs"
adb -s $D shell "screencap -p $DSCRAP/scap2-prescript.png; pidof com.ps2x.runner" 2>&1 | tee "$OUT/prescript.txt"
sleep 30
adb -s $D shell "screencap -p $DSCRAP/scap2-settled.png" 2>&1 | tee "$OUT/settled.txt"
adb -s $D shell "simpleperf record -g --app com.ps2x.runner -o $DSCRAP/perf-menu.data --duration 30" 2>&1 | tee "$OUT/simpleperf-record.txt"
adb -s $D shell "ls -l $DSCRAP/perf-menu.data; screencap -p $DSCRAP/scap2-postrec.png; pidof com.ps2x.runner" 2>&1 | tee "$OUT/after-record.txt"
adb -s $D pull $DSCRAP/perf-menu.data "$OUT/perf-menu.data" 2>&1 | tail -1
adb -s $D pull $FILES/frames/upload-latest.txt "$OUT/upload-latest.txt" 2>&1 | tail -1
for s in focus prescript settled postrec; do adb -s $D pull $DSCRAP/scap2-$s.png "$OUT/scap2-$s.png" 2>&1 | tail -1; done
ls -l "$OUT"
kill $LC1 2>/dev/null
echo "LAUNCH2_END=$(date -u +%FT%TZ)"
