from pathlib import Path

p = Path('/Users/brad/dev/ssx3-work/E60/codegen/sub_003FEB78_0x3feb78.cpp')
s = p.read_text()
assert s.count('#include <stdexcept>') == 1
s = s.replace('#include <stdexcept>', '#include <stdexcept>\n#include \"runtime/ee_scheduler.h\"\n#include <cstdio>\n#include <cstdlib>\n#include <cstring>')
anchor = '    // 0x3feb90: 0x48220800  qmfc2.ni    $v0, $vf1\n'
assert s.count(anchor) == 1
tap = '''    // E60: bounded, default-off raw VU0 data snapshot at sceVu0MemReadQ.
    static unsigned e60_records = 0;
    const char *e60_path = std::getenv("PS2X_E60_TAP");
    const uint64_t e60_tick = runtime->eeScheduler().currentVSyncTick();
    if (e60_path && *e60_path && e60_records < 16) {
        struct E60Record {
            char magic[4]; uint64_t tick; uint32_t caller; uint32_t vi1;
            uint8_t qword[16]; uint8_t memory[4096];
        } record{};
        std::memcpy(record.magic, "E60A", 4);
        record.tick = e60_tick;
        record.caller = GPR_U32(ctx, 31) - 8u;
        record.vi1 = GPR_U32(ctx, 5) & 0xffffu;
        std::memcpy(record.qword, Ps2Vu0DataAt(runtime, record.vi1 << 4), 16);
        std::memcpy(record.memory, runtime->memory().getVU0Data(), 4096);
        if (std::FILE *file = std::fopen(e60_path, "ab")) {
            std::fwrite(&record, sizeof(record), 1, file);
            std::fclose(file);
            ++e60_records;
        }
    }
'''
s = s.replace(anchor, tap + anchor)
p.write_text(s)
