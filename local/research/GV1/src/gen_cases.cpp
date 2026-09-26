// GV1: FMAC test cases + expected results from the real VR4 core (fork b97b241 sources,
// VU1Interpreter::execUpperForTest, direct flag commit). Operand generator = VR4's unit test
// (ps2xTest/src/ps2_vu1_tests.cpp, "VR4 vector FMAC core matches the scalar reference"), same
// xorshift seed; differences: FMAC ops only (the GPU kernel's scope), fd forced != 0, direct
// flags (mode 1) only, no queued setup ops.
#include "runtime/ps2_vu1.h"
#include "runtime/gs/gs_frontend.h"
#include "runtime/ps2_memory.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <chrono>

// Link stubs: the VU sources reference these; FMAC ops never reach them.
void GS::processGIFPacket(const uint8_t *, uint32_t) { std::abort(); }
void PS2Memory::submitGifPacket(GifPathId, const uint8_t *, uint32_t, bool, bool) { std::abort(); }

struct Case
{
    uint32_t instr, q, i, mac, status, pad[3];
    uint32_t vs[4], vt[4], acc[4], dst[4];
};
struct Expect
{
    uint32_t out[4];
    uint32_t mac, status, pad[2];
};

static uint32_t bitsOf(float f) { uint32_t b; std::memcpy(&b, &f, 4); return b; }
static float asFloat(uint32_t b) { float f; std::memcpy(&f, &b, 4); return f; }

int main(int argc, char **argv)
{
    const uint64_t cases = argc > 1 ? std::strtoull(argv[1], nullptr, 10) : 1000000u;
    const char *outPath = argc > 2 ? argv[2] : "cases.bin";
    std::vector<uint32_t> fmacOps;
    const auto isFmacOp = [](uint32_t code)
    {
        return code <= 0x0Fu || (code >= 0x18u && code <= 0x1Cu) || code == 0x1Eu ||
               (code >= 0x20u && code <= 0x2Au) || code == 0x2Cu || code == 0x2Du || code == 0x2Eu;
    };
    for (uint32_t op = 0; op <= 0x2Fu; ++op)
        if (isFmacOp(op)) fmacOps.push_back(op);
    for (uint32_t code = 0; code <= 0x30u; ++code)
    {
        if (code == 0x2Bu) continue;
        const uint32_t word = 0x3Cu | (code & 3u) | ((code >> 2) << 6);
        if (isFmacOp(code)) fmacOps.push_back(word);
    }
    uint64_t rng = 0x9E3779B97F4A7C15ull;
    const auto next = [&rng]() { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; };
    const auto operand = [&next]() -> uint32_t
    {
        const uint64_t r = next();
        const uint32_t sign = (r & 1u) != 0u ? 0x80000000u : 0u;
        uint32_t mantissa = static_cast<uint32_t>(r >> 8) & 0x7FFFFFu;
        switch ((r >> 1) & 3u) { case 0: mantissa = 0u; break; case 1: mantissa = 0x7FFFFFu; break; default: break; }
        uint32_t exponent = 0u;
        switch ((r >> 3) % 14u)
        {
        case 0: return sign;
        case 1: return sign | ((static_cast<uint32_t>(r >> 32) & 0x7FFFFFu) | 1u);
        case 2: return sign | 0x7F800000u;
        case 3: return sign | 0x7F800000u | ((static_cast<uint32_t>(r >> 32) & 0x7FFFFFu) | 1u);
        case 4: exponent = 0xFEu - static_cast<uint32_t>((r >> 40) & 1u); break;
        case 5: exponent = 1u + static_cast<uint32_t>((r >> 40) & 1u); break;
        case 6: case 7: exponent = 0x3Eu + static_cast<uint32_t>((r >> 40) % 5u); break;
        case 8: case 9: exponent = 0xBDu + static_cast<uint32_t>((r >> 40) % 5u); break;
        case 10: exponent = 0x7Eu + static_cast<uint32_t>((r >> 40) % 3u); break;
        default: exponent = 1u + static_cast<uint32_t>((r >> 40) % 0xFEu); break;
        }
        return sign | (exponent << 23) | mantissa;
    };

    std::vector<Case> cs(cases);
    std::vector<Expect> ex(cases);
    VU1Interpreter scalar, simd;
    uint64_t formMismatch = 0, nO = 0, nU = 0, nZ = 0;
    for (uint64_t n = 0; n < cases; ++n)
    {
        const uint32_t dest = 1u + static_cast<uint32_t>(next() % 15u);
        const uint32_t regs = static_cast<uint32_t>(next());
        const uint32_t ft = regs & 31u, fs = (regs >> 5) & 31u, fd = 1u + ((regs >> 10) & 31u) % 31u;
        const uint32_t opWord = fmacOps[next() % fmacOps.size()];
        const bool special = (opWord & 0x3Cu) == 0x3Cu;
        const uint32_t instr = (dest << 21) | (ft << 16) | (fs << 11) | (special ? opWord : (opWord | (fd << 6)));
        VU1State start{};
        for (auto &row : start.vf)
            for (float &value : row) value = asFloat(operand());
        if (next() % 8u == 0u)
        {
            const uint32_t flip = (next() & 1u) != 0u ? 0x80000000u : 0u;
            for (uint32_t c = 0; c < 4u; ++c)
            {
                const uint32_t b = bitsOf(start.vf[fs][c]);
                start.vf[ft][c] = asFloat(b ^ flip);
                start.acc[c] = asFloat(b ^ (flip ^ 0x80000000u));
            }
        }
        else
            for (float &value : start.acc) value = asFloat(operand());
        start.q = asFloat(operand());
        start.i = asFloat(operand());
        start.mac = static_cast<uint32_t>(next()) & 0xFFFFu;
        start.status = static_cast<uint32_t>(next()) & 0xFFFu;
        start.clip = static_cast<uint32_t>(next()) & 0xFFFFFFu;
        start.vf[0][0] = 0.0f; start.vf[0][1] = 0.0f; start.vf[0][2] = 0.0f; start.vf[0][3] = 1.0f;

        Case &c = cs[n];
        c.instr = instr; c.q = bitsOf(start.q); c.i = bitsOf(start.i);
        c.mac = start.mac; c.status = start.status;
        for (int k = 0; k < 4; ++k)
        {
            c.vs[k] = bitsOf(start.vf[fs][k]); c.vt[k] = bitsOf(start.vf[ft][k]);
            c.acc[k] = bitsOf(start.acc[k]);
            c.dst[k] = special ? c.acc[k] : bitsOf(start.vf[fd][k]);
        }
        std::vector<uint64_t> snap[2];
        for (int form = 0; form < 2; ++form)
        {
            VU1Interpreter &vu = form == 0 ? scalar : simd;
            vu.reset();
            vu.state() = start;
            vu.execUpperForTest(instr, form == 1, true);
            snap[form] = vu.fmacStateForTest();
        }
        formMismatch += snap[0] != snap[1];
        const VU1State &s = simd.state();
        Expect &e = ex[n];
        for (int k = 0; k < 4; ++k) e.out[k] = special ? bitsOf(s.acc[k]) : bitsOf(s.vf[fd][k]);
        e.mac = s.mac; e.status = s.status;
        nO += (s.status & 8u) != 0; nU += (s.status & 4u) != 0; nZ += (s.status & 1u) != 0;
    }
    FILE *f = std::fopen(outPath, "wb");
    std::fwrite(cs.data(), sizeof(Case), cs.size(), f);
    std::fwrite(ex.data(), sizeof(Expect), ex.size(), f);
    std::fclose(f);
    std::printf("cases=%llu fmac_ops=%zu scalar_vs_simd_mismatch=%llu status O=%llu U=%llu Z=%llu -> %s\n",
                (unsigned long long)cases, fmacOps.size(), (unsigned long long)formMismatch,
                (unsigned long long)nO, (unsigned long long)nU, (unsigned long long)nZ, outPath);

    // CPU throughput of the real core (one thread): a dependent 4-op transform chain
    // (MULAx, MADDAy, MADDAz, MADDw vf5 <- vf1..4 x vf6), as B2a10's matrix x vector.
    const uint32_t chain[4] = {
        (15u << 21) | (6u << 16) | (1u << 11) | 0x3Cu | (0x18u & 3u) | ((0x18u >> 2) << 6),  // MULAx
        (15u << 21) | (6u << 16) | (2u << 11) | 0x3Cu | (0x09u & 3u) | ((0x09u >> 2) << 6),  // MADDAy
        (15u << 21) | (6u << 16) | (3u << 11) | 0x3Cu | (0x0Au & 3u) | ((0x0Au >> 2) << 6),  // MADDAz
        (15u << 21) | (6u << 16) | (4u << 11) | (5u << 6) | 0x0Bu,                            // MADDw
    };
    for (int form = 1; form >= 0; --form)
    {
        VU1Interpreter &vu = simd;
        vu.reset();
        for (int r = 1; r <= 6; ++r)
            for (int k = 0; k < 4; ++k) vu.state().vf[r][k] = 0.5f + 0.25f * r + 0.125f * k;
        const uint64_t iters = 20000000u;
        const auto t0 = std::chrono::steady_clock::now();
        for (uint64_t n = 0; n < iters; ++n)
        {
            for (uint32_t w : chain) vu.execUpperForTest(w, form == 1, true);
            vu.state().vf[6][0] = vu.state().vf[5][1] * 0.5f; // feed back so the chain is dependent
        }
        const double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
        std::printf("cpu_core form=%s ops=%llu seconds=%.3f Mops/s=%.1f (1 thread, direct flags) chk=%08x\n",
                    form ? "simd" : "scalar", (unsigned long long)(iters * 4), s, iters * 4 / s / 1e6,
                    bitsOf(vu.state().vf[5][0]) ^ vu.state().mac);
    }
    return formMismatch != 0;
}
