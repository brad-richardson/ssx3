#!/usr/bin/env bash
# G8: draw-aware trigger hunks on the G7 tree + incremental rebuild.
# Reuses /home/brad/pcsx2-g7/pcsx2 (T4 rev 9056c083 + R1 one-liner + G7 hunks,
# verified before patching). No new clone, ninja -j2 (K1 rule).
# Runs INSIDE WSL as brad.
set -x
date -u
uptime
cd /home/brad/pcsx2-g7/pcsx2
git rev-parse HEAD
git status --short
git diff --stat
python3 - <<'EOF'
import io
# H1 (G8-GS-CTR): global Transfer counter definition in GS.cpp.
p = "pcsx2/GS/GS.cpp"
s = io.open(p, encoding="utf-8").read()
before = 'extern std::atomic<int> g_g7_execps2_count; // G7: defined in R5900OpcodeImpl.cpp.\n'
after = (before +
         'std::atomic<int> g_g8_transfer_count{0}; // G8: Transfer-packet counter, incremented on the GS thread in GSState::Transfer.\n')
assert s.count(before) == 1, ("G8-CTR", s.count(before))
s = s.replace(before, after)
# H2 (G8-GS-TRIG): replace the G7 entry+60 trigger with the draw-aware trigger
# (queue 5-frame dump K=500 transfers after the first non-zero-transfer vsync
# past game entry). G7's queue call is replaced, not duplicated.
before = ('\t// G7: one-shot auto GS dump (5 frames) 60 vsyncs after game entry (ExecPS2 #5).\n'
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
after = ('\t// G8: draw-aware one-shot auto GS dump (5 frames). Queues K transfers after\n'
         '\t// the first non-zero-transfer vsync past game entry (ExecPS2 #5).\n'
         '\t{\n'
         '\t\tstatic int g8_vsync_index = 0;\n'
         '\t\tstatic bool g8_armed = false;\n'
         '\t\tstatic int g8_prev_total = 0;\n'
         '\t\tstatic int g8_first_nonzero_vsync = -1;\n'
         '\t\tstatic int g8_first_nonzero_total = 0;\n'
         '\t\tstatic bool g8_dump_queued = false;\n'
         '\t\tif (!g8_dump_queued && g_g7_execps2_count.load(std::memory_order_relaxed) >= 5)\n'
         '\t\t{\n'
         '\t\t\tconst int total = g_g8_transfer_count.load(std::memory_order_relaxed);\n'
         '\t\t\tif (!g8_armed)\n'
         '\t\t\t{\n'
         '\t\t\t\tg8_armed = true;\n'
         '\t\t\t\tg8_prev_total = total;\n'
         '\t\t\t}\n'
         '\t\t\telse\n'
         '\t\t\t{\n'
         '\t\t\t\tconst int this_vsync = total - g8_prev_total;\n'
         '\t\t\t\tg8_prev_total = total;\n'
         '\t\t\t\tif (this_vsync > 0 && g8_first_nonzero_vsync < 0)\n'
         '\t\t\t\t{\n'
         '\t\t\t\t\tg8_first_nonzero_vsync = g8_vsync_index;\n'
         '\t\t\t\t\tg8_first_nonzero_total = total;\n'
         '\t\t\t\t\tConsole.WriteLn("G8_FIRST_NONZERO vsync=%d transfers=%d", g8_vsync_index, total);\n'
         '\t\t\t\t}\n'
         '\t\t\t\tif (g8_first_nonzero_vsync >= 0 && (total - g8_first_nonzero_total) >= 500)\n'
         '\t\t\t\t{\n'
         '\t\t\t\t\tg8_dump_queued = true;\n'
         '\t\t\t\t\tConsole.WriteLn("G8_DUMP_QUEUED vsync=%d transfers=%d K=500", g8_vsync_index, total);\n'
         '\t\t\t\t\tGSQueueSnapshot(std::string(), 5);\n'
         '\t\t\t\t}\n'
         '\t\t\t}\n'
         '\t\t}\n'
         '\t\tg8_vsync_index++;\n'
         '\t}\n')
assert s.count(before) == 1, ("G8-TRIG", s.count(before))
s = s.replace(before, after)
io.open(p, "w", encoding="utf-8").write(s)
# H3 (G8-STATE-INC): extern decl + <atomic> in GSState.cpp.
p = "pcsx2/GS/GSState.cpp"
s = io.open(p, encoding="utf-8").read()
before = '#include <bit>\n'
after = ('#include <bit>\n#include <atomic>\n\nextern std::atomic<int> g_g8_transfer_count; // G8: defined in GS.cpp, incremented below on the GS thread.\n')
assert s.count(before) == 1, ("G8-INC", s.count(before))
s = s.replace(before, after)
# H4 (G8-STATE-CTR): increment next to the dump emission in GSState::Transfer.
before = ('\tif (m_dump && mem > start)\n'
          '\t\tm_dump->Transfer(index, start, mem - start);\n')
after = ('\t// G8: count Transfer packets on the GS thread (same mem>start condition as the dump writer below).\n'
         '\tif (mem > start)\n'
         '\t\tg_g8_transfer_count.fetch_add(1, std::memory_order_relaxed);\n'
         + before)
assert s.count(before) == 1, ("G8-CTR2", s.count(before))
s = s.replace(before, after)
io.open(p, "w", encoding="utf-8").write(s)
print("G8_PATCH_OK")
EOF
git diff --stat
git diff pcsx2/GS/GSState.cpp | head -60
if [ -d /home/brad/pcsx2-r1/.ccache ]; then
  export CCACHE_DIR=/home/brad/pcsx2-r1/.ccache
else
  export CCACHE_DIR=/home/brad/pcsx2-g7/.ccache
fi
export CCACHE_BASEDIR=/home/brad/pcsx2-g7/pcsx2
export CCACHE_COMPRESS=true CCACHE_COMPRESSLEVEL=9 CCACHE_MAXSIZE=2G
du -sb /home/brad/pcsx2-g7/pcsx2/build
ninja -C build -j2 2>&1 | tee /home/brad/pcsx2-g7/build-g8.log
echo "BUILD_EXIT:${PIPESTATUS[0]}"
date -u
du -sb /home/brad/pcsx2-g7/pcsx2/build
sha256sum build/bin/pcsx2-qt
stat -c %s build/bin/pcsx2-qt
# R1 + T4 reference binaries + trees must be untouched:
sha256sum /home/brad/pcsx2-r1/pcsx2/build/bin/pcsx2-qt
sha256sum /home/brad/pcsx2-t4/pcsx2/build/bin/pcsx2-qt
git -C /home/brad/pcsx2-r1/pcsx2 status --short
git -C /home/brad/pcsx2-t4/pcsx2 status --short
echo G8_BUILD_DONE
