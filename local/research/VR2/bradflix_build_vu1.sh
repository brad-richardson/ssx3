#!/bin/bash
# Canonical bradflix runner build (HS1): the F5 recipe of record behind a
# shared ccache, so every lane compiles only what it changed. Counterpart
# to local/tooling/build/mac_build.sh (RS1) for the correctness host.
#
# Usage:
#   bradflix_build.sh <fork-sha> <build-name> [--det]
#
#   <fork-sha>    fork commit (full or unambiguous short) on origin/ssx3.
#                Checked out detached on bradflix; never pushed.
#   <build-name>  plain name; the remote build dir is created fresh at
#                ~/dev/ssx3-work/HS1/<build-name> (refuses to reuse).
#   --det         PS2X_ENABLE_DET_HASH_TAP=ON (default OFF)
#
# Syncs inputs SHA-checked (codegen, VU1 images, ISO/ELF, parallel-gs +
# Granite, fork checkout), builds in Docker (image ssx3-hs1) with ccache
# (cache in bind-mounted ~/dev/ssx3-work/ccache, CCACHE_BASEDIR=/work),
# prints wall + ccache hit rate + runner SHA (two reads).
#
# Cold = fresh build name + empty ccache; warm = fresh build name + hot
# ccache. DIAG_TAPS is always OFF here (HS1: DIAG instrumentation blew one
# unity TU to ~25 min; correctness builds never need it).
set -euo pipefail

if [ $# -lt 2 ]; then sed -n '2,14p' "$0"; exit 2; fi
SHA_IN=$1; NAME=$2; shift 2
DET=OFF
while [ $# -gt 0 ]; do
  case $1 in
    --det) DET=ON;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
  shift
done
case "$NAME" in *..*|*/*|"" ) echo "bad build-name: $NAME" >&2; exit 2;; esac

REMOTE="bradflix"
RROOT="dev/ssx3-work/HS1"
RCCACHE="dev/ssx3-work/ccache"
IMAGE="ssx3-hs1"
# Game-code unity batch size: fork default 32 (HS1 step 1 measured 16 as
# no better cold: 411 s vs 400 s at 32 — header re-parse eats the -O3 tail
# saving; -O1 halves the hot TU but taxes every boot's wall and still only
# projects to ~300 s, so -O3 stands; see REPORT.md).
BATCH=32
REPO=/Users/brad/dev/ssx3  # VR2 copy lives outside the repo

ISO_SHA='3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
ELF_SHA='1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
CODEGEN_SHA='8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'
CODEGEN_VF0_SHA='89953ba218efd63c2fdba28116765d524977f1233d0e370d22111a762e02383d'
PGS_PIN='1b3a2948cc55e74f975e42b79d08983f31c2dbb6'
GRANITE_PIN='166ba21a247a681903cc9d0bb6562fe50a554c85'

CODEGEN_DIR=$HOME/dev/ssx3-work/codegen-ssx3
VU1_DIR=${VR2_VU1_DIR:?set VR2_VU1_DIR}
RVU1DIR=${VR2_RVU1DIR:?set VR2_RVU1DIR}
ELF_PATH=$HOME/dev/ssx3-work/E32-inputs/cd/SLUS_207.72
ISO_PATH=$HOME/dev/ssx3-work/E32-inputs/SSX\ 3\ \(USA\).iso
PGS_DIR=$HOME/dev/ssx3-work/parallel-gs-ssx3

echo "== preflight (mini canonical pins)"
[ -f "$CODEGEN_DIR/register_functions.cpp" ] || { echo "missing $CODEGEN_DIR" >&2; exit 2; }
[ "$(shasum -a 256 "$CODEGEN_DIR/register_functions.cpp" | cut -d' ' -f1)" = "$CODEGEN_SHA" ] || { echo "mini codegen register mismatch" >&2; exit 2; }
[ "$(shasum -a 256 "$CODEGEN_DIR/sub_003FE828_0x3fe828.cpp" | cut -d' ' -f1)" = "$CODEGEN_VF0_SHA" ] || { echo "mini codegen vf0 mismatch" >&2; exit 2; }
[ "$(shasum -a 256 "$ELF_PATH" | cut -d' ' -f1)" = "$ELF_SHA" ] || { echo "mini ELF mismatch" >&2; exit 2; }
echo "-- mini ISO sha (3 GB, one read)"
[ "$(shasum -a 256 "$ISO_PATH" | cut -d' ' -f1)" = "$ISO_SHA" ] || { echo "mini ISO mismatch" >&2; exit 2; }
(cd "$VU1_DIR" && shasum -a 256 vu1_*.cpp) > /tmp/hs1-vu1mini.sha
VU1_MINI=$(shasum -a 256 /tmp/hs1-vu1mini.sha | cut -d' ' -f1)
if [ -n "${VR2_PGS_PIN:-}" ]; then PGS_PIN=$VR2_PGS_PIN; echo "-- VR2: remote paraLLEl pin override $PGS_PIN (mini check skipped)";
else [ "$(git -C "$PGS_DIR" rev-parse HEAD)" = "$PGS_PIN" ] || { echo "mini PGS mismatch" >&2; exit 2; }; fi
[ "$(git -C "$PGS_DIR/Granite" rev-parse HEAD)" = "$GRANITE_PIN" ] || { echo "mini Granite mismatch" >&2; exit 2; }
echo "-- mini canonical OK"

echo "== preflight (bradflix)"
ssh -o ConnectTimeout=10 "$REMOTE" 'echo bradflix; uptime; df -h ~/dev/ssx3-work | tail -1' || exit 1
echo "-- containers (hands off; load check only)"
ssh "$REMOTE" 'docker ps --format "{{.Names}} {{.Status}}"' | head -n 25
LOAD1=$(ssh "$REMOTE" 'cat /proc/loadavg' | cut -d' ' -f1 | cut -d. -f1)
[ "${LOAD1:-0}" -gt 14 ] && echo "WARNING: bradflix load $LOAD1 high; continuing" >&2 || true
ssh "$REMOTE" "test -e ~/$RROOT/$NAME" && { echo "refusing to reuse ~/$RROOT/$NAME" >&2; exit 2; } || true

echo "== fork checkout $SHA_IN"
# VR2 copy: a private export (PS2Recomp-vr2, git archive of the SHA, no .git),
# so another lane's checkout in the shared PS2Recomp cannot change sources mid-build.
ssh "$REMOTE" "cd ~/$RROOT/PS2Recomp && git fetch origin ssx3 2>&1 | tail -1; rm -rf ../PS2Recomp-vr2 && mkdir ../PS2Recomp-vr2 && git archive $SHA_IN | tar -C ../PS2Recomp-vr2 -xf -" || exit 1
FULL_SHA="$(ssh "$REMOTE" "git -C ~/$RROOT/PS2Recomp rev-parse $SHA_IN^{commit}")"
case "$FULL_SHA" in *[!0-9a-f]*|"") echo "bad SHA from remote: $FULL_SHA" >&2; exit 2;; esac
[ "${#FULL_SHA}" -eq 40 ] || { echo "bad SHA from remote: $FULL_SHA" >&2; exit 2; }
echo "remote HEAD: $FULL_SHA"

rsha() { ssh "$REMOTE" "sha256sum ~/$RROOT/$1 2>/dev/null | cut -d' ' -f1" || true; }

echo "== inputs (verify, sync on mismatch)"
if [ "$(rsha codegen/register_functions.cpp)" != "$CODEGEN_SHA" ] || \
   [ "$(rsha codegen/sub_003FE828_0x3fe828.cpp)" != "$CODEGEN_VF0_SHA" ]; then
  echo "-- syncing codegen from mini"
  COPYFILE_DISABLE=1 tar -C "$CODEGEN_DIR" -cf - . | ssh "$REMOTE" "mkdir -p ~/$RROOT/codegen && tar -C ~/$RROOT/codegen -xf -"
  [ "$(rsha codegen/register_functions.cpp)" = "$CODEGEN_SHA" ] || { echo "codegen re-verify failed" >&2; exit 2; }
  [ "$(rsha codegen/sub_003FE828_0x3fe828.cpp)" = "$CODEGEN_VF0_SHA" ] || { echo "codegen vf0 re-verify failed" >&2; exit 2; }
else echo "-- codegen OK"; fi

RVU1=$(ssh "$REMOTE" "(cd ~/$RROOT/$RVU1DIR 2>/dev/null && sha256sum vu1_*.cpp | sha256sum | cut -d' ' -f1)" || true)
if [ "$RVU1" != "$VU1_MINI" ]; then
  echo "-- syncing vu1gen from mini"
  COPYFILE_DISABLE=1 tar -C "$VU1_DIR" -cf - . | ssh "$REMOTE" "mkdir -p ~/$RROOT/$RVU1DIR && tar -C ~/$RROOT/$RVU1DIR -xf -"
  RVU1=$(ssh "$REMOTE" "(cd ~/$RROOT/$RVU1DIR && sha256sum vu1_*.cpp | sha256sum | cut -d' ' -f1)")
  [ "$RVU1" = "$VU1_MINI" ] || { echo "vu1gen re-verify failed" >&2; exit 2; }
else echo "-- vu1gen OK"; fi

if [ "$(rsha inputs/SLUS_207.72)" != "$ELF_SHA" ]; then
  echo "-- syncing ELF from mini"
  scp "$ELF_PATH" "$REMOTE:$RROOT/inputs/SLUS_207.72" || exit 1
  [ "$(rsha inputs/SLUS_207.72)" = "$ELF_SHA" ] || { echo "ELF re-verify failed" >&2; exit 2; }
else echo "-- ELF OK"; fi

if [ "$(ssh "$REMOTE" "sha256sum ~/$RROOT/inputs/SSX\\ 3\\ \\(USA\\).iso 2>/dev/null | cut -d' ' -f1" || true)" != "$ISO_SHA" ]; then
  if [ "$(ssh "$REMOTE" "sha256sum ~/dev/ssx3-work/LX1/inputs/SSX\\ 3\\ \\(USA\\).iso 2>/dev/null | cut -d' ' -f1" || true)" = "$ISO_SHA" ]; then
    echo "-- copying ISO from LX1 dir on bradflix (verified)"
    ssh "$REMOTE" "cp ~/dev/ssx3-work/LX1/inputs/SSX\\ 3\\ \\(USA\\).iso ~/$RROOT/inputs/" || exit 1
  else
    echo "-- syncing ISO from mini (3 GB)"
    scp "$ISO_PATH" "$REMOTE:$RROOT/inputs/SSX 3 (USA).iso" || exit 1
  fi
  [ "$(ssh "$REMOTE" "sha256sum ~/$RROOT/inputs/SSX\\ 3\\ \\(USA\\).iso | cut -d' ' -f1")" = "$ISO_SHA" ] || { echo "ISO re-verify failed" >&2; exit 2; }
else echo "-- ISO OK"; fi

RPGS=$(ssh "$REMOTE" "git -C ~/$RROOT/parallel-gs rev-parse HEAD 2>/dev/null" || true)
RGRAN=$(ssh "$REMOTE" "git -C ~/$RROOT/parallel-gs/Granite rev-parse HEAD 2>/dev/null" || true)
if [ "$RPGS" != "$PGS_PIN" ] || [ "$RGRAN" != "$GRANITE_PIN" ]; then
  # VR2 copy: the shared parallel-gs belongs to every lane; never re-clone it here.
  echo "shared parallel-gs is $RPGS / $RGRAN, want $PGS_PIN / $GRANITE_PIN: stop" >&2; exit 2
else echo "-- parallel-gs $RPGS / Granite $RGRAN OK"; fi

echo "== image $IMAGE (cached layers are fast)"
scp "$REPO/local/tooling/build/Dockerfile.bradflix" "$REMOTE:$RROOT/" || exit 1
ssh "$REMOTE" "cd ~/$RROOT && docker build -t $IMAGE -f Dockerfile.bradflix . 2>&1 | tail -1" || exit 1
IMAGE_ID=$(ssh "$REMOTE" "docker images $IMAGE --format '{{.ID}}'")
echo "image: $IMAGE $IMAGE_ID"

echo "== ccache before"
ssh "$REMOTE" "mkdir -p ~/$RCCACHE && docker run --rm --user 1000:1000 -e CCACHE_DIR=/ccache -v ~/$RCCACHE:/ccache $IMAGE ccache -s | grep -iE 'cache size|cacheable|hits|misses' | head -n 6" || true

echo "== configure $RROOT/$NAME (det=$DET)"
START=$SECONDS
ssh "$REMOTE" "docker run --rm --user 1000:1000 -e HOME=/work -e CCACHE_DIR=/ccache -e CCACHE_BASEDIR=/work -w /work -v ~/$RROOT:/work -v ~/$RCCACHE:/ccache $IMAGE cmake -S /work/PS2Recomp-vr2 -B /work/$NAME -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache -DPS2X_GAME_CODEGEN_DIR=/work/codegen -DPS2X_VU1_RECOMP_DIR=/work/$RVU1DIR -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=$DET -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/work/parallel-gs -DPS2X_ENABLE_SCCACHE=OFF -DPS2X_RUNNER_UNITY_BUILD_BATCH_SIZE=$BATCH -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_C_FLAGS=-msse4.1 -DCMAKE_CXX_FLAGS=-msse4.1 > ~/$RROOT/$NAME-configure.log 2>&1; echo CONFIGURE_RC=\$?; grep -m1 'VU1 recomp' ~/$RROOT/$NAME-configure.log" || exit 1

echo "== build (16 jobs)"
ssh "$REMOTE" "docker run --rm --user 1000:1000 -e HOME=/work -e CCACHE_DIR=/ccache -e CCACHE_BASEDIR=/work -w /work -v ~/$RROOT:/work -v ~/$RCCACHE:/ccache $IMAGE cmake --build /work/$NAME --parallel 16 --target ps2x_tests ps2EntryRunner > ~/$RROOT/$NAME-build.log 2>&1; echo BUILD_RC=\$?; tail -1 ~/$RROOT/$NAME-build.log" || exit 1
echo "--- wall: $((SECONDS - START)) s (configure+build) ---"

echo "== ccache after"
ssh "$REMOTE" "docker run --rm --user 1000:1000 -e CCACHE_DIR=/ccache -v ~/$RCCACHE:/ccache $IMAGE ccache -s | grep -iE 'cache size|cacheable|hits|misses' | head -n 6" || true

R1=$(ssh "$REMOTE" "sha256sum ~/$RROOT/$NAME/ps2xRuntime/ps2EntryRunner | cut -d' ' -f1")
R2=$(ssh "$REMOTE" "sha256sum ~/$RROOT/$NAME/ps2xRuntime/ps2EntryRunner | cut -d' ' -f1")
[ "$R1" = "$R2" ] || { echo "two runner SHA reads differ" >&2; exit 2; }
SIZE=$(ssh "$REMOTE" "stat -c%s ~/$RROOT/$NAME/ps2xRuntime/ps2EntryRunner")
echo "runner: ~/$RROOT/$NAME/ps2xRuntime/ps2EntryRunner sha=$R1 size=$SIZE fork=$FULL_SHA det=$DET image=$IMAGE_ID"
