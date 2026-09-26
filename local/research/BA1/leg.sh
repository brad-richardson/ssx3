#!/bin/bash
# BA1 per-leg driver: holds ONE atomic Odin lease (BA1) from install through
# play-restore, so no install/launch/force-stop ever lands on another lane's
# session (G3: an unleased install killed VK2's stress run). Queue: BA1 runs
# after F6 Part 1 + VK2; claim fails (no touch) if the device is held.
# Usage: leg.sh <base|o3|lto> <label>   (e.g. leg.sh base R1)
set -euo pipefail
apk=${1:?usage: leg.sh base\|o3\|lto label}; label=${2:?usage: leg.sh base\|o3\|lto label}
SSX3=$HOME/dev/ssx3; S=$(cat $SSX3/local/odin-serial); PKG=com.ps2x.runner
FILES=/storage/emulated/0/Android/data/$PKG/files
LEASE_TOOL=$SSX3/local/tooling/odin_lease.sh
case "$apk" in
  base) WANT=2dcf2ae9719ee0302e7e3db7572b2263d16cfa2c35ddf7e4c81ffabae6d69abf ;;
  o3)   WANT=bec0d84c915bf68326608d7c201b726951e4b1678df147fa1ad204cd1b4223e4 ;;
  lto)  WANT=96271ec8e1c4f57c9698a0ad88bdf9f9f025345ad982a3755fb4531ca5e49710 ;;
  *) echo "bad apk: $apk" >&2; exit 2 ;;
esac
APK=$HOME/dev/ssx3-work/BA1/odin/app-$apk.apk
out=$(bash "$LEASE_TOOL" claim BA1) || { echo "claim failed, touching nothing: $out" >&2; exit 2; }
echo "CLAIM $out"
trap 'bash "$LEASE_TOOL" release BA1' EXIT
# Fresh hold: a running app is either a stray or Brad himself. Brad = play
# env + F5 play APK: abort loudly. Anything else running = stray: stop it.
pid=$(adb -s "$S" shell pidof $PKG || true)
if [ -n "$pid" ]; then
  env=$(adb -s "$S" shell sha256sum $FILES/ps2x.env | cut -d' ' -f1)
  bp=$(adb -s "$S" shell pm path $PKG | sed 's/^package://' | tr -d '\r')
  ins=$(adb -s "$S" shell sha256sum "$bp" | cut -d' ' -f1)
  if [ "$env" = a8d651a7e55f7e29f1345f28f4ea634e06ae757f535e29439ab61c930bcc0ebd ] && \
     [ "$ins" = 4ff81032a175689be276819381f5ff52710e37101f99289d76b25a5c95609753 ]; then
    echo "BRAD MAY BE PLAYING (pid $pid, play env+APK): aborting, releasing" >&2; exit 3
  fi
  echo "STRAY pid $pid (env $env ins $ins): force-stop under our hold"
  adb -s "$S" shell am force-stop $PKG
fi
h1=$(shasum -a 256 "$APK" | cut -d' ' -f1); h2=$(shasum -a 256 "$APK" | cut -d' ' -f1)
[ "$h1" = "$WANT" ] && [ "$h2" = "$WANT" ] || { echo "$apk APK SHA mismatch" >&2; exit 1; }
adb -s "$S" install -r "$APK"
bp=$(adb -s "$S" shell pm path $PKG | sed 's/^package://' | tr -d '\r')
ins=$(adb -s "$S" shell sha256sum "$bp" | cut -d' ' -f1)
[ "$ins" = "$WANT" ] || { echo "installed base.apk mismatch: $ins" >&2; exit 1; }
echo "INSTALLED $ins"
python3 $SSX3/local/research/BA1/cooldown.py --label "$label"
python3 $SSX3/local/research/BA1/launch.py --label "$label"
python3 $SSX3/local/research/F4/phases.py $SSX3/local/research/BA1/logs/"$label" | tee $SSX3/local/research/BA1/logs/"$label"/phases.txt
bash $SSX3/local/research/BA1/restore-play.sh
echo "LEG $label($apk) DONE"
