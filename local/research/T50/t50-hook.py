#!/usr/bin/env python3
"""T50 bounded log-only patch (pcsx2-g7, on top of the T49 tree).

EE-interpreter read watch on the two 16-byte VU1-microcode source windows
(EE 0x004349b8 and 0x00435bf8) during Select Character settled: the game
copies microcode from its library into a packet buffer with EE code (E40:
12,160 MPGs flowed inline, no REF tags, no constant in code), so the
question is which EE loads read those source bytes, from which pc, with
which registers.

Lines (emulog channel, unanchored grep `srcread |T50_'):
  srcread vsync=<n> addr=0x<phys> size=<4|8|16> pc=0x<guest pc> ra=0x<> fn=-
    a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x
    t0=%08x ... t9=%08x s0=%08x ... s7=%08x        (GPR low 32 bits at the load)
  T50_SRCREAD_FULL region=<0|1> vsync=<n>          (once per region at 64 hits)

Gate (T49 shape): /tmp/t50-arm seen + T48 window + dump-vsync gate
(g_t49_winstart >= 0, g_t48_vsync >= winstart). First 64 hits per region
then silent. Hooks live in the EE interpreter only (LW/LWU/LWL/LWR/LD/
LDL/LDR/LQ call-sites); under the EE recompiler the code never executes,
so default-off cost is zero there (one throttled arm-probe + a few
branches per interp load otherwise).

Hunks assert count==1 each, abort otherwise. Idempotent: aborts if T50
already applied.
"""
import sys

G = "/home/brad/pcsx2-g7/pcsx2"
RI = G + "/pcsx2/R5900OpcodeImpl.cpp"


def apply_after_once(text, find, add, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)
    return text.replace(find, find + add, 1)


def replace_once(text, find, repl, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)
    return text.replace(find, repl, 1)


T50_DECLS = r"""
// T50: srcread watch on the two 16-byte microcode source windows (log-only; EE interp only).
#include <cstdio>
extern std::atomic<int> g_t48_vsync; // T50: defined in GS.cpp (T48 vsync mirror).
extern std::atomic<bool> g_t48_window; // T50: defined in GS.cpp (T48 window flag).
extern std::atomic<int> g_t49_winstart; // T50: defined in GS.cpp (T49 winstart mirror).
bool g_t50_armed = false;
u32 g_t50_arm_ctr = 0;
u32 g_t50_hits0 = 0; // region 0 (EE 0x004349b8..0x004349c7) lines logged.
u32 g_t50_hits1 = 0; // region 1 (EE 0x00435bf8..0x00435c07) lines logged.
static bool t50_gate()
{
	if (!g_t50_armed)
	{
		if ((++g_t50_arm_ctr & 1023) != 0) return false;
		FILE* t50af = fopen("/tmp/t50-arm", "r");
		if (!t50af) return false;
		fclose(t50af);
		g_t50_armed = true;
	}
	if (!g_t48_window.load(std::memory_order_relaxed)) return false;
	int t50_ws = g_t49_winstart.load(std::memory_order_relaxed);
	int t50_vs = g_t48_vsync.load(std::memory_order_relaxed);
	return t50_ws >= 0 && t50_vs >= t50_ws;
}
// Log EE interp loads overlapping the two 16-byte source windows (first 64 hits per region).
void t50_read_watch(u32 vaddr, u32 size)
{
	if (!t50_gate()) return;
	u32 pbase = vaddr & 0x1fffffff;
	u32 lo = pbase & ~(size - 1);
	int region = -1;
	if (lo + size > 0x004349b8 && lo < 0x004349c8) region = 0;
	else if (lo + size > 0x00435bf8 && lo < 0x00435c08) region = 1;
	else if (pbase >= 0x004349b8 && pbase < 0x004349c8) region = 0;
	else if (pbase >= 0x00435bf8 && pbase < 0x00435c08) region = 1;
	else return;
	u32* cnt = (region == 0) ? &g_t50_hits0 : &g_t50_hits1;
	if (*cnt >= 64)
		return;
	(*cnt)++;
	if (*cnt == 64)
		Console.WriteLn("T50_SRCREAD_FULL region=%d vsync=%d", region, g_t48_vsync.load(std::memory_order_relaxed));
	Console.WriteLn("srcread vsync=%d addr=0x%x size=%u pc=0x%x ra=0x%x fn=- a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x t0=%08x t1=%08x t2=%08x t3=%08x t4=%08x t5=%08x t6=%08x t7=%08x t8=%08x t9=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x",
		g_t48_vsync.load(std::memory_order_relaxed), lo, size, cpuRegs.pc, cpuRegs.GPR.r[31].UL[0],
		cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0],
		cpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0],
		cpuRegs.GPR.r[8].UL[0], cpuRegs.GPR.r[9].UL[0], cpuRegs.GPR.r[10].UL[0], cpuRegs.GPR.r[11].UL[0],
		cpuRegs.GPR.r[12].UL[0], cpuRegs.GPR.r[13].UL[0], cpuRegs.GPR.r[14].UL[0], cpuRegs.GPR.r[15].UL[0],
		cpuRegs.GPR.r[24].UL[0], cpuRegs.GPR.r[25].UL[0],
		cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0],
		cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0], cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0]);
}
"""

T50_LW_FIND = (
    "\tu32 temp = memRead32(addr);\n"
    "\n"
    "\tif (!_Rt_) return;\n"
    "\tcpuRegs.GPR.r[_Rt_].SD[0] = (s32)temp;"
)
T50_LW_REPL = (
    "\tu32 temp = memRead32(addr);\n"
    "\n"
    "\tif (!_Rt_) return;\n"
    "\tt50_read_watch(addr, 4); // T50: srcread watch (log-only).\n"
    "\tcpuRegs.GPR.r[_Rt_].SD[0] = (s32)temp;"
)

T50_LWU_FIND = (
    "\tu32 temp = memRead32(addr);\n"
    "\n"
    "\tif (!_Rt_) return;\n"
    "\tcpuRegs.GPR.r[_Rt_].UD[0] = temp;"
)
T50_LWU_REPL = (
    "\tu32 temp = memRead32(addr);\n"
    "\n"
    "\tif (!_Rt_) return;\n"
    "\tt50_read_watch(addr, 4); // T50: srcread watch (log-only).\n"
    "\tcpuRegs.GPR.r[_Rt_].UD[0] = temp;"
)

T50_LWL_FIND = (
    "\tu32 mem = memRead32(addr & ~3);\n"
    "\n"
    "\tif (!_Rt_) return;\n"
    "\n"
    "\t// ensure the compiler does correct sign extension into 64 bits by using s32"
)
T50_LWL_ADD = (
    "\n"
    "\tt50_read_watch(addr, 4); // T50: srcread watch (log-only)."
)

T50_LWR_FIND = (
    "\tu32 mem = memRead32(addr & ~3);\n"
    "\n"
    "\tif (!_Rt_) return;\n"
    "\n"
    "\t// Use unsigned math here, and conditionally sign extend below, when needed."
)
T50_LWR_ADD = (
    "\n"
    "\tt50_read_watch(addr, 4); // T50: srcread watch (log-only)."
)

T50_LD_FIND = "\tcpuRegs.GPR.r[_Rt_].UD[0] = memRead64(addr);"
T50_LD_ADD = "\n\tt50_read_watch(addr, 8); // T50: srcread watch (log-only)."

T50_LDL_FIND = (
    "\tu64 mem = memRead64(addr & ~7);\n"
    "\n"
    "\tif( !_Rt_ ) return;"
)
T50_LDL_ADD = (
    "\n"
    "\tt50_read_watch(addr, 8); // T50: srcread watch (log-only)."
)

T50_LDR_FIND = (
    "\tu64 mem = memRead64(addr & ~7);\n"
    "\n"
    "\tif (!_Rt_) return;"
)
T50_LDR_ADD = (
    "\n"
    "\tt50_read_watch(addr, 8); // T50: srcread watch (log-only)."
)

T50_LQ_FIND = "\tmemRead128(addr & ~0xf, (u128*)gpr_GetWritePtr(_Rt_));"
T50_LQ_ADD = "\n\tt50_read_watch(addr, 16); // T50: srcread watch (log-only)."


def main():
    ri = open(RI, encoding="utf-8").read()
    assert "t50_read_watch" not in ri, "T50 already applied to R5900OpcodeImpl.cpp"
    ri = apply_after_once(ri, "#include <atomic>\n", T50_DECLS, "T50-D0")
    ri = replace_once(ri, T50_LW_FIND, T50_LW_REPL, "T50-LW")
    ri = replace_once(ri, T50_LWU_FIND, T50_LWU_REPL, "T50-LWU")
    ri = apply_after_once(ri, T50_LWL_FIND, T50_LWL_ADD, "T50-LWL")
    ri = apply_after_once(ri, T50_LWR_FIND, T50_LWR_ADD, "T50-LWR")
    ri = apply_after_once(ri, T50_LD_FIND, T50_LD_ADD, "T50-LD")
    ri = apply_after_once(ri, T50_LDL_FIND, T50_LDL_ADD, "T50-LDL")
    ri = apply_after_once(ri, T50_LDR_FIND, T50_LDR_ADD, "T50-LDR")
    ri = apply_after_once(ri, T50_LQ_FIND, T50_LQ_ADD, "T50-LQ")
    open(RI, "w", encoding="utf-8").write(ri)
    print("T50 hook applied: RI(9) ok")


if __name__ == "__main__":
    main()
