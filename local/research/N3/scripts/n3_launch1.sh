#!/bin/bash
# N3 launch 1: start app, capture logcat + screencaps + cpu/thermal, 300 s cap
set -u
export COPYFILE_DISABLE=1
DEV=622c49b1
SSD="/Volumes/Extreme SSD/n2-android/n3-launch1"
FILES=/storage/emulated/0/Android/data/com.ps2x.runner/files
DSCRAP=/data/local/tmp/n3
mkdir -p "$SSD"
adb -s $DEV shell "mkdir -p $DSCRAP $FILES/frames && rm -f $DSCRAP/scap-*.png && echo DIRS_OK"
adb -s $DEV shell am force-stop com.ps2x.runner
adb -s $DEV logcat -c
adb -s $DEV logcat -b main -b crash -s ps2x raylib > "$SSD/logcat-ps2x-raylib.txt" 2>&1 &
LC1=$!
adb -s $DEV logcat -b main -b system -b crash > "$SSD/logcat-full.txt" 2>&1 &
LC2=$!
sleep 2
T0=$(date +%s); echo "LAUNCH_AT=$(date -u +%FT%TZ)"
adb -s $DEV shell am start -n com.ps2x.runner/android.app.NativeActivity 2>&1 | tee "$SSD/am-start.txt"
for i in $(seq 0 14); do
  sleep 20
  EL=$(( $(date +%s) - T0 ))
  adb -s $DEV shell "screencap -p $DSCRAP/scap-$(printf %02d $i).png; pidof com.ps2x.runner" > "$SSD/tick-$(printf %02d $i).txt" 2>&1
  echo "TICK $i EL=${EL}s $(cat "$SSD/tick-$(printf %02d $i).txt" | tr '\n' ' ')"
  if [ $(( i % 3 )) -eq 2 ]; then
    adb -s $DEV shell 'dumpsys cpuinfo' > "$SSD/cpuinfo-$i.txt" 2>&1
    adb -s $DEV shell 'for z in /sys/class/thermal/thermal_zone*; do echo -n "$z $(cat $z/type 2>/dev/null) "; cat $z/temp 2>/dev/null; done' > "$SSD/thermal-$i.txt" 2>&1
  fi
done
echo "LOOP_END_EL=$(( $(date +%s) - T0 ))s"
kill $LC1 $LC2 2>/dev/null
adb -s $DEV shell "ls -l $DSCRAP/ | head -20; du -sh $FILES/frames 2>/dev/null; pidof com.ps2x.runner; echo PIDOF_RC=$?"
adb -s $DEV pull $DSCRAP "$SSD/device-scap" 2>&1 | tail -2
adb -s $DEV pull $FILES/frames "$SSD/device-frames" 2>&1 | tail -2
adb -s $DEV shell am force-stop com.ps2x.runner
ls -l "$SSD" | head -30
