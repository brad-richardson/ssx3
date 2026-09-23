#!/bin/bash
# N4 launch 1: clean env to title + 30s simpleperf + PNG check. Cap ~300 s.
set -u
D=622c49b1
OUT=~/dev/ssx3-work/N4/launch1
FILES=/storage/emulated/0/Android/data/com.ps2x.runner/files
DSCRAP=/data/local/tmp/n4
mkdir -p "$OUT"
echo "LAUNCH1_AT=$(date -u +%FT%TZ)"
adb -s $D shell "mkdir -p $DSCRAP $FILES/frames && rm -rf $FILES/frames && mkdir -p $FILES/frames && rm -f $DSCRAP/scap-*.png $DSCRAP/perf1.data && echo DIRS_OK"
adb -s $D shell am force-stop com.ps2x.runner
adb -s $D logcat -c
adb -s $D logcat -b main -b crash -s ps2x raylib > "$OUT/logcat-ps2x-raylib.txt" 2>&1 &
LC1=$!
adb -s $D shell am start -n com.ps2x.runner/android.app.NativeActivity 2>&1 | tee "$OUT/am-start.txt"
sleep 6
adb -s $D shell input keyevent 4
sleep 4
adb -s $D shell "screencap -p $DSCRAP/scap-focus.png; pidof com.ps2x.runner" 2>&1 | tee "$OUT/focus.txt"
PID=$(adb -s $D shell pidof com.ps2x.runner | tr -d '\r')
echo "PID=$PID"
sleep 18
adb -s $D shell "screencap -p $DSCRAP/scap-title.png; ls $FILES/frames | head -8" 2>&1 | tee "$OUT/title.txt"
echo "--- simpleperf record 30s ---"
adb -s $D shell "simpleperf record -g -p $PID -o $DSCRAP/perf1.data --duration 30" 2>&1 | tee "$OUT/simpleperf-record.txt"
echo "RECORD_RC=$?"
sleep 2
adb -s $D shell "ls -l $DSCRAP/perf1.data; ls $FILES/frames | head -10; du -sh $FILES/frames" 2>&1 | tee "$OUT/after-record.txt"
adb -s $D pull $DSCRAP/perf1.data "$OUT/perf1.data" 2>&1 | tail -1
adb -s $D pull $FILES/frames/upload-latest.png "$OUT/upload-latest.png" 2>&1 | tail -1
adb -s $D pull $FILES/frames/upload-latest.txt "$OUT/upload-latest.txt" 2>&1 | tail -1
adb -s $D pull $DSCRAP/scap-focus.png "$OUT/scap-focus.png" 2>&1 | tail -1
adb -s $D pull $DSCRAP/scap-title.png "$OUT/scap-title.png" 2>&1 | tail -1
file "$OUT/upload-latest.png" 2>&1
ls -l "$OUT"
kill $LC1 2>/dev/null
echo "LAUNCH1_END=$(date -u +%FT%TZ)"
