#!/usr/bin/env bash
set -euo pipefail
G=/home/brad/pcsx2-g7
P=$G/pcsx2/pcsx2/R5900OpcodeImpl.cpp
pgrep -af 'gradle|ninja|clang|pcsx2' > /home/brad/au4/prebuild2-jobs.txt || true
if [ -s /home/brad/au4/prebuild2-jobs.txt ]; then cat /home/brad/au4/prebuild2-jobs.txt; exit 20; fi
python3 - <<'PY'
from pathlib import Path
p=Path('/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp')
s=p.read_text()
a='#include <cstdlib>\n'
assert s.count(a)>=1
s=s.replace(a,a+'\nextern u32 g_t65_ee_vsync; // AU4: defined by the T65 Counters.cpp hook.\n',1)
a='\t\t\t\textern u32 g_t65_ee_vsync;\n'
assert s.count(a)==1
s=s.replace(a,'')
a='std::fwrite(&g_t65_ee_vsync, sizeof(g_t65_ee_vsync), 1, au4_file);'
assert s.count(a)==1
s=s.replace(a,'std::fwrite(&::g_t65_ee_vsync, sizeof(::g_t65_ee_vsync), 1, au4_file);')
p.write_text(s)
PY
cd "$G/pcsx2"
git diff -- pcsx2/R5900OpcodeImpl.cpp > /home/brad/au4/au4-patch.diff
cmake --build "$G/pcsx2/build" --target pcsx2-qt pcsx2-gsrunner -j2 > /home/brad/au4/build2.log 2>&1 || { grep -E 'error:|FAILED:|undefined symbol|ninja: build stopped' /home/brad/au4/build2.log | head -30; exit 21; }
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" "$G/pcsx2/build/bin/pcsx2-gsrunner" > /home/brad/au4/bin-sha-read1.txt
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" "$G/pcsx2/build/bin/pcsx2-gsrunner" > /home/brad/au4/bin-sha-read2.txt
cat /home/brad/au4/bin-sha-read1.txt /home/brad/au4/bin-sha-read2.txt
