#!/usr/bin/env python3
"""T51 redirect patch (pcsx2-g7, on top of the T51 working tree):
E40 Part-6 showed the recomp kicks both chains every vsync with all CALLs at
0x435bd0; PCSX2 must have some CALLs at 0x434990. Two additions (log-only):

(1) ctag: at SC settled, dump every VIF1 chain tag processed in [V,V+1]
    (V = first gated vsync) in E40's format:
    `ctag tag_at=0x<> id=<> qwc=<> addr=0x<> tte=<16hex>`
    (tag_at = tadr at setup; id/qwc = tag word 0; addr = tag word 1 raw;
    tte = tag words 2,3 in memory order). Hook sits next to T50's tag tap in
    vif1SetupTransfer (chain path only; MFIFO drain excluded by design).
    Cap 4000 + T51C_CAP once.
(2) tagaddrwrite: whole-(statefile-)boot EE-store watch on the ADDR words
    (tag_at+4) of CALL tags pointing at 0x434990. Addresses come from a file
    (/tmp/t51-watch, hex one per line, <=16) written after capture A, armed
    from load:
    `tagaddrwrite vsync=<n> addr=0x<> value=0x<> pc=0x<> ra=0x<> a0=..a3
      v0 v1 t0..t9 s0..s7` (post-write word + 28 GPRs), first 64 per address
    (+T51W_CAP per address). No vsync window (whole boot). Interp only.
Keeps all T51 st/sema/irq/gsreg/dmareg taps as built.

Hunks assert counts, abort otherwise. Idempotent: aborts if applied.
"""

RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"
V1D = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Vif1_Dma.cpp"


def check(text, find, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)


def apply_after_once(text, find, add, name):
    check(text, find, name)
    return text.replace(find, find + add, 1)


V1D_DECLS = r"""
// T51c: SC chain-tag dump (log-only; VIF1 chain path, dump vsyncs V..V+1).
#include <atomic>
#include <cstdio>
extern std::atomic<int> g_t48_vsync; // T51c: defined in GS.cpp (T48 vsync mirror).
extern std::atomic<bool> g_t48_window; // T51c: defined in GS.cpp (T48 window flag).
extern std::atomic<int> g_t49_winstart; // T51c: defined in GS.cpp (T49 winstart mirror).
std::atomic<int> g_t51c_winstart{-1}; // T51c: first gated vsync (this TU).
std::atomic<bool> g_t51c_armed{false};
std::atomic<bool> g_t51c_free{false};
std::atomic<u32> g_t51c_arm_ctr{0};
std::atomic<u32> g_t51c_n{0};
static bool t51c_gate_vsync(int* t51vp)
{
	if (!g_t51c_armed.load(std::memory_order_relaxed))
	{
		if ((g_t51c_arm_ctr.fetch_add(1, std::memory_order_relaxed) & 1023) != 0) return false;
		FILE* t51af = fopen("/tmp/t51-arm", "r");
		if (!t51af) return false;
		fclose(t51af);
		g_t51c_armed.store(true, std::memory_order_relaxed);
	}
	if (!g_t51c_free.load(std::memory_order_relaxed))
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
			g_t51c_free.store(true, std::memory_order_relaxed);
		}
	}
	int t51_exp = -1;
	int t51_vs = g_t48_vsync.load(std::memory_order_relaxed);
	if (g_t51c_winstart.compare_exchange_strong(t51_exp, t51_vs, std::memory_order_relaxed))
		Console.WriteLn("T51C_WINDOW vsync=%d", t51_vs);
	int t51_ws = g_t51c_winstart.load(std::memory_order_relaxed);
	if (!(t51_ws >= 0 && t51_vs >= t51_ws && t51_vs <= t51_ws + 1)) return false;
	*t51vp = t51_vs;
	return true;
}
// One VIF1 chain tag at setup time, E40 ctag format (id/qwc = word 0, addr = word 1 raw, tte = words 2,3).
static void t51c_tag(u32 t51_tag_at, tDMA_TAG* t51_ptag)
{
	int t51_vs = 0;
	if (!t51c_gate_vsync(&t51_vs)) return;
	u32 k = g_t51c_n.fetch_add(1, std::memory_order_relaxed);
	if (k == 4000) { Console.WriteLn("T51C_CAP vsync=%d", t51_vs); return; }
	if (k > 4000) return;
	u32 w0 = t51_ptag[0]._u32, w1 = t51_ptag[1]._u32, w2 = t51_ptag[2]._u32, w3 = t51_ptag[3]._u32;
	Console.WriteLn("ctag tag_at=0x%x id=%u qwc=%u addr=0x%x tte=%08x%08x",
		t51_tag_at, t51_ptag->ID, w0 & 0xffff, w1, w2, w3);
	(void)t51_vs;
}
"""

RI_WATCH = r"""
// T51w: whole-boot ADDR-word write watch (log-only; addresses from /tmp/t51-watch).
#include <cstdlib>
#define T51W_MAXA 16
static u32 g_t51w_addr[T51W_MAXA];
static u32 g_t51w_naddr = 0;
static u32 g_t51w_hits[T51W_MAXA];
static bool g_t51w_armed = false;
static u32 g_t51w_arm_ctr = 0;
static bool t51w_arm()
{
	if (g_t51w_armed) return true;
	if ((++g_t51w_arm_ctr & 1023) != 0) return false; // EE interp thread only.
	FILE* t51wf = fopen("/tmp/t51-watch", "r");
	if (!t51wf) return false;
	char t51line[64];
	while (g_t51w_naddr < T51W_MAXA && fgets(t51line, sizeof(t51line), t51wf))
	{
		u32 a = (u32)strtoul(t51line, nullptr, 0);
		if (a == 0) continue;
		g_t51w_addr[g_t51w_naddr] = a & ~3u;
		g_t51w_hits[g_t51w_naddr] = 0;
		g_t51w_naddr++;
	}
	fclose(t51wf);
	g_t51w_armed = true;
	Console.WriteLn("T51W_ARMED naddr=%u", g_t51w_naddr);
	return true;
}
// EE store overlapping a watched ADDR word (post-write word + 28 GPRs, first 64 per address).
static void t51w_watch(u32 vaddr, u32 size)
{
	if (!t51w_arm()) return;
	u32 pbase = vaddr & 0x1fffffff;
	u32 lo = pbase;
	u32 hi = pbase + size;
	int t51_vs = g_t48_vsync.load(std::memory_order_relaxed);
	for (u32 i = 0; i < g_t51w_naddr; i++)
	{
		u32 w = g_t51w_addr[i];
		if (w + 4 <= lo || w >= hi) continue;
		u32 k = g_t51w_hits[i]++;
		if (k >= 64)
		{
			if (k == 64) Console.WriteLn("T51W_CAP vsync=%d addr=0x%x", t51_vs, w);
			continue;
		}
		Console.WriteLn("tagaddrwrite vsync=%d addr=0x%x value=0x%x pc=0x%x ra=0x%x a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x t0=%08x t1=%08x t2=%08x t3=%08x t4=%08x t5=%08x t6=%08x t7=%08x t8=%08x t9=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x",
			t51_vs, w, memRead32(w), cpuRegs.pc, cpuRegs.GPR.r[31].UL[0],
			cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0],
			cpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0],
			cpuRegs.GPR.r[8].UL[0], cpuRegs.GPR.r[9].UL[0], cpuRegs.GPR.r[10].UL[0], cpuRegs.GPR.r[11].UL[0],
			cpuRegs.GPR.r[12].UL[0], cpuRegs.GPR.r[13].UL[0], cpuRegs.GPR.r[14].UL[0], cpuRegs.GPR.r[15].UL[0],
			cpuRegs.GPR.r[24].UL[0], cpuRegs.GPR.r[25].UL[0],
			cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0],
			cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0], cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0]);
	}
}
"""

T51W_CALL = " t51w_watch(%s, %s); // T51w: ADDR-word watch (log-only)."


def main():
    ri = open(RI, encoding="utf-8").read()
    v1d = open(V1D, encoding="utf-8").read()
    assert "t51c_tag" not in v1d, "T51c already applied to Vif1_Dma.cpp"
    assert "t51w_watch" not in ri, "T51w already applied to R5900OpcodeImpl.cpp"
    # Vif1_Dma anchors.
    check(v1d, '#include "Vif_Dynarec.h"\n', "T51c-VD0")
    check(v1d, "\tt50b_tag_tap(vif1ch.tadr, ptag->ID, vif1ch.chcr.MOD); // T50b: chain-tag tap (log-only).\n", "T51c-VD1")
    # RI anchors: decl append point + the 9 T51 store-watch call lines.
    check(ri, "std::atomic<int> g_t51e_semaid_vs{-1};\n", "T51w-RI0")
    sites = [
        ("\tt51e_store_watch(addr, 1); // T51: struct-window store watch (log-only).\n", 1, "T51w-SB", "addr", "1"),
        ("\tt51e_store_watch(addr, 2); // T51: struct-window store watch (log-only).\n", 1, "T51w-SH", "addr", "2"),
        ("  t51e_store_watch(addr, 4); // T51: struct-window store watch (log-only).\n", 1, "T51w-SW", "addr", "4"),
        ("    t51e_store_watch(addr, 8); // T51: struct-window store watch (log-only).\n", 1, "T51w-SD", "addr", "8"),
        ("\tt51e_store_watch(addr & ~7, 8); // T51: struct-window store watch (log-only).\n", 2, "T51w-SDL/R", "addr & ~7", "8"),
        ("\tt51e_store_watch(addr & ~0xf, 16); // T51: struct-window store watch (log-only).\n", 1, "T51w-SQ", "addr & ~0xf", "16"),
        ("\tt51e_store_watch(addr & ~3, 4); // T51: struct-window store watch (log-only).\n", 2, "T51w-SWL/R", "addr & ~3", "4"),
    ]
    for find, want, nm, _a, _s in sites:
        n = ri.count(find)
        assert n == want, "%s: anchor count=%d, want %d" % (nm, n, want)

    v1d = apply_after_once(v1d, '#include "Vif_Dynarec.h"\n', V1D_DECLS, "T51c-VD0")
    v1d = apply_after_once(v1d,
        "\tt50b_tag_tap(vif1ch.tadr, ptag->ID, vif1ch.chcr.MOD); // T50b: chain-tag tap (log-only).\n",
        "\t{ t51c_tag(vif1ch.tadr, ptag); } // T51c: chain-tag dump (log-only).\n", "T51c-VD1")
    open(V1D, "w", encoding="utf-8").write(v1d)

    ri = apply_after_once(ri, "std::atomic<int> g_t51e_semaid_vs{-1};\n", RI_WATCH, "T51w-RI0")
    for find, want, nm, a, s in sites:
        # preserve the call line's own indent:
        indent = find[: len(find) - len(find.lstrip())]
        ri = ri.replace(find, find + indent + (T51W_CALL % (a, s)).strip() + "\n")
    open(RI, "w", encoding="utf-8").write(ri)

    print("T51 redirect hook applied: V1D(2) + RI(1 decl + 9 watch calls) ok")


if __name__ == "__main__":
    main()
