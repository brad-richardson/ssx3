#!/bin/bash
# I31: re-apply Brad's save + manual-play env to an iOS device's Documents.
# Idempotent: compares exact remote sizes via `info files --json-output` and
# skips each item already present with the right size (devicectl also skips
# unmodified files on copy). Verifies after; exits 1 on any mismatch.
# Save bytes stay private in SAVE_SRC (default E55D16 scratch); the env text
# is embedded below. No launch, no install. Usage:
#   bash deploy-ios.sh ipad|iphone|<UDID> [SAVE_SRC]
set -euo pipefail
APP=org.ps2x.ps2entryrunner
case "${1:-}" in
  ipad) DEVICE=00008112-001224302184A01E ;;
  iphone) DEVICE=00008140-0002505001F3001C ;;
  0000*) DEVICE="$1" ;;
  *) echo "usage: $0 ipad|iphone|<UDID> [SAVE_SRC]" >&2; exit 2 ;;
esac
SAVE_SRC="${2:-$HOME/dev/ssx3-work/E55D16/mc0}"
GAM=BASLUS-20772-GAM0001
SET=BASLUS-20772-SET0001
for f in "$GAM/BASLUS-20772-GAM0001" "$GAM/icon.sys" "$GAM/ssx1.ico" \
         "$SET/BASLUS-20772-SET0001" "$SET/icon.sys" "$SET/ssx1.ico"; do
  test -f "$SAVE_SRC/$f" || { echo "missing save file: $SAVE_SRC/$f" >&2; exit 2; }
done
xcrun devicectl list devices 2>/dev/null | grep -F "$DEVICE" | grep -Eq 'available|connected' \
  || { echo "device $DEVICE not available" >&2; exit 2; }

ENV_TMP="$(mktemp -t i31-ps2x-env)"
trap 'rm -f "$ENV_TMP"' EXIT
cat > "$ENV_TMP" <<'EOF'
# I31 manual-play default for Brad's devices (lives in the app's Documents
# folder as ps2x.env; overrides the bundled ps2x.env key by key).
# Empty value clears the bundled I26-FAST script: the game waits at the
# title for real input. Tests re-arm scripted input per launch with
# devicectl launch -e PS2X_PAD_SCRIPT=<script> (launcher env wins over
# both files). All other bundled keys (BOOT_ELF, CD_IMAGE, MC_ROOT,
# SKIP_MOVIE, DEINTERLACE, SOUND) are inherited unchanged.
PS2X_PAD_SCRIPT=
EOF

remote_sizes() { # -> "size path" lines for Documents
  xcrun devicectl device info files --device "$DEVICE" \
    --domain-type appDataContainer --domain-identifier "$APP" \
    --subdirectory Documents --json-output - 2>/dev/null \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(f\"{f['metadata']['size']} {f['name']}\") for f in d['result']['files']]"
}

need_mc0=0; need_env=0
REMOTE="$(remote_sizes)"
for f in "$GAM/BASLUS-20772-GAM0001" "$GAM/icon.sys" "$GAM/ssx1.ico" \
         "$SET/BASLUS-20772-SET0001" "$SET/icon.sys" "$SET/ssx1.ico"; do
  want="$(stat -f%z "$SAVE_SRC/$f")"
  echo "$REMOTE" | grep -Fqx "$want mc0/$f" || need_mc0=1
done
want_env="$(stat -f%z "$ENV_TMP")"
echo "$REMOTE" | grep -Fqx "$want_env ps2x.env" || need_env=1

[ "$need_mc0" = 0 ] && echo "SKIP mc0 (all 6 files present with exact sizes)"
[ "$need_env" = 0 ] && echo "SKIP ps2x.env (present, $want_env bytes)"
[ "$need_mc0" = 1 ] && xcrun devicectl device copy to --device "$DEVICE" \
  --domain-type appDataContainer --domain-identifier "$APP" \
  --source "$SAVE_SRC" --destination Documents/mc0
[ "$need_env" = 1 ] && xcrun devicectl device copy to --device "$DEVICE" \
  --domain-type appDataContainer --domain-identifier "$APP" \
  --source "$ENV_TMP" --destination Documents/ps2x.env

REMOTE2="$(remote_sizes)"
fail=0
for f in "$GAM/BASLUS-20772-GAM0001" "$GAM/icon.sys" "$GAM/ssx1.ico" \
         "$SET/BASLUS-20772-SET0001" "$SET/icon.sys" "$SET/ssx1.ico"; do
  want="$(stat -f%z "$SAVE_SRC/$f")"
  echo "$REMOTE2" | grep -Fqx "$want mc0/$f" \
    && echo "OK $want mc0/$f" || { echo "MISMATCH mc0/$f (want $want)" >&2; fail=1; }
done
echo "$REMOTE2" | grep -Fqx "$want_env ps2x.env" \
  && echo "OK $want_env ps2x.env" || { echo "MISMATCH ps2x.env" >&2; fail=1; }
exit "$fail"
