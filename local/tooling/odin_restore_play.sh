#!/bin/bash
# odin_restore_play.sh [LABEL] [SAVE_SRC]
# Canonical Odin play-state restore (F7 Part 3): installs Brad's play build
# from ~/dev/ssx3-work/odin-play/ (APK + ps2x.env + SHA256SUMS), pushes the
# play env, verifies both SHAs and Brad's 6 saves, empties mc0-test,
# force-stops. No launch. Later lanes restore this build after their runs.
# Lease via local/tooling/odin_lease.sh (atomic); exits 1 if held.
set -euo pipefail
LABEL="${1:-PLAY}"
SAVE_SRC="${2:-$HOME/dev/ssx3-work/E55D16/mc0}"
S=$(cat ~/dev/ssx3/local/odin-serial)
PKG=com.ps2x.runner
FILES=/storage/emulated/0/Android/data/$PKG/files
PLAYDIR=$HOME/dev/ssx3-work/odin-play
APK=$PLAYDIR/app-release.apk
ENV=$PLAYDIR/ps2x.env
# Pins come from the canonical SHA256SUMS (never hard-coded here: a play-env change must not break restores).
WANT_APK=$(awk '$2=="app-release.apk"{print $1}' "$PLAYDIR/SHA256SUMS")
WANT_ENV=$(awk '$2=="ps2x.env"{print $1}' "$PLAYDIR/SHA256SUMS")
[ ${#WANT_APK} -eq 64 ] && [ ${#WANT_ENV} -eq 64 ] || { echo "bad SHA256SUMS in $PLAYDIR" >&2; exit 1; }
GAM=BASLUS-20772-GAM0001
SET=BASLUS-20772-SET0001
LEASESH=~/dev/ssx3/local/tooling/odin_lease.sh
echo "PRE lease=$(bash "$LEASESH" status) pid=$(adb -s "$S" shell pidof $PKG || true)"
bash "$LEASESH" claim "$LABEL" || { echo "lease held, refusing" >&2; exit 1; }
trap 'bash "$LEASESH" release "$LABEL"' EXIT
(cd "$PLAYDIR" && shasum -a 256 -c SHA256SUMS)
h1=$(shasum -a 256 "$APK" | cut -d' ' -f1); h2=$(shasum -a 256 "$APK" | cut -d' ' -f1)
echo "APK local $h1 $h2"
[ "$h1" = "$WANT_APK" ] && [ "$h2" = "$WANT_APK" ] || { echo "play APK SHA mismatch" >&2; exit 1; }
adb -s "$S" shell am force-stop $PKG
adb -s "$S" install -r "$APK"
bp=$(adb -s "$S" shell pm path $PKG | sed 's/^package://' | tr -d '\r')
bsha=$(adb -s "$S" shell sha256sum "$bp" | cut -d' ' -f1)
echo "INSTALLED $bp $bsha"
[ "$bsha" = "$WANT_APK" ] || { echo "installed base.apk mismatch" >&2; exit 1; }
adb -s "$S" push "$ENV" "$FILES/ps2x.env"
esha=$(adb -s "$S" shell sha256sum $FILES/ps2x.env | cut -d' ' -f1)
echo "ENV $esha"
[ "$esha" = "$WANT_ENV" ] || { echo "env mismatch" >&2; exit 1; }
fail=0
for f in "$GAM/BASLUS-20772-GAM0001" "$GAM/icon.sys" "$GAM/ssx1.ico" \
         "$SET/BASLUS-20772-SET0001" "$SET/icon.sys" "$SET/ssx1.ico"; do
  want=$(shasum -a 256 "$SAVE_SRC/$f" | cut -d' ' -f1)
  have=$(adb -s "$S" shell "sha256sum $FILES/mc0/$f" | cut -d' ' -f1)
  if [ "$have" != "$want" ]; then adb -s "$S" push "$SAVE_SRC/$f" "$FILES/mc0/$f"; fi
  have=$(adb -s "$S" shell "sha256sum $FILES/mc0/$f" | cut -d' ' -f1)
  [ "$have" = "$want" ] && echo "OK ${want:0:12}… mc0/$f" || { echo "MISMATCH mc0/$f" >&2; fail=1; }
done
[ "$fail" = 0 ] || exit 1
adb -s "$S" shell "rm -rf $FILES/mc0-test/*; ls -A $FILES/mc0-test | wc -l; am force-stop $PKG"
# Fan: put Brad's pre-run fan_mode back if odin_cooldown.py changed it (never 0 = off).
fanprev=$(adb -s "$S" shell cat /data/local/tmp/mg/fan_prev 2>/dev/null | tr -dc 0-9)
if [ -n "$fanprev" ] && [ "$fanprev" != 0 ]; then adb -s "$S" shell "settings put system fan_mode $fanprev && rm -f /data/local/tmp/mg/fan_prev"; echo "FAN restored fan_mode=$fanprev"; fi
echo "END pid=$(adb -s "$S" shell pidof $PKG || echo none) battery=$(adb -s "$S" shell dumpsys battery | grep -m1 level)"
