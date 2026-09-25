// AU9: replay PCSX2 tag-3 records (tagbuf.bin from the AU9 PCSX2 hook) through the fork's
// ps2_snd_spu.h driver + SPU model, SPU RAM from a PCSX2 dump; writes 512 stereo s16 frames
// per tick and a tick index (u32 ns per tick) so the output lines up with the PCSX2 tap.
// Build: clang++ -std=c++20 -O2 -I<fork>/ps2xRuntime/include spu_replay.cpp -o spu_replay
// Usage: spu_replay tagbuf.bin spuram.bin ns_from out.raw out.idx
#include "ps2_snd_spu.h"
#include <cstdio>
#include <cstdlib>
#include <vector>
int main(int argc, char **argv)
{
    if (argc < 6) return 2;
    FILE *tb = std::fopen(argv[1], "rb"), *sr = std::fopen(argv[2], "rb");
    const unsigned long nsFrom = std::strtoul(argv[3], nullptr, 0);
    FILE *out = std::fopen(argv[4], "wb"), *idx = std::fopen(argv[5], "wb");
    std::vector<uint8_t> ram(ps2_snd_spu::kRamBytes);
    if (std::fread(ram.data(), 1, ram.size(), sr) != ram.size()) return 3;
    ps2_snd_spu::Spu spu;
    spu.writeRam(0, ram.data(), ram.size());
    ps2_snd_spu::Driver drv;
    uint32_t hdr[4];
    std::vector<uint8_t> buf;
    unsigned ticks = 0;
    while (std::fread(hdr, 4, 4, tb) == 4)
    {
        buf.resize(hdr[3] + 0x240u);
        if (std::fread(buf.data(), 1, buf.size(), tb) != buf.size()) break;
        if (hdr[2] < nsFrom) continue;
        drv.update(buf.data() + 0x18, spu); // tag 3 payload (AU9 E6)
        int32_t d0[1024], d1[1024];
        spu.render(d0, d1, 512);
        int16_t o[1024];
        for (int i = 0; i < 1024; ++i) o[i] = ps2_snd_spu::clamp16(d0[i] + d1[i]);
        std::fwrite(o, 2, 1024, out);
        std::fwrite(&hdr[2], 4, 1, idx);
        ++ticks;
    }
    std::fprintf(stderr, "ticks %u keyons %llu\n", ticks, (unsigned long long)drv.keyOns());
    return 0;
}
