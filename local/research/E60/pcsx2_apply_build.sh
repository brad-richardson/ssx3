#!/usr/bin/env bash
set -euo pipefail
G=/home/brad/pcsx2-g7
E=/home/brad/e60
P=$G/pcsx2/pcsx2/Interpreter.cpp
mkdir -p "$E" "$G/pre-e60"
pgrep -af 'gradle|ninja|clang|pcsx2-qt' > "$E/prebuild-jobs.txt" || true
if [ -s "$E/prebuild-jobs.txt" ]; then cat "$E/prebuild-jobs.txt"; exit 20; fi
cp "$P" "$G/pre-e60/Interpreter.cpp"
cp "$G/pcsx2/build/bin/pcsx2-qt" "$G/pre-e60/pcsx2-qt"
sha256sum "$G/pre-e60/Interpreter.cpp" "$G/pre-e60/pcsx2-qt" > "$E/pre-sha.txt"
python3 - <<'PY'
from pathlib import Path
p = Path('/home/brad/pcsx2-g7/pcsx2/pcsx2/Interpreter.cpp')
s = p.read_text()
inc = '#include <cstdlib>\n'
assert s.count(inc) == 1
s = s.replace(inc, inc + '#include <cstring> // E60 raw VU0 tap\n')
a = '\tconst u32 pc = cpuRegs.pc;\n\tif (pc == 0x362f70) t55_ret();'
assert s.count(a) == 1
tap = '''\tconst u32 pc = cpuRegs.pc;
\t// E60: interpreter-safe, bounded raw VU0 data snapshot at sceVu0MemReadQ.
\tif (pc == 0x3feb8c) {
\t\tstatic unsigned e60_records = 0;
\t\tconst char* e60_path = std::getenv("PCSX2_E60_TAP");
\t\tif (e60_path && *e60_path && e60_records < 16) {
\t\t\tif (FILE* arm = std::fopen("/home/brad/e60/arm", "rb")) {
\t\t\t\tstd::fclose(arm);
\t\t\t\tstruct E60Record {
\t\t\t\t\tchar magic[4]; u64 tick; u32 caller; u32 vi1;
\t\t\t\t\tu8 qword[16]; u8 memory[4096];
\t\t\t\t} record{};
\t\t\t\tstd::memcpy(record.magic, "E60P", 4);
\t\t\t\trecord.tick = (u64)g_t48_vsync.load(std::memory_order_relaxed);
\t\t\t\trecord.caller = cpuRegs.GPR.r[31].UL[0] - 8u;
\t\t\t\trecord.vi1 = VU0.VI[1].UL;
\t\t\t\tstd::memcpy(record.qword, VU0.Mem + ((record.vi1 & 0xffu) << 4), 16);
\t\t\t\tstd::memcpy(record.memory, VU0.Mem, 4096);
\t\t\t\tif (FILE* out = std::fopen(e60_path, "ab")) {
\t\t\t\t\tstd::fwrite(&record, sizeof(record), 1, out);
\t\t\t\t\tstd::fclose(out);
\t\t\t\t\tConsole.WriteLn("E60_VU0 n=%u vsync=%llu caller=%08x vi1=%x", e60_records,
\t\t\t\t\t\t(unsigned long long)record.tick, record.caller, record.vi1);
\t\t\t\t\t++e60_records;
\t\t\t\t}
\t\t\t}
\t\t}
\t}
\tif (pc == 0x362f70) t55_ret();'''
s = s.replace(a, tap)
p.write_text(s)
PY
diff -u "$G/pre-e60/Interpreter.cpp" "$P" > "$E/pcsx2-hunk.diff" || true
cmake --build "$G/pcsx2/build" --target pcsx2-qt pcsx2-gsrunner -j2 > "$E/build.log" 2>&1 || {
  grep -E 'error:|FAILED:|undefined symbol|ninja: build stopped' "$E/build.log" | head -30 || true
  exit 21
}
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" "$G/pcsx2/build/bin/pcsx2-gsrunner" > "$E/bin-sha-read1.txt"
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" "$G/pcsx2/build/bin/pcsx2-gsrunner" > "$E/bin-sha-read2.txt"
diff -u "$E/bin-sha-read1.txt" "$E/bin-sha-read2.txt"
