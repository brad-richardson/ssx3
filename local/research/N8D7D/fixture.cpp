// N8D7D: synthetic count-one, non-promoted display-field adapter fixture.
// The expected pixels are coordinate formulas, never readback or swizzle output.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "gs/gs_util.hpp"

using namespace ParallelGS;
constexpr uint32_t W = 512, H = 224, VRAM_BYTES = 4u * 1024u * 1024u;
constexpr uint32_t VRAM_MASK = VRAM_BYTES - 1u;
constexpr uint32_t TILE_W = 32, TILE_H = 14;

struct Case {
    const char *name;
    uint32_t psm, fbp, fbw, dbx, dby, phase, stride;
};

static const Case cases[] = {
    {"fbp_0", PSMCT32, 0, 8, 0, 0, 0, 1},
    {"fbp_112", PSMCT32, 112, 8, 0, 0, 0, 1},
    {"fbw_8", PSMCT32, 1, 8, 0, 0, 0, 1},
    {"fbw_9", PSMCT32, 1, 9, 0, 0, 0, 1},
    {"phase_0_stride_1", PSMCT32, 1, 8, 3, 4, 0, 1},
    {"phase_1_stride_1", PSMCT32, 1, 8, 3, 4, 1, 1},
    {"phase_0_stride_2", PSMCT32, 1, 8, 3, 4, 0, 2},
    {"phase_1_stride_2", PSMCT32, 1, 8, 3, 4, 1, 2},
    {"psmct16", PSMCT16, 1, 8, 3, 4, 1, 2},
    {"psmct16s", PSMCT16S, 1, 8, 3, 4, 1, 2},
    {"wrap_32", PSMCT32, 511, 8, 64, 0, 0, 1},
    {"wrap_16", PSMCT16, 511, 8, 64, 0, 0, 1},
};

static bool is16(uint32_t psm) { return psm == PSMCT16 || psm == PSMCT16S; }
static uint16_t payload16(uint32_t x, uint32_t y, uint32_t seed) {
    return uint16_t(((x * 7 + y * 3 + seed * 11) & 31u) |
                    (((x * 3 + y * 13 + seed * 5) & 31u) << 5) |
                    (((x * 11 + y * 5 + seed * 17) & 31u) << 10) |
                    (((x + y + seed) & 1u) << 15));
}
static uint32_t payload32(uint32_t x, uint32_t y, uint32_t seed) {
    return ((17*x + 3*y + 11*seed) & 255u) |
           (((5*x + 13*y + 29*seed) & 255u) << 8) |
           (((7*x + 19*y + 47*seed) & 255u) << 16) |
           (((x + 23*y + 61*seed) & 255u) << 24);
}
static std::array<uint8_t, 4> expand(uint32_t psm, uint32_t payload) {
    if (is16(psm)) return {uint8_t((payload & 31u) << 3),
                           uint8_t(((payload >> 5) & 31u) << 3),
                           uint8_t(((payload >> 10) & 31u) << 3),
                           uint8_t((payload & 0x8000u) ? 255 : 0)};
    return {uint8_t(payload), uint8_t(payload >> 8),
            uint8_t(payload >> 16), uint8_t(payload >> 24)};
}
static uint64_t fnv(const uint8_t *p, size_t n) {
    uint64_t h = 14695981039346656037ull;
    for (size_t i = 0; i < n; ++i) h = (h ^ p[i]) * 1099511628211ull;
    return h;
}
static std::string hex64(uint64_t n) {
    std::ostringstream s; s << "fnv1a64:" << std::hex << std::setfill('0') << std::setw(16) << n;
    return s.str();
}
static std::array<uint16_t, TILE_W * TILE_H> tiles(const std::vector<uint8_t> &rgba) {
    std::array<uint16_t, TILE_W * TILE_H> t{};
    for (uint32_t y = 0; y < H; ++y)
        for (uint32_t x = 0; x < W; ++x) {
            size_t p = 4u * (size_t(y) * W + x);
            if (std::max({rgba[p], rgba[p+1], rgba[p+2]}) >= 32)
                ++t[(y / 16) * TILE_W + (x / 16)];
        }
    return t;
}
static std::string tile_hash(const std::array<uint16_t, TILE_W * TILE_H> &t) {
    std::vector<uint8_t> bytes;
    bytes.reserve(t.size() * 2);
    for (uint16_t v : t) { bytes.push_back(uint8_t(v)); bytes.push_back(uint8_t(v >> 8)); }
    return hex64(fnv(bytes.data(), bytes.size()));
}

int main(int argc, char **argv) {
    if (argc != 2) { std::cerr << "usage: fixture result.json\n"; return 2; }
    std::ofstream out(argv[1]);
    if (!out) { std::cerr << "cannot open result.json\n"; return 2; }
    const uint32_t golden112 = 917504, goldenWrap = 0;
    const uint32_t actual112 = 4u * swizzle_PS2(0, 0, 112u * PGS_BLOCKS_PER_PAGE, 8, PSMCT32, VRAM_MASK);
    const uint32_t actualWrap = 4u * swizzle_PS2(64, 0, 511u * PGS_BLOCKS_PER_PAGE, 8, PSMCT32, VRAM_MASK);
    bool all_ok = actual112 == golden112 && actualWrap == goldenWrap;
    out << "{\n  \"source_pin\": \"3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd\",\n"
           "  \"compiler_command\": \"c++ -std=c++17 -O2 -I. -Igs -IGranite/math -IGranite/vulkan -IGranite/util -IGranite/third_party /Users/brad/dev/ssx3/local/research/N8D7D/fixture.cpp -o /tmp/n8d7d-fixture\",\n"
           "  \"field\": {\"width\": 512, \"height\": 224, \"super_samples\": 1, \"promoted\": false},\n"
           "  \"golden_offsets\": ["
        << "{\"name\":\"fbp112_0_0\",\"expected_byte\":" << golden112 << ",\"actual_byte\":" << actual112 << ",\"pass\":" << (actual112 == golden112 ? "true" : "false") << "},"
        << "{\"name\":\"fbp511_dbx64_0_0\",\"expected_byte\":" << goldenWrap << ",\"actual_byte\":" << actualWrap << ",\"pass\":" << (actualWrap == goldenWrap ? "true" : "false") << "}],\n"
        << "  \"cases\": [\n";
    for (size_t ci = 0; ci < std::size(cases); ++ci) {
        const Case &c = cases[ci];
        const bool half = is16(c.psm);
        std::vector<uint32_t> vram(VRAM_BYTES / 4, 0xa5a5a5a5u);
        std::vector<uint8_t> seen(VRAM_BYTES / (half ? 2u : 4u), 0);
        std::vector<uint8_t> expected(size_t(W) * H * 4);
        uint32_t conflicting = 0, aliases = 0;
        uint32_t first_x = 0, first_y = 0;
        for (uint32_t y = 0; y < H; ++y) for (uint32_t x = 0; x < W; ++x) {
            const uint32_t sx = c.dbx + x, sy = c.dby + c.phase + y * c.stride;
            if (sx >= 2048 || sy >= 2048) { std::cerr << "coordinate guard failed\n"; return 3; }
            const uint32_t value = half ? payload16(x,y,uint32_t(ci)+1) : payload32(x,y,uint32_t(ci)+1);
            const size_t off = 4u * (size_t(y) * W + x);
            const auto rgba = expand(c.psm, value);
            std::copy(rgba.begin(), rgba.end(), expected.begin() + off);
            const uint32_t addr = swizzle_PS2(sx,sy,c.fbp*PGS_BLOCKS_PER_PAGE,c.fbw,c.psm,VRAM_MASK);
            const uint32_t old = half ? reinterpret_cast<const uint16_t*>(vram.data())[addr] : vram[addr];
            if (seen[addr]) { ++aliases; if (old != value) { ++conflicting; if (conflicting == 1) { first_x=x; first_y=y; } } }
            else { seen[addr] = 1; if (half) reinterpret_cast<uint16_t*>(vram.data())[addr] = uint16_t(value); else vram[addr] = value; }
        }
        std::vector<uint8_t> actual(size_t(W) * H * 4);
        if (conflicting == 0) {
            if (half) {
                std::vector<uint16_t> raw(size_t(W) * H);
                for (uint32_t y=0; y<H; ++y) {
                    uint32_t sy=c.dby+c.phase+y*c.stride;
                    if (c.psm == PSMCT16) vram_readback<PSMCT16>(raw.data()+size_t(y)*W,vram.data(),c.fbp*PGS_BLOCKS_PER_PAGE,c.fbw,c.dbx,sy,W,1,VRAM_MASK);
                    else vram_readback<PSMCT16S>(raw.data()+size_t(y)*W,vram.data(),c.fbp*PGS_BLOCKS_PER_PAGE,c.fbw,c.dbx,sy,W,1,VRAM_MASK);
                }
                for (size_t i=0; i<raw.size(); ++i) { auto rgba=expand(c.psm,raw[i]); std::copy(rgba.begin(),rgba.end(),actual.begin()+i*4); }
            } else {
                std::vector<uint32_t> raw(size_t(W) * H);
                for (uint32_t y=0; y<H; ++y)
                    vram_readback<PSMCT32>(raw.data()+size_t(y)*W,vram.data(),c.fbp*PGS_BLOCKS_PER_PAGE,c.fbw,c.dbx,c.dby+c.phase+y*c.stride,W,1,VRAM_MASK);
                for (size_t i=0; i<raw.size(); ++i) { auto rgba=expand(c.psm,raw[i]); std::copy(rgba.begin(),rgba.end(),actual.begin()+i*4); }
            }
        }
        uint32_t pixel_mismatch=0;
        for (size_t i=0; i<actual.size(); i+=4)
            pixel_mismatch += !std::equal(actual.begin()+i,actual.begin()+i+4,expected.begin()+i);
        auto expected_tiles=tiles(expected), actual_tiles=tiles(actual);
        uint32_t tile_mismatch=0, expected_active=0, actual_active=0;
        for (size_t i=0; i<expected_tiles.size(); ++i) {
            tile_mismatch += expected_tiles[i] != actual_tiles[i];
            expected_active += expected_tiles[i] >= 32;
            actual_active += actual_tiles[i] >= 32;
        }
        bool supported=conflicting == 0;
        bool ok=supported && pixel_mismatch == 0 && tile_mismatch == 0 && actual.size() == 458752 && actual_tiles.size() == 448;
        all_ok &= ok;
        if (ci) out << ",\n";
        out << "    {\"name\":\"" << c.name << "\",\"psm\":" << c.psm
            << ",\"fbp\":" << c.fbp << ",\"fbw\":" << c.fbw << ",\"dbx\":" << c.dbx
            << ",\"dby\":" << c.dby << ",\"phase\":" << c.phase << ",\"stride\":" << c.stride
            << ",\"supported\":" << (supported?"true":"false") << ",\"alias_count\":" << aliases
            << ",\"conflicting_writes\":" << conflicting << ",\"first_conflict_xy\":[" << first_x << "," << first_y << "]"
            << ",\"expected_pixel_mismatches\":0,\"actual_pixel_mismatches\":" << pixel_mismatch
            << ",\"expected_tile_mismatches\":0,\"actual_tile_mismatches\":" << tile_mismatch
            << ",\"expected_output_bytes\":" << expected.size() << ",\"actual_output_bytes\":" << actual.size()
            << ",\"expected_tile_counts\":" << expected_tiles.size() << ",\"actual_tile_counts\":" << actual_tiles.size()
            << ",\"expected_active_tiles\":" << expected_active << ",\"actual_active_tiles\":" << actual_active
            << ",\"expected_output_hash\":\"" << hex64(fnv(expected.data(),expected.size()))
            << "\",\"actual_output_hash\":\"" << hex64(fnv(actual.data(),actual.size()))
            << "\",\"expected_tile_hash\":\"" << tile_hash(expected_tiles)
            << "\",\"actual_tile_hash\":\"" << tile_hash(actual_tiles) << "\",\"pass\":" << (ok?"true":"false") << "}";
        std::cout << c.name << " pixels=" << pixel_mismatch << " tiles=" << tile_mismatch
                  << " aliases=" << aliases << " conflicts=" << conflicting << (ok?" PASS":" FAIL") << '\n';
    }
    out << "\n  ],\n  \"pass\": " << (all_ok?"true":"false") << "\n}\n";
    std::cout << "golden fbp112=" << actual112 << " wrap32=" << actualWrap << " total=" << (all_ok?"PASS":"FAIL") << '\n';
    return all_ok ? 0 : 1;
}
