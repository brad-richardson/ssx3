#!/usr/bin/env bash
set -euo pipefail
G=/home/brad/pcsx2-g7
P=$G/pcsx2/pcsx2/R5900OpcodeImpl.cpp
mkdir -p "$G/pre-au4" /home/brad/au4
pgrep -af 'gradle|ninja|clang|pcsx2' > /home/brad/au4/prebuild-jobs.txt || true
if [ -s /home/brad/au4/prebuild-jobs.txt ]; then cat /home/brad/au4/prebuild-jobs.txt; exit 20; fi
cp "$P" "$G/pre-au4/R5900OpcodeImpl.cpp"
cp "$G/pcsx2/build/bin/pcsx2-qt" "$G/pre-au4/pcsx2-qt.pre-au4"
sha256sum "$G/pre-au4/R5900OpcodeImpl.cpp" "$G/pre-au4/pcsx2-qt.pre-au4" > /home/brad/au4/pre-au4-sha.txt
python3 - <<'PY'
from pathlib import Path
p=Path('/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp')
s=p.read_text()
a='#include "VMManager.h"\n'
assert s.count(a)==1
s=s.replace(a,a+'\n#include <cstdio>\n#include <cstdlib>\n')
a='\t\tcase Syscall::sceSifSetDma:\n'
assert s.count(a)==1
hook='''\t\tcase Syscall::sceSifSetDma:
			// AU4: read-only EE tag-1 capture. Each record is u32 EE vsync + 0x620 EE bytes.
			if (std::getenv("PCSX2_AU4_CAPTURE"))
			{
				extern u32 g_t65_ee_vsync;
				static FILE* au4_file = nullptr;
				static bool au4_open_attempted = false;
				const u32 desc = cpuRegs.GPR.n.a0.UL[0];
				const u32 count = cpuRegs.GPR.n.a1.UL[0];
				if (count <= 32 && desc < 0x02000000 && (desc & 15) == 0)
				{
					for (u32 i = 0; i < count; i++)
					{
						const u32 src = memRead32(desc + i * 16);
						const u32 size = memRead32(desc + i * 16 + 8);
						if (src != 0x00512e40 || size < 0x620)
							continue;
						if (memRead32(src) != 1 || memRead32(src + 4) != 0x600 || memRead32(src + 0x610) != 5)
							continue;
						if (!au4_open_attempted)
						{
							au4_open_attempted = true;
							au4_file = std::fopen("/home/brad/au4/pcsx2-tag1.bin", "ab");
							Console.WriteLn("AU4_TAG_OPEN src=%08x size=%x ok=%d", src, size, au4_file != nullptr);
						}
						if (au4_file)
						{
							std::fwrite(&g_t65_ee_vsync, sizeof(g_t65_ee_vsync), 1, au4_file);
							std::fwrite(PSM(src), 1, 0x620, au4_file);
							std::fflush(au4_file);
						}
					}
				}
			}
'''
s=s.replace(a,hook)
p.write_text(s)
PY
cd "$G/pcsx2"
git diff -- pcsx2/R5900OpcodeImpl.cpp > /home/brad/au4/au4-patch.diff
cmake --build "$G/pcsx2/build" --target pcsx2-qt pcsx2-gsrunner -j2 > /home/brad/au4/build.log 2>&1 || { tail -100 /home/brad/au4/build.log; exit 21; }
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" "$G/pcsx2/build/bin/pcsx2-gsrunner" > /home/brad/au4/bin-sha-read1.txt
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" "$G/pcsx2/build/bin/pcsx2-gsrunner" > /home/brad/au4/bin-sha-read2.txt
cat /home/brad/au4/bin-sha-read1.txt /home/brad/au4/bin-sha-read2.txt
