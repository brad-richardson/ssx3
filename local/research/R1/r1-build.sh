#!/usr/bin/env bash
# R1: separate pc-tagged PCSX2 Devel clone+patch+build (runs INSIDE WSL as brad).
# T4 tree/binary untouched: fresh local clone at /home/brad/pcsx2-r1/pcsx2,
# one-line patch, same T4 configure flags, Devel build. Unattended (~5 min).
set -x
date -u
rm -rf /home/brad/pcsx2-r1
mkdir -p /home/brad/pcsx2-r1
git clone /home/brad/pcsx2-t4/pcsx2 /home/brad/pcsx2-r1/pcsx2 || { echo R1_FAIL:CLONE; exit 1; }
cd /home/brad/pcsx2-r1/pcsx2
git rev-parse HEAD
git status --short
grep -n "Bios call" pcsx2/R5900OpcodeImpl.cpp
python3 - <<'EOF'
import io
p = "pcsx2/R5900OpcodeImpl.cpp"
s = io.open(p, encoding="utf-8").read()
before = '\tBIOS_LOG("Bios call: %s (%x)", R5900::bios[call], call);'
after = '\tBIOS_LOG("Bios call: %s (%x) pc=%x a0=%x", R5900::bios[call], call, cpuRegs.pc, cpuRegs.GPR.n.a0.UL[0]);'
assert s.count(before) == 1, s.count(before)
io.open(p, "w", encoding="utf-8").write(s.replace(before, after))
print("R1_PATCH_OK")
EOF
git diff --stat
git diff
export CCACHE_BASEDIR=/home/brad/pcsx2-r1/pcsx2 CCACHE_DIR=/home/brad/pcsx2-r1/.ccache
export CCACHE_COMPRESS=true CCACHE_COMPRESSLEVEL=9 CCACHE_MAXSIZE=2G
cmake -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Devel \
  -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF \
  -DCMAKE_PREFIX_PATH=/home/brad/deps \
  -DCMAKE_C_COMPILER=clang \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_EXE_LINKER_FLAGS_INIT="-fuse-ld=lld" \
  -DCMAKE_MODULE_LINKER_FLAGS_INIT="-fuse-ld=lld" \
  -DCMAKE_C_COMPILER_LAUNCHER=ccache \
  -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
  -DENABLE_SETCAP=OFF \
  -DDISABLE_ADVANCE_SIMD=TRUE \
  -DUSE_LINKED_FFMPEG=ON \
  -DCMAKE_DISABLE_PRECOMPILE_HEADERS=ON 2>&1 | tee /home/brad/pcsx2-r1/build-config.log
echo "CONFIG_EXIT:${PIPESTATUS[0]}"
date -u
ninja -C build -j10 2>&1 | tee /home/brad/pcsx2-r1/build-build.log
echo "BUILD_EXIT:${PIPESTATUS[0]}"
date -u
sha256sum build/bin/pcsx2-qt
stat -c %s build/bin/pcsx2-qt
grep -c PCSX2_DEVBUILD build/build.ninja || true
# T4 reference binary + tree must be untouched:
sha256sum /home/brad/pcsx2-t4/pcsx2/build/bin/pcsx2-qt
stat -c %s /home/brad/pcsx2-t4/pcsx2/build/bin/pcsx2-qt
git -C /home/brad/pcsx2-t4/pcsx2 status --short
echo R1_BUILD_DONE
