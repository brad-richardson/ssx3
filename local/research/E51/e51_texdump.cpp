// E51: decode a texture from a native GS VRAM image (4 MiB) to PPM using
// the runtime's own swizzle tables (header-only).
// Usage: e51_texdump <vram.bin> <psm hex: 14|13|0> <tbp> <tbw> <w> <h> <cbp> <csa> <out.ppm>
// PSMT4/PSMT8 take a CT32 CLUT (CSM1): 4-bit index i -> (i&7, i>>3) in an
// 8x2 block at cbp; 8-bit index uses the CSM1 16x16 layout (bits 3/4 swapped).
#include "runtime/gs/ps2_gs_psmct32.h"
#include "runtime/gs/ps2_gs_psmt4.h"
#include "runtime/gs/ps2_gs_psmt8.h"

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

static uint32_t rd32(const std::vector<uint8_t> &v, uint32_t a)
{
    a &= 0x3FFFFFu;
    return v[a] | (v[a + 1] << 8) | (v[a + 2] << 16) | (static_cast<uint32_t>(v[a + 3]) << 24);
}

int main(int argc, char **argv)
{
    if (argc != 10)
    {
        std::fprintf(stderr, "usage: %s vram psm tbp tbw w h cbp csa out.ppm\n", argv[0]);
        return 2;
    }
    std::FILE *f = std::fopen(argv[1], "rb");
    if (!f)
        return 1;
    std::vector<uint8_t> vram(4u << 20);
    if (std::fread(vram.data(), 1, vram.size(), f) != vram.size())
        return 1;
    std::fclose(f);
    const uint32_t psm = std::strtoul(argv[2], nullptr, 16);
    const uint32_t tbp = std::strtoul(argv[3], nullptr, 0), tbw = std::strtoul(argv[4], nullptr, 0);
    const uint32_t w = std::strtoul(argv[5], nullptr, 0), h = std::strtoul(argv[6], nullptr, 0);
    const uint32_t cbp = std::strtoul(argv[7], nullptr, 0), csa = std::strtoul(argv[8], nullptr, 0);
    std::FILE *o = std::fopen(argv[9], "wb");
    std::fprintf(o, "P6\n%u %u\n255\n", w, h);
    for (uint32_t y = 0; y < h; ++y)
    {
        for (uint32_t x = 0; x < w; ++x)
        {
            uint32_t c = 0;
            if (psm == 0x14)
            {
                const uint32_t na = GSPSMT4::addrPSMT4(tbp, tbw, x, y);
                const uint8_t byte = vram[(na >> 1) & 0x3FFFFFu];
                const uint32_t idx = ((na & 1u) ? (byte >> 4) : byte) & 0xFu;
                const uint32_t e = idx + csa * 16u;
                c = rd32(vram, GSPSMCT32::addrPSMCT32(cbp, 1, e & 7u, (e >> 3) & 1u) + 0u);
                if (csa)
                    c = rd32(vram, GSPSMCT32::addrPSMCT32(cbp, 1, (e & 7u) + ((e >> 4) & 1u) * 8u, ((e >> 3) & 1u) + ((e >> 5) * 2u)));
            }
            else if (psm == 0x13)
            {
                const uint32_t a = GSPSMT8::addrPSMT8(tbp, tbw, x, y);
                const uint32_t idx = vram[a & 0x3FFFFFu];
                const uint32_t sw = (idx & 0xE7u) | ((idx & 0x08u) << 1) | ((idx & 0x10u) >> 1);
                c = rd32(vram, GSPSMCT32::addrPSMCT32(cbp, 1, sw & 0xFu, sw >> 4));
            }
            else
            {
                c = rd32(vram, GSPSMCT32::addrPSMCT32(tbp, tbw, x, y));
            }
            const uint8_t px[3] = {static_cast<uint8_t>(c), static_cast<uint8_t>(c >> 8), static_cast<uint8_t>(c >> 16)};
            std::fwrite(px, 1, 3, o);
        }
    }
    std::fclose(o);
    return 0;
}
