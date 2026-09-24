#!/usr/bin/env bash
set -euo pipefail
G=/home/brad/pcsx2-g7
A=/home/brad/au4
P=$G/pcsx2/pcsx2/R5900OpcodeImpl.cpp
pgrep -af 'gradle|ninja|clang|pcsx2' > "$A/part2-prebuild-jobs.txt" || true
if [ -s "$A/part2-prebuild-jobs.txt" ]; then cat "$A/part2-prebuild-jobs.txt"; exit 20; fi
cp "$P" "$G/pre-au4/R5900OpcodeImpl.cpp.part1"
sha256sum "$G/pre-au4/R5900OpcodeImpl.cpp.part1" > "$A/part2-pre-sha.txt"
python3 - <<'PY'
from pathlib import Path
p=Path('/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp')
s=p.read_text()
a='\t\t\t\tstatic bool au4_open_attempted = false;\n'
assert s.count(a)==1
s=s.replace(a,a+'\t\t\t\tstatic bool au4_desc_logged = false;\n')
a='\t\t\t\t\t\tconst u32 size = memRead32(desc + i * 16 + 8);\n'
assert s.count(a)==1
s=s.replace(a,a+'''\t\t\t\t\t\tif (desc == 0x0050c800 && !au4_desc_logged)
						{
							au4_desc_logged = true;
							Console.WriteLn("AU4_DESC desc=%08x src=%08x size=%x dst=%08x", desc, src, size, memRead32(desc + i * 16 + 4));
						}
''')
a='''						if (src != 0x00512e40 || size < 0x620)
							continue;
						if (memRead32(src) != 1 || memRead32(src + 4) != 0x600 || memRead32(src + 0x610) != 5)
							continue;
'''
assert s.count(a)==1
s=s.replace(a,'''						if (src != 0x00512b80 || size < 0x8e0)
							continue;
						const u32 tag1 = src + 0x2c0;
						if (memRead32(tag1) != 1 || memRead32(tag1 + 4) != 0x600 ||
							memRead32(tag1 + 8) != 0 || memRead32(tag1 + 12) != 0 ||
							memRead32(tag1 + 0x610) != 5)
							continue;
''')
a='std::fwrite(PSM(src), 1, 0x620, au4_file);'
assert s.count(a)==1
s=s.replace(a,'std::fwrite(PSM(tag1), 1, 0x620, au4_file);')
p.write_text(s)
PY
diff -u "$G/pre-au4/R5900OpcodeImpl.cpp.part1" "$P" > "$A/part2-hunk.diff" || true
cmake --build "$G/pcsx2/build" --target pcsx2-qt pcsx2-gsrunner -j2 > "$A/part2-build.log" 2>&1 || { grep -E 'error:|FAILED:|undefined symbol|ninja: build stopped' "$A/part2-build.log" | head -30; exit 21; }
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" "$G/pcsx2/build/bin/pcsx2-gsrunner" > "$A/part2-bin-sha-read1.txt"
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" "$G/pcsx2/build/bin/pcsx2-gsrunner" > "$A/part2-bin-sha-read2.txt"
diff -u "$A/part2-bin-sha-read1.txt" "$A/part2-bin-sha-read2.txt"
cat "$A/part2-bin-sha-read1.txt"
