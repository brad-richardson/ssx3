#!/usr/bin/env python3
"""T66 hook (pcsx2-g7, on the T65 tree): camera-object quaternion watch + object dump. Log-only, one TU.

- t66 store/DMA watch on phys 0x00bc5950..0x00bc595f (the quaternion at object 0x00bc5920 + 0x30), via the
  existing T58/T59 fold (t58_store_watch / t58_dma_watch, EE interpreter stores incl. SWC1/SQC2):
  first 32 writes as full `t66w` lines (pc, at=pc-4 when it holds cpuRegs.code, code, ra, a0-a3 v0 v1 s0-s7,
  the 4 quaternion words after the write); SWC1 adds `t66f` (fpr0-31 + ACC), SQC2 adds `t66v` (VF[ft] + VF00-31);
  after the cap, up to 64 `t66chg` lines when the quaternion value changes; `t66cen` per-vsync writer census.
- /tmp/t66-dump (checked at most once per GS vsync mirror): dump object 0x00bc5920..0x00bc599f on 3 consecutive
  vsyncs (`t66obj`), and once scan EE RAM for the T65 SC camera qw0 words and for (0x3f3504f3, 0x3f3504f3) pairs
  (`t66scan`).
"""
import sys

RI = sys.argv[1] if len(sys.argv) > 1 else "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"

ANCHOR_FN = "void t58_store_watch(u32 vaddr, u32 size)\n{\n\tt59_maybe_dump(); // T59: end-dump gate.\n"
NEW_FN = r"""// T66: camera-object quaternion watch (phys 0x00bc5950..0x00bc595f) + object dump (log-only).
#include "VU.h" // T66: VU0 regs for SQC2 lines.
#include <cstring>
static u32 g_t66_n = 0, g_t66_chg = 0;
static u32 g_t66_prev[4] = {0, 0, 0, 0};
static bool g_t66_prev_ok = false;
struct t66_pcn { u32 pc; u32 n; u32 q[4]; };
static t66_pcn g_t66_cen[64];
static int g_t66_cen_n = 0, g_t66_cen_vs = -1;
static void t66_cen_flush()
{
	if (g_t66_cen_n <= 0) return;
	static char lb[8192];
	int o = snprintf(lb, sizeof(lb), "t66cen vsync=%d", g_t66_cen_vs);
	for (int i = 0; i < g_t66_cen_n && o < 7900; i++)
		o += snprintf(lb + (u32)o, sizeof(lb) - (u32)o, " pc=0x%x:n=%u:q=%08x,%08x,%08x,%08x", g_t66_cen[i].pc, g_t66_cen[i].n,
			g_t66_cen[i].q[0], g_t66_cen[i].q[1], g_t66_cen[i].q[2], g_t66_cen[i].q[3]);
	Console.WriteLn("%s", lb);
	g_t66_cen_n = 0;
}
static float t66_f(u32 u) { float f; memcpy(&f, &u, 4); return f; }
static void t66_emit(const char* via, u32 vaddr, u32 src)
{
	const int vs = g_t48_vsync.load(std::memory_order_relaxed);
	u32 q[4];
	for (int i = 0; i < 4; i++) q[i] = memRead32(0x80bc5950u + 4u * (u32)i);
	if (vs != g_t66_cen_vs) { t66_cen_flush(); g_t66_cen_vs = vs; }
	int k;
	for (k = 0; k < g_t66_cen_n; k++) if (g_t66_cen[k].pc == cpuRegs.pc) break;
	if (k == g_t66_cen_n && g_t66_cen_n < 64) { g_t66_cen[k].pc = cpuRegs.pc; g_t66_cen[k].n = 0; g_t66_cen_n++; }
	if (k < g_t66_cen_n) { g_t66_cen[k].n++; memcpy(g_t66_cen[k].q, q, sizeof(q)); }
	const bool chg = !g_t66_prev_ok || memcmp(q, g_t66_prev, sizeof(q)) != 0;
	memcpy(g_t66_prev, q, sizeof(q)); g_t66_prev_ok = true;
	const bool full = g_t66_n < 32;
	if (!full && !(chg && g_t66_chg < 64)) return;
	if (full) g_t66_n++; else g_t66_chg++;
	const u32 code = cpuRegs.code, pc = cpuRegs.pc;
	const u32 at = (memRead32(pc - 4) == code) ? pc - 4 : 0;
	Console.WriteLn("%s vsync=%d via=%s vaddr=0x%x src=0x%x pc=0x%x at=0x%x code=%08x ra=0x%x q=%08x,%08x,%08x,%08x qf=%.7g,%.7g,%.7g,%.7g a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x sp=%08x",
		full ? "t66w" : "t66chg", vs, via, vaddr, src, pc, at, code, cpuRegs.GPR.r[31].UL[0], q[0], q[1], q[2], q[3],
		t66_f(q[0]), t66_f(q[1]), t66_f(q[2]), t66_f(q[3]),
		cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0], cpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0],
		cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0], cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0],
		cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0], cpuRegs.GPR.r[29].UL[0]);
	const u32 op = code >> 26, ft = (code >> 16) & 0x1f;
	if (via[0] == 's' && op == 0x39) // SWC1
	{
		static char lb[1024];
		int o = snprintf(lb, sizeof(lb), "t66f vsync=%d ft=%u acc=%08x", vs, ft, fpuRegs.ACC.UL);
		for (int i = 0; i < 32; i++) o += snprintf(lb + (u32)o, sizeof(lb) - (u32)o, " f%d=%08x", i, fpuRegs.fpr[i].UL);
		Console.WriteLn("%s", lb);
	}
	else if (via[0] == 's' && op == 0x3e) // SQC2
	{
		static char lb[2048];
		int o = snprintf(lb, sizeof(lb), "t66v vsync=%d ft=%u acc=%08x,%08x,%08x,%08x", vs, ft, VU0.ACC.UL[0], VU0.ACC.UL[1], VU0.ACC.UL[2], VU0.ACC.UL[3]);
		for (int i = 0; i < 32; i++)
			o += snprintf(lb + (u32)o, sizeof(lb) - (u32)o, " vf%d=%08x,%08x,%08x,%08x", i, VU0.VF[i].UL[0], VU0.VF[i].UL[1], VU0.VF[i].UL[2], VU0.VF[i].UL[3]);
		Console.WriteLn("%s", lb);
	}
}
static int g_t66_gate_vs = -1;
static int g_t66_left = -1;
static void t66_maybe_dump() // T66: /tmp/t66-dump -> 3 vsyncs of object words + one RAM scan (<=1 fopen per vsync).
{
	const int vs = g_t48_vsync.load(std::memory_order_relaxed);
	if (vs == g_t66_gate_vs) return;
	g_t66_gate_vs = vs;
	if (g_t66_left == 0) return;
	if (g_t66_left < 0)
	{
		FILE* f = fopen("/tmp/t66-dump", "r");
		if (!f) return;
		fclose(f);
		g_t66_left = 3;
		static const u32 cam[4] = {0xbf093f99u, 0x00000000u, 0x3380419au, 0x33800000u};
		int ncam = 0, nq = 0;
		for (u32 a = 0; a + 16 <= 0x02000000u; a += 4)
		{
			const u32 w = memRead32(0x80000000u | a);
			if (w == cam[0] && ncam < 32 && memRead32(0x80000000u | (a + 4)) == cam[1] && memRead32(0x80000000u | (a + 8)) == cam[2] && memRead32(0x80000000u | (a + 12)) == cam[3])
			{
				ncam++;
				Console.WriteLn("t66scan vsync=%d kind=scqw0 addr=0x%08x", vs, a);
			}
			if (w == 0x3f3504f3u && nq < 64 && memRead32(0x80000000u | (a + 4)) == 0x3f3504f3u)
			{
				nq++;
				Console.WriteLn("t66scan vsync=%d kind=qpair addr=0x%08x prev2=%08x,%08x", vs, a, memRead32(0x80000000u | (a - 8)), memRead32(0x80000000u | (a - 4)));
			}
		}
		Console.WriteLn("t66scan vsync=%d done scqw0=%d qpair=%d", vs, ncam, nq);
	}
	g_t66_left--;
	for (u32 r = 0; r < 8; r++)
	{
		const u32 a = 0x80bc5920u + 16u * r;
		const u32 w0 = memRead32(a), w1 = memRead32(a + 4), w2 = memRead32(a + 8), w3 = memRead32(a + 12);
		Console.WriteLn("t66obj vsync=%d off=0x%02x %08x %08x %08x %08x (%.7g %.7g %.7g %.7g)", vs, 16u * r, w0, w1, w2, w3, t66_f(w0), t66_f(w1), t66_f(w2), t66_f(w3));
	}
	if (g_t66_left == 0) { t66_cen_flush(); Console.WriteLn("t66obj_done vsync=%d t66w=%u t66chg=%u", vs, g_t66_n, g_t66_chg); }
}
"""

ANCHOR_CALL = "\tu32 hi = lo + size;\n\tt61_apc_tick(g_t48_vsync.load(std::memory_order_relaxed)); // T61: flush on change.\n"
NEW_CALL = "\tif (lo < 0x00bc5960u && hi > 0x00bc5950u) t66_emit(\"store\", vaddr, 0); // T66: quaternion watch.\n"

ANCHOR_TOP = "\tt59_maybe_dump(); // T59: end-dump gate.\n\tu32 lo;\n"
NEW_TOP = "\tt66_maybe_dump(); // T66: object dump gate.\n"

ANCHOR_DMA = "\tu32 end = base + bytes;\n\tt60_dma_tpl(host, base, end - base); // T60: template-word watch (log-only).\n"
NEW_DMA = "\tif ((base & 0x01FFFFFFu) < 0x00bc5960u && (base & 0x01FFFFFFu) + bytes > 0x00bc5950u) t66_emit(via, base, src); // T66: DMA into the quaternion.\n"


def main():
    body = open(RI, encoding="utf-8").read()
    assert "t66_" not in body, "T66 already applied"
    for name, a in (("fn", ANCHOR_FN), ("call", ANCHOR_CALL), ("top", ANCHOR_TOP), ("dma", ANCHOR_DMA)):
        n = body.count(a)
        assert n == 1, f"{name}: anchor count {n}"
    body = body.replace(ANCHOR_FN, NEW_FN + ANCHOR_FN, 1)
    body = body.replace(ANCHOR_CALL, ANCHOR_CALL + NEW_CALL, 1)
    body = body.replace(ANCHOR_TOP, ANCHOR_TOP + NEW_TOP, 1)
    body = body.replace(ANCHOR_DMA, ANCHOR_DMA + NEW_DMA, 1)
    open(RI, "w", encoding="utf-8").write(body)
    print("T66_HOOK_OK anchors=4")


main()
