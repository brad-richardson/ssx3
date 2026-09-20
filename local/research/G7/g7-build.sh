#!/usr/bin/env bash
# G7: PCSX2 auto-GS-dump clone+patch+build (runs INSIDE WSL as brad).
# T4 AND R1 trees/binaries untouched: fresh local clone of T4 at
# /home/brad/pcsx2-g7/pcsx2, R1 one-liner (epoch verification) + G7
# two-hunk auto-dump patch, T4 configure flags, ninja -j2 (K1 rule).
set -x
date -u
rm -rf /home/brad/pcsx2-g7/pcsx2
mkdir -p /home/brad/pcsx2-g7
git clone /home/brad/pcsx2-t4/pcsx2 /home/brad/pcsx2-g7/pcsx2 || { echo G7_FAIL:CLONE; exit 1; }
cd /home/brad/pcsx2-g7/pcsx2
git rev-parse HEAD
git status --short
python3 - <<'EOF'
import io
# Hunk 1 (R1 one-liner, kept for ExecPS2 epoch verification in the G7 emulog).
p = "pcsx2/R5900OpcodeImpl.cpp"
s = io.open(p, encoding="utf-8").read()
before = '\tBIOS_LOG("Bios call: %s (%x)", R5900::bios[call], call);'
after = '\tBIOS_LOG("Bios call: %s (%x) pc=%x a0=%x", R5900::bios[call], call, cpuRegs.pc, cpuRegs.GPR.n.a0.UL[0]);'
assert s.count(before) == 1, ("R1", s.count(before))
s = s.replace(before, after)
# Hunk 2 (G7-EE): ExecPS2 counter for the auto-dump trigger.
# NOTE: must be at GLOBAL scope: SYSCALL() lives inside
# R5900::Interpreter::OpcodeImpl (R5900OpcodeImpl.cpp:248-1286).
before = 'namespace R5900 {\n'
after = ('#include <atomic>\n\n'
         '// G7: counts ExecPS2 syscalls (global scope); the GS thread auto-queues one\n'
         '// 5-frame GS dump 60 vsyncs after the 5th (game entry). One-shot capture aid.\n'
         'std::atomic<int> g_g7_execps2_count{0};\n\nnamespace R5900 {\n')
assert s.count(before) == 1, ("G7EE-DECL", s.count(before))
s = s.replace(before, after)
before = '\t\tcase Syscall::ExecPS2:\n\t\t{\n'
after = ('\t\tcase Syscall::ExecPS2:\n\t\t{\n'
         '\t\t\tg_g7_execps2_count.fetch_add(1, std::memory_order_relaxed);\n')
assert s.count(before) == 1, ("G7EE-INC", s.count(before))
s = s.replace(before, after)
io.open(p, "w", encoding="utf-8").write(s)
# Hunk 3 (G7-GS): vsync hook that queues the dump on the GS thread.
p = "pcsx2/GS/GS.cpp"
s = io.open(p, encoding="utf-8").read()
before = '#include "VMManager.h"\n'
after = '#include "VMManager.h"\n\n#include <atomic>\n\nextern std::atomic<int> g_g7_execps2_count; // G7: defined in R5900OpcodeImpl.cpp.\n'
assert s.count(before) == 1, ("G7GS-INC", s.count(before))
s = s.replace(before, after)
before = ('void GSvsync(u32 field, bool registers_written)\n{\n'
          '\t// Update this here because we need to check if the pending draw affects the current frame, so our regs need to be updated.\n')
after = (before +
         '\t// G7: one-shot auto GS dump (5 frames) 60 vsyncs after game entry (ExecPS2 #5).\n'
         '\t{\n'
         '\t\tstatic int g7_since_entry = 0;\n'
         '\t\tstatic bool g7_dump_queued = false;\n'
         '\t\tif (!g7_dump_queued && g_g7_execps2_count.load(std::memory_order_relaxed) >= 5 && ++g7_since_entry == 60)\n'
         '\t\t{\n'
         '\t\t\tg7_dump_queued = true;\n'
         '\t\t\tConsole.WriteLn("G7_DUMP_QUEUED");\n'
         '\t\t\tGSQueueSnapshot(std::string(), 5);\n'
         '\t\t}\n'
         '\t}\n')
assert s.count(before) == 1, ("G7GS-HOOK", s.count(before))
s = s.replace(before, after)
io.open(p, "w", encoding="utf-8").write(s)
print("G7_PATCH_OK")
EOF
git diff --stat
git diff
if [ -d /home/brad/pcsx2-r1/.ccache ]; then
  export CCACHE_DIR=/home/brad/pcsx2-r1/.ccache
else
  export CCACHE_DIR=/home/brad/pcsx2-g7/.ccache
fi
export CCACHE_BASEDIR=/home/brad/pcsx2-g7/pcsx2
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
  -DCMAKE_DISABLE_PRECOMPILE_HEADERS=ON 2>&1 | tee /home/brad/pcsx2-g7/build-config.log
echo "CONFIG_EXIT:${PIPESTATUS[0]}"
date -u
ninja -C build -j2 2>&1 | tee /home/brad/pcsx2-g7/build-build.log
echo "BUILD_EXIT:${PIPESTATUS[0]}"
date -u
sha256sum build/bin/pcsx2-qt
stat -c %s build/bin/pcsx2-qt
grep -c PCSX2_DEVBUILD build/build.ninja || true
# R1 + T4 reference binaries + trees must be untouched:
sha256sum /home/brad/pcsx2-r1/pcsx2/build/bin/pcsx2-qt
sha256sum /home/brad/pcsx2-t4/pcsx2/build/bin/pcsx2-qt
git -C /home/brad/pcsx2-r1/pcsx2 status --short
git -C /home/brad/pcsx2-t4/pcsx2 status --short
echo G7_BUILD_DONE
