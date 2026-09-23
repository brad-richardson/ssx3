#!/usr/bin/env python3
"""T54 hook (pcsx2-g7, on top of the T53 working tree = HEAD 9056c083 + T51/T53 hooks).

At EE pc 0x363cf4 (the `jal func_364CD0` in the render-list walker
sub_00363C20): per vsync, count calls by a1 (mode 0-15); for the first 8 per
mode log the record address s3 + its first 4 words:
  drec  vsync=<n> mode=<m> count=<c>
  drecs vsync=<n> mode=<m> addr=0x<x> w0=0x.. w1=0x.. w2=0x.. w3=0x..
Inside the interpreter JAL(), cpuRegs.pc == instr_pc+4, so the site is
cpuRegs.pc == 0x363cf8. Hook fires at JAL entry (before _SetLink), so ra is
the walker's return (0x363cfc expected). Flush of the previous vsync's drec
lines happens on the first call of the next vsync (the kill-cut final vsync
keeps its drecs lines but no drec summary: noted, recoverable by counting).

Plus a mirror-folded store watch for the mode-6 producer hunt, driven by
/tmp/t54-watch (record-word addresses from the census capture):
  dprod vsync=<n> addr=0x<> value=0x<> pc=0x<> ra=0x<> a0..a3 v0 v1 t0..t9 s0..s7 tu=<ri|swc1|sqc2>
First 64 per (address, TU). RI (9 integer store sites, next to the t51w calls)
+ SWC1 + SQC2, same folded-mask scheme as T53 (0x0fffffff).

Log-only. Idempotent: aborts if applied. Asserts every anchor count.
"""

import re

RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"
FPU = "/home/brad/pcsx2-g7/pcsx2/pcsx2/FPU.cpp"
VU0 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU0.cpp"
INTERP = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Interpreter.cpp"


def check(text, find, want, name):
    n = text.count(find)
    assert n == want, "%s: anchor count=%d, want %d" % (name, n, want)


def rep1(text, old, new, name):
    check(text, old, 1, name)
    return text.replace(old, new, 1)


T54_INTERP_TOP = """
// T54: draw-record census includes/externs (log-only).
#include <atomic>
#include <cstdio>
#include <cstdlib>
extern std::atomic<int> g_t48_vsync; // T54: defined in GS.cpp (T48 vsync mirror).
"""

T54_CENSUS = """
// T54: draw-record census at the walker jal (log-only; site pc==0x363cf8 inside JAL).
static int g_t54_lastvs = -1;
static u32 g_t54_cnt[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
static u32 g_t54_seen[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
static void t54_census(u32 a1, u32 s3)
{
\tint t54_vs = g_t48_vsync.load(std::memory_order_relaxed);
\tif (t54_vs != g_t54_lastvs)
\t{
\t\tif (g_t54_lastvs >= 0)
\t\t{
\t\t\tfor (u32 m = 0; m < 16; m++)
\t\t\t{
\t\t\t\tif (g_t54_cnt[m]) Console.WriteLn("drec vsync=%d mode=%u count=%u", g_t54_lastvs, m, g_t54_cnt[m]);
\t\t\t}
\t\t}
\t\tfor (u32 m = 0; m < 16; m++) { g_t54_cnt[m] = 0; g_t54_seen[m] = 0; }
\t\tg_t54_lastvs = t54_vs;
\t}
\tu32 t54_mode = a1 & 15u;
\tg_t54_cnt[t54_mode]++;
\tif (g_t54_seen[t54_mode] < 8)
\t{
\t\tg_t54_seen[t54_mode]++;
\t\tConsole.WriteLn("drecs vsync=%d mode=%u addr=0x%x w0=0x%x w1=0x%x w2=0x%x w3=0x%x",
\t\t\tt54_vs, t54_mode, s3, memRead32(s3), memRead32(s3 + 4), memRead32(s3 + 8), memRead32(s3 + 12));
\t}
}
"""

T54W_DECL = """
// T54: mirror-folded record-word producer watch (log-only; addresses from /tmp/t54-watch).
#define T54W_MAXA 64
static u32 g_t54w_addr[T54W_MAXA];
static u32 g_t54w_naddr = 0;
static u32 g_t54w_hits[T54W_MAXA];
static bool g_t54w_armed = false;
static u32 g_t54w_arm_ctr = 0;
static bool t54w_arm()
{
\tif (g_t54w_armed) return true;
\tif ((++g_t54w_arm_ctr & 1023) != 0) return false; // EE interp thread only.
\tFILE* t54wf = fopen("/tmp/t54-watch", "r");
\tif (!t54wf) return false;
\tchar t54line[64];
\twhile (g_t54w_naddr < T54W_MAXA && fgets(t54line, sizeof(t54line), t54wf))
\t{
\t\tu32 a = (u32)strtoul(t54line, nullptr, 0);
\t\tif (a == 0) continue;
\t\tg_t54w_addr[g_t54w_naddr] = (a & 0x0fffffff) & ~3u; // T54: fold 0x00/0x20/0x30/0x80 mirrors (E41/T53).
\t\tg_t54w_hits[g_t54w_naddr] = 0;
\t\tg_t54w_naddr++;
\t}
\tfclose(t54wf);
\tg_t54w_armed = true;
\tConsole.WriteLn("T54W_ARMED naddr=%u", g_t54w_naddr);
\treturn true;
}
// EE store overlapping a watched record word (post-write word + 24 GPRs, first 64 per address per TU).
static void t54w_watch(u32 vaddr, u32 size)
{
\tif (!t54w_arm()) return;
\tu32 pbase = vaddr & 0x0fffffff; // T54: fold mirrors (E41/T53).
\tu32 lo = pbase;
\tu32 hi = pbase + size;
\tint t54_vs = g_t48_vsync.load(std::memory_order_relaxed);
\tfor (u32 i = 0; i < g_t54w_naddr; i++)
\t{
\t\tu32 w = g_t54w_addr[i];
\t\tif (w + 4 <= lo || w >= hi) continue;
\t\tu32 k = g_t54w_hits[i]++;
\t\tif (k >= 64)
\t\t{
\t\t\tif (k == 64) Console.WriteLn("T54W_CAP vsync=%d addr=0x%x", t54_vs, w);
\t\t\tcontinue;
\t\t}
\t\tConsole.WriteLn("dprod vsync=%d addr=0x%x value=0x%x pc=0x%x ra=0x%x a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x t0=%08x t1=%08x t2=%08x t3=%08x t4=%08x t5=%08x t6=%08x t7=%08x t8=%08x t9=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x tu=T54TU",
\t\t\tt54_vs, w, memRead32(w), cpuRegs.pc, cpuRegs.GPR.r[31].UL[0],
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


def tu_decl(tu):
    return T54W_DECL.replace("tu=T54TU", "tu=" + tu)


def main():
    interp = open(INTERP, encoding="utf-8").read()
    ri = open(RI, encoding="utf-8").read()
    fpu = open(FPU, encoding="utf-8").read()
    vu0 = open(VU0, encoding="utf-8").read()

    assert "t54_census" not in interp, "T54 census already in Interpreter.cpp"
    assert "t54w_watch" not in ri, "T54 already in R5900OpcodeImpl.cpp"
    assert "t54w_watch" not in fpu, "T54 already in FPU.cpp"
    assert "t54w_watch" not in vu0, "T54 already in VU0.cpp"
    assert "/tmp/t54-watch" not in ri, "T54 watch already in R5900OpcodeImpl.cpp"
    assert "T53W_ARMED" in ri, "T53 baseline missing in R5900OpcodeImpl.cpp"
    assert "t53w_watch(addr, 4)" in fpu, "T53 baseline missing in FPU.cpp"
    assert "t53w_watch(addr, 16)" in vu0, "T53 baseline missing in VU0.cpp"

    # --- Interpreter.cpp: census ---
    check(interp, '#include "Common.h"\n', 1, "Interp-top")
    check(interp, "void JAL()\n{", 1, "Interp-JAL")
    interp = interp.replace('#include "Common.h"\n',
                            '#include "Common.h"\n' + T54_INTERP_TOP, 1)
    interp = interp.replace("void JAL()\n{",
                            T54_CENSUS + "void JAL()\n{", 1)
    interp = interp.replace(
        "void JAL()\n{\n\t// 0x3563b8 is the start address",
        "void JAL()\n{\n\tif (cpuRegs.pc == 0x363cf8) t54_census(cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[19].UL[0]); // T54: walker-jal census (log-only; jal @0x363cf4, a1=mode, s3=record).\n\t// 0x3563b8 is the start address",
        1)
    open(INTERP, "w", encoding="utf-8").write(interp)

    # --- R5900OpcodeImpl.cpp: T54W decl + 9 call sites ---
    check(ri, "static void t51w_watch(u32 vaddr, u32 size)", 1, "RI-decl-anchor")
    ri = rep1(ri, "static void t51w_watch(u32 vaddr, u32 size)",
              tu_decl("ri") + "static void t51w_watch(u32 vaddr, u32 size)",
              "RI-decl")
    lines = ri.split("\n")
    ncall = 0
    for idx, ln in enumerate(lines):
        m = re.match(r"^(\s*)t51w_watch\(([^)]+)\);(.*)$", ln)
        if m and "static void" not in ln:
            indent, args, tail = m.groups()
            lines[idx] = ln + "\n" + indent + "t54w_watch(%s); // T54: record-word producer watch (log-only)." % args
            ncall += 1
    assert ncall == 9, "RI call sites=%d, want 9" % ncall
    ri = "\n".join(lines)
    open(RI, "w", encoding="utf-8").write(ri)

    # --- FPU.cpp: SWC1 ---
    check(fpu, "void SWC1() {", 1, "FPU-site")
    check(fpu, "\tt53w_watch(addr, 4); // T53: ADDR-word watch (log-only).", 1, "FPU-call")
    fpu = fpu.replace("void SWC1() {", tu_decl("swc1") + "void SWC1() {", 1)
    fpu = fpu.replace("\tt53w_watch(addr, 4); // T53: ADDR-word watch (log-only).",
                      "\tt53w_watch(addr, 4); // T53: ADDR-word watch (log-only).\n\tt54w_watch(addr, 4); // T54: record-word producer watch (log-only).", 1)
    open(FPU, "w", encoding="utf-8").write(fpu)

    # --- VU0.cpp: SQC2 ---
    check(vu0, "\tvoid SQC2() {", 1, "VU0-site")
    check(vu0, "\t\tt53w_watch(addr, 16); // T53: ADDR-word watch (log-only).", 1, "VU0-call")
    vu0 = vu0.replace("\tvoid SQC2() {", tu_decl("sqc2") + "\tvoid SQC2() {", 1)
    vu0 = vu0.replace("\t\tt53w_watch(addr, 16); // T53: ADDR-word watch (log-only).",
                      "\t\tt53w_watch(addr, 16); // T53: ADDR-word watch (log-only).\n\t\tt54w_watch(addr, 16); // T54: record-word producer watch (log-only).", 1)
    open(VU0, "w", encoding="utf-8").write(vu0)

    print("T54 hook applied: Interp(census) + RI(decl+9) + FPU(SWC1) + VU0(SQC2) ok")


if __name__ == "__main__":
    main()
