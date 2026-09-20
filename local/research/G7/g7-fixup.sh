#!/usr/bin/env bash
# G7 fixup: g_g7_execps2_count was defined inside R5900::Interpreter::OpcodeImpl
# (link error); move it to global scope in the existing tree and rebuild.
# Runs INSIDE WSL as brad. Mirrors corrected hunk 2 of g7-build.sh.
set -x
cd /home/brad/pcsx2-g7/pcsx2
python3 - <<'EOF'
import io
p = "pcsx2/R5900OpcodeImpl.cpp"
s = io.open(p, encoding="utf-8").read()
bad = ('#include "Sifcmd.h"\n\n#include <atomic>\n\n'
       '// G7: counts ExecPS2 syscalls; the GS thread auto-queues one 5-frame GS dump\n'
       '// 60 vsyncs after the 5th (game entry). One-shot capture aid, not a product change.\n'
       'std::atomic<int> g_g7_execps2_count{0};\n\nvoid SYSCALL()')
assert s.count(bad) == 1, ("UNWIND", s.count(bad))
s = s.replace(bad, '#include "Sifcmd.h"\n\nvoid SYSCALL()')
anchor = 'namespace R5900 {\n'
assert s.count(anchor) == 1, ("ANCHOR", s.count(anchor))
s = s.replace(anchor,
    '#include <atomic>\n\n'
    '// G7: counts ExecPS2 syscalls (global scope); the GS thread auto-queues one\n'
    '// 5-frame GS dump 60 vsyncs after the 5th (game entry). One-shot capture aid.\n'
    'std::atomic<int> g_g7_execps2_count{0};\n\nnamespace R5900 {\n')
io.open(p, "w", encoding="utf-8").write(s)
print("G7_FIXUP_OK")
EOF
git diff --stat
if [ -d /home/brad/pcsx2-r1/.ccache ]; then
  export CCACHE_DIR=/home/brad/pcsx2-r1/.ccache
else
  export CCACHE_DIR=/home/brad/pcsx2-g7/.ccache
fi
export CCACHE_BASEDIR=/home/brad/pcsx2-g7/pcsx2
export CCACHE_COMPRESS=true CCACHE_COMPRESSLEVEL=9 CCACHE_MAXSIZE=2G
ninja -C build -j2 2>&1 | tee /home/brad/pcsx2-g7/build-fixup.log
echo "BUILD_EXIT:${PIPESTATUS[0]}"
sha256sum build/bin/pcsx2-qt
stat -c %s build/bin/pcsx2-qt
echo G7_FIXUP_DONE
