#!/bin/bash
# VR4 copy of local/tooling/build/bradflix_build.sh with one addition: --cmake ARG
# (repeatable) appends a raw cmake -D option to the configure line.
# Canonical bradflix runner build (HS1, concurrency-safe since HS2): the F5
# recipe of record behind a shared ccache, so every lane compiles only what
# it changed. Counterpart to local/tooling/build/mac_build.sh (RS1) for the
# correctness host.
#
# Usage:
#   bradflix_build.sh <fork-sha> <build-name> [--det] [--vu1 DIR]
#                     [--vu0 DIR] [--codegen DIR] [--pgs-pin SHA]
#
#   <fork-sha>    fork commit (full or unambiguous short) present in the
#                mini's ~/dev/PS2Recomp clone (pushed or not). Exported
#                with git archive into <build-name>/src on bradflix; the
#                old shared HS1/PS2Recomp checkout is never touched.
#   <build-name>  plain name; the remote build dir is claimed fresh at
#                ~/dev/ssx3-work/HS1/<build-name> (refuses to reuse).
#   --det         PS2X_ENABLE_DET_HASH_TAP=ON (default OFF)
#   --vu1 DIR     PS2X_VU1_RECOMP_DIR on the mini (default: canonical
#                ~/dev/ssx3-work/vu1gen-ssx3)
#   --vu0 DIR     PS2X_VU0_RECOMP_DIR on the mini (default: canonical
#                ~/dev/ssx3-work/vu0gen-ssx3; a no-op for revs before VR3)
#   --codegen DIR PS2X_GAME_CODEGEN_DIR on the mini (default: canonical
#                ~/dev/ssx3-work/codegen-ssx3)
#   --pgs-pin SHA full 40-hex paraLLEl pin (default: canonical pin below)
#
# Concurrency (HS2): several lanes build at once. Shared inputs live in
# content-addressed dirs (codegen-<sha12>, vu1gen-<manifest12>,
# vu0gen-<manifest12>, pgs-<pin12>), staged privately, verified, then published with one atomic
# mv under ~/dev/ssx3-work/HS1/.setup.lock (flock). Shared dirs are never
# modified or deleted. The lock is released before compiling. The Docker
# image, ccache mount and cmake flags are byte-identical to HS1; only -S/-B
# and the three input -D paths changed.
#
# Cold = fresh build name + empty ccache; warm = fresh build name + hot
# ccache. DIAG_TAPS is always OFF here (HS1: DIAG instrumentation blew one
# unity TU to ~25 min; correctness builds never need it).
set -euo pipefail

if [ $# -lt 2 ]; then sed -n '2,23p' "$0"; exit 2; fi
SHA_IN=$1; NAME=$2; shift 2
DET=OFF
VU1_ARG=""; VU0_ARG=""; CODEGEN_ARG=""; PGS_PIN_ARG=""; EXTRA=""
while [ $# -gt 0 ]; do
  case $1 in
    --det) DET=ON;;
    --vu1) VU1_ARG=$2; shift;;
    --vu0) VU0_ARG=$2; shift;;
    --codegen) CODEGEN_ARG=$2; shift;;
    --pgs-pin) PGS_PIN_ARG=$2; shift;;
    --cmake) case "$2" in *[!A-Za-z0-9_=-]* ) echo "bad --cmake: $2" >&2; exit 2;; esac; EXTRA="$EXTRA $2"; shift;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
  shift
done
case "$NAME" in *..*|*/*|"" ) echo "bad build-name: $NAME" >&2; exit 2;; esac
case "$NAME" in *[!A-Za-z0-9_.-]* ) echo "bad build-name: $NAME" >&2; exit 2;; esac

REMOTE="bradflix"
RROOT="dev/ssx3-work/HS1"
RCCACHE="dev/ssx3-work/ccache"
RLOCK="$RROOT/.setup.lock"
IMAGE="ssx3-hs1"
# Game-code unity batch size: fork default 32 (HS1 step 1 measured 16 as
# no better cold: 411 s vs 400 s at 32 — header re-parse eats the -O3 tail
# saving; -O1 halves the hot TU but taxes every boot's wall and still only
# projects to ~300 s, so -O3 stands; see REPORT.md).
BATCH=32
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
FORK=$HOME/dev/PS2Recomp

ISO_SHA='3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
ELF_SHA='1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
CODEGEN_SHA='8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'
CODEGEN_VF0_SHA='89953ba218efd63c2fdba28116765d524977f1233d0e370d22111a762e02383d'
PGS_PIN='3d72467033ce6c4a8c7319e567880578aca39f6b'
GRANITE_PIN='166ba21a247a681903cc9d0bb6562fe50a554c85'
PGS_SUBMODULES=29

CODEGEN_DIR=$HOME/dev/ssx3-work/codegen-ssx3
VU1_DIR=$HOME/dev/ssx3-work/vu1gen-ssx3
VU0_DIR=$HOME/dev/ssx3-work/vu0gen-ssx3
ELF_PATH=$HOME/dev/ssx3-work/E32-inputs/cd/SLUS_207.72
ISO_PATH=$HOME/dev/ssx3-work/E32-inputs/SSX\ 3\ \(USA\).iso
PGS_DIR=$HOME/dev/ssx3-work/parallel-gs-ssx3

[ -n "$CODEGEN_ARG" ] && CODEGEN_DIR=$CODEGEN_ARG
[ -n "$VU1_ARG" ] && VU1_DIR=$VU1_ARG
[ -n "$VU0_ARG" ] && VU0_DIR=$VU0_ARG
[ -n "$PGS_PIN_ARG" ] && PGS_PIN=$PGS_PIN_ARG
case "$PGS_PIN" in *[!0-9a-f]* ) echo "bad --pgs-pin: $PGS_PIN" >&2; exit 2;; esac
[ "${#PGS_PIN}" -eq 40 ] || { echo "bad --pgs-pin (want full 40-hex): $PGS_PIN" >&2; exit 2; }

echo "== resolve fork SHA (mini clone, pushed or not)"
[ -d "$FORK" ] || { echo "missing fork clone: $FORK" >&2; exit 2; }
FULL_SHA="$(git -C "$FORK" rev-parse --verify "$SHA_IN^{commit}" 2>/dev/null)" || { echo "unknown fork SHA (not in $FORK; fetch first): $SHA_IN" >&2; exit 2; }
case "$FULL_SHA" in *[!0-9a-f]*|"") echo "bad SHA: $FULL_SHA" >&2; exit 2;; esac
[ "${#FULL_SHA}" -eq 40 ] || { echo "bad SHA: $FULL_SHA" >&2; exit 2; }
echo "fork: $FULL_SHA $(git -C "$FORK" log --format=%s -1 "$FULL_SHA")"

echo "== preflight (mini inputs)"
[ -f "$CODEGEN_DIR/register_functions.cpp" ] || { echo "missing $CODEGEN_DIR/register_functions.cpp" >&2; exit 2; }
[ -f "$CODEGEN_DIR/sub_003FE828_0x3fe828.cpp" ] || { echo "missing $CODEGEN_DIR/sub_003FE828_0x3fe828.cpp" >&2; exit 2; }
if [ -n "$CODEGEN_ARG" ]; then
  CODEGEN_SHA="$(shasum -a 256 "$CODEGEN_DIR/register_functions.cpp" | cut -d' ' -f1)"
  CODEGEN_VF0_SHA="$(shasum -a 256 "$CODEGEN_DIR/sub_003FE828_0x3fe828.cpp" | cut -d' ' -f1)"
  echo "-- custom codegen: $CODEGEN_DIR"
else
  [ "$(shasum -a 256 "$CODEGEN_DIR/register_functions.cpp" | cut -d' ' -f1)" = "$CODEGEN_SHA" ] || { echo "mini codegen register mismatch" >&2; exit 2; }
  [ "$(shasum -a 256 "$CODEGEN_DIR/sub_003FE828_0x3fe828.cpp" | cut -d' ' -f1)" = "$CODEGEN_VF0_SHA" ] || { echo "mini codegen vf0 mismatch" >&2; exit 2; }
fi
C12="$(printf %s "$CODEGEN_SHA" | cut -c1-12)"
[ -f "$ELF_PATH" ] || { echo "missing $ELF_PATH" >&2; exit 2; }
[ "$(shasum -a 256 "$ELF_PATH" | cut -d' ' -f1)" = "$ELF_SHA" ] || { echo "mini ELF mismatch" >&2; exit 2; }
echo "-- mini ISO sha (3 GB, one read)"
[ "$(shasum -a 256 "$ISO_PATH" | cut -d' ' -f1)" = "$ISO_SHA" ] || { echo "mini ISO mismatch" >&2; exit 2; }
ls "$VU1_DIR"/vu1_*.cpp >/dev/null || { echo "no vu1_*.cpp in $VU1_DIR" >&2; exit 2; }
VU1_MINI=$(cd "$VU1_DIR" && shasum -a 256 vu1_*.cpp | shasum -a 256 | cut -d' ' -f1)
V12="$(printf %s "$VU1_MINI" | cut -c1-12)"
[ -n "$VU1_ARG" ] && echo "-- custom vu1: $VU1_DIR ($VU1_MINI)"
ls "$VU0_DIR"/vu0_*.cpp >/dev/null || { echo "no vu0_*.cpp in $VU0_DIR" >&2; exit 2; }
VU0_MINI=$(cd "$VU0_DIR" && shasum -a 256 vu0_*.cpp | shasum -a 256 | cut -d' ' -f1)
V012="$(printf %s "$VU0_MINI" | cut -c1-12)"
[ -n "$VU0_ARG" ] && echo "-- custom vu0: $VU0_DIR ($VU0_MINI)"
P12="$(printf %s "$PGS_PIN" | cut -c1-12)"
if [ -z "$PGS_PIN_ARG" ]; then
  [ "$(git -C "$PGS_DIR" rev-parse HEAD)" = "$PGS_PIN" ] || { echo "mini PGS mismatch" >&2; exit 2; }
  [ "$(git -C "$PGS_DIR/Granite" rev-parse HEAD)" = "$GRANITE_PIN" ] || { echo "mini Granite mismatch" >&2; exit 2; }
else echo "-- custom pgs-pin: $PGS_PIN"; fi
echo "-- mini inputs OK (codegen-$C12 vu1gen-$V12 vu0gen-$V012 pgs-$P12)"

RCODEGEN="codegen-$C12"; RVU1="vu1gen-$V12"; RVU0="vu0gen-$V012"; RPGS="pgs-$P12"

echo "== preflight (bradflix)"
ssh -o ConnectTimeout=10 "$REMOTE" 'echo bradflix; uptime; df -h ~/dev/ssx3-work | tail -1' || exit 1
echo "-- containers (hands off; load check only)"
ssh "$REMOTE" 'docker ps --format "{{.Names}} {{.Status}}"' | head -n 25
LOAD1=$(ssh "$REMOTE" 'cat /proc/loadavg' | cut -d' ' -f1 | cut -d. -f1)
[ "${LOAD1:-0}" -gt 14 ] && echo "WARNING: bradflix load $LOAD1 high; continuing" >&2 || true

echo "== claim build dir $RROOT/$NAME (under the setup lock)"
ssh "$REMOTE" "flock -w 300 ~/$RLOCK mkdir ~/$RROOT/$NAME" || { echo "refusing to reuse ~/$RROOT/$NAME" >&2; exit 2; }

echo "== fork export $FULL_SHA -> $RROOT/$NAME/src"
git -C "$FORK" archive "$FULL_SHA" | ssh "$REMOTE" "mkdir -p ~/$RROOT/$NAME/src && tar -C ~/$RROOT/$NAME/src -xf - && echo $FULL_SHA > ~/$RROOT/$NAME/fork-sha.txt && test -f ~/$RROOT/$NAME/src/CMakeLists.txt && echo EXPORT_OK" || exit 1

rsha() { ssh "$REMOTE" "sha256sum ~/$RROOT/$1 2>/dev/null | cut -d' ' -f1" || true; }

echo "== inputs (content-addressed; shared dirs are never modified)"
if [ "$(rsha $RCODEGEN/register_functions.cpp)" = "$CODEGEN_SHA" ] && \
   [ "$(rsha $RCODEGEN/sub_003FE828_0x3fe828.cpp)" = "$CODEGEN_VF0_SHA" ]; then
  echo "-- $RCODEGEN OK"
else
  echo "-- staging $RCODEGEN from mini"
  STAGE=".stage-$NAME-codegen"
  ssh "$REMOTE" "rm -rf ~/$RROOT/$STAGE; mkdir -p ~/$RROOT/$STAGE" || exit 1
  COPYFILE_DISABLE=1 tar -C "$CODEGEN_DIR" -cf - . | ssh "$REMOTE" "tar -C ~/$RROOT/$STAGE -xf -" || exit 1
  if [ "$(rsha $STAGE/register_functions.cpp)" != "$CODEGEN_SHA" ] || \
     [ "$(rsha $STAGE/sub_003FE828_0x3fe828.cpp)" != "$CODEGEN_VF0_SHA" ]; then
    ssh "$REMOTE" "rm -rf ~/$RROOT/$STAGE" || true
    echo "staged codegen re-verify failed" >&2; exit 2
  fi
  ssh "$REMOTE" "flock -w 600 ~/$RLOCK bash -s" "$RROOT" "$RCODEGEN" "$STAGE" "$CODEGEN_SHA" "$CODEGEN_VF0_SHA" <<'EOF' || exit 1
set -euo pipefail
RROOT=$1 DEST=$2 STAGE=$3 SHA=$4 VF0=$5
if [ "$(sha256sum ~/$RROOT/$DEST/register_functions.cpp 2>/dev/null | cut -d' ' -f1)" = "$SHA" ] && \
   [ "$(sha256sum ~/$RROOT/$DEST/sub_003FE828_0x3fe828.cpp 2>/dev/null | cut -d' ' -f1)" = "$VF0" ]; then
  echo "shared $DEST already published; discarding stage"
  rm -rf ~/$RROOT/$STAGE
elif [ -e ~/$RROOT/$DEST ]; then
  echo "ERROR: ~/$RROOT/$DEST exists with wrong content; refusing to touch it" >&2; exit 2
else
  mv ~/$RROOT/$STAGE ~/$RROOT/$DEST && echo "published $DEST"
fi
EOF
fi

RVU1SUM=$(ssh "$REMOTE" "(cd ~/$RROOT/$RVU1 2>/dev/null && sha256sum vu1_*.cpp | sha256sum | cut -d' ' -f1)" || true)
if [ "$RVU1SUM" = "$VU1_MINI" ]; then
  echo "-- $RVU1 OK"
else
  echo "-- staging $RVU1 from mini"
  STAGE=".stage-$NAME-vu1"
  ssh "$REMOTE" "rm -rf ~/$RROOT/$STAGE; mkdir -p ~/$RROOT/$STAGE" || exit 1
  COPYFILE_DISABLE=1 tar -C "$VU1_DIR" -cf - . | ssh "$REMOTE" "tar -C ~/$RROOT/$STAGE -xf -" || exit 1
  STAGE_SUM=$(ssh "$REMOTE" "(cd ~/$RROOT/$STAGE && sha256sum vu1_*.cpp | sha256sum | cut -d' ' -f1)")
  if [ "$STAGE_SUM" != "$VU1_MINI" ]; then
    ssh "$REMOTE" "rm -rf ~/$RROOT/$STAGE" || true
    echo "staged vu1gen re-verify failed" >&2; exit 2
  fi
  ssh "$REMOTE" "flock -w 600 ~/$RLOCK bash -s" "$RROOT" "$RVU1" "$STAGE" "$VU1_MINI" <<'EOF' || exit 1
set -euo pipefail
RROOT=$1 DEST=$2 STAGE=$3 WANT=$4
HAVE=$(cd ~/$RROOT/$DEST 2>/dev/null && sha256sum vu1_*.cpp | sha256sum | cut -d' ' -f1 || true)
if [ "$HAVE" = "$WANT" ]; then
  echo "shared $DEST already published; discarding stage"
  rm -rf ~/$RROOT/$STAGE
elif [ -e ~/$RROOT/$DEST ]; then
  echo "ERROR: ~/$RROOT/$DEST exists with wrong content; refusing to touch it" >&2; exit 2
else
  mv ~/$RROOT/$STAGE ~/$RROOT/$DEST && echo "published $DEST"
fi
EOF
fi

RVU0SUM=$(ssh "$REMOTE" "(cd ~/$RROOT/$RVU0 2>/dev/null && sha256sum vu0_*.cpp | sha256sum | cut -d' ' -f1)" || true)
if [ "$RVU0SUM" = "$VU0_MINI" ]; then
  echo "-- $RVU0 OK"
else
  echo "-- staging $RVU0 from mini"
  STAGE=".stage-$NAME-vu0"
  ssh "$REMOTE" "rm -rf ~/$RROOT/$STAGE; mkdir -p ~/$RROOT/$STAGE" || exit 1
  COPYFILE_DISABLE=1 tar -C "$VU0_DIR" -cf - . | ssh "$REMOTE" "tar -C ~/$RROOT/$STAGE -xf -" || exit 1
  STAGE_SUM=$(ssh "$REMOTE" "(cd ~/$RROOT/$STAGE && sha256sum vu0_*.cpp | sha256sum | cut -d' ' -f1)")
  if [ "$STAGE_SUM" != "$VU0_MINI" ]; then
    ssh "$REMOTE" "rm -rf ~/$RROOT/$STAGE" || true
    echo "staged vu0gen re-verify failed" >&2; exit 2
  fi
  ssh "$REMOTE" "flock -w 600 ~/$RLOCK bash -s" "$RROOT" "$RVU0" "$STAGE" "$VU0_MINI" <<'EOF' || exit 1
set -euo pipefail
RROOT=$1 DEST=$2 STAGE=$3 WANT=$4
HAVE=$(cd ~/$RROOT/$DEST 2>/dev/null && sha256sum vu0_*.cpp | sha256sum | cut -d' ' -f1 || true)
if [ "$HAVE" = "$WANT" ]; then
  echo "shared $DEST already published; discarding stage"
  rm -rf ~/$RROOT/$STAGE
elif [ -e ~/$RROOT/$DEST ]; then
  echo "ERROR: ~/$RROOT/$DEST exists with wrong content; refusing to touch it" >&2; exit 2
else
  mv ~/$RROOT/$STAGE ~/$RROOT/$DEST && echo "published $DEST"
fi
EOF
fi

if [ "$(rsha inputs/SLUS_207.72)" = "$ELF_SHA" ]; then
  echo "-- ELF OK"
else
  echo "-- staging ELF from mini"
  STAGE=".stage-$NAME-elf"
  scp "$ELF_PATH" "$REMOTE:$RROOT/$STAGE" || exit 1
  [ "$(rsha $STAGE)" = "$ELF_SHA" ] || { ssh "$REMOTE" "rm -f ~/$RROOT/$STAGE" || true; echo "staged ELF re-verify failed" >&2; exit 2; }
  ssh "$REMOTE" "flock -w 600 ~/$RLOCK bash -s" "$RROOT" "$STAGE" "$ELF_SHA" <<'EOF' || exit 1
set -euo pipefail
RROOT=$1 STAGE=$2 WANT=$3
if [ "$(sha256sum ~/$RROOT/inputs/SLUS_207.72 2>/dev/null | cut -d' ' -f1)" = "$WANT" ]; then
  echo "shared inputs/SLUS_207.72 already present; discarding stage"
  rm -f ~/$RROOT/$STAGE
else
  mv ~/$RROOT/$STAGE ~/$RROOT/inputs/SLUS_207.72 && echo "published inputs/SLUS_207.72"
fi
EOF
fi

if [ "$(ssh "$REMOTE" "sha256sum ~/$RROOT/inputs/SSX\\ 3\\ \\(USA\\).iso 2>/dev/null | cut -d' ' -f1" || true)" = "$ISO_SHA" ]; then
  echo "-- ISO OK"
else
  STAGE=".stage-$NAME-iso"
  if [ "$(ssh "$REMOTE" "sha256sum ~/dev/ssx3-work/LX1/inputs/SSX\\ 3\\ \\(USA\\).iso 2>/dev/null | cut -d' ' -f1" || true)" = "$ISO_SHA" ]; then
    echo "-- staging ISO from LX1 dir on bradflix (verified)"
    ssh "$REMOTE" "cp ~/dev/ssx3-work/LX1/inputs/SSX\\ 3\\ \\(USA\\).iso ~/$RROOT/$STAGE" || exit 1
  else
    echo "-- staging ISO from mini (3 GB)"
    scp "$ISO_PATH" "$REMOTE:$RROOT/$STAGE" || exit 1
  fi
  [ "$(rsha $STAGE)" = "$ISO_SHA" ] || { ssh "$REMOTE" "rm -f ~/$RROOT/$STAGE" || true; echo "staged ISO re-verify failed" >&2; exit 2; }
  ssh "$REMOTE" "flock -w 600 ~/$RLOCK bash -s" "$RROOT" "$STAGE" "$ISO_SHA" <<'EOF' || exit 1
set -euo pipefail
RROOT=$1 STAGE=$2 WANT=$3
if [ "$(sha256sum ~/$RROOT/inputs/SSX\ 3\ \(USA\).iso 2>/dev/null | cut -d' ' -f1)" = "$WANT" ]; then
  echo "shared ISO already present; discarding stage"
  rm -f ~/$RROOT/$STAGE
else
  mv ~/$RROOT/$STAGE ~/$RROOT/inputs/SSX\ 3\ \(USA\).iso && echo "published ISO"
fi
EOF
fi

pgs_ok() {
  [ "$(ssh "$REMOTE" "git -C ~/$RROOT/$RPGS rev-parse HEAD 2>/dev/null" || true)" = "$PGS_PIN" ] && \
  [ "$(ssh "$REMOTE" "git -C ~/$RROOT/$RPGS/Granite rev-parse HEAD 2>/dev/null" || true)" = "$GRANITE_PIN" ] && \
  [ "$(ssh "$REMOTE" "git -C ~/$RROOT/$RPGS submodule status --recursive 2>/dev/null | wc -l" || true)" = "$PGS_SUBMODULES" ]
}
if [ -n "$PGS_PIN_ARG" ]; then
  echo "-- custom pgs-pin: expecting a same-count ($PGS_SUBMODULES) tree"
fi
if pgs_ok; then
  echo "-- $RPGS $PGS_PIN / Granite $GRANITE_PIN OK"
elif ssh "$REMOTE" "test -e ~/$RROOT/$RPGS"; then
  echo "ERROR: ~/$RROOT/$RPGS exists but fails verification; refusing to touch it" >&2; exit 2
else
  echo "-- cloning $RPGS pins on bradflix (private stage, then atomic publish)"
  STAGE=".pgs-stage-$NAME"
  ssh "$REMOTE" "rm -rf ~/$RROOT/$STAGE; mkdir -p ~/$RROOT/$STAGE" || exit 1
  ssh "$REMOTE" "cd ~/$RROOT/$STAGE && git clone --recursive --branch ssx3 https://github.com/brad-richardson/parallel-gs.git pgs 2>&1 | tail -1" || exit 1
  ssh "$REMOTE" "git -C ~/$RROOT/$STAGE/pgs checkout --detach $PGS_PIN 2>&1 | tail -1 && git -C ~/$RROOT/$STAGE/pgs/Granite checkout --detach $GRANITE_PIN 2>&1 | tail -1 && git -C ~/$RROOT/$STAGE/pgs submodule update --init --recursive 2>&1 | tail -1" || exit 1
  STAGE_PGS=$(ssh "$REMOTE" "git -C ~/$RROOT/$STAGE/pgs rev-parse HEAD")
  STAGE_GRAN=$(ssh "$REMOTE" "git -C ~/$RROOT/$STAGE/pgs/Granite rev-parse HEAD")
  STAGE_SUBS=$(ssh "$REMOTE" "git -C ~/$RROOT/$STAGE/pgs submodule status --recursive | wc -l")
  if [ "$STAGE_PGS" != "$PGS_PIN" ] || [ "$STAGE_GRAN" != "$GRANITE_PIN" ] || [ "$STAGE_SUBS" != "$PGS_SUBMODULES" ]; then
    ssh "$REMOTE" "rm -rf ~/$RROOT/$STAGE" || true
    echo "staged PGS re-verify failed ($STAGE_PGS / $STAGE_GRAN / $STAGE_SUBS subs)" >&2; exit 2
  fi
  ssh "$REMOTE" "flock -w 600 ~/$RLOCK bash -s" "$RROOT" "$RPGS" "$STAGE" "$PGS_PIN" "$GRANITE_PIN" "$PGS_SUBMODULES" <<'EOF' || exit 1
set -euo pipefail
RROOT=$1 DEST=$2 STAGE=$3 PGS=$4 GRAN=$5 SUBS=$6
if [ "$(git -C ~/$RROOT/$DEST rev-parse HEAD 2>/dev/null || true)" = "$PGS" ] && \
   [ "$(git -C ~/$RROOT/$DEST/Granite rev-parse HEAD 2>/dev/null || true)" = "$GRAN" ] && \
   [ "$(git -C ~/$RROOT/$DEST submodule status --recursive 2>/dev/null | wc -l || true)" = "$SUBS" ]; then
  echo "shared $DEST already published; discarding stage"
  rm -rf ~/$RROOT/$STAGE
elif [ -e ~/$RROOT/$DEST ]; then
  echo "ERROR: ~/$RROOT/$DEST exists with wrong content; refusing to touch it" >&2; exit 2
else
  mv ~/$RROOT/$STAGE/pgs ~/$RROOT/$DEST && rm -rf ~/$RROOT/$STAGE && echo "published $DEST"
fi
EOF
fi

echo "== image $IMAGE (cached layers are fast)"
scp "$REPO/local/tooling/build/Dockerfile.bradflix" "$REMOTE:$RROOT/.stage-$NAME-Dockerfile" || exit 1
ssh "$REMOTE" "flock -w 600 ~/$RLOCK bash -s" "$RROOT" "$IMAGE" ".stage-$NAME-Dockerfile" <<'EOF' || exit 1
set -euo pipefail
RROOT=$1 IMAGE=$2 STAGE=$3
cd ~/$RROOT && docker build -t $IMAGE -f $STAGE . 2>&1 | tail -1
rm -f ~/$RROOT/$STAGE
EOF
IMAGE_ID=$(ssh "$REMOTE" "docker images $IMAGE --format '{{.ID}}'")
echo "image: $IMAGE $IMAGE_ID"

echo "== ccache before"
ssh "$REMOTE" "mkdir -p ~/$RCCACHE && docker run --rm --user 1000:1000 -e CCACHE_DIR=/ccache -v ~/$RCCACHE:/ccache $IMAGE ccache -s | grep -iE 'cache size|cacheable|hits|misses' | head -n 6" || true

echo "== configure $RROOT/$NAME (det=$DET)"
START=$SECONDS
ssh "$REMOTE" "docker run --rm --user 1000:1000 -e HOME=/work -e CCACHE_DIR=/ccache -e CCACHE_BASEDIR=/work -w /work -v ~/$RROOT:/work -v ~/$RCCACHE:/ccache $IMAGE cmake -S /work/$NAME/src -B /work/$NAME -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache -DPS2X_GAME_CODEGEN_DIR=/work/$RCODEGEN -DPS2X_VU1_RECOMP_DIR=/work/$RVU1 -DPS2X_VU0_RECOMP_DIR=/work/$RVU0 -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=$DET -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/work/$RPGS -DPS2X_ENABLE_SCCACHE=OFF -DPS2X_RUNNER_UNITY_BUILD_BATCH_SIZE=$BATCH -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_C_FLAGS=-msse4.1 -DCMAKE_CXX_FLAGS=-msse4.1$EXTRA > ~/$RROOT/$NAME-configure.log 2>&1; echo CONFIGURE_RC=\$?; grep -m1 'VU1 recomp' ~/$RROOT/$NAME-configure.log" || exit 1

echo "== build (16 jobs)"
ssh "$REMOTE" "docker run --rm --user 1000:1000 -e HOME=/work -e CCACHE_DIR=/ccache -e CCACHE_BASEDIR=/work -w /work -v ~/$RROOT:/work -v ~/$RCCACHE:/ccache $IMAGE cmake --build /work/$NAME --parallel 16 --target ps2x_tests ps2EntryRunner > ~/$RROOT/$NAME-build.log 2>&1; echo BUILD_RC=\$?; tail -1 ~/$RROOT/$NAME-build.log" || exit 1
echo "--- wall: $((SECONDS - START)) s (configure+build) ---"

echo "== ccache after"
ssh "$REMOTE" "docker run --rm --user 1000:1000 -e CCACHE_DIR=/ccache -v ~/$RCCACHE:/ccache $IMAGE ccache -s | grep -iE 'cache size|cacheable|hits|misses' | head -n 6" || true

R1=$(ssh "$REMOTE" "sha256sum ~/$RROOT/$NAME/ps2xRuntime/ps2EntryRunner | cut -d' ' -f1")
R2=$(ssh "$REMOTE" "sha256sum ~/$RROOT/$NAME/ps2xRuntime/ps2EntryRunner | cut -d' ' -f1")
[ "$R1" = "$R2" ] || { echo "two runner SHA reads differ" >&2; exit 2; }
SIZE=$(ssh "$REMOTE" "stat -c%s ~/$RROOT/$NAME/ps2xRuntime/ps2EntryRunner")
echo "runner: ~/$RROOT/$NAME/ps2xRuntime/ps2EntryRunner sha=$R1 size=$SIZE fork=$FULL_SHA det=$DET image=$IMAGE_ID src=$NAME/src codegen=$RCODEGEN vu1=$RVU1 vu0=$RVU0 pgs=$RPGS"
