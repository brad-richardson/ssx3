#!/bin/zsh
# usage: run_live.sh <label> [extra env lines...]   (lease "N8X1 explore" held; knob APK installed)
# Live boot per N8D2 env; screencap at menu (guest tick >= MENU_TICK) and at first [frame:dump] tick>=2050.
set -u
export ANDROID_SERIAL=622c49b1
PKG=com.ps2x.runner; F=/storage/emulated/0/Android/data/$PKG/files
label=$1; shift
out=/Users/brad/dev/ssx3-work/N8X1/runs/live-$label; mkdir -p $out
stamp=$(date +%s); dumps=$F/n8x1-live-$label-$stamp
[[ "$(adb shell cat /data/local/tmp/mg/LEASE)" == "N8X1 explore" ]] || { echo "LEASE not ours"; exit 1; }
adb shell dumpsys window policy | grep -q "showing=false" || { echo "BLOCKER keyguard showing"; exit 2; }
bat=$(adb shell dumpsys battery); lvl=$(echo $bat | awk '/level:/{print $2}'); st=$(echo $bat | awk '/status:/{print $2}')
echo "battery level=$lvl status=$st"
(( lvl >= 20 )) && [[ $st == 2 || $st == 5 || ( $st == 3 && $lvl -ge 90 ) ]] || { echo "battery gate"; exit 3; }
echo "mc0: $(adb shell ls $F/mc0 | wc -l) entries"
sed -n 1,5p /Users/brad/dev/ssx3/local/research/N8D2/ps2x.env > $out/ps2x.env   # backend, turnip, skip movie, cd image, pad script
cat >> $out/ps2x.env <<E2
PS2X_PAD_SCRIPT_CLOCK=vsync
PS2X_VSYNC_RATE_LOG=1
PS2X_FRAME_DUMP_DIR=$dumps
PS2X_FRAME_DUMP_ONCE_TICKS=${MENU_TICK:-1000},2050,999999
E2
for l in "$@"; do echo $l >> $out/ps2x.env; done
grep -q "PS2X_GS_CAPTURE" $out/ps2x.env && { echo forbidden; exit 4; }
adb shell mkdir -p $dumps
adb push $out/ps2x.env $F/ps2x.env >/dev/null
adb shell am force-stop $PKG; adb logcat -c
adb logcat -v epoch -s ps2x ps2x-hwcompat DEBUG libc AndroidRuntime Granite TU MESA > $out/logcat.txt 2>&1 &
lp=$!
t0=$(date +%s); adb shell am start -n $PKG/android.app.NativeActivity >/dev/null
sleep 1.5; adb shell input keyevent 4
menu=0; race=0
while true; do
  sleep 1
  tick=$(grep -a -o "\[vsync-rate\] tick=[0-9]*" $out/logcat.txt | tail -1 | grep -o "[0-9]*$"); tick=${tick:-0}
  el=$(( $(date +%s) - t0 ))
  if (( menu == 0 && tick >= ${MENU_TICK:-1000} )); then adb shell screencap -p /data/local/tmp/n8x1-menu.png; menu=$tick; echo "menu screencap at guest tick~$tick t=${el}s"; fi
  if (( race == 0 )) && grep -a -q -E "\[frame:dump\] seq=[0-9]+ tick=(20[5-9][0-9]|2[1-9][0-9][0-9])" $out/logcat.txt; then
    adb shell screencap -p /data/local/tmp/n8x1-race.png; race=$tick; echo "race screencap at guest tick~$tick t=${el}s"; break; fi
  [[ -z "$(adb shell pidof $PKG)" ]] && { echo "app exited t=${el}s tick=$tick"; break; }
  (( el > ${WALL:-400} )) && { echo "WALL cap tick=$tick"; break; }
done
sleep 1; kill $lp 2>/dev/null
adb shell am force-stop $PKG; [[ -z "$(adb shell pidof $PKG)" ]] && echo "force-stopped ok"
adb pull /data/local/tmp/n8x1-menu.png $out/screen-menu.png >/dev/null 2>&1 && adb shell rm /data/local/tmp/n8x1-menu.png
adb pull /data/local/tmp/n8x1-race.png $out/screen-race.png >/dev/null 2>&1 && adb shell rm /data/local/tmp/n8x1-race.png
adb pull $dumps $out/dumps >/dev/null 2>&1
grep -a -E "\[vsync-rate\]" $out/logcat.txt | tail -3 | cut -c30-250
grep -a -E "GameThread|frame:dump|n8x1\]|FATAL|SIGSEGV" $out/logcat.txt | cut -c30-250 | head -12
ls -l $out $out/dumps 2>/dev/null | grep -v total
