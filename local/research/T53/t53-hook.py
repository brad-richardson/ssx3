#!/usr/bin/env python3
"""T53 hook (pcsx2-g7, on top of the T51 working tree = HEAD 9056c083 + T51 hooks).

T51's whole-boot ADDR-word watch saw 0 writes on the four CALL->0x434990 ADDR
words (0x63d434/0x63dcb4/0x70a0b4/0x70a934). E41 (recomp side) showed why a raw
watch can miss: the game stores through 0x00/0x20/0x30/0x80 mirrors and/or a
low-level fast path, so a raw-address compare misses. T53:

(1) RI fold-fix (in place, T51w names kept): compare (addr & 0x0FFFFFFF) and
    store watch addresses folded; watch file becomes /tmp/t53-watch (8 words:
    the four 0x434990-bound ADDR words + the four 0x435bd0-bound ADDR words
    0x63c654/0x63c8a4/0x63cb64/0x63cdf4 = tag_at+4 of T51's 0x63c650-class
    CALL sites); markers T51W_* -> T53W_*. Line format unchanged
    (`tagaddrwrite vsync addr value pc ra a0..s7`, post-write word, 64/address).
(2) Coverage: T51 hooked the 9 integer store opcodes in R5900OpcodeImpl.cpp
    but NOT SWC1 (FPU.cpp) / SQC2 (VU0.cpp). Audit: no LL/SC interpreter impl
    exists (game would trap), SDC1 does not exist on the EE, MMI/COP0 have no
    RAM stores, CACHE is a stub, PREF is a no-op, SYSCALL-internal memWrites
    are HLE setup (excluded, noted). So SWC1+SQC2 complete the EE interp store
    set: each gets a self-contained T53 watch block (same file/format/caps,
    per-TU 64/address) + one call after its memWrite.
Log-only. Idempotent: aborts if applied. Asserts every anchor count.
"""

RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"
FPU = "/home/brad/pcsx2-g7/pcsx2/pcsx2/FPU.cpp"
VU0 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU0.cpp"


def check(text, find, want, name):
    n = text.count(find)
    assert n == want, "%s: anchor count=%d, want %d" % (name, n, want)


def rep1(text, old, new, name):
    check(text, old, 1, name)
    return text.replace(old, new, 1)


T53_TOP = """
// T53: folded-mirror ADDR-word watch includes/externs (log-only).
#include <atomic>
#include <cstdio>
#include <cstdlib>
extern std::atomic<int> g_t48_vsync; // T53: defined in GS.cpp (T48 vsync mirror).
"""

T53_DECL = """
// T53: folded-mirror ADDR-word write watch (log-only; addresses from /tmp/t53-watch).
#define T53W_MAXA 16
static u32 g_t53w_addr[T53W_MAXA];
static u32 g_t53w_naddr = 0;
static u32 g_t53w_hits[T53W_MAXA];
static bool g_t53w_armed = false;
static u32 g_t53w_arm_ctr = 0;
static bool t53w_arm()
{
\tif (g_t53w_armed) return true;
\tif ((++g_t53w_arm_ctr & 1023) != 0) return false; // EE interp thread only.
\tFILE* t53wf = fopen("/tmp/t53-watch", "r");
\tif (!t53wf) return false;
\tchar t53line[64];
\twhile (g_t53w_naddr < T53W_MAXA && fgets(t53line, sizeof(t53line), t53wf))
\t{
\t\tu32 a = (u32)strtoul(t53line, nullptr, 0);
\t\tif (a == 0) continue;
\t\tg_t53w_addr[g_t53w_naddr] = (a & 0x0fffffff) & ~3u; // T53: fold 0x00/0x20/0x30/0x80 mirrors (E41).
\t\tg_t53w_hits[g_t53w_naddr] = 0;
\t\tg_t53w_naddr++;
\t}
\tfclose(t53wf);
\tg_t53w_armed = true;
\tConsole.WriteLn("T53W_ARMED naddr=%u", g_t53w_naddr);
\treturn true;
}
// EE store overlapping a watched ADDR word (post-write word + 28 GPRs, first 64 per address per TU).
static void t53w_watch(u32 vaddr, u32 size)
{
\tif (!t53w_arm()) return;
\tu32 pbase = vaddr & 0x0fffffff; // T53: fold mirrors (E41); T51's 0x1fffffff missed 0x2/0x3 mirrors.
\tu32 lo = pbase;
\tu32 hi = pbase + size;
\tint t53_vs = g_t48_vsync.load(std::memory_order_relaxed);
\tfor (u32 i = 0; i < g_t53w_naddr; i++)
\t{
\t\tu32 w = g_t53w_addr[i];
\t\tif (w + 4 <= lo || w >= hi) continue;
\t\tu32 k = g_t53w_hits[i]++;
\t\tif (k >= 64)
\t\t{
\t\t\tif (k == 64) Console.WriteLn("T53W_CAP vsync=%d addr=0x%x", t53_vs, w);
\t\t\tcontinue;
\t\t}
\t\tConsole.WriteLn("tagaddrwrite vsync=%d addr=0x%x value=0x%x pc=0x%x ra=0x%x a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x t0=%08x t1=%08x t2=%08x t3=%08x t4=%08x t5=%08x t6=%08x t7=%08x t8=%08x t9=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x",
\t\t\tt53_vs, w, memRead32(w), cpuRegs.pc, cpuRegs.GPR.r[31].UL[0],
\t\t\tcpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0],
\t\t\tcpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0],
\t\t\tcpuRegs.GPR.r[8].UL[0], cpuRegs.GPR.r[9].UL[0], cpuRegs.GPR.r[10].UL[0], cpuRegs.GPR.r[11].UL[0],
\t\t\tcpuRegs.GPR.r[12].UL[0], cpuRegs.GPR.r[13].UL[0], cpuRegs.GPR.r[14].UL[0], cpuRegs.GPR.r[15].UL[0],
\t\t\tcpuRegs.GPR.r[24].UL[0], cpuRegs.GPR.r[25].UL[0],
\t\t\tcpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0],
\t\t\tcpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0], cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0]);
\t}
}
"""


def main():
    ri = open(RI, encoding="utf-8").read()
    fpu = open(FPU, encoding="utf-8").read()
    vu0 = open(VU0, encoding="utf-8").read()

    assert "t53w_watch" not in fpu, "T53 already in FPU.cpp"
    assert "t53w_watch" not in vu0, "T53 already in VU0.cpp"
    assert "/tmp/t53-watch" not in ri, "T53 already in R5900OpcodeImpl.cpp"
    assert "T53W_ARMED" not in ri, "T53 already in R5900OpcodeImpl.cpp"

    # --- RI fold-fix (5 one-line edits, T51w names kept) ---
    ri = rep1(ri, '\tFILE* t51wf = fopen("/tmp/t51-watch", "r");',
              '\tFILE* t51wf = fopen("/tmp/t53-watch", "r"); // T53: 8-word watch file.',
              "RI-watchfile")
    ri = rep1(ri, "\t\tg_t51w_addr[g_t51w_naddr] = a & ~3u;",
              "\t\tg_t51w_addr[g_t51w_naddr] = (a & 0x0fffffff) & ~3u; // T53: fold mirrors (E41).",
              "RI-addrfold")
    ri = rep1(ri, "static void t51w_watch(u32 vaddr, u32 size)\n{\n\tif (!t51w_arm()) return;\n\tu32 pbase = vaddr & 0x1fffffff;",
              "static void t51w_watch(u32 vaddr, u32 size)\n{\n\tif (!t51w_arm()) return;\n\tu32 pbase = vaddr & 0x0fffffff; // T53: fold 0x00/0x20/0x30/0x80 mirrors (E41).",
              "RI-storefold")
    ri = rep1(ri, '\tConsole.WriteLn("T51W_ARMED naddr=%u", g_t51w_naddr);',
              '\tConsole.WriteLn("T53W_ARMED naddr=%u", g_t51w_naddr); // T53.',
              "RI-armed")
    ri = rep1(ri, '\t\t\tif (k == 64) Console.WriteLn("T51W_CAP vsync=%d addr=0x%x", t51_vs, w);',
              '\t\t\tif (k == 64) Console.WriteLn("T53W_CAP vsync=%d addr=0x%x", t51_vs, w); // T53.',
              "RI-cap")
    open(RI, "w", encoding="utf-8").write(ri)

    # --- FPU.cpp: SWC1 ---
    check(fpu, '#include "Common.h"\n', 1, "FPU-top")
    check(fpu, "void SWC1() {", 1, "FPU-site")
    check(fpu, "\tmemWrite32(addr, fpuRegs.fpr[_Rt_].UL);", 1, "FPU-call")
    fpu = fpu.replace('#include "Common.h"\n', '#include "Common.h"\n' + T53_TOP, 1)
    fpu = fpu.replace("void SWC1() {", T53_DECL + "void SWC1() {", 1)
    fpu = fpu.replace("\tmemWrite32(addr, fpuRegs.fpr[_Rt_].UL);",
                      "\tmemWrite32(addr, fpuRegs.fpr[_Rt_].UL);\n\tt53w_watch(addr, 4); // T53: ADDR-word watch (log-only).", 1)
    open(FPU, "w", encoding="utf-8").write(fpu)

    # --- VU0.cpp: SQC2 ---
    check(vu0, '#include "Common.h"\n', 1, "VU0-top")
    check(vu0, "\tvoid SQC2() {", 1, "VU0-site")
    check(vu0, "\t\tmemWrite128(addr, VU0.VF[_Ft_].UQ);", 1, "VU0-call")
    vu0 = vu0.replace('#include "Common.h"\n', '#include "Common.h"\n' + T53_TOP, 1)
    vu0 = vu0.replace("\tvoid SQC2() {", T53_DECL + "\tvoid SQC2() {", 1)
    vu0 = vu0.replace("\t\tmemWrite128(addr, VU0.VF[_Ft_].UQ);",
                      "\t\tmemWrite128(addr, VU0.VF[_Ft_].UQ);\n\t\tt53w_watch(addr, 16); // T53: ADDR-word watch (log-only).", 1)
    open(VU0, "w", encoding="utf-8").write(vu0)

    print("T53 hook applied: RI(5 fold/file/marker edits) + FPU(SWC1) + VU0(SQC2) ok")


if __name__ == "__main__":
    main()
