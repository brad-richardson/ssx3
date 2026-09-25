#!/bin/sh
# bradflix_boot.sh — build + det-boot the PS2Recomp fork on bradflix (x86_64),
# pull result.json + det-hash lines + frames back to the mini.
#
# The build and boot run on bradflix inside the ssx3-lx1 docker image (Ubuntu
# 24.04 + clang + X11/GL + FFmpeg + xvfb; see local/research/LX1/Dockerfile),
# because bradflix has no passwordless sudo for system deps. No Mac P-lane
# lease is needed; bradflix has its own (one heavy job at a time):
# ~/dev/ssx3-work/BRADFLIX_LEASE, claimed here and released on every path.
#
# Usage:
#   bradflix_boot.sh --sha <fork-sha> --label <name> [--stop-tick 2400]
#                    [--pull-dir ~/dev/ssx3-work/LX1/from-bradflix/<label>]
#                    [--skip-build] [--skip-boot]
#
#   --sha: full (or unambiguous short) fork commit on origin/ssx3. Checked out
#          detached on bradflix; never pushed.
#   --label: run label; remote dir ~/dev/ssx3-work/LX1/run/<label> (fresh).
#   --skip-build: reuse the existing build-<sha> dir (fails if no runner).
#   --skip-boot: build (+ suite) only, then pull the build receipts.
#
# Boot shape (see local/research/LX1/lx1_boot.py): CPU GS backend, det-hash
# tap build, I26-FAST, empty mc0, PS2X_SKIP_MOVIE=1, PS2X_DETERMINISTIC=1,
# sound off (AU10 guest-identical), frames via the 0.5 s snapshotter.
# Everything lives under ~/dev/ssx3-work/LX1 on bradflix, never /tmp.
#
# Known x86 deltas (LX1): the fork sets no x86 SIMD arch flag, so the build
# passes -msse4.1 (E-lane follow-up: add it to the fork's CMake); the E53
# fegetround suite check fails on x86 (glibc reads the x87 CW, the runtime
# manages MXCSR only; SSE math verified correct) — suite failure is recorded
# but does not stop the boot.
set -eu

SHA=""; LABEL=""; STOP_TICK="2400"; PULL_DIR=""; SKIP_BUILD=0; SKIP_BOOT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --sha) SHA="$2"; shift 2;;
    --label) LABEL="$2"; shift 2;;
    --stop-tick) STOP_TICK="$2"; shift 2;;
    --pull-dir) PULL_DIR="$2"; shift 2;;
    --skip-build) SKIP_BUILD=1; shift;;
    --skip-boot) SKIP_BOOT=1; shift;;
    -h|--help) sed -n '1,30p' "$0"; exit 0;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done
[ -n "$SHA" ] && [ -n "$LABEL" ] || { echo "need --sha and --label" >&2; exit 2; }
case "$LABEL" in *..*|*/*) echo "bad label" >&2; exit 2;; esac
[ -n "$PULL_DIR" ] || PULL_DIR="$HOME/dev/ssx3-work/LX1/from-bradflix/$LABEL"

REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
REMOTE="bradflix"
RROOT="dev/ssx3-work/LX1"
LEASE="dev/ssx3-work/BRADFLIX_LEASE"
NONCE="mini-$$-$(date +%s)"

echo "== preflight"
ssh -o ConnectTimeout=10 "$REMOTE" 'echo bradflix; uptime' || exit 1
if ssh "$REMOTE" "test -d ~/$LEASE"; then
  echo "bradflix lease held:" >&2
  ssh "$REMOTE" "cat ~/$LEASE/HOLDER 2>/dev/null || true" >&2
  exit 1
fi

release() { # only release a lease we claimed (nonce match)
  ssh "$REMOTE" "grep -q '$NONCE' ~/$LEASE/HOLDER 2>/dev/null && rm -rf ~/$LEASE && echo released || echo 'lease not ours; left in place'" || true
}
trap release EXIT INT TERM
ssh "$REMOTE" "mkdir ~/$LEASE && echo 'owner=$NONCE purpose=bradflix_boot.sh' > ~/$LEASE/HOLDER && cat ~/$LEASE/HOLDER"

echo "== sync docker context + driver"
scp "$REPO/local/research/LX1/Dockerfile" "$REPO/local/research/LX1/lx1_boot.py" "$REMOTE:$RROOT/"

echo "== checkout $SHA"
ssh "$REMOTE" "cd ~/$RROOT/PS2Recomp && git fetch origin ssx3 && git checkout --detach $SHA" || exit 1
FULL_SHA="$(ssh "$REMOTE" "git -C ~/$RROOT/PS2Recomp rev-parse HEAD")"
case "$FULL_SHA" in
  *[!0-9a-f]*|"") echo "bad SHA from remote: $FULL_SHA" >&2; exit 2;;
esac
[ "${#FULL_SHA}" -eq 40 ] || { echo "bad SHA from remote: $FULL_SHA" >&2; exit 2; }
echo "remote HEAD: $FULL_SHA"
SHORT="$(printf '%s' "$FULL_SHA" | cut -c1-9)"
BUILD_DIR="$RROOT/build-$SHORT"

if [ "$SKIP_BUILD" -eq 0 ]; then
  echo "== docker build (cached layers are fast)"
  ssh "$REMOTE" "cd ~/$RROOT && docker build -t ssx3-lx1 -f Dockerfile . 2>&1 | tail -1"
  echo "== configure $BUILD_DIR"
  ssh "$REMOTE" "docker run --rm --user 1000:1000 -e HOME=/work -w /work -v ~/$RROOT:/work ssx3-lx1 cmake -S /work/PS2Recomp -B /work/build-$SHORT -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DPS2X_GAME_CODEGEN_DIR=/work/codegen -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=ON -DCMAKE_C_FLAGS=-msse4.1 -DCMAKE_CXX_FLAGS=-msse4.1 2>&1 | tail -2"
  echo "== build + suite"
  ssh "$REMOTE" "docker run --rm --user 1000:1000 -e HOME=/work -w /work -v ~/$RROOT:/work ssx3-lx1 cmake --build /work/build-$SHORT --parallel 16 --target ps2x_tests ps2EntryRunner > ~/$RROOT/build-$SHORT.log 2>&1; echo BUILD_RC=\$?; tail -1 ~/$RROOT/build-$SHORT.log"
  ssh "$REMOTE" "docker run --rm --user 1000:1000 -e HOME=/work -w /work/PS2Recomp -v ~/$RROOT:/work ssx3-lx1 /work/build-$SHORT/ps2xTest/ps2x_tests > ~/$RROOT/suite-$SHORT.log 2>&1; R=\$?; echo SUITE_RC=\$R; tail -4 ~/$RROOT/suite-$SHORT.log; exit \$R" || echo "WARNING: suite failed; continuing (known x86 E53 fegetround delta)"
else
  ssh "$REMOTE" "test -x ~/$BUILD_DIR/ps2xRuntime/ps2EntryRunner" || { echo "no runner at $BUILD_DIR" >&2; exit 1; }
fi
RUNNER_SHA="$(ssh "$REMOTE" "sha256sum ~/$BUILD_DIR/ps2xRuntime/ps2EntryRunner | cut -d' ' -f1")"
echo "runner: $BUILD_DIR/ps2xRuntime/ps2EntryRunner sha=$RUNNER_SHA"

if [ "$SKIP_BOOT" -eq 0 ]; then
  echo "== boot $LABEL to tick $STOP_TICK"
  ssh "$REMOTE" "cd ~/$RROOT && python3 lx1_boot.py --runner ~/$BUILD_DIR/ps2xRuntime/ps2EntryRunner --label '$LABEL' --stop-tick '$STOP_TICK' 2>&1 | tail -2"
fi

echo "== pull back to $PULL_DIR"
mkdir -p "$PULL_DIR"
scp "$REMOTE:$RROOT/run/$LABEL/result.json" "$REMOTE:$RROOT/run/$LABEL/boot.log" "$REMOTE:$RROOT/run/$LABEL/trace.jsonl" "$PULL_DIR/" 2>/dev/null || echo "(no run dir pulled; build-only?)"
scp "$REMOTE:$RROOT/suite-$SHORT.log" "$REMOTE:$RROOT/build-$SHORT.log" "$PULL_DIR/" 2>/dev/null || true
mkdir -p "$PULL_DIR/snap"
scp "$REMOTE:$RROOT/run/$LABEL/frames/snap/snap-*" "$PULL_DIR/snap/" 2>/dev/null || echo "(no frames pulled)"
grep -c "det-hash:v1" "$PULL_DIR/boot.log" 2>/dev/null || true
echo "done: $PULL_DIR"
