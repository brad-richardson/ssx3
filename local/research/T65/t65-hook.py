#!/usr/bin/env python3
# T65 hook: log-only taps on the T64 tree (validate every anchor, then write).
#  GSState.cpp  per-vsync PATH1 vertex box (xy/z) + on/off/straddle prim counts
#  GS.cpp       per-vsync T65_BOX line (armed by /tmp/t65-arm), VU dump request (/tmp/t65-vu-now)
#  Counters.cpp EE-thread vsync counter
#  VU1micro.cpp binary VF/VI/ACC + VU1 data memory (+ micro memory when it changed) at every
#               program start over 3 EE vsyncs per request
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/brad/pcsx2-g7/pcsx2/pcsx2"

EDITS = []


def edit(path, anchor, new, mode="after"):
    EDITS.append((path, anchor, new, mode))


# ---------------------------------------------------------------- GSState.cpp
edit("GS/GSState.cpp", "int g_t48_curpath = -1;\n", """// T65: per-vsync PATH1 box + prim classification (log-only; GS thread; armed per vsync by GS.cpp).
bool g_t65_on = false;
unsigned long long g_t65_n[8] = {}; // 0 p1 verts, 1 on, 2 off, 3 straddle, 4 adc prims, 5 non-p1 prims, 6 non-p1 verts, 7 zero-area (subset of 1-3)
int g_t65_vbox[4] = {0x7fffffff, -0x7fffffff, 0x7fffffff, -0x7fffffff}; // abs raw 12.4 x0 x1 y0 y1, all PATH1 verts
int g_t65_pbox[4] = {0x7fffffff, -0x7fffffff, 0x7fffffff, -0x7fffffff}; // XYOFFSET-relative 12.4, non-ADC PATH1 prims
unsigned int g_t65_z[2] = {0xffffffffu, 0u};
int g_t65_last[6] = {-1, -1, -1, -1, -1, -1}; // OFX OFY SCAX0 SCAX1 SCAY0 SCAY1 (last classified prim)
unsigned long long g_t65_ctxchg = 0; // classified prims whose offset/scissor differ from the previous one
""")

edit("GS/GSState.cpp", "\tvtx_buff.xy_tail = ++xy_tail;\n", """	// T65: PATH1 vertex box (every kicked vertex, ADC included).
	if (g_t65_on)
	{
		if (g_t48_curpath == 1)
		{
			const int t65x = m_v.XYZ.X, t65y = m_v.XYZ.Y;
			const unsigned int t65z = m_v.XYZ.Z;
			g_t65_n[0]++;
			if (t65x < g_t65_vbox[0]) g_t65_vbox[0] = t65x;
			if (t65x > g_t65_vbox[1]) g_t65_vbox[1] = t65x;
			if (t65y < g_t65_vbox[2]) g_t65_vbox[2] = t65y;
			if (t65y > g_t65_vbox[3]) g_t65_vbox[3] = t65y;
			if (t65z < g_t65_z[0]) g_t65_z[0] = t65z;
			if (t65z > g_t65_z[1]) g_t65_z[1] = t65z;
		}
		else
			g_t65_n[6]++;
	}
""")

edit("GS/GSState.cpp", "\t// Skip draws when scissor is out of range (i.e. bottom-right is less than top-left), since everything will get clipped.\n", """	// T65: classify each completed prim before PCSX2's cull (skip here = caller's ADC flag only).
	if (g_t65_on)
	{
		if (g_t48_curpath != 1)
			g_t65_n[5]++;
		else if (skip != 0)
			g_t65_n[4]++;
		else
		{
			const int t65ofx = static_cast<int>(m_context->XYOFFSET.OFX), t65ofy = static_cast<int>(m_context->XYOFFSET.OFY);
			int t65x0 = 0x7fffffff, t65x1 = -0x7fffffff, t65y0 = 0x7fffffff, t65y1 = -0x7fffffff;
			for (u32 t65k = 0; t65k < n; t65k++)
			{
				const GSVertex& t65v = (prim == GS_TRIANGLEFAN && t65k == 2) ? vtx_buff.buff[head] : vtx_buff.buff[tail - 1 - t65k];
				const int t65x = static_cast<int>(t65v.XYZ.X) - t65ofx, t65y = static_cast<int>(t65v.XYZ.Y) - t65ofy;
				if (t65x < t65x0) t65x0 = t65x;
				if (t65x > t65x1) t65x1 = t65x;
				if (t65y < t65y0) t65y0 = t65y;
				if (t65y > t65y1) t65y1 = t65y;
			}
			const int t65s[4] = {static_cast<int>(m_context->SCISSOR.SCAX0), static_cast<int>(m_context->SCISSOR.SCAX1),
				static_cast<int>(m_context->SCISSOR.SCAY0), static_cast<int>(m_context->SCISSOR.SCAY1)};
			const int t65sx0 = t65s[0] * 16, t65sx1 = (t65s[1] + 1) * 16, t65sy0 = t65s[2] * 16, t65sy1 = (t65s[3] + 1) * 16;
			if (t65x1 < t65sx0 || t65x0 > t65sx1 || t65y1 < t65sy0 || t65y0 > t65sy1)
				g_t65_n[2]++;
			else if (t65x0 >= t65sx0 && t65x1 <= t65sx1 && t65y0 >= t65sy0 && t65y1 <= t65sy1)
				g_t65_n[1]++;
			else
				g_t65_n[3]++;
			if (t65x0 == t65x1 || t65y0 == t65y1)
				g_t65_n[7]++;
			if (t65x0 < g_t65_pbox[0]) g_t65_pbox[0] = t65x0;
			if (t65x1 > g_t65_pbox[1]) g_t65_pbox[1] = t65x1;
			if (t65y0 < g_t65_pbox[2]) g_t65_pbox[2] = t65y0;
			if (t65y1 > g_t65_pbox[3]) g_t65_pbox[3] = t65y1;
			if (g_t65_last[0] >= 0 && (g_t65_last[0] != t65ofx || g_t65_last[1] != t65ofy || g_t65_last[2] != t65s[0] || g_t65_last[3] != t65s[1] || g_t65_last[4] != t65s[2] || g_t65_last[5] != t65s[3]))
				g_t65_ctxchg++;
			g_t65_last[0] = t65ofx; g_t65_last[1] = t65ofy;
			g_t65_last[2] = t65s[0]; g_t65_last[3] = t65s[1]; g_t65_last[4] = t65s[2]; g_t65_last[5] = t65s[3];
		}
	}

""", mode="before")

# ---------------------------------------------------------------- GS.cpp
edit("GS/GS.cpp", "extern unsigned long long g_t48_bytes[4]; // T48: defined in GSState.cpp, per-index byte counts.\n", """extern bool g_t65_on; // T65: defined in GSState.cpp (box/classification taps).
extern unsigned long long g_t65_n[8];
extern int g_t65_vbox[4];
extern int g_t65_pbox[4];
extern unsigned int g_t65_z[2];
extern int g_t65_last[6];
extern unsigned long long g_t65_ctxchg;
extern std::atomic<int> g_t65_vu_req; // T65: defined in VU1micro.cpp (VU1 dump requests).
""")

edit("GS/GS.cpp", "\t\tg_t48_vsync.store(g8_vsync_index, std::memory_order_relaxed);\n", """		{ // T65: per-vsync box line while /tmp/t65-arm exists; /tmp/t65-vu-now requests one VU1 dump (consumed).
			if (g_t65_on)
			{
				Console.WriteLn("T65_BOX vsync=%d p1_verts=%llu vx=%.4f..%.4f vy=%.4f..%.4f z=%u..%u prims_on=%llu off=%llu strad=%llu zeroarea=%llu adc=%llu px=%.4f..%.4f py=%.4f..%.4f of=%d,%d sc=%d..%d,%d..%d ctxchg=%llu np1_prims=%llu np1_verts=%llu",
					g8_vsync_index, g_t65_n[0], g_t65_vbox[0] / 16.0, g_t65_vbox[1] / 16.0, g_t65_vbox[2] / 16.0, g_t65_vbox[3] / 16.0,
					g_t65_z[0], g_t65_z[1], g_t65_n[1], g_t65_n[2], g_t65_n[3], g_t65_n[7], g_t65_n[4],
					g_t65_pbox[0] / 16.0, g_t65_pbox[1] / 16.0, g_t65_pbox[2] / 16.0, g_t65_pbox[3] / 16.0,
					g_t65_last[0] >= 0 ? g_t65_last[0] / 16 : -1, g_t65_last[1] >= 0 ? g_t65_last[1] / 16 : -1,
					g_t65_last[2], g_t65_last[3], g_t65_last[4], g_t65_last[5], g_t65_ctxchg, g_t65_n[5], g_t65_n[6]);
			}
			for (int t65i = 0; t65i < 8; t65i++) g_t65_n[t65i] = 0;
			g_t65_vbox[0] = g_t65_pbox[0] = 0x7fffffff; g_t65_vbox[1] = g_t65_pbox[1] = -0x7fffffff;
			g_t65_vbox[2] = g_t65_pbox[2] = 0x7fffffff; g_t65_vbox[3] = g_t65_pbox[3] = -0x7fffffff;
			g_t65_z[0] = 0xffffffffu; g_t65_z[1] = 0u; g_t65_ctxchg = 0;
			FILE* t65af = fopen("/tmp/t65-arm", "r");
			g_t65_on = (t65af != nullptr);
			if (t65af) fclose(t65af);
			FILE* t65qf = fopen("/tmp/t65-vu-now", "r");
			if (t65qf)
			{
				fclose(t65qf);
				remove("/tmp/t65-vu-now");
				const int t65r = g_t65_vu_req.fetch_add(1, std::memory_order_relaxed) + 1;
				Console.WriteLn("T65_VU_REQ vsync=%d n=%d", g8_vsync_index, t65r);
			}
		} // T65
""")

# ---------------------------------------------------------------- Counters.cpp
edit("Counters.cpp", "static __fi void VSyncStart(u64 sCycle)\n{\n", """	g_t65_ee_vsync++; // T65: EE-thread vsync counter (VU1 dump windows).
""")
edit("Counters.cpp", "static __fi void VSyncStart(u64 sCycle)\n", """u32 g_t65_ee_vsync = 0; // T65: read by VU1micro.cpp.
""", mode="before")

# ---------------------------------------------------------------- VU1micro.cpp
edit("VU1micro.cpp", "void vu1ExecMicro(u32 addr)\n", r"""// T65: one binary dump per request: every VU1 program start over 3 EE vsyncs (log-only, sync VU1 only).
std::atomic<int> g_t65_vu_req{0};
extern u32 g_t65_ee_vsync; // T65: defined in Counters.cpp.
static int t65_served = 0;
static std::FILE* t65_f = nullptr;
static u32 t65_from = 0, t65_to = 0, t65_seq = 0, t65_last_mfnv = 0;
static u32 t65_fnv(const u8* p, u32 n)
{
	u32 h = 2166136261u;
	for (u32 i = 0; i < n; i++) { h ^= p[i]; h *= 16777619u; }
	return h;
}
static void t65_vu_dump()
{
	const int req = g_t65_vu_req.load(std::memory_order_relaxed);
	if (!t65_f && req > t65_served)
	{
		t65_served = req;
		t65_from = g_t65_ee_vsync + 1;
		t65_to = t65_from + 3;
		t65_seq = 0;
		t65_last_mfnv = 0;
		char path[128];
		std::snprintf(path, sizeof(path), "/home/brad/pcsx2-g7/t65-vu1-%d.bin", t65_served);
		t65_f = std::fopen(path, "wb");
		Console.WriteLn("T65_VU_ARM n=%d ee_vsync=%u from=%u to=%u gs_vsync=%d path=%s ok=%d", t65_served, g_t65_ee_vsync, t65_from, t65_to,
			g_t48_vsync.load(std::memory_order_relaxed), path, t65_f ? 1 : 0);
	}
	if (!t65_f)
		return;
	const u32 ev = g_t65_ee_vsync;
	if (ev >= t65_to)
	{
		std::fclose(t65_f);
		t65_f = nullptr;
		Console.WriteLn("T65_VU_DONE n=%d records=%u ee_vsync=%u", t65_served, t65_seq, ev);
		return;
	}
	if (ev < t65_from)
		return;
	const u32 dfnv = t65_fnv(VU1.Mem, 0x4000);
	const u32 mfnv = t65_fnv(VU1.Micro, 0x4000);
	const u32 has_micro = (mfnv != t65_last_mfnv) ? 1u : 0u;
	t65_last_mfnv = mfnv;
	const u32 tpc = VU1.VI[REG_TPC].UL;
	u32 hdr[20] = {0x52353654u, t65_seq, ev, static_cast<u32>(g_t48_vsync.load(std::memory_order_relaxed)), tpc,
		static_cast<u32>(VU1.cycle), static_cast<u32>(VU1.cycle >> 32), static_cast<u32>(g_t48_vu_xg), static_cast<u32>(g_t48_vu_xg >> 32),
		vif1Regs.top, vif1Regs.tops, vif1Regs.itop, vif1Regs.itops, vif1Regs.base, vif1Regs.ofst, vif1Regs.stat.DBF ? 1u : 0u,
		dfnv, mfnv, has_micro, 0u};
	u32 regs[32 + 128 + 4];
	for (u32 i = 0; i < 32; i++) regs[i] = VU1.VI[i].UL;
	for (u32 i = 0; i < 32; i++)
		for (u32 j = 0; j < 4; j++) regs[32 + i * 4 + j] = VU1.VF[i].UL[j];
	for (u32 j = 0; j < 4; j++) regs[160 + j] = VU1.ACC.UL[j];
	std::fwrite(hdr, sizeof(hdr), 1, t65_f);
	std::fwrite(regs, sizeof(regs), 1, t65_f);
	std::fwrite(VU1.Mem, 0x4000, 1, t65_f);
	if (has_micro)
		std::fwrite(VU1.Micro, 0x4000, 1, t65_f);
	Console.WriteLn("T65_VUREC n=%d seq=%u ee_vsync=%u gs_vsync=%d tpc=0x%x dfnv=%08x mfnv=%08x micro=%u xg=%llu tops=0x%x itops=0x%x top=0x%x itop=0x%x base=0x%x ofst=0x%x dbf=%u",
		t65_served, t65_seq, ev, g_t48_vsync.load(std::memory_order_relaxed), tpc, dfnv, mfnv, has_micro, g_t48_vu_xg,
		vif1Regs.tops, vif1Regs.itops, vif1Regs.top, vif1Regs.itop, vif1Regs.base, vif1Regs.ofst, vif1Regs.stat.DBF ? 1u : 0u);
	t65_seq++;
}

""", mode="before")

edit("VU1micro.cpp", "\tg_t48_vu_win = g_t48_window.load(std::memory_order_relaxed);\n", """	t65_vu_dump(); // T65
""")

# ---------------------------------------------------------------- apply
texts = {}
for path, anchor, new, mode in EDITS:
    full = f"{ROOT}/{path}"
    if full not in texts:
        texts[full] = open(full).read()
        if "T65" in texts[full]:
            sys.exit(f"ABORT: {path} already carries T65 text")
    t = texts[full]
    c = t.count(anchor)
    if c != 1:
        sys.exit(f"ABORT: anchor count {c} in {path}: {anchor[:60]!r}")
    texts[full] = t.replace(anchor, anchor + new if mode == "after" else new + anchor)
for full, t in texts.items():
    open(full, "w").write(t)
    print("wrote", full)
print("T65_HOOK_OK edits=%d" % len(EDITS))
