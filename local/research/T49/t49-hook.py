#!/usr/bin/env python3
"""T49 bounded log-only patch (pcsx2-g7, on top of the T48 tree).

For the FIRST MSCAL at PCSX2 start_pc 0x8, 0x2 and 0x257 at/after the T48
dump vsync (Select Character settled, T48 Capture A settle point), trace in
E37 line formats (byte PCs = PCSX2 unit x 8):
  0. vi-entry : all 16 VU1 VI regs at program entry: `vi-entry vi00=<4hex> ... vi15=<4hex>`.
  1. vumem : full 16 KB VU1 data memory at program start, one line per qword:
     `vumem <row-dec> <w0> <w1> <w2> <w3>` (hex, 8 digits, x..w).
  2. vif   : every VIF1 command since the previous MSCAL:
     `vif <cmd-name> num=<> addr=<eff-row> fmt=<> usn=<> mask=<hex> cl=<> wl=<> ...`
     (field order matches E37; T49-only tail: code/flg/top).
  3. pair  : every executed pair until the 4th arrival at byte PC 0x418
     (entry + 3 full loop iterations + the arrival pair), then stop
     (0x8/0x2); the 0x257 trace instead runs to its E-bit:
     `pair pc=0x<byte-pc> up=<hex> lo=<hex> <disasm> | vi ... | vf ... | rd ... | wr ...`
     VI in 16-bit hex, only changed regs; rd = pre-state rows, wr = post-state.
  4. vi-exit (0x257 only): all 16 VI at its E-bit: `vi-exit vsync=<> start_pc=0x257 pairs=<> vi00=...`.

Hunks assert count==1 each, abort otherwise. Idempotent: aborts if T49
already applied. Behavior: counters + gated logs only; no renderer, EE,
timing or content change. Interpreter-only tracing (hooks live in the
interpreter files); under microVU only the vumem/vif dump would fire.
"""
import sys

G = "/home/brad/pcsx2-g7/pcsx2"
GS = G + "/pcsx2/GS/GS.cpp"
V1 = G + "/pcsx2/VU1micro.cpp"
VI = G + "/pcsx2/VU1microInterp.cpp"
VO = G + "/pcsx2/VUops.cpp"
VT = G + "/pcsx2/Vif_Transfer.cpp"
VC = G + "/pcsx2/Vif_Codes.cpp"


def apply_after_once(text, find, add, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)
    return text.replace(find, find + add, 1)


def replace_once(text, find, repl, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)
    return text.replace(find, repl, 1)


T49_V1_DECLS = r"""
// T49: entry-trace of the first MSCAL at start_pc 0x8/0x2 (+0x257, see below).
// Log-only; armed by /tmp/t49-arm + T48 window + dump-vsync gate; interp only.
#include <cstdio>
extern std::atomic<int> g_t49_winstart; // T49: defined in GS.cpp, mirrors t48_winstart.
bool g_t49_armed = false;
bool g_t49_done8 = false;
bool g_t49_done2 = false;
bool g_t49_done257 = false;
bool g_t49_pair_active = false;
bool g_t49_stop_on_ebit = false; // true for the 0x257 trace: pairs run to E-bit, not to the 4th arrival at 0x418.
bool g_t49_exit_armed = false; // true while the traced 0x257 program may still reach its E-bit (for the vi-exit line).
u32 g_t49_startpc = 0;
u32 g_t49_arrivals = 0;
u32 g_t49_pairs = 0;
u32 g_t49_vi[32];
u32 g_t49_vf[32][4];
u8 g_t49_mem[16384];
u32 g_t49_touch[16];
u32 g_t49_ntouch = 0;
struct t49_vifent { u32 code; u32 cl; u32 wl; u32 mask; u32 tops; u32 itops; u32 d[8]; u32 nd; u32 seq; };
t49_vifent g_t49_vif[4096];
u32 g_t49_vif_seq = 0;
u32 g_t49_vif_mark = 0;
u32 g_t49_vif_dumped = 0;
static const char* t49_vif_name(u32 cmd)
{
	switch (cmd)
	{
		case 0x00: return "NOP";
		case 0x01: return "STCYCL";
		case 0x02: return "OFFSET";
		case 0x03: return "BASE";
		case 0x04: return "ITOP";
		case 0x05: return "STMOD";
		case 0x06: return "MSKPATH3";
		case 0x07: return "MARK";
		case 0x10: return "FLUSHE";
		case 0x11: return "FLUSH";
		case 0x13: return "FLUSHA";
		case 0x14: return "MSCAL";
		case 0x15: return "MSCALF";
		case 0x17: return "MSCNT";
		case 0x20: return "STMASK";
		case 0x30: return "STROW";
		case 0x31: return "STCOL";
		case 0x4a: return "MPG";
		case 0x50: return "DIRECT";
		case 0x51: return "DIRECTHL";
		default: break;
	}
	if (cmd >= 0x60 && cmd <= 0x7f) return "UNPACK";
	return "NULL";
}
void t49_vif_record(u32 code, const u32* data, u32 avail, u32 cl, u32 wl, u32 mask, u32 tops, u32 itops)
{
	u32 cmd = (code >> 24) & 0x7f;
	u32 s = ++g_t49_vif_seq;
	t49_vifent* e = &g_t49_vif[s & 4095];
	e->code = code; e->cl = cl; e->wl = wl; e->mask = mask; e->tops = tops; e->itops = itops; e->nd = 0;
	u32 want = 0;
	if (cmd >= 0x60 && cmd <= 0x7f) want = 8;
	else if (cmd == 0x30 || cmd == 0x31) want = 4;
	else if (cmd == 0x20) want = 1;
	if (want > 0 && avail > 1)
	{
		u32 n = want < (avail - 1) ? want : (avail - 1);
		for (u32 i = 0; i < n; i++) e->d[i] = data[1 + i];
		e->nd = n;
	}
	e->seq = s;
}
void t49_vif_mark_fn() { g_t49_vif_mark = g_t49_vif_seq; }
"""

T49_V1_DUMP = r"""
	// T49: entry trace of the first MSCAL at start_pc 0x8/0x2/0x257 at/after the dump vsync (log-only).
	if (!g_t49_armed) { FILE* t49af = fopen("/tmp/t49-arm", "r"); if (t49af) { fclose(t49af); g_t49_armed = true; } }
	if (g_t49_pair_active)
	{
		Console.WriteLn("T49_END vsync=%d start_pc=0x%x pairs=%u reason=preempted", g_t48_vsync.load(std::memory_order_relaxed), g_t49_startpc, g_t49_pairs);
		g_t49_pair_active = false;
	}
	g_t49_exit_armed = false; // any new MSCAL supersedes a pending 0x257 vi-exit.
	{
		u32 t49_tpc = VU1.VI[REG_TPC].UL;
		int t49_vs = g_t48_vsync.load(std::memory_order_relaxed);
		int t49_ws = g_t49_winstart.load(std::memory_order_relaxed);
		bool t49_want = g_t49_armed && g_t48_window.load(std::memory_order_relaxed) && t49_ws >= 0 && t49_vs >= t49_ws
			&& ((t49_tpc == 0x8 && !g_t49_done8) || (t49_tpc == 0x2 && !g_t49_done2) || (t49_tpc == 0x257 && !g_t49_done257));
		if (t49_want)
		{
			if (t49_tpc == 0x8) g_t49_done8 = true; else if (t49_tpc == 0x2) g_t49_done2 = true; else g_t49_done257 = true;
			g_t49_startpc = t49_tpc; g_t49_arrivals = 0; g_t49_pairs = 0; g_t49_ntouch = 0;
			g_t49_stop_on_ebit = (t49_tpc == 0x257);
			g_t49_exit_armed = (t49_tpc == 0x257);
			Console.WriteLn("T49_BEGIN vsync=%d start_pc=0x%x bytepc=0x%x tops=0x%x itops=0x%x base=0x%x ofst=0x%x dbf=%d",
				t49_vs, t49_tpc, t49_tpc << 3,
				vif1Regs.tops, vif1Regs.itops, vif1Regs.base, vif1Regs.ofst, vif1Regs.stat.DBF ? 1 : 0);
			{
				char t49_viline[256];
				int t49_vo = snprintf(t49_viline, sizeof(t49_viline), "vi-entry");
				for (u32 i = 0; i < 16 && t49_vo < (int)sizeof(t49_viline) - 14; i++)
					t49_vo += snprintf(t49_viline + t49_vo, sizeof(t49_viline) - t49_vo, " vi%02u=%04x", i, VU1.VI[i].UL & 0xffff);
				t49_viline[sizeof(t49_viline) - 1] = 0;
				Console.WriteLn("%s", t49_viline);
			}
			u32* t49_m32 = (u32*)VU1.Mem;
			for (u32 r = 0; r < 1024; r++)
				Console.WriteLn("vumem %u %08x %08x %08x %08x", r, t49_m32[r * 4], t49_m32[r * 4 + 1], t49_m32[r * 4 + 2], t49_m32[r * 4 + 3]);
			u32 t49_span = g_t49_vif_mark - g_t49_vif_dumped;
			if (t49_span > 4096) Console.WriteLn("T49_VIF_TRUNCATED kept=4096 dropped=%u", t49_span - 4096);
			u32 t49_s0 = (t49_span > 4096) ? (g_t49_vif_mark - 4096) : (g_t49_vif_dumped + 1);
			static const char* const t49_vntbl[] = {"S", "V2", "V3", "V4"};
			static const u32 t49_vltbl[] = {32, 16, 8, 5};
			for (u32 s = t49_s0; s < g_t49_vif_mark; s++)
			{
				t49_vifent* e = &g_t49_vif[s & 4095];
				if (e->seq != s) continue;
				u32 code = e->code, cmd = (code >> 24) & 0x7f;
				bool is_unp = (cmd >= 0x60 && cmd <= 0x7f);
				u32 num = (code >> 16) & 0xff;
				if (is_unp && num == 0) num = 256;
				bool flg = ((code >> 15) & 1) != 0;
				u32 addr = code & 0x3ff;
				if (is_unp && flg) addr = (addr + e->tops) & 0x3ff;
				char fmt[16];
				u32 usn = 0;
				if (is_unp)
				{
					u32 vn = (cmd >> 2) & 0x3, vl = cmd & 0x3;
					snprintf(fmt, sizeof(fmt), "V%s_%u", t49_vntbl[vn], t49_vltbl[vl]);
					usn = (code >> 14) & 1;
				}
				else { snprintf(fmt, sizeof(fmt), "-"); }
				char line[640];
				int o = snprintf(line, sizeof(line), "vif %s num=%u addr=%u fmt=%s usn=%u mask=%08x cl=%u wl=%u",
					t49_vif_name(cmd), num, addr, fmt, usn, e->mask, e->cl, e->wl);
				if (cmd == 0x30 || cmd == 0x31)
				{
					o += snprintf(line + o, sizeof(line) - o, "%s", cmd == 0x30 ? " row=" : " col=");
					for (u32 i = 0; i < e->nd && o < (int)sizeof(line) - 9; i++)
						o += snprintf(line + o, sizeof(line) - o, "%s%08x", i ? " " : "", e->d[i]);
				}
				else if (e->nd > 0)
				{
					o += snprintf(line + o, sizeof(line) - o, " data=");
					for (u32 i = 0; i < e->nd && o < (int)sizeof(line) - 9; i++)
						o += snprintf(line + o, sizeof(line) - o, "%s%08x", i ? " " : "", e->d[i]);
				}
				snprintf(line + o, sizeof(line) - o, " code=%08x flg=%u tops=%u", code, flg ? 1 : 0, e->tops);
				line[sizeof(line) - 1] = 0;
				Console.WriteLn("%s", line);
			}
			g_t49_vif_dumped = g_t49_vif_mark;
			g_t49_pair_active = true;
		}
	}
"""

T49_VI_EXTERNS = r"""
extern bool g_t49_pair_active; // T49: defined in VU1micro.cpp.
extern bool g_t49_stop_on_ebit;
extern bool g_t49_exit_armed;
extern u32 g_t48_vu_startpc; // T49: T48's begin-record, defined in VU1micro.cpp.
extern u32 g_t49_startpc;
extern u32 g_t49_arrivals;
extern u32 g_t49_pairs;
extern u32 g_t49_vi[32];
extern u32 g_t49_vf[32][4];
extern u8 g_t49_mem[16384];
extern u32 g_t49_touch[16];
extern u32 g_t49_ntouch;
"""

T49_VI_DISASM = r"""
// T49: compact pair disassembler (log-only; lower + upper-direct names mirror the VUops tables; upper FD groups + unknowns fall back to hex).
#include <cstdio>
static bool t49_close_after_pair = false; // T49: set at the E-bit of the traced 0x257 program; the epilogue prints T49_END after that pair's line.
static const char* const t49_lodir[48] = {
	"LQ", "SQ", 0, 0, "ILW", "ISW", "IADDIU", "ISUBIU",
	0, 0, 0, 0, 0, 0, 0, 0,
	"FCEQ", "FCSET", "FCAND", "FCOR", "FSEQ", "FSSET", "FSAND", "FSOR",
	"FMEQ", 0, "FMAND", "FMOR", "FCGET", 0, 0, 0,
	"B", "BAL", 0, 0, "JR", "JALR", "IBEQ", "IBNE",
	"IBLTZ", "IBGTZ", "IBLEZ", "IBGEZ", 0, 0, 0, 0,
};
static const char* const t49_updir[48] = {
	"ADDx", "ADDy", "ADDz", "ADDw", "SUBx", "SUBy", "SUBz", "SUBw",
	"MADDx", "MADDy", "MADDz", "MADDw", "MSUBx", "MSUBy", "MSUBz", "MSUBw",
	"MAXx", "MAXy", "MAXz", "MAXw", "MINIx", "MINIy", "MINIz", "MINIw",
	"MULx", "MULy", "MULz", "MULw", "MULq", "MAXi", "MULi", "MINIi",
	"ADDq", "MADDq", "ADDi", "MADDi", "SUBq", "MSUBq", "SUBi", "MSUBi",
	"ADD", "MADD", "MUL", "MAX", "SUB", "MSUB", "OPMSUB", "MINI",
};
static const char* t49_t3_name(u32 t3, u32 fd, char* out, size_t cap)
{
	static const char* const t00[32] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "MOVE", "LQI", "DIV", "MTIR",
		"RNEXT", 0, 0, 0, 0, "MFP", "XTOP", "XGKICK", "ESADD", "EATANxy", "ESQRT", "ESIN",
		0, 0, 0, 0,
	};
	static const char* const t01[32] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "MR32", "SQI", "SQRT", "MFIR",
		"RGET", 0, 0, 0, 0, 0, "XITOP", 0, "ERSADD", "EATANxz", "ERSQRT", "EATAN",
		0, 0, 0, 0,
	};
	static const char* const t10[32] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "LQD", "RSQRT", "ILWR",
		"RINIT", 0, 0, 0, 0, 0, 0, 0, "ELENG", "ESUM", "ERCPR", "EEXP",
		0, 0, 0, 0,
	};
	static const char* const t11[32] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "SQD", "WAITQ", "ISWR",
		"RXOR", 0, 0, 0, 0, 0, 0, 0, "ERLENG", 0, "WAITP", 0,
		0, 0, 0, 0,
	};
	const char* n = 0;
	if (t3 == 0) n = t00[fd];
	else if (t3 == 1) n = t01[fd];
	else if (t3 == 2) n = t10[fd];
	else if (t3 == 3) n = t11[fd];
	if (n) { snprintf(out, cap, "%s", n); return out; }
	snprintf(out, cap, "T3%u.%02x", t3, fd);
	return out;
}
static void t49_disasm(u32 up, u32 lo, char* out, size_t cap)
{
	char un[16], ln[32], xyz[8];
	u32 ui = up & 0x3f;
	if (ui <= 0x2f && t49_updir[ui]) snprintf(un, sizeof(un), "%s", t49_updir[ui]);
	else if (ui >= 0x3c) snprintf(un, sizeof(un), "UFD%u.%02x", ui - 0x3c, (up >> 6) & 0x1f);
	else snprintf(un, sizeof(un), "U%02x", ui);
	int p = 0;
	if ((up >> 24) & 1) xyz[p++] = 'x';
	if ((up >> 23) & 1) xyz[p++] = 'y';
	if ((up >> 22) & 1) xyz[p++] = 'z';
	if ((up >> 21) & 1) xyz[p++] = 'w';
	if (p == 0) xyz[p++] = '-';
	xyz[p] = 0;
	u32 lop = (lo >> 25) & 0x7f;
	if (lop <= 0x2f && t49_lodir[lop]) snprintf(ln, sizeof(ln), "%s", t49_lodir[lop]);
	else if (lop == 0x30) snprintf(ln, sizeof(ln), "IADD");
	else if (lop == 0x31) snprintf(ln, sizeof(ln), "ISUB");
	else if (lop == 0x32) snprintf(ln, sizeof(ln), "IADDI");
	else if (lop == 0x34) snprintf(ln, sizeof(ln), "IAND");
	else if (lop == 0x35) snprintf(ln, sizeof(ln), "IOR");
	else if (lop == 0x40)
	{
		u32 sub = lo & 0x3f;
		if (sub >= 0x3c) t49_t3_name(sub - 0x3c, (lo >> 6) & 0x1f, ln, sizeof(ln));
		else snprintf(ln, sizeof(ln), "LO40.%02x", sub);
	}
	else snprintf(ln, sizeof(ln), "LO%02x", lop);
	snprintf(out, cap, "%c%c%c%c %s.%s+%s",
		(up & 0x40000000) ? 'E' : '.', (up & 0x10000000) ? 'D' : '.',
		(up & 0x08000000) ? 'T' : '.', (up & 0x80000000) ? 'I' : '.',
		un, xyz, ln);
}
"""

T49_VI_EPILOGUE = r"""
	// T49: pair-trace epilogue (log-only).
	if (t49_log)
	{
		g_t49_pairs++;
		char t49_line[4096]; size_t t49_o = 0;
		char t49_dis[128]; t49_disasm(t49_up, t49_lo, t49_dis, sizeof(t49_dis));
		t49_o += snprintf(t49_line + t49_o, sizeof(t49_line) - t49_o, "pair pc=0x%x up=%08x lo=%08x %s | vi", t49_pc, t49_up, t49_lo, t49_dis);
		if (t49_o >= sizeof(t49_line) - 1) t49_o = sizeof(t49_line) - 1;
		for (u32 i = 0; i < 32; i++)
		{
			if (VU->VI[i].UL == g_t49_vi[i]) continue;
			if (t49_o < sizeof(t49_line) - 24)
				t49_o += snprintf(t49_line + t49_o, sizeof(t49_line) - t49_o, " %u:%04x->%04x", i, g_t49_vi[i] & 0xffff, VU->VI[i].UL & 0xffff);
		}
		if (t49_o < sizeof(t49_line) - 6) t49_o += snprintf(t49_line + t49_o, sizeof(t49_line) - t49_o, " | vf");
		u32 t49_vfn = 0;
		static const char t49_vfc[4] = {'x', 'y', 'z', 'w'};
		for (u32 i = 0; i < 32; i++) for (u32 c = 0; c < 4; c++)
		{
			if (VU->VF[i].UL[c] == g_t49_vf[i][c]) continue;
			if (t49_vfn < 8 && t49_o < sizeof(t49_line) - 32)
				t49_o += snprintf(t49_line + t49_o, sizeof(t49_line) - t49_o, " %u.%c:%08x->%08x", i, t49_vfc[c], g_t49_vf[i][c], VU->VF[i].UL[c]);
			t49_vfn++;
		}
		if (t49_vfn > 8 && t49_o < sizeof(t49_line) - 16)
			t49_o += snprintf(t49_line + t49_o, sizeof(t49_line) - t49_o, " +%u more", t49_vfn - 8);
		u32 t49_rows[16]; u32 t49_nrows = 0;
		for (u32 k = 0; k < g_t49_ntouch && t49_nrows < 16; k++)
		{
			bool seen = false;
			for (u32 j = 0; j < t49_nrows; j++) if (t49_rows[j] == g_t49_touch[k]) { seen = true; break; }
			if (!seen) t49_rows[t49_nrows++] = g_t49_touch[k];
		}
		u32 t49_lop = (t49_lo >> 25) & 0x7f;
		bool t49_store = (t49_lop == 1 || t49_lop == 5);
		if (t49_lop == 0x40)
		{
			u32 sub = t49_lo & 0x3f;
			if (sub >= 0x3c)
			{
				u32 t3 = sub - 0x3c, fd = (t49_lo >> 6) & 0x1f;
				if ((t3 == 1 && fd == 0x0d) || (t3 == 3 && fd == 0x0d) || (t3 == 3 && fd == 0x0f)) t49_store = true;
			}
		}
		u32* t49_pre = (u32*)g_t49_mem;
		u32* t49_post = (u32*)VU->Mem;
		if (t49_o < sizeof(t49_line) - 6) t49_o += snprintf(t49_line + t49_o, sizeof(t49_line) - t49_o, "%s", t49_store ? " | wr" : " | rd");
		u32 t49_shown = 0;
		for (u32 k = 0; k < t49_nrows; k++)
		{
			if (t49_shown >= 8) break;
			u32 r = t49_rows[k];
			u32* w = t49_store ? (t49_post + r * 4) : (t49_pre + r * 4);
			if (t49_o < sizeof(t49_line) - 48)
				t49_o += snprintf(t49_line + t49_o, sizeof(t49_line) - t49_o, " %u:%08x %08x %08x %08x", r, w[0], w[1], w[2], w[3]);
			t49_shown++;
		}
		if (t49_nrows > t49_shown && t49_o < sizeof(t49_line) - 16)
			t49_o += snprintf(t49_line + t49_o, sizeof(t49_line) - t49_o, " +%u more", t49_nrows - t49_shown);
		t49_line[sizeof(t49_line) - 1] = 0;
		Console.WriteLn("%s", t49_line);
		if (t49_close_after_pair)
		{
			t49_close_after_pair = false;
			Console.WriteLn("T49_END vsync=%d start_pc=0x%x pairs=%u reason=ebit", g_t48_vsync.load(std::memory_order_relaxed), g_t49_startpc, g_t49_pairs);
			g_t49_pair_active = false;
		}
	}
"""

T49_VI_EBIT = r"""
			// T49: vi-exit for the traced 0x257 program (log-only).
			if (g_t49_exit_armed && g_t48_vu_startpc == 0x257)
			{
				char t49_exline[256];
				int t49_exo = snprintf(t49_exline, sizeof(t49_exline), "vi-exit vsync=%d start_pc=0x257 pairs=%u",
					g_t48_vsync.load(std::memory_order_relaxed), g_t49_pairs);
				for (u32 i = 0; i < 16 && t49_exo < (int)sizeof(t49_exline) - 14; i++)
					t49_exo += snprintf(t49_exline + t49_exo, sizeof(t49_exline) - t49_exo, " vi%02u=%04x", i, VU->VI[i].UL & 0xffff);
				t49_exline[sizeof(t49_exline) - 1] = 0;
				Console.WriteLn("%s", t49_exline);
				g_t49_exit_armed = false;
				if (g_t49_pair_active && g_t49_startpc == 0x257)
					t49_close_after_pair = true; // the epilogue below prints T49_END reason=ebit after this pair's line.
			}
"""

T49_VO_DECLS = r"""
extern u32 g_t49_touch[16]; // T49: defined in VU1micro.cpp.
extern u32 g_t49_ntouch;
extern bool g_t49_pair_active;
__fi void t49_touch(u32 row) { if (g_t49_ntouch < 16) g_t49_touch[g_t49_ntouch++] = row; }
"""


T49_VI_PROLOGUE = r"""
	// T49: pair-trace prologue (log-only; snapshots for delta print at function end).
	u32 t49_pc = 0, t49_up = 0, t49_lo = 0;
	bool t49_log = false;
	if (g_t49_pair_active)
	{
		t49_pc = (VU->VI[REG_TPC].UL - 8) & 0x3fff;
		t49_up = ptr[1]; t49_lo = ptr[0];
		if (t49_pc == 0x418 && !g_t49_stop_on_ebit)
		{
			if (g_t49_arrivals >= 4)
			{
				Console.WriteLn("T49_END vsync=%d start_pc=0x%x pairs=%u reason=loop-done", g_t48_vsync.load(std::memory_order_relaxed), g_t49_startpc, g_t49_pairs);
				g_t49_pair_active = false;
			}
			else g_t49_arrivals++;
		}
		if (g_t49_pair_active)
		{
			if (g_t49_pairs >= 20000)
			{
				Console.WriteLn("T49_END vsync=%d start_pc=0x%x pairs=%u reason=cap", g_t48_vsync.load(std::memory_order_relaxed), g_t49_startpc, g_t49_pairs);
				g_t49_pair_active = false;
			}
			else
			{
				for (u32 i = 0; i < 32; i++) { g_t49_vi[i] = VU->VI[i].UL; for (u32 c = 0; c < 4; c++) g_t49_vf[i][c] = VU->VF[i].UL[c]; }
				u8* t49_mp = VU->Mem;
				for (u32 i = 0; i < 16384; i++) g_t49_mem[i] = t49_mp[i];
				g_t49_ntouch = 0;
				t49_log = true;
			}
		}
	}
"""

def main():
    # ---- GS.cpp: dump-vsync mirror (T49 gate needs winstart on the EE side) ----
    gs = open(GS, encoding="utf-8").read()
    assert "g_t49_winstart" not in gs, "T49 already applied to GS.cpp"
    gs = apply_after_once(gs, "std::atomic<bool> g_t48_window{false}; // T48: widened dump-window flag for VU1 gating.\n",
                          "std::atomic<int> g_t49_winstart{-1}; // T49: dump-window start mirror (GS writes / EE reads).\n",
                          "T49-GS1")
    gs = apply_after_once(gs, "\t\t\t\t\tt48_winstart = g8_vsync_index + 1;\n",
                          "\t\t\t\t\tg_t49_winstart.store(t48_winstart, std::memory_order_relaxed); // T49: mirror for the dump-vsync gate.\n",
                          "T49-GS2")
    open(GS, "w", encoding="utf-8").write(gs)

    # ---- VU1micro.cpp: T49 globals + record/mark helpers ----
    v1 = open(V1, encoding="utf-8").read()
    assert "g_t49_pair_active" not in v1, "T49 already applied to VU1micro.cpp"
    v1 = apply_after_once(v1, "extern std::atomic<bool> g_t48_window;\n",
                          T49_V1_DECLS, "T49-V1a")
    v1 = replace_once(v1, "\tCpuVU1->SetStartPC(VU1.VI[REG_TPC].UL << 3);\n",
                        T49_V1_DUMP + "\tCpuVU1->SetStartPC(VU1.VI[REG_TPC].UL << 3);\n", "T49-V1b")
    open(V1, "w", encoding="utf-8").write(v1)

    # ---- VU1microInterp.cpp: disassembler + pair prologue/epilogue ----
    vi = open(VI, encoding="utf-8").read()
    assert "g_t49_pair_active" not in vi, "T49 already applied to VU1microInterp.cpp"
    vi = apply_after_once(vi, "extern std::atomic<bool> g_t48_window;\n",
                          T49_VI_EXTERNS, "T49-VI0")
    vi = apply_after_once(vi, '#include "VUmicro.h"\n',
                          T49_VI_DISASM, "T49-VI1")
    vi = replace_once(vi,
                      "\tptr = (u32*)&VU->Micro[VU->VI[REG_TPC].UL];\n\tVU->VI[REG_TPC].UL += 8;\n",
                      "\tptr = (u32*)&VU->Micro[VU->VI[REG_TPC].UL];\n\tVU->VI[REG_TPC].UL += 8;\n" + T49_VI_PROLOGUE,
                      "T49-VI2")
    vi = apply_after_once(vi, "\t// Progress the write position of the FMAC pipeline by one place\n",
                          T49_VI_EPILOGUE,
                          "T49-VI3")
    vi = apply_after_once(vi, "\t\t\t\tg_t48_vu_active = false;\n\t\t\t}\n",
                          T49_VI_EBIT,
                          "T49-VI4")
    open(VI, "w", encoding="utf-8").write(vi)

    # ---- VUops.cpp: GET_VU_MEM row tap ----
    vo = open(VO, encoding="utf-8").read()
    assert "t49_touch" not in vo, "T49 already applied to VUops.cpp"
    vo = apply_after_once(vo,
                          "u64 g_t48_vu_xg = 0; // T48: XGKICK-instruction counter (log-only; def here, record in VU1micro.cpp).\n",
                          T49_VO_DECLS,
                          "T49-VO1")
    vo = replace_once(vo,
                      "\tif (VU == &vuRegs[1])\n\t\treturn (u32*)(vuRegs[1].Mem + (addr & 0x3fff));\n",
                      "\tif (VU == &vuRegs[1])\n\t{\n\t\tif (g_t49_pair_active) t49_touch((addr & 0x3fff) >> 4); // T49: tap VU1 interp mem rows (log-only).\n\t\treturn (u32*)(vuRegs[1].Mem + (addr & 0x3fff));\n\t}\n",
                      "T49-VO2")
    open(VO, "w", encoding="utf-8").write(vo)

    # ---- Vif_Transfer.cpp: record every VIF1 command ----
    vt = open(VT, encoding="utf-8").read()
    assert "t49_vif_record" not in vt, "T49 already applied to Vif_Transfer.cpp"
    vt = apply_after_once(vt, '#include "Vif_Dynarec.h"\n',
                          'extern void t49_vif_record(u32 code, const u32* data, u32 avail, u32 cl, u32 wl, u32 mask, u32 tops, u32 itops); // T49: defined in VU1micro.cpp.\n',
                          "T49-VT1")
    vt = apply_after_once(vt,
                          '\t\t\tVIF_LOG("New VifCMD %x tagsize %x irq %d", vifX.cmd, vifX.tag.size, vifX.irq);\n',
                          '\t\t\tif (idx == 1) t49_vif_record(data[0], data, pSize, vifXRegs.cycle.cl, vifXRegs.cycle.wl, vifXRegs.mask, vifXRegs.tops, vifXRegs.itops); // T49: record every VIF1 command (log-only).\n',
                          "T49-VT2")
    open(VT, "w", encoding="utf-8").write(vt)

    # ---- Vif_Codes.cpp: mark packet starts at MSCAL-family ----
    vc = open(VC, encoding="utf-8").read()
    assert "t49_vif_mark_fn" not in vc, "T49 already applied to Vif_Codes.cpp"
    vc = apply_after_once(vc, '#include "Vif_Dynarec.h"\n',
                          'extern void t49_vif_mark_fn(); // T49: defined in VU1micro.cpp.\n',
                          "T49-VC1")
    vc = replace_once(vc, "\t\tvuExecMicro(idx, static_cast<u16>(vifXRegs.code), false);\n",
                      "\t\tif (idx == 1) t49_vif_mark_fn(); // T49: packet boundary (log-only).\n\t\tvuExecMicro(idx, static_cast<u16>(vifXRegs.code), false);\n",
                      "T49-VC2")
    vc = replace_once(vc, "\t\tvuExecMicro(idx, static_cast<u16>(vifXRegs.code), true);\n",
                      "\t\tif (idx == 1) t49_vif_mark_fn(); // T49: packet boundary (log-only).\n\t\tvuExecMicro(idx, static_cast<u16>(vifXRegs.code), true);\n",
                      "T49-VC3")
    vc = replace_once(vc, "\t\tvuExecMicro(idx, -1, false);\n",
                      "\t\tif (idx == 1) t49_vif_mark_fn(); // T49: packet boundary (log-only).\n\t\tvuExecMicro(idx, -1, false);\n",
                      "T49-VC4")
    open(VC, "w", encoding="utf-8").write(vc)

    print("T49 hook applied: GS(2) + V1(2) + VI(5) + VO(2) + VT(2) + VC(4) ok")


if __name__ == "__main__":
    main()

