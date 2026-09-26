#!/bin/bash
# BA1 close-out: put Brad's F5 play build back exactly (brief rule): F5 APK
# 4ff81032… (two local SHA reads, installed base.apk SHA), Brad's save + env via
# I31 deploy-odin.sh with F5's play knobs (env must read a8d651a7…), scratch and
# mc0-test emptied, app stopped, lease released. No launch.
set -euo pipefail
S=$(cat ~/dev/ssx3/local/odin-serial)
PKG=com.ps2x.runner
FILES=/storage/emulated/0/Android/data/$PKG/files
APK=$HOME/dev/ssx3-work/F5/odin/app-release.apk
WANT_APK=4ff81032a175689be276819381f5ff52710e37101f99289d76b25a5c95609753
WANT_ENV=a8d651a7e55f7e29f1345f28f4ea634e06ae757f535e29439ab61c930bcc0ebd
lease=$(adb -s "$S" shell cat /data/local/tmp/mg/LEASE)
echo "PRE lease=$lease pid=$(adb -s "$S" shell pidof $PKG || true)"
case "$lease" in LEASE_FREE*|BA1\ *) ;; *) echo "lease held: $lease" >&2; exit 1;; esac
LEASE_TOOL=$HOME/dev/ssx3/local/tooling/odin_lease.sh
out=$(bash "$LEASE_TOOL" claim BA1) || { echo "atomic claim failed: $out" >&2; exit 1; }
echo "CLAIM $out"
trap 'bash "$LEASE_TOOL" release BA1' EXIT
h1=$(shasum -a 256 "$APK" | cut -d' ' -f1); h2=$(shasum -a 256 "$APK" | cut -d' ' -f1)
echo "APK local $h1 $h2"
[ "$h1" = "$WANT_APK" ] && [ "$h2" = "$WANT_APK" ] || { echo "F5 APK SHA mismatch" >&2; exit 1; }
adb -s "$S" shell am force-stop $PKG
adb -s "$S" install -r "$APK"
bp=$(adb -s "$S" shell pm path $PKG | sed 's/^package://' | tr -d '\r')
bsha=$(adb -s "$S" shell sha256sum "$bp" | cut -d' ' -f1)
echo "INSTALLED $bp $bsha"
[ "$bsha" = "$WANT_APK" ] || { echo "installed base.apk mismatch" >&2; exit 1; }
bash ~/dev/ssx3/local/research/I31/deploy-odin.sh "$S" "$HOME/dev/ssx3-work/E55D16/mc0" ~/dev/ssx3/local/research/F5/play-knobs.env
esha=$(adb -s "$S" shell sha256sum $FILES/ps2x.env | cut -d' ' -f1)
echo "ENV $esha"
[ "$esha" = "$WANT_ENV" ] || { echo "env mismatch" >&2; exit 1; }
adb -s "$S" shell "rm -rf /data/local/tmp/ba1 $FILES/ba1dump; rm -rf $FILES/mc0-test/*; ls -A $FILES/mc0-test | wc -l; am force-stop $PKG"
echo "END pid=$(adb -s "$S" shell pidof $PKG || echo none) battery=$(adb -s "$S" shell dumpsys battery | grep -m1 level)"
