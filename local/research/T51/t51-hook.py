#!/usr/bin/env python3
"""T51 patch (pcsx2-g7, on top of the T48-T50 working tree): render-DMA
thread state-machine trace at Select Character settled.

Over 5 consecutive vsyncs (winstart..winstart+4, latched per-TU at gate open):
(1) st: every EE interp store overlapping 0x6214E0-0x621520 (struct +0x5A80..+0x5AC0):
    `st vsync=<n> addr=0x<> value=0x<> pc=0x<> ra=0x<> intc=<0/1>`
    (post-write word read-back; intc = CP0 Status.EXL at store time)
(2) sema: every SignalSema/iSignalSema/WaitSema/PollSema (0x42-0x45) whose a0
    equals *(0x6214E0+0x28/0x2C) or the orchestrator's +0x4C word (=s0+0x5ACC):
    `sema vsync=<n> pc=0x<> ra=0x<> call=<name> id=<n> m=+0x<>`
    plus one `semaid vsync=<n> w28=0x<> w2c=0x<> w4c=0x<>` sample per vsync.
    Hook sits at SYSCALL entry (sema calls fall through to the real BIOS).
(3) irq: every mask-enabled (will-deliver) INTC/DMAC request:
    `irq vsync=<n> cause=0x<> ch=<intc|dmac>:<n> handler=0x<>`
    (cause = INTC_STAT / DMAC_STAT; handler = interrupted EE pc at request;
    the game's registered handler runs later via the BIOS dispatcher.)
(4) D1 kicks: T50's dmareg hook already in tree (touched by the same arm/free
    files); gsreg bonus: GIF A+D SIGNAL/FINISH/LABEL events:
    `gsreg vsync=<n> reg=<SIGNAL|FINISH|LABEL>`
Gate per TU (self-contained, no cross-TU deps): /tmp/t51-arm + (/tmp/t51-free
OR the T48 window+winstart fallback on the EE/Hw side; free-only on GS side).
Caps: st 4000, sema 512, irq 1500, gs 256 (each +CAP once). All log-only.

Hunks assert count==1 each, abort otherwise. Idempotent: aborts if applied.
"""
import sys

G = "/home/brad/pcsx2-g7/pcsx2"
RI = G + "/pcsx2/R5900OpcodeImpl.cpp"
HW = G + "/pcsx2/Hw.cpp"
GS = G + "/pcsx2/GS/GSState.cpp"


def check(text, find, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)


def apply_after_line(text, find, add, name):
    """Insert add (with caller's indent) right after the line containing find."""
    check(text, find, name)
    i = text.index(find)
    eol = text.index("\n", i) + 1
    return text[:eol] + add + text[eol:]


def insert_before_line_with(text, substr, add, name):
    """Insert add before the single line containing substr, same indent."""
    lines = text.split("\n")
    idx = [i for i, ln in enumerate(lines) if substr in ln]
    assert len(idx) == 1, "%s: line count=%d, want 1" % (name, len(idx))
    i = idx[0]
    indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
    lines.insert(i, indent + add)
    return "\n".join(lines)


def replace_last_in_span(text, start_mark, add_after, name):
    """Within the function starting at start_mark, append add_after after the
    last line that is exactly '\\t);' (the multi-line memWrite close)."""
    si = text.index(start_mark)
    ei = text.index("\n}\n", si) + len("\n}\n")
    span = text[si:ei]
    n = span.count("\n\t);")
    assert n == 1, "%s: close count=%d, want 1" % (name, n)
    span2 = span.replace("\n\t);", "\n\t);\n" + add_after, 1)
    return text[:si] + span2 + text[ei:]


# ---------------- EE interp side (R5900OpcodeImpl.cpp) ----------------
RI_DECLS = r"""
// T51: render-DMA state-machine trace (log-only; EE interp stores + sema syscalls).
#include <atomic>
#include <cstdio>
extern std::atomic<int> g_t48_vsync; // T51: defined in GS.cpp (T48 vsync mirror).
extern std::atomic<bool> g_t48_window; // T51: defined in GS.cpp (T48 window flag).
extern std::atomic<int> g_t49_winstart; // T51: defined in GS.cpp (T49 winstart mirror).
std::atomic<int> g_t51e_winstart{-1}; // T51: first gated vsync (this TU).
std::atomic<bool> g_t51e_armed{false};
std::atomic<bool> g_t51e_free{false};
std::atomic<u32> g_t51e_arm_ctr{0};
std::atomic<u32> g_t51e_n_st{0};
std::atomic<u32> g_t51e_n_sema{0};
std::atomic<int> g_t51e_semaid_vs{-1};
static bool t51e_arm_free()
{
	if (!g_t51e_armed.load(std::memory_order_relaxed))
	{
		if ((g_t51e_arm_ctr.fetch_add(1, std::memory_order_relaxed) & 1023) != 0) return false;
		FILE* t51af = fopen("/tmp/t51-arm", "r");
		if (!t51af) return false;
		fclose(t51af);
		g_t51e_armed.store(true, std::memory_order_relaxed);
	}
	if (!g_t51e_free.load(std::memory_order_relaxed))
	{
		FILE* t51ff = fopen("/tmp/t51-free", "r");
		if (!t51ff)
		{
			if (!g_t48_window.load(std::memory_order_relaxed)) return false;
			int t51_ws = g_t49_winstart.load(std::memory_order_relaxed);
			int t51_vs = g_t48_vsync.load(std::memory_order_relaxed);
			if (!(t51_ws >= 0 && t51_vs >= t51_ws)) return false;
		}
		else
		{
			fclose(t51ff);
			g_t51e_free.store(true, std::memory_order_relaxed);
		}
	}
	int t51_exp = -1;
	int t51_vs = g_t48_vsync.load(std::memory_order_relaxed);
	if (g_t51e_winstart.compare_exchange_strong(t51_exp, t51_vs, std::memory_order_relaxed))
		Console.WriteLn("T51_WINDOW tu=ee vsync=%d", t51_vs);
	return true;
}
// Open only for the first 5 gated vsyncs.
static bool t51e_gate()
{
	if (!t51e_arm_free()) return false;
	int t51_ws = g_t51e_winstart.load(std::memory_order_relaxed);
	int t51_vs = g_t48_vsync.load(std::memory_order_relaxed);
	return t51_ws >= 0 && t51_vs >= t51_ws && t51_vs <= t51_ws + 4;
}
// EE store overlapping the render-DMA struct window 0x6214E0-0x621520 (post-write words).
static void t51e_store_watch(u32 vaddr, u32 size)
{
	if (!t51e_gate()) return;
	u32 pbase = vaddr & 0x1fffffff;
	u32 lo = pbase;
	u32 hi = pbase + size;
	if (hi <= 0x6214e0 || lo >= 0x621521) return;
	u32 lane0 = lo & ~3u;
	if (lane0 < 0x6214e0) lane0 = 0x6214e0;
	u32 laneN = (hi + 3) & ~3u;
	if (laneN > 0x621524) laneN = 0x621524;
	int t51_vs = g_t48_vsync.load(std::memory_order_relaxed);
	int t51_intc = cpuRegs.CP0.n.Status.b.EXL ? 1 : 0;
	for (u32 lane = lane0; lane < laneN; lane += 4)
	{
		u32 k = g_t51e_n_st.fetch_add(1, std::memory_order_relaxed);
		if (k == 4000) { Console.WriteLn("T51_ST_CAP vsync=%d", t51_vs); return; }
		if (k > 4000) return;
		Console.WriteLn("st vsync=%d addr=0x%x value=0x%x pc=0x%x ra=0x%x intc=%d",
			t51_vs, lane, memRead32(lane), cpuRegs.pc, cpuRegs.GPR.r[31].UL[0], t51_intc);
	}
}
// SignalSema/iSignalSema/WaitSema/PollSema at SYSCALL entry (they run the real BIOS).
static void t51e_syscall_watch(u8 call)
{
	const char* t51cn = nullptr;
	if (call == 0x42) t51cn = "SignalSema";
	else if (call == 0x43) t51cn = "iSignalSema";
	else if (call == 0x44) t51cn = "WaitSema";
	else if (call == 0x45) t51cn = "PollSema";
	else return;
	if (!t51e_gate()) return;
	u32 k = g_t51e_n_sema.fetch_add(1, std::memory_order_relaxed);
	int t51_vs = g_t48_vsync.load(std::memory_order_relaxed);
	if (k == 512) { Console.WriteLn("T51_SEMA_CAP vsync=%d", t51_vs); return; }
	if (k > 512) return;
	u32 t51a0 = cpuRegs.GPR.n.a0.UL[0];
	u32 t51w28 = memRead32(0x621508);
	u32 t51w2c = memRead32(0x62150c);
	u32 t51w4c = memRead32(0x62152c);
	if (g_t51e_semaid_vs.load(std::memory_order_relaxed) != t51_vs)
	{
		g_t51e_semaid_vs.store(t51_vs, std::memory_order_relaxed);
		Console.WriteLn("semaid vsync=%d w28=0x%x w2c=0x%x w4c=0x%x", t51_vs, t51w28, t51w2c, t51w4c);
	}
	const char* t51m = nullptr;
	if (t51a0 == t51w28) t51m = "+0x28";
	else if (t51a0 == t51w2c) t51m = "+0x2c";
	else if (t51a0 == t51w4c) t51m = "+0x4c";
	else return;
	Console.WriteLn("sema vsync=%d pc=0x%x ra=0x%x call=%s id=%u m=%s",
		t51_vs, cpuRegs.pc, cpuRegs.GPR.r[31].UL[0], t51cn, t51a0, t51m);
}
"""

# ---------------- Hw side (Hw.cpp: INTC/DMAC request tap) ----------------
HW_DECLS = r"""
// T51: INTC/DMAC will-deliver request tap (log-only; EE/VU thread, atomics).
#include <atomic>
#include <cstdio>
extern std::atomic<int> g_t48_vsync; // T51: defined in GS.cpp (T48 vsync mirror).
extern std::atomic<bool> g_t48_window; // T51: defined in GS.cpp (T48 window flag).
extern std::atomic<int> g_t49_winstart; // T51: defined in GS.cpp (T49 winstart mirror).
std::atomic<int> g_t51h_winstart{-1}; // T51: first gated vsync (this TU).
std::atomic<bool> g_t51h_armed{false};
std::atomic<bool> g_t51h_free{false};
std::atomic<u32> g_t51h_arm_ctr{0};
std::atomic<u32> g_t51h_n_irq{0};
static bool t51h_gate()
{
	if (!g_t51h_armed.load(std::memory_order_relaxed))
	{
		if ((g_t51h_arm_ctr.fetch_add(1, std::memory_order_relaxed) & 1023) != 0) return false;
		FILE* t51af = fopen("/tmp/t51-arm", "r");
		if (!t51af) return false;
		fclose(t51af);
		g_t51h_armed.store(true, std::memory_order_relaxed);
	}
	if (!g_t51h_free.load(std::memory_order_relaxed))
	{
		FILE* t51ff = fopen("/tmp/t51-free", "r");
		if (!t51ff)
		{
			if (!g_t48_window.load(std::memory_order_relaxed)) return false;
			int t51_ws = g_t49_winstart.load(std::memory_order_relaxed);
			int t51_vs = g_t48_vsync.load(std::memory_order_relaxed);
			if (!(t51_ws >= 0 && t51_vs >= t51_ws)) return false;
		}
		else
		{
			fclose(t51ff);
			g_t51h_free.store(true, std::memory_order_relaxed);
		}
	}
	int t51_exp = -1;
	int t51_vs = g_t48_vsync.load(std::memory_order_relaxed);
	if (g_t51h_winstart.compare_exchange_strong(t51_exp, t51_vs, std::memory_order_relaxed))
		Console.WriteLn("T51_WINDOW tu=hw vsync=%d", t51_vs);
	int t51_ws = g_t51h_winstart.load(std::memory_order_relaxed);
	return t51_ws >= 0 && t51_vs >= t51_ws && t51_vs <= t51_ws + 4;
}
// Mask-enabled INTC (src 0) / DMAC (src 1) request: cause bits, channel, interrupted pc.
static void t51h_irq_watch(int t51src, int t51n)
{
	u32 t51stat, t51mask;
	const char* t51sn;
	if (t51src == 0) { t51stat = psHu32(INTC_STAT); t51mask = psHu32(INTC_MASK); t51sn = "intc"; }
	else { t51stat = psHu32(DMAC_STAT); t51mask = (u32)psHu16(DMAC_STAT + 2); t51sn = "dmac"; }
	if (!(t51mask & (1u << t51n))) return; // masked: pends, not delivered.
	if (!t51h_gate()) return;
	u32 k = g_t51h_n_irq.fetch_add(1, std::memory_order_relaxed);
	int t51_vs = g_t48_vsync.load(std::memory_order_relaxed);
	if (k == 1500) { Console.WriteLn("T51_IRQ_CAP vsync=%d", t51_vs); return; }
	if (k > 1500) return;
	Console.WriteLn("irq vsync=%d cause=0x%x ch=%s:%d handler=0x%x",
		t51_vs, t51stat, t51sn, t51n, cpuRegs.pc);
}
"""

# ---------------- GS side (GSState.cpp: SIGNAL/FINISH/LABEL tap) ----------------
GS_DECLS = r"""
// T51: GS SIGNAL/FINISH/LABEL event tap (log-only; GS thread, free-gate only).
#include <atomic>
#include <cstdio>
extern std::atomic<int> g_t48_vsync; // T51: defined in GS.cpp (T48 vsync mirror).
std::atomic<int> g_t51g_winstart{-1}; // T51: first gated vsync (this TU).
std::atomic<bool> g_t51g_armed{false};
std::atomic<bool> g_t51g_free{false};
std::atomic<u32> g_t51g_arm_ctr{0};
std::atomic<u32> g_t51g_n_gs{0};
static bool t51g_gate()
{
	if (!g_t51g_armed.load(std::memory_order_relaxed))
	{
		if ((g_t51g_arm_ctr.fetch_add(1, std::memory_order_relaxed) & 1023) != 0) return false;
		FILE* t51af = fopen("/tmp/t51-arm", "r");
		if (!t51af) return false;
		fclose(t51af);
		g_t51g_armed.store(true, std::memory_order_relaxed);
	}
	if (!g_t51g_free.load(std::memory_order_relaxed))
	{
		FILE* t51ff = fopen("/tmp/t51-free", "r");
		if (!t51ff) return false;
		fclose(t51ff);
		g_t51g_free.store(true, std::memory_order_relaxed);
	}
	int t51_exp = -1;
	int t51_vs = g_t48_vsync.load(std::memory_order_relaxed);
	if (g_t51g_winstart.compare_exchange_strong(t51_exp, t51_vs, std::memory_order_relaxed))
		Console.WriteLn("T51_WINDOW tu=gs vsync=%d", t51_vs);
	int t51_ws = g_t51g_winstart.load(std::memory_order_relaxed);
	return t51_ws >= 0 && t51_vs >= t51_ws && t51_vs <= t51_ws + 4;
}
static void t51g_ad(u32 t51ad)
{
	const char* t51rn = (t51ad == 0x60) ? "SIGNAL" : (t51ad == 0x61) ? "FINISH" : (t51ad == 0x62) ? "LABEL" : nullptr;
	if (!t51rn) return;
	if (!t51g_gate()) return;
	u32 k = g_t51g_n_gs.fetch_add(1, std::memory_order_relaxed);
	int t51_vs = g_t48_vsync.load(std::memory_order_relaxed);
	if (k == 256) { Console.WriteLn("T51_GS_CAP vsync=%d", t51_vs); return; }
	if (k > 256) return;
	Console.WriteLn("gsreg vsync=%d reg=%s", t51_vs, t51rn);
}
"""


def main():
    ri = open(RI, encoding="utf-8").read()
    hw = open(HW, encoding="utf-8").read()
    gs = open(GS, encoding="utf-8").read()
    assert "t51e_store_watch" not in ri, "T51 already applied to RI"
    assert "t51h_irq_watch" not in hw, "T51 already applied to HW"
    assert "t51g_ad" not in gs, "T51 already applied to GS"
    # Validate every anchor before writing anything.
    check(ri, "// T50: srcread watch on the two 16-byte microcode source windows (log-only; EE interp only).\n", "T51-RI0")
    check(ri, "\tmemWrite8(addr, cpuRegs.GPR.r[_Rt_].UC[0]);\n", "T51-RI-SB")
    check(ri, "\tmemWrite16(addr, cpuRegs.GPR.r[_Rt_].US[0]);\n", "T51-RI-SH")
    check(ri, "  memWrite32(addr, cpuRegs.GPR.r[_Rt_].UL[0]);\n", "T51-RI-SW")
    check(ri, "    memWrite64(addr,cpuRegs.GPR.r[_Rt_].UD[0]);\n", "T51-RI-SD")
    check(ri, "\tmemWrite64(addr & ~7, mem);\n", "T51-RI-SDL")
    check(ri, "\tmemWrite64(addr & ~7, mem );\n", "T51-RI-SDR")
    check(ri, "\tmemWrite128(addr & ~0xf, cpuRegs.GPR.r[_Rt_].UQ);\n", "T51-RI-SQ")
    assert ri.count("void SWL()") == 1, "SWL span"
    assert ri.count("void SWR()") == 1, "SWR span"
    check(ri, '\tBIOS_LOG("Bios call: %s (%x) pc=%x a0=%x", R5900::bios[call], call, cpuRegs.pc, cpuRegs.GPR.n.a0.UL[0]);\n', "T51-RI-SC")
    check(hw, '#include "Hardware.h"\n', "T51-HW0")
    check(hw, "\tpsHu32(INTC_STAT) |= 1<<n;\n", "T51-HW1")
    check(hw, "\tpsHu32(DMAC_STAT) |= 1<<n;\n", "T51-HW2")
    check(gs, '#include "common/Console.h"\n', "T51-GS0")
    for sub, nm in [
        ("(this->*m_fpGIFRegHandlers[r->A_D.ADDR & 0x7F])(&r->r);", "T51-GS1"),
        ("(this->*m_fpGIFRegHandlers[((GIFPackedReg*)mem)->A_D.ADDR & 0x7F])(&((GIFPackedReg*)mem)->r);", "T51-GS2"),
        ("(this->*m_fpGIFRegHandlers[path.GetReg() & 0x7F])((GIFReg*)mem);", "T51-GS3"),
    ]:
        nlines = sum(1 for ln in gs.split("\n") if sub in ln)
        assert nlines == 1, "%s: line count=%d, want 1" % (nm, nlines)

    ri = apply_after_line(ri, "// T50: srcread watch on the two 16-byte microcode source windows (log-only; EE interp only).\n",
                           RI_DECLS, "T51-RI0")
    ri = apply_after_line(ri, "\tmemWrite8(addr, cpuRegs.GPR.r[_Rt_].UC[0]);\n",
                           "\tt51e_store_watch(addr, 1); // T51: struct-window store watch (log-only).\n", "T51-RI-SB")
    ri = apply_after_line(ri, "\tmemWrite16(addr, cpuRegs.GPR.r[_Rt_].US[0]);\n",
                           "\tt51e_store_watch(addr, 2); // T51: struct-window store watch (log-only).\n", "T51-RI-SH")
    ri = apply_after_line(ri, "  memWrite32(addr, cpuRegs.GPR.r[_Rt_].UL[0]);\n",
                           "  t51e_store_watch(addr, 4); // T51: struct-window store watch (log-only).\n", "T51-RI-SW")
    ri = apply_after_line(ri, "    memWrite64(addr,cpuRegs.GPR.r[_Rt_].UD[0]);\n",
                           "    t51e_store_watch(addr, 8); // T51: struct-window store watch (log-only).\n", "T51-RI-SD")
    ri = apply_after_line(ri, "\tmemWrite64(addr & ~7, mem);\n",
                           "\tt51e_store_watch(addr & ~7, 8); // T51: struct-window store watch (log-only).\n", "T51-RI-SDL")
    ri = apply_after_line(ri, "\tmemWrite64(addr & ~7, mem );\n",
                           "\tt51e_store_watch(addr & ~7, 8); // T51: struct-window store watch (log-only).\n", "T51-RI-SDR")
    ri = apply_after_line(ri, "\tmemWrite128(addr & ~0xf, cpuRegs.GPR.r[_Rt_].UQ);\n",
                           "\tt51e_store_watch(addr & ~0xf, 16); // T51: struct-window store watch (log-only).\n", "T51-RI-SQ")
    ri = replace_last_in_span(ri, "void SWL()",
                               "\tt51e_store_watch(addr & ~3, 4); // T51: struct-window store watch (log-only).\n", "T51-RI-SWL")
    ri = replace_last_in_span(ri, "void SWR()",
                               "\tt51e_store_watch(addr & ~3, 4); // T51: struct-window store watch (log-only).\n", "T51-RI-SWR")
    ri = apply_after_line(ri, '\tBIOS_LOG("Bios call: %s (%x) pc=%x a0=%x", R5900::bios[call], call, cpuRegs.pc, cpuRegs.GPR.n.a0.UL[0]);\n',
                           "\tt51e_syscall_watch(call); // T51: sema syscall watch (log-only).\n", "T51-RI-SC")
    open(RI, "w", encoding="utf-8").write(ri)

    hw = apply_after_line(hw, '#include "Hardware.h"\n', HW_DECLS, "T51-HW0")
    hw = apply_after_line(hw, "\tpsHu32(INTC_STAT) |= 1<<n;\n",
                           "\tt51h_irq_watch(0, n); // T51: INTC request tap (log-only).\n", "T51-HW1")
    hw = apply_after_line(hw, "\tpsHu32(DMAC_STAT) |= 1<<n;\n",
                           "\tt51h_irq_watch(1, n); // T51: DMAC request tap (log-only).\n", "T51-HW2")
    open(HW, "w", encoding="utf-8").write(hw)

    gs = apply_after_line(gs, '#include "common/Console.h"\n', GS_DECLS, "T51-GS0")
    gs = insert_before_line_with(gs, "(this->*m_fpGIFRegHandlers[r->A_D.ADDR & 0x7F])(&r->r);",
                                  "{ t51g_ad(r->A_D.ADDR & 0x7F); } // T51: SIGNAL/FINISH/LABEL tap (log-only).", "T51-GS1")
    gs = insert_before_line_with(gs, "(this->*m_fpGIFRegHandlers[((GIFPackedReg*)mem)->A_D.ADDR & 0x7F])(&((GIFPackedReg*)mem)->r);",
                                  "{ t51g_ad(((GIFPackedReg*)mem)->A_D.ADDR & 0x7F); } // T51: SIGNAL/FINISH/LABEL tap (log-only).", "T51-GS2")
    gs = insert_before_line_with(gs, "(this->*m_fpGIFRegHandlers[path.GetReg() & 0x7F])((GIFReg*)mem);",
                                  "{ t51g_ad(path.GetReg() & 0x7F); } // T51: SIGNAL/FINISH/LABEL tap (log-only).", "T51-GS3")
    open(GS, "w", encoding="utf-8").write(gs)

    print("T51 hook applied: RI(11) + HW(3) + GS(4) ok")


if __name__ == "__main__":
    main()
