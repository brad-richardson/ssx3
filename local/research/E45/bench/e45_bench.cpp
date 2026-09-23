// E45 VU1 FMAC A/B bench: runs fixed VU1 microprograms with deterministic
// synthetic inputs through the real VU1Interpreter (ps2_vu1_{core,lower,
// upper}.cpp), hashing all architectural state + VU data memory after each
// program and timing ns per issued pair.
//
// Variants: default build is VuWide=double; -DPS2X_VU_WIDE_QUAD=1 restores
// the old long-double (quad on Linux/Android arm64) type. Pass =
// double-Odin hash == Mac hash per program.
//
// Programs (brief-allowed fallback: E40/T50 carry DMA-chain source
// addresses and FNVs, not byte-exact payloads, so the suite's program
// shapes plus an FMAC-heavy loop stand in):
//   P0 smoke      5 issued pairs: ADD/MUL/MADD/SUB + SQ to VU-mem
//   P1 opsweep    36 FMAC ops (regular encoding) + delay = 37 issued
//   P2 special    36 FMAC ops (special/ACC encoding) + delay = 37 issued
//   P3 fmacloop   6-FMAC body x (N+1) trips + E-bit end, (N+1)*8+2 issued
//   P4 torture    overflow/underflow/cancel/denormal boundaries + SQ/LQ
//
// Every program ends with an E-bit pair plus a NOP/NOP delay slot, which
// flushes all writeback pipelines, so the hash covers committed state.
// Analytic issued counts are verified by end-PC asserts (a reserved-op
// halt or truncation would land pc elsewhere and fail loudly).

#include "runtime/gs/gs_frontend.h"
#include "runtime/gs/ps2_gif_arbiter.h"
#include "runtime/ps2_memory.h"
#include "runtime/ps2_vu1.h"

#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

// ---- minimal SHA-256 (public-domain style) ----
namespace
{
    struct Sha256
    {
        uint32_t h[8] = {0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
                         0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u};
        uint8_t buf[64]{};
        uint32_t bufLen = 0;
        uint64_t totalLen = 0;

        static uint32_t rotr(uint32_t x, uint32_t n) { return (x >> n) | (x << (32u - n)); }

        void block(const uint8_t *p)
        {
            static const uint32_t k[64] = {
                0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u, 0x3956c25bu, 0x59f111f1u,
                0x923f82a4u, 0xab1c5ed5u, 0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u,
                0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u, 0xe49b69c1u, 0xefbe4786u,
                0x0fc19dc6u, 0x240ca1ccu, 0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
                0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u, 0xc6e00bf3u, 0xd5a79147u,
                0x06ca6351u, 0x14292967u, 0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u,
                0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u, 0xa2bfe8a1u, 0xa81a664bu,
                0xc24b8b70u, 0xc76c51a3u, 0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
                0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u, 0x391c0cb3u, 0x4ed8aa4au,
                0x5b9cca4fu, 0x682e6ff3u, 0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u,
                0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u};
            uint32_t w[64];
            for (int i = 0; i < 16; ++i)
                w[i] = (static_cast<uint32_t>(p[i * 4]) << 24) |
                       (static_cast<uint32_t>(p[i * 4 + 1]) << 16) |
                       (static_cast<uint32_t>(p[i * 4 + 2]) << 8) | static_cast<uint32_t>(p[i * 4 + 3]);
            for (int i = 16; i < 64; ++i)
            {
                const uint32_t s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3);
                const uint32_t s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10);
                w[i] = w[i - 16] + s0 + w[i - 7] + s1;
            }
            uint32_t a = h[0], b = h[1], c = h[2], d = h[3], e = h[4], f = h[5], g = h[6], z = h[7];
            for (int i = 0; i < 64; ++i)
            {
                const uint32_t s1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
                const uint32_t ch = (e & f) ^ (~e & g);
                const uint32_t t1 = z + s1 + ch + k[i] + w[i];
                const uint32_t s0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
                const uint32_t mj = (a & b) ^ (a & c) ^ (b & c);
                const uint32_t t2 = s0 + mj;
                z = g;
                g = f;
                f = e;
                e = d + t1;
                d = c;
                c = b;
                b = a;
                a = t1 + t2;
            }
            h[0] += a;
            h[1] += b;
            h[2] += c;
            h[3] += d;
            h[4] += e;
            h[5] += f;
            h[6] += g;
            h[7] += z;
        }

        void update(const void *data, size_t len)
        {
            const auto *p = static_cast<const uint8_t *>(data);
            totalLen += len;
            while (len > 0)
            {
                const size_t take = 64u - bufLen < len ? 64u - bufLen : len;
                std::memcpy(buf + bufLen, p, take);
                bufLen += static_cast<uint32_t>(take);
                p += take;
                len -= take;
                if (bufLen == 64u)
                {
                    block(buf);
                    bufLen = 0;
                }
            }
        }

        void final(uint8_t out[32])
        {
            const uint64_t bitLen = totalLen * 8u;
            uint8_t pad = 0x80;
            update(&pad, 1);
            pad = 0x00;
            while (bufLen != 56u)
                update(&pad, 1);
            uint8_t lenBytes[8];
            for (int i = 0; i < 8; ++i)
                lenBytes[i] = static_cast<uint8_t>(bitLen >> (56 - i * 8));
            const uint32_t saved = bufLen;
            (void)saved;
            update(lenBytes, 8);
            for (int i = 0; i < 8; ++i)
            {
                out[i * 4] = static_cast<uint8_t>(h[i] >> 24);
                out[i * 4 + 1] = static_cast<uint8_t>(h[i] >> 16);
                out[i * 4 + 2] = static_cast<uint8_t>(h[i] >> 8);
                out[i * 4 + 3] = static_cast<uint8_t>(h[i]);
            }
        }
    };

    std::string sha256Hex(const void *data, size_t len)
    {
        Sha256 s;
        s.update(data, len);
        uint8_t out[32];
        s.final(out);
        char hex[65];
        for (int i = 0; i < 32; ++i)
            std::snprintf(hex + i * 2, 3, "%02x", out[i]);
        return std::string(hex, 64);
    }
} // namespace

// ---- VU1 encodings (same shapes as ps2xTest ps2_vu1_tests.cpp) ----
namespace
{
    constexpr uint32_t kUpperNop = 0x000002FFu;
    constexpr uint32_t kLowerNop = 0u;
    constexpr uint32_t kEbit = 0x40000000u;

    uint32_t makeUpper(uint8_t op, uint8_t dest, uint8_t ft, uint8_t fs, uint8_t fd)
    {
        return (static_cast<uint32_t>(dest & 0xFu) << 21) | (static_cast<uint32_t>(ft & 0x1Fu) << 16) |
               (static_cast<uint32_t>(fs & 0x1Fu) << 11) | (static_cast<uint32_t>(fd & 0x1Fu) << 6) |
               static_cast<uint32_t>(op & 0x3Fu);
    }

    uint32_t makeUpperSpecial(uint8_t specialOp, uint8_t dest, uint8_t ft, uint8_t fs)
    {
        return (static_cast<uint32_t>(dest & 0xFu) << 21) | (static_cast<uint32_t>(ft & 0x1Fu) << 16) |
               (static_cast<uint32_t>(fs & 0x1Fu) << 11) | (static_cast<uint32_t>(specialOp & 0x7Cu) << 4) |
               static_cast<uint32_t>(specialOp & 0x3u) | 0x3Cu;
    }

    uint32_t makeSq(uint8_t dest, uint8_t sourceVf, uint8_t baseVi, int16_t imm)
    {
        return (0x01u << 25) | (static_cast<uint32_t>(dest & 0xFu) << 21) |
               (static_cast<uint32_t>(baseVi & 0xFu) << 16) | (static_cast<uint32_t>(sourceVf & 0x1Fu) << 11) |
               (static_cast<uint32_t>(imm) & 0x7FFu);
    }

    uint32_t makeLq(uint8_t dest, uint8_t targetVf, uint8_t baseVi, int16_t imm)
    {
        return (static_cast<uint32_t>(dest & 0xFu) << 21) | (static_cast<uint32_t>(targetVf & 0x1Fu) << 16) |
               (static_cast<uint32_t>(baseVi & 0xFu) << 11) | (static_cast<uint32_t>(imm) & 0x7FFu);
    }

    uint32_t makeIaddiu(uint8_t it, uint8_t is, int16_t imm)
    {
        return (0x08u << 25) | (static_cast<uint32_t>(it & 0xFu) << 16) |
               (static_cast<uint32_t>(is & 0xFu) << 11) | (static_cast<uint32_t>(imm) & 0x7FFu);
    }

    uint32_t makeIbne(uint8_t is, uint8_t it, int16_t imm)
    {
        return (0x29u << 25) | (static_cast<uint32_t>(it & 0xFu) << 16) |
               (static_cast<uint32_t>(is & 0xFu) << 11) | (static_cast<uint32_t>(imm) & 0x7FFu);
    }

    struct Pair
    {
        uint32_t lower;
        uint32_t upper;
    };

    uint64_t xorshift64(uint64_t &s)
    {
        s ^= s >> 12;
        s ^= s << 25;
        s ^= s >> 27;
        return s * 0x2545F4914F6CDD1Du;
    }
} // namespace

int main(int argc, char **argv)
{
    // SHA-256 self-test: sha256("abc").
    if (sha256Hex("abc", 3) != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
    {
        std::fprintf(stderr, "E45 FATAL: sha256 self-test failed\n");
        return 2;
    }

    const int iters = argc > 1 ? std::atoi(argv[1]) : 20;
    const int loopN = argc > 2 ? std::atoi(argv[2]) : 2048;
    if (iters < 1 || loopN < 1 || loopN > 100000)
    {
        std::fprintf(stderr, "E45 FATAL: bad args (iters loopN)\n");
        return 2;
    }

#if defined(PS2X_VU_WIDE_QUAD) && PS2X_VU_WIDE_QUAD
    const char *variant = "quad";
#else
    const char *variant = "double";
#endif
    std::printf("E45 variant=%s sizeofVuWide=%u iters=%d loopN=%d\n", variant,
                static_cast<unsigned>(sizeof(VuWide)), iters, loopN);
    std::fflush(stdout);

    // Edge-case float bits: zeros, denormals, FLT_MIN/MAX bounds, inf/nan
    // (clamped by normalizeOperand), fractions, big/small normals.
    static const uint32_t kEdge[] = {
        0x00000000u, 0x80000000u, 0x00000001u, 0x007FFFFFu, 0x80000001u, 0x00800000u, 0x80800000u,
        0x00800001u, 0x3F800000u, 0xBF800000u, 0x40000000u, 0xC0000000u, 0x3F000000u, 0xBF000000u,
        0x7F7FFFFFu, 0xFF7FFFFFu, 0x7F7FFFFEu, 0x7F000000u, 0x7F800000u, 0xFF800000u, 0x7FC00000u,
        0xFFC00000u, 0x33800000u, 0xB3800000u, 0x4B000000u, 0xCB000000u, 0x3DCCCCCDu, 0xBDCCCCCDu,
        0x42C80000u, 0xC2C80000u, 0x3FC00000u, 0xBFC00000u,
    };
    constexpr size_t kEdgeN = sizeof(kEdge) / sizeof(kEdge[0]);

    struct Program
    {
        const char *name;
        std::vector<Pair> pairs; // includes trailing NOP/NOP delay slot
        VU1State inputs;
        std::vector<uint8_t> dataMem;
        uint64_t issued = 0;
        uint32_t endPc = 0;
        int32_t expectVi1 = INT32_MIN; // INT32_MIN = no check
    };
    std::vector<Program> progs;

    auto baseInputs = [&]()
    {
        VU1State s{};
        for (uint32_t r = 1; r < 32; ++r)
            for (uint32_t c = 0; c < 4; ++c)
            {
                uint32_t bits = kEdge[(r * 4u + c) % kEdgeN];
                std::memcpy(&s.vf[r][c], &bits, sizeof(bits));
            }
        static const int32_t kVi[16] = {0, 1, 2, 4, 8, -1, -7, 0x7FFF, 0x7FFFFFFF, INT32_MIN,
                                        12345, -12345, 0x100, 0x3FF, 42, -42};
        for (uint32_t r = 0; r < 16; ++r)
            s.vi[r] = kVi[r];
        {
            static const uint32_t kAcc[4] = {0x3F800000u, 0xBF800000u, 0x3F000000u, 0x40000000u};
            for (uint32_t c = 0; c < 4; ++c)
                std::memcpy(&s.acc[c], &kAcc[c], sizeof(uint32_t));
        }
        s.q = 2.0f;
        s.p = 0.0f;
        {
            uint32_t bits = 0x80800000u;
            std::memcpy(&s.i, &bits, sizeof(bits));
        } // i = -FLT_MIN
        s.r = 0x3F800000u;
        return s;
    };

    auto baseDataMem = [&]()
    {
        std::vector<uint8_t> m(PS2_VU1_DATA_SIZE);
        uint64_t s = 0x123456789ABCDEFull;
        for (size_t off = 0; off < m.size(); off += 8)
        {
            const uint64_t v = xorshift64(s);
            std::memcpy(m.data() + off, &v, sizeof(v));
        }
        for (uint32_t q = 0; q < 4; ++q)
            for (uint32_t c = 0; c < 4; ++c)
            {
                uint32_t bits = kEdge[(q * 4u + c) % kEdgeN];
                std::memcpy(m.data() + q * 16u + c * 4u, &bits, sizeof(bits));
            }
        return m;
    };

    // P0 smoke.
    {
        Program p;
        p.name = "P0-smoke";
        p.pairs = {
            {kLowerNop, makeUpper(0x28u, 0xFu, 2u, 1u, 10u)},  // ADD.xyzw vf10, vf1, vf2
            {kLowerNop, makeUpper(0x2Au, 0xFu, 4u, 3u, 11u)},  // MUL.xyzw vf11, vf3, vf4
            {kLowerNop, makeUpper(0x29u, 0xFu, 6u, 5u, 12u)},  // MADD.xyzw vf12, vf5, vf6
            {makeSq(0xFu, 12u, 3u, 0), makeUpper(0x2Cu, 0xFu, 8u, 7u, 13u) | kEbit}, // SQ + SUB|E
            {kLowerNop, kUpperNop},
        };
        p.inputs = baseInputs();
        p.dataMem = baseDataMem();
        progs.push_back(std::move(p));
    }

    // P1 op sweep, regular encoding: every op handled by
    // calculateFmacExactResult's op<0x3C path.
    {
        static const uint8_t kOps[] = {0x00u, 0x01u, 0x02u, 0x03u, 0x04u, 0x05u, 0x06u, 0x07u,
                                       0x08u, 0x09u, 0x0Au, 0x0Bu, 0x0Cu, 0x0Du, 0x0Eu, 0x0Fu,
                                       0x18u, 0x19u, 0x1Au, 0x1Bu, 0x1Cu, 0x1Eu, 0x20u, 0x21u,
                                       0x22u, 0x23u, 0x24u, 0x25u, 0x26u, 0x27u, 0x28u, 0x29u,
                                       0x2Au, 0x2Cu, 0x2Du, 0x2Eu};
        Program p;
        p.name = "P1-opsweep";
        for (size_t k = 0; k < sizeof(kOps); ++k)
        {
            const uint8_t fs = static_cast<uint8_t>(1u + (k % 7u));
            const uint8_t ft = static_cast<uint8_t>(2u + ((k + 3u) % 6u));
            const uint8_t fd = static_cast<uint8_t>(9u + (k % 20u));
            p.pairs.push_back({kLowerNop, makeUpper(kOps[k], 0xFu, ft, fs, fd)});
        }
        p.pairs.back().upper |= kEbit;
        p.pairs.push_back({kLowerNop, kUpperNop});
        p.inputs = baseInputs();
        p.dataMem = baseDataMem();
        progs.push_back(std::move(p));
    }

    // P2 special sweep: same ops via the special/ACC encoding.
    {
        static const uint8_t kOps[] = {0x00u, 0x01u, 0x02u, 0x03u, 0x04u, 0x05u, 0x06u, 0x07u,
                                       0x08u, 0x09u, 0x0Au, 0x0Bu, 0x0Cu, 0x0Du, 0x0Eu, 0x0Fu,
                                       0x18u, 0x19u, 0x1Au, 0x1Bu, 0x1Cu, 0x1Eu, 0x20u, 0x21u,
                                       0x22u, 0x23u, 0x24u, 0x25u, 0x26u, 0x27u, 0x28u, 0x29u,
                                       0x2Au, 0x2Cu, 0x2Du, 0x2Eu};
        Program p;
        p.name = "P2-special";
        for (size_t k = 0; k < sizeof(kOps); ++k)
        {
            const uint8_t fs = static_cast<uint8_t>(1u + (k % 7u));
            const uint8_t ft = static_cast<uint8_t>(2u + ((k + 3u) % 6u));
            p.pairs.push_back({kLowerNop, makeUpperSpecial(kOps[k], 0xFu, ft, fs)});
        }
        p.pairs.back().upper |= kEbit;
        p.pairs.push_back({kLowerNop, kUpperNop});
        p.inputs = baseInputs();
        p.dataMem = baseDataMem();
        progs.push_back(std::move(p));
    }

    // P3 FMAC-heavy loop: 6-pair body (dependent chains + independent),
    // head runs loopN+1 times (branch compares pre-increment counter).
    {
        Program p;
        p.name = "P3-fmacloop";
        p.pairs = {
            {kLowerNop, makeUpper(0x29u, 0xFu, 2u, 1u, 10u)}, // MADD vf10, vf1, vf2
            {kLowerNop, makeUpper(0x29u, 0xFu, 3u, 10u, 11u)}, // MADD vf11, vf10, vf3 (dep)
            {kLowerNop, makeUpper(0x2Au, 0xFu, 5u, 4u, 12u)}, // MUL vf12, vf4, vf5
            {kLowerNop, makeUpper(0x2Du, 0xFu, 7u, 6u, 13u)}, // MSUB vf13, vf6, vf7
            {kLowerNop, makeUpper(0x28u, 0xFu, 12u, 11u, 14u)}, // ADD vf14, vf11, vf12 (dep)
            {kLowerNop, makeUpper(0x29u, 0xFu, 14u, 13u, 10u)}, // MADD vf10, vf13, vf14 (dep)
            {makeIbne(1u, 2u, -7), kUpperNop},                 // pc48: back to pc0
            {makeIaddiu(1u, 1u, 1), kUpperNop},                // delay: vi1++
            {kLowerNop, kUpperNop | kEbit},
            {kLowerNop, kUpperNop},
        };
        p.inputs = baseInputs();
        p.inputs.vi[1] = 0;
        p.inputs.vi[2] = loopN;
        p.issued = static_cast<uint64_t>(loopN + 1) * 8u + 2u;
        p.expectVi1 = loopN + 1;
        p.dataMem = baseDataMem();
        progs.push_back(std::move(p));
    }

    // P4 boundary torture: overflow/underflow/cancellation/denormal FMACs
    // plus SQ/LQ VU-mem roundtrip.
    {
        Program p;
        p.name = "P4-torture";
        p.pairs = {
            {kLowerNop, makeUpper(0x2Au, 0xFu, 21u, 20u, 22u)}, // MAX*MAX -> +clamp
            {kLowerNop, makeUpper(0x29u, 0xFu, 21u, 20u, 22u)}, // acc+MAX*MAX -> +clamp
            {kLowerNop, makeUpper(0x2Au, 0xFu, 24u, 23u, 25u)}, // MIN*MIN -> +0 (U|Z)
            {kLowerNop, makeUpper(0x2Du, 0xFu, 24u, 23u, 25u)}, // acc-tiny
            {kLowerNop, makeUpper(0x28u, 0xFu, 28u, 27u, 26u)}, // x+(-x) -> +0 (Z)
            {kLowerNop, makeUpper(0x2Cu, 0xFu, 27u, 27u, 26u)}, // x-x -> +0
            {kLowerNop, makeUpper(0x28u, 0xFu, 31u, 30u, 29u)}, // denormal flush -> 0
            {kLowerNop, makeUpper(0x1Cu, 0xFu, 0u, 20u, 26u)},  // MULq MAX*2 -> overflow
            {kLowerNop, makeUpper(0x1Eu, 0xFu, 0u, 20u, 26u)},  // MULi MAX*i
            {kLowerNop, makeUpper(0x22u, 0xFu, 0u, 23u, 26u)},  // ADDi MIN+(-MIN) -> 0
            {kLowerNop, makeUpper(0x24u, 0xFu, 0u, 20u, 26u)},  // SUBq MAX-2
            {kLowerNop, makeUpper(0x21u, 0xFu, 0u, 20u, 26u)},  // MADDq
            {kLowerNop, makeUpper(0x27u, 0xFu, 0u, 21u, 26u)},  // MSUBi
            {kLowerNop, makeUpper(0x2Eu, 0xFu, 19u, 18u, 16u)}, // OPMULA cross
            {kLowerNop, makeUpper(0x28u, 0xFu, 15u, 15u, 15u)}, // near-max doubling
            {kLowerNop, makeUpper(0x19u, 0xFu, 19u, 18u, 17u)}, // MULy bc
            {kLowerNop, makeUpper(0x02u, 0xFu, 19u, 18u, 17u)}, // ADDz bc
            {kLowerNop, makeUpper(0x0Bu, 0xFu, 19u, 18u, 17u)}, // MADDw bc
            {makeSq(0xFu, 22u, 4u, 0), kUpperNop},              // SQ clamped MAX
            {makeSq(0xFu, 25u, 4u, 1), kUpperNop},              // SQ underflow 0
            {makeLq(0xFu, 15u, 5u, 0), kUpperNop},              // LQ reload
            {kLowerNop, makeUpper(0x2Au, 0xFu, 1u, 15u, 15u)},  // MAX*1.0
            {kLowerNop, makeUpper(0x29u, 0xFu, 21u, 21u, 22u) | kEbit},
            {kLowerNop, kUpperNop},
        };
        p.inputs = baseInputs();
        auto poke = [&](uint8_t r, uint32_t b0, uint32_t b1, uint32_t b2, uint32_t b3)
        {
            uint32_t b[4] = {b0, b1, b2, b3};
            for (uint32_t c = 0; c < 4; ++c)
                std::memcpy(&p.inputs.vf[r][c], &b[c], sizeof(uint32_t));
        };
        poke(20u, 0x7F7FFFFFu, 0x7F7FFFFFu, 0x7F7FFFFFu, 0x7F7FFFFFu); // +MAX
        poke(21u, 0x7F7FFFFFu, 0xFF7FFFFFu, 0x7F7FFFFEu, 0x7F000000u); // MAX mix
        poke(23u, 0x00800000u, 0x00800000u, 0x80800000u, 0x00800001u); // MIN mix
        poke(24u, 0x00800000u, 0x3F800000u, 0x00800001u, 0x33800000u);
        poke(27u, 0x3FC00000u, 0x42C80000u, 0x7F7FFFFFu, 0x00800000u); // +x
        poke(28u, 0xBFC00000u, 0xC2C80000u, 0xFF7FFFFFu, 0x80800000u); // -x
        poke(30u, 0x00000001u, 0x007FFFFFu, 0x00000001u, 0x007FFFFFu); // +den
        poke(31u, 0x80000001u, 0x807FFFFFu, 0x33800000u, 0xB3800000u); // -den/tiny
        poke(15u, 0x7F000000u, 0x7F000000u, 0x7F000000u, 0x7F000000u); // near-max
        poke(18u, 0x4B000000u, 0xCB000000u, 0x3DCCCCCDu, 0xBDCCCCCDu);
        poke(19u, 0x40000000u, 0xBF800000u, 0x42C80000u, 0xC2C80000u);
        p.inputs.vi[4] = 8;
        p.inputs.vi[5] = 8;
        p.dataMem = baseDataMem();
        progs.push_back(std::move(p));
    }

    for (auto &p : progs)
    {
        if (p.issued == 0)
            p.issued = p.pairs.size();
        // End pc is the last static pair + 8 even when branches re-execute
        // pairs (trip counts are verified by register checks instead).
        p.endPc = static_cast<uint32_t>(p.pairs.size() * 8u);
    }

    static uint8_t codeBuf[PS2_VU1_CODE_SIZE];
    static uint8_t dataBuf[PS2_VU1_DATA_SIZE];
    GS gs; // stub-constructed; bench programs never XGkick

    constexpr uint32_t kBudget = 1u << 20;
    bool ok = true;
    for (const auto &p : progs)
    {
        std::memset(codeBuf, 0, sizeof(codeBuf));
        for (size_t i = 0; i < p.pairs.size(); ++i)
        {
            std::memcpy(codeBuf + i * 8u, &p.pairs[i].lower, 4u);
            std::memcpy(codeBuf + i * 8u + 4u, &p.pairs[i].upper, 4u);
        }

        VU1Interpreter vu;
        auto runOnce = [&]() -> uint64_t
        {
            vu.reset();
            vu.state() = p.inputs;
            std::memcpy(dataBuf, p.dataMem.data(), p.dataMem.size());
            const uint64_t c0 = vu.state().cycles;
            vu.execute(codeBuf, PS2_VU1_CODE_SIZE, dataBuf, PS2_VU1_DATA_SIZE, gs, nullptr, 0u, 0u, 0u,
                       kBudget);
            return vu.state().cycles - c0;
        };

        runOnce(); // warmup
        runOnce();
        const auto t0 = std::chrono::steady_clock::now();
        uint64_t cyclesUsed = 0;
        for (int i = 0; i < iters; ++i)
            cyclesUsed = runOnce();
        const auto t1 = std::chrono::steady_clock::now();
        const uint64_t nsTotal =
            static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count());

        // Fresh hash run (state after one timed-equivalent execution).
        runOnce();
        const VU1State &st = vu.state();
        bool progOk = true;
        if (st.pc != p.endPc)
        {
            std::fprintf(stderr, "E45 FAIL %s: end pc=0x%x want 0x%x (truncated/reserved?)\n", p.name, st.pc,
                         p.endPc);
            progOk = false;
        }
        if (cyclesUsed * 2u >= kBudget)
        {
            std::fprintf(stderr, "E45 FAIL %s: cycles %llu near budget %u\n", p.name,
                         static_cast<unsigned long long>(cyclesUsed), kBudget);
            progOk = false;
        }
        if (p.expectVi1 != INT32_MIN && st.vi[1] != p.expectVi1)
        {
            std::fprintf(stderr, "E45 FAIL %s: vi1=%d want %d\n", p.name, st.vi[1], p.expectVi1);
            progOk = false;
        }

        Sha256 h;
        h.update(st.vf, sizeof(st.vf));
        h.update(st.vi, sizeof(st.vi));
        h.update(st.acc, sizeof(st.acc));
        h.update(&st.q, sizeof(st.q));
        h.update(&st.p, sizeof(st.p));
        h.update(&st.i, sizeof(st.i));
        h.update(&st.r, sizeof(st.r));
        h.update(&st.pc, sizeof(st.pc));
        h.update(&st.mac, sizeof(st.mac));
        h.update(&st.clip, sizeof(st.clip));
        h.update(&st.status, sizeof(st.status));
        h.update(dataBuf, sizeof(dataBuf));
        uint8_t digest[32];
        h.final(digest);
        char hex[65];
        for (int i = 0; i < 32; ++i)
            std::snprintf(hex + i * 2, 3, "%02x", digest[i]);

        const double nsPerInstr = static_cast<double>(nsTotal) / (static_cast<double>(iters) * p.issued);
        std::printf("E45 prog=%s variant=%s iters=%d issued=%llu cycles=%llu ns_total=%llu ns_per_instr=%.1f "
                    "pc_end=0x%x sha=%s %s\n",
                    p.name, variant, iters, static_cast<unsigned long long>(p.issued),
                    static_cast<unsigned long long>(cyclesUsed), static_cast<unsigned long long>(nsTotal),
                    nsPerInstr, st.pc, hex, progOk ? "OK" : "FAIL");
        std::fflush(stdout);
        ok = ok && progOk;
    }
    std::printf("E45 %s\n", ok ? "ALL_OK" : "FAILURES");
    return ok ? 0 : 1;
}
