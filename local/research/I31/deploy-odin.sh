#!/bin/bash
# I31: re-apply Brad's save + manual-play env to the Odin. Idempotent: each
# item is skipped when the device already holds the same bytes (sha256sum
# compare); verifies after; exits 1 on any mismatch. No install, no launch.
# Automated test launchers must NOT use Brad's card: set PS2X_MC_ROOT to an
# empty files/mc0-test/ in their own env, and restore Brad's env after
# (I26-FAST derails on a seeded card). Usage:
#   bash deploy-odin.sh [SERIAL] [SAVE_SRC]
set -euo pipefail
SERIAL="${1:-$(cat ~/dev/ssx3/local/odin-serial)}"
SAVE_SRC="${2:-$HOME/dev/ssx3-work/E55D16/mc0}"
PKG=com.ps2x.runner
FILES=/storage/emulated/0/Android/data/$PKG/files
GAM=BASLUS-20772-GAM0001
SET=BASLUS-20772-SET0001
for f in "$GAM/BASLUS-20772-GAM0001" "$GAM/icon.sys" "$GAM/ssx1.ico" \
         "$SET/BASLUS-20772-SET0001" "$SET/icon.sys" "$SET/ssx1.ico"; do
  test -f "$SAVE_SRC/$f" || { echo "missing save file: $SAVE_SRC/$f" >&2; exit 2; }
done
adb -s "$SERIAL" get-state 2>/dev/null | grep -qx device \
  || { echo "device $SERIAL not ready" >&2; exit 2; }

ENV_TMP="$(mktemp -t i31-odin-env)"
trap 'rm -f "$ENV_TMP"' EXIT
cat > "$ENV_TMP" <<'EOF'
# I31 Brad's manual-play default (device default ps2x.env).
# The game waits at the title for real input: no PS2X_PAD_SCRIPT, no
# capture/dump keys (they would write GBs and cost speed). Tests use
# their own env (script via PS2X_PAD_SCRIPT, empty card via PS2X_MC_ROOT
# to files/mc0-test) and restore this file after.
PS2X_GS_BACKEND=parallel
PS2X_GS_TURNIP=1
PS2X_CD_IMAGE=/storage/emulated/0/Android/data/com.ps2x.runner/files/SSX3.iso
PS2X_SKIP_MOVIE=1
PS2X_SOUND=1
EOF

want_env="$(shasum -a 256 "$ENV_TMP" | cut -d' ' -f1)"
have_env="$(adb -s "$SERIAL" shell "sha256sum $FILES/ps2x.env" 2>/dev/null | cut -d' ' -f1 || true)"
if [ "$have_env" = "$want_env" ]; then
  echo "SKIP ps2x.env (device holds Brad's env $want_env)"
else
  adb -s "$SERIAL" push "$ENV_TMP" "$FILES/ps2x.env"
fi

for f in "$GAM/BASLUS-20772-GAM0001" "$GAM/icon.sys" "$GAM/ssx1.ico" \
         "$SET/BASLUS-20772-SET0001" "$SET/icon.sys" "$SET/ssx1.ico"; do
  want="$(shasum -a 256 "$SAVE_SRC/$f" | cut -d' ' -f1)"
  have="$(adb -s "$SERIAL" shell "sha256sum $FILES/mc0/$f" 2>/dev/null | cut -d' ' -f1 || true)"
  if [ "$have" = "$want" ]; then
    echo "SKIP $f (SHA matches)"
  else
    adb -s "$SERIAL" push "$SAVE_SRC/$f" "$FILES/mc0/$f"
  fi
done

fail=0
have_env="$(adb -s "$SERIAL" shell "sha256sum $FILES/ps2x.env" | cut -d' ' -f1)"
[ "$have_env" = "$want_env" ] && echo "OK ps2x.env $have_env" \
  || { echo "MISMATCH ps2x.env" >&2; fail=1; }
for f in "$GAM/BASLUS-20772-GAM0001" "$GAM/icon.sys" "$GAM/ssx1.ico" \
         "$SET/BASLUS-20772-SET0001" "$SET/icon.sys" "$SET/ssx1.ico"; do
  want="$(shasum -a 256 "$SAVE_SRC/$f" | cut -d' ' -f1)"
  have="$(adb -s "$SERIAL" shell "sha256sum $FILES/mc0/$f" | cut -d' ' -f1)"
  [ "$have" = "$want" ] && echo "OK ${want:0:12}… mc0/$f" \
    || { echo "MISMATCH mc0/$f" >&2; fail=1; }
done
exit "$fail"
