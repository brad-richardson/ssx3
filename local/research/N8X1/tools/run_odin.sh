#!/bin/zsh
# usage: run_odin.sh <label> <device-stream-path> [extra env lines...]
# Lease "N8X1 explore" must already be held. Pushes replay env, one am start, waits for exit,
# pulls hashes (+ ppm if any), force-stops. Does NOT restore env (done at session end).
set -u
export ANDROID_SERIAL=622c49b1
PKG=com.ps2x.runner
F=/storage/emulated/0/Android/data/$PKG/files
label=$1; stream=$2; shift 2
out=/Users/brad/dev/ssx3-work/N8X1/runs/odin-$label; mkdir -p $out
stamp=$(date +%s)
[[ "$(adb shell cat /data/local/tmp/mg/LEASE)" == "N8X1 explore" ]] || { echo "LEASE not ours"; exit 1; }
adb shell dumpsys window policy | grep -q "showing=false" || { echo "BLOCKER keyguard showing"; exit 2; }
bat=$(adb shell dumpsys battery); lvl=$(echo $bat | awk '/level:/{print $2}'); st=$(echo $bat | awk '/status:/{print $2}')
echo "battery level=$lvl status=$st"
(( lvl >= 20 )) || { echo "battery low"; exit 3; }
[[ $st == 2 || $st == 5 || ( $st == 3 && $lvl -ge 90 ) ]] || { echo "not charging"; exit 3; }
hashes=$F/n8x1-$label-$stamp.hashes; ppmdir=$F/n8x1-$label-frames-$stamp
{
  echo PS2X_GS_REPLAY_ONDEVICE=1
  echo PS2X_GS_REPLAY_CAPTURE=$stream
  echo PS2X_GS_REPLAY_BACKEND=parallel
  echo PS2X_GS_TURNIP=1
  echo PS2X_GS_REPLAY_STEP=${STEP:-1}
  echo PS2X_GS_REPLAY_PPM_TICKS=${PPM_TICKS:-2050}
  echo PS2X_GS_REPLAY_PKTSEQ=1
  echo PS2X_GS_REPLAY_PPM_DIR=$ppmdir
  echo PS2X_GS_REPLAY_OUT=$hashes
  for l in "$@"; do echo $l; done
} > $out/ps2x.env
grep -q "PS2X_GS_CAPTURE=" $out/ps2x.env && { echo "forbidden capture key"; exit 4; }
adb shell mkdir -p $ppmdir
adb push $out/ps2x.env $F/ps2x.env >/dev/null
adb shell am force-stop $PKG
adb logcat -c
if [[ -n "${LOGALL:-}" ]]; then adb logcat -v epoch > $out/logcat.txt 2>&1 & else adb logcat -v epoch -s ps2x ps2x-hwcompat DEBUG libc AndroidRuntime vulkan freedreno MESA TU > $out/logcat.txt 2>&1 & fi
lp=$!
t0=$(date +%s)
adb shell am start -n $PKG/android.app.NativeActivity >/dev/null
sleep 1.5; adb shell input keyevent 4
while true; do
  sleep 0.5
  grep -q -E "replay (ok|failed|rejected)" $out/logcat.txt && break
  pid=$(adb shell pidof $PKG)
  [[ -z $pid ]] && break
  (( $(date +%s) - t0 > ${WALL:-240} )) && { echo "WALL cap"; break; }
done
echo "elapsed=$(( $(date +%s) - t0 ))s"
sleep 1; kill $lp 2>/dev/null
adb shell am force-stop $PKG
[[ -z "$(adb shell pidof $PKG)" ]] && echo "force-stopped ok"
adb pull $hashes $out/parallel.hashes >/dev/null 2>&1 || echo "no hashes file"
adb pull $ppmdir $out/frames >/dev/null 2>&1
wc -l < $out/parallel.hashes 2>/dev/null
grep -E "replay ok|replay failed|rejected|init ok|ps2x.env: set (TU|MESA|VK|IR3|FD)" $out/logcat.txt | cut -c1-200 | head
