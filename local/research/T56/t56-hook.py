#!/usr/bin/env python3
"""T56 hook (pcsx2-g7, on top of the T55 working tree = HEAD 9056c083 + T48-T55 hooks).

Who writes scratchpad item words 0x70000000..0x7000000c and
0x70000500..0x7000050c (4 words each, 8 total)? Every path into the
scratchpad is watched:

- EE stores: the 9 interpreter store ops in R5900OpcodeImpl.cpp
  (SB/SH/SW/SWL/SWR/SD/SDL/SDR/SQ) + SWC1 (FPU.cpp) + SQC2 (VU0.cpp).
  Line: spw vsync=<n> addr=0x<> value=0x<> via=<op> pc=0x<> ra=0x<> a0..s7
- SPR DMA toSPR (channel 9): SPR1transfer (normal+chain incl. TTE tag
  transfer) + _SPR1interleave in SPR.cpp.
  Line: spw ... via=spr-dma src=0x<EE madr> pc=... (pc/ra/regs are the
  EE state at DMA time; the writer key is src).

Plus a file-driven second watch (/tmp/t56-watch2, one hex addr per line,
word-aligned, <=64) in the same spw format with via=<op>: capture 2
uses it for the EE source word of a DMA copy with NO rebuild.

Caps: first 64 per watched word, then one T56_CAP line per word.
Log-only. Idempotent: aborts if applied. Asserts every anchor count.
"""

import re

RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"
FPU = "/home/brad/pcsx2-g7/pcsx2/pcsx2/FPU.cpp"
VU0 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU0.cpp"
SPR = "/home/brad/pcsx2-g7/pcsx2/pcsx2/SPR.cpp"

REGS_FMT = ("a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x "
            "t0=%08x t1=%08x t2=%08x t3=%08x t4=%08x t5=%08x t6=%08x t7=%08x t8=%08x t9=%08x "
            "s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x")
REGS_ARGS = ("cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0], "
             "cpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0], "
             "cpuRegs.GPR.r[8].UL[0], cpuRegs.GPR.r[9].UL[0], cpuRegs.GPR.r[10].UL[0], cpuRegs.GPR.r[11].UL[0], "
             "cpuRegs.GPR.r[12].UL[0], cpuRegs.GPR.r[13].UL[0], cpuRegs.GPR.r[14].UL[0], cpuRegs.GPR.r[15].UL[0], "
             "cpuRegs.GPR.r[24].UL[0], cpuRegs.GPR.r[25].UL[0], "
             "cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0], "
             "cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0], cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0]")


def emit_fn(has_src):
    src_fmt = " src=0x%x" if has_src else ""
    src_arg = ", srcmadr" if has_src else ""
    rf = REGS_FMT  # substituted as an argument value: never re-scanned for % specs
    return ("""static void t56_emit(u32 w, u32 val, const char* via%s%s)
{
\tint t56_vs = g_t48_vsync.load(std::memory_order_relaxed);
\tConsole.WriteLn("spw vsync=%%d addr=0x%%x value=0x%%x via=%%s%s pc=0x%%x ra=0x%%x %s",
\t\tt56_vs, w, val, via%s, cpuRegs.pc, cpuRegs.GPR.r[31].UL[0], %s);
}
""" % ("," if has_src else "", " u32 srcmadr" if has_src else "", src_fmt, rf, src_arg, REGS_ARGS))


T56_RI_DECL = """
// T56: scratchpad item writer watch (log-only; 8 fixed words + /tmp/t56-watch2 file addrs).
static const u32 g_t56_fixed[8] = {0x70000000u, 0x70000004u, 0x70000008u, 0x7000000cu, 0x70000500u, 0x70000504u, 0x70000508u, 0x7000050cu};
static u32 g_t56_hits[8] = {0, 0, 0, 0, 0, 0, 0, 0};
#define T56W2_MAXA 64
static u32 g_t56w2_addr[T56W2_MAXA];
static u32 g_t56w2_hits[T56W2_MAXA];
static u32 g_t56w2_naddr = 0;
static bool g_t56w2_armed = false;
static u32 g_t56w2_arm_ctr = 0;
static bool t56w2_arm()
{
\tif (g_t56w2_armed) return true;
\tif ((++g_t56w2_arm_ctr & 1023) != 0) return false; // EE interp thread only.
\tFILE* t56wf = fopen("/tmp/t56-watch2", "r");
\tif (!t56wf) return false;
\tchar t56line[64];
\twhile (g_t56w2_naddr < T56W2_MAXA && fgets(t56line, sizeof(t56line), t56wf))
\t{
\t\tu32 a = (u32)strtoul(t56line, nullptr, 0);
\t\tif (a == 0) continue;
\t\tg_t56w2_addr[g_t56w2_naddr] = a & ~3u;
\t\tg_t56w2_hits[g_t56w2_naddr] = 0;
\t\tg_t56w2_naddr++;
\t}
\tfclose(t56wf);
\tg_t56w2_armed = true;
\tConsole.WriteLn("T56W_ARMED naddr=%u", g_t56w2_naddr);
\treturn true;
}
""" + emit_fn(False) + """static void t56_watch(u32 vaddr, u32 size, const char* via)
{
\tu32 lo = vaddr;
\tu32 hi = vaddr + size;
\tfor (u32 i = 0; i < 8; i++)
\t{
\t\tu32 w = g_t56_fixed[i];
\t\tif (w + 4 <= lo || w >= hi) continue;
\t\tu32 k = g_t56_hits[i]++;
\t\tif (k >= 64)
\t\t{
\t\t\tif (k == 64) Console.WriteLn("T56_CAP vsync=%d addr=0x%x", g_t48_vsync.load(std::memory_order_relaxed), w);
\t\t\tcontinue;
\t\t}
\t\tt56_emit(w, memRead32(w), via);
\t}
\tif (!t56w2_arm()) return;
\tfor (u32 i = 0; i < g_t56w2_naddr; i++)
\t{
\t\tu32 w = g_t56w2_addr[i];
\t\tif (w + 4 <= lo || w >= hi) continue;
\t\tu32 k = g_t56w2_hits[i]++;
\t\tif (k >= 64)
\t\t{
\t\t\tif (k == 64) Console.WriteLn("T56_CAP vsync=%d addr=0x%x", g_t48_vsync.load(std::memory_order_relaxed), w);
\t\t\tcontinue;
\t\t}
\t\tt56_emit(w, memRead32(w), via);
\t}
}
"""

T56_SPR_DECL = """
// T56: toSPR (channel 9) scratchpad writer watch (log-only; same 8 fixed words).
static const u32 g_t56s_fixed[8] = {0x70000000u, 0x70000004u, 0x70000008u, 0x7000000cu, 0x70000500u, 0x70000504u, 0x70000508u, 0x7000050cu};
static u32 g_t56s_hits[8] = {0, 0, 0, 0, 0, 0, 0, 0};
""" + emit_fn(True).replace("t56_emit", "t56s_emit") + """static void t56_spr_watch(u32 sadr, u32 bytes, u32 madr)
{
\tu32 end = sadr + bytes;
\tfor (u32 i = 0; i < 8; i++)
\t{
\t\tu32 off = g_t56s_fixed[i] - 0x70000000u;
\t\tu32 srcmadr;
\t\tif (off >= sadr && off < end) srcmadr = madr + (off - sadr);
\t\telse if (end > 0x4000u && off < (end & 0x3fffu)) srcmadr = madr + (0x4000u - sadr) + off; // wrapped transfer
\t\telse continue;
\t\tu32 k = g_t56s_hits[i]++;
\t\tif (k >= 64)
\t\t{
\t\t\tif (k == 64) Console.WriteLn("T56_CAP vsync=%d addr=0x%x", g_t48_vsync.load(std::memory_order_relaxed), g_t56s_fixed[i]);
\t\t\tcontinue;
\t\t}
\t\tt56s_emit(g_t56s_fixed[i], psSu32(off), "spr-dma", srcmadr);
\t}
}
"""


def check(text, find, want, name):
    n = text.count(find)
    assert n == want, "%s: anchor count=%d, want %d" % (name, n, want)


def main():
    ri = open(RI, encoding="utf-8").read()
    fpu = open(FPU, encoding="utf-8").read()
    vu0 = open(VU0, encoding="utf-8").read()
    spr = open(SPR, encoding="utf-8").read()

    assert "t56_watch" not in ri, "T56 already in R5900OpcodeImpl.cpp"
    assert "t56_watch" not in fpu, "T56 already in FPU.cpp"
    assert "t56_watch" not in vu0, "T56 already in VU0.cpp"
    assert "t56_spr_watch" not in spr, "T56 already in SPR.cpp"
    assert "t54w_watch(addr, 1)" in ri, "T54 baseline missing in RI"
    assert "t53w_watch(addr, 4)" in fpu, "T53 baseline missing in FPU.cpp"
    assert "t53w_watch(addr, 16)" in vu0, "T53 baseline missing in VU0.cpp"
    assert "SPR1transfer" in spr, "SPR baseline missing in SPR.cpp"

    # --- RI: decl + 9 call sites, in file order SB/SH/SW/SWL/SWR/SD/SDL/SDR/SQ ---
    check(ri, "static void t51w_watch(u32 vaddr, u32 size)", 1, "RI-decl-anchor")
    ri = ri.replace("static void t51w_watch(u32 vaddr, u32 size)",
                    T56_RI_DECL + "static void t51w_watch(u32 vaddr, u32 size)", 1)
    want_seq = [("(addr, 1)", "sb"), ("(addr, 2)", "sh"), ("(addr, 4)", "sw"),
                ("(addr & ~3, 4)", "swl"), ("(addr & ~3, 4)", "swr"),
                ("(addr, 8)", "sd"), ("(addr & ~7, 8)", "sdl"), ("(addr & ~7, 8)", "sdr"),
                ("(addr & ~0xf, 16)", "sq")]
    lines = ri.split("\n")
    got = []
    ncall = 0
    for idx, ln in enumerate(lines):
        m = re.match(r"^(\s*)t54w_watch(\(.*\))\;(.*)$", ln)
        if m and "static void" not in ln:
            indent, args, tail = m.groups()
            assert ncall < 9, "more than 9 t54w sites in RI"
            want_args, via = want_seq[ncall]
            assert args == want_args, "RI site %d: args=%s, want %s" % (ncall, args, want_args)
            lines[idx] = ln + "\n" + indent + 't56_watch%s, "%s"); // T56: scratchpad writer watch (log-only).' % (args[:-1], via)
            got.append(via)
            ncall += 1
    assert ncall == 9, "RI call sites=%d, want 9" % ncall
    assert got == [v for _, v in want_seq], "RI via order=%s" % got
    ri = "\n".join(lines)
    open(RI, "w", encoding="utf-8").write(ri)

    # --- FPU.cpp: SWC1 ---
    check(fpu, "void SWC1() {", 1, "FPU-site")
    check(fpu, "\tt54w_watch(addr, 4); // T54: record-word producer watch (log-only).", 1, "FPU-call")
    fpu = fpu.replace("void SWC1() {", T56_RI_DECL + "void SWC1() {", 1)
    fpu = fpu.replace("\tt54w_watch(addr, 4); // T54: record-word producer watch (log-only).",
                      "\tt54w_watch(addr, 4); // T54: record-word producer watch (log-only).\n\tt56_watch(addr, 4, \"swc1\"); // T56: scratchpad writer watch (log-only).", 1)
    open(FPU, "w", encoding="utf-8").write(fpu)

    # --- VU0.cpp: SQC2 ---
    check(vu0, "\tvoid SQC2() {", 1, "VU0-site")
    check(vu0, "\t\tt54w_watch(addr, 16); // T54: record-word producer watch (log-only).", 1, "VU0-call")
    vu0 = vu0.replace("\tvoid SQC2() {", T56_RI_DECL + "\tvoid SQC2() {", 1)
    vu0 = vu0.replace("\t\tt54w_watch(addr, 16); // T54: record-word producer watch (log-only).",
                      "\t\tt54w_watch(addr, 16); // T54: record-word producer watch (log-only).\n\t\tt56_watch(addr, 16, \"sqc2\"); // T56: scratchpad writer watch (log-only).", 1)
    open(VU0, "w", encoding="utf-8").write(vu0)

    # --- SPR.cpp: decl + 2 toSPR sites ---
    check(spr, '#include "MTVU.h"', 1, "SPR-inc")
    spr = spr.replace('#include "MTVU.h"',
                      '#include "MTVU.h"\n#include <atomic>\nextern std::atomic<int> g_t48_vsync; // T56: defined in GS.cpp (T48 vsync mirror).', 1)
    check(spr, "static void TestClearVUs(u32 madr, u32 qwc, bool isWrite)", 1, "SPR-decl-anchor")
    spr = spr.replace("static void TestClearVUs(u32 madr, u32 qwc, bool isWrite)",
                      T56_SPR_DECL + "static void TestClearVUs(u32 madr, u32 qwc, bool isWrite)", 1)
    check(spr, "\tmemcpy_to_spr(spr1ch.sadr, (u8*)data, qwc*16);", 1, "SPR-xfer")
    spr = spr.replace("\tmemcpy_to_spr(spr1ch.sadr, (u8*)data, qwc*16);",
                      "\tmemcpy_to_spr(spr1ch.sadr, (u8*)data, qwc*16);\n\tt56_spr_watch(spr1ch.sadr, (u32)(qwc*16), spr1ch.madr); // T56: toSPR writer watch (log-only).", 1)
    check(spr, "\t\tmemcpy_to_spr(spr1ch.sadr, (u8*)pMem, spr1ch.qwc*16);", 1, "SPR-interleave")
    spr = spr.replace("\t\tmemcpy_to_spr(spr1ch.sadr, (u8*)pMem, spr1ch.qwc*16);",
                      "\t\tmemcpy_to_spr(spr1ch.sadr, (u8*)pMem, spr1ch.qwc*16);\n\t\tt56_spr_watch(spr1ch.sadr, spr1ch.qwc*16, spr1ch.madr); // T56: toSPR interleave writer watch (log-only).", 1)
    open(SPR, "w", encoding="utf-8").write(spr)

    print("T56 hook applied: RI(decl+9) + FPU(SWC1) + VU0(SQC2) + SPR(decl+2) ok")


if __name__ == "__main__":
    main()
