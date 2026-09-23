#!/usr/bin/env python3
"""T50 second patch (pcsx2-g7, on top of T50 hook 1): MPG-imm0 payload source
+ D1 DMA-register write watch + /tmp/t50-free gate fallback.

(1) mpgpay: for every VIF1 MPG with imm=0 at SC settled, the EE address its
    payload came from (vif1ch.madr at command time + chain-tag tap):
    `mpgpay vsync=<n> imm=0 num=<> src=0x<raw>&0x<masked> mode=<chain:id|normal>
      tag_at=<0x...|->`
    src raw = vif1ch.madr at MPG pass1; masked = raw & 0x1FFFFFFF. madr is the
    DMA fetch pointer: at command time it sits at/just past the MPG code word
    in the stream (prefetch/FIFO ahead by at most hundreds of bytes); the
    payload follows immediately, so src identifies the 2 KB payload region
    (candidate bases 0x4349b8/0x435bf8 are 0x1240 apart with disjoint 2 KB
    payloads). mode/tag_at come from a silent per-tag tap in
    vif1SetupTransfer (+Vif1_MFIFO drain); normal-mode MPGs (no tag) print
    mode=normal tag_at=-.
(2) dmareg: EE writes to D1_CHCR/MADR/QWC/TADR (0x10009000/10/20/30):
    `dmareg vsync=<n> reg=<D1_...> value=0x<> pc=0x<> ra=0x<> a0..a3 v0 v1
      t0..t9 s0..s7` (first 256, then T50_DMAREG_CAP once). Hook sits in
    dmacWrite32 after the busy-hack (only applied writes logged); pc/ra/GPRs
    are exact under the EE interpreter (boot3 config).
Gate: /tmp/t50-arm + (/tmp/t50-free OR (T48 window + winstart gate)). The
free fallback covers statefile boots where no dump trigger sets winstart
(G13 auto-dump consumes the one-shot there). Hook 1's srcread gate gets the
same fallback (2 hunks here, same file).

Hunks assert count==1 each, abort otherwise. Idempotent: aborts if applied.
"""
import sys

G = "/home/brad/pcsx2-g7/pcsx2"
RI = G + "/pcsx2/R5900OpcodeImpl.cpp"
V1D = G + "/pcsx2/Vif1_Dma.cpp"
VC = G + "/pcsx2/Vif_Codes.cpp"
MF = G + "/pcsx2/Vif1_MFIFO.cpp"
DM = G + "/pcsx2/Dmac.cpp"


def apply_after_once(text, find, add, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)
    return text.replace(find, find + add, 1)


def replace_once(text, find, repl, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)
    return text.replace(find, repl, 1)


T50B_DECLS = r"""
// T50b: mpgpay/dmareg trace (log-only).
#include <atomic>
#include <cstdio>
extern std::atomic<int> g_t48_vsync; // T50b: defined in GS.cpp (T48 vsync mirror).
extern std::atomic<bool> g_t48_window; // T50b: defined in GS.cpp (T48 window flag).
extern std::atomic<int> g_t49_winstart; // T50b: defined in GS.cpp (T49 winstart mirror).
bool g_t50b_armed = false;
bool g_t50b_free = false;
u32 g_t50b_arm_ctr = 0;
u32 g_t50b_mpg_n = 0;
u32 g_t50b_dm_n = 0;
bool g_t50b_dm_capped = false;
u32 g_t50b_tag_at = 0;
u32 g_t50b_tag_id = 0;
u32 g_t50b_tag_mod = 0;
bool g_t50b_tag_valid = false;
static bool t50b_gate()
{
	if (!g_t50b_armed)
	{
		if ((++g_t50b_arm_ctr & 1023) != 0) return false;
		FILE* t50af = fopen("/tmp/t50-arm", "r");
		if (!t50af) return false;
		fclose(t50af);
		g_t50b_armed = true;
	}
	if (!g_t50b_free)
	{
		FILE* t50ff = fopen("/tmp/t50-free", "r");
		if (t50ff) { fclose(t50ff); g_t50b_free = true; }
	}
	if (g_t50b_free) return true;
	if (!g_t48_window.load(std::memory_order_relaxed)) return false;
	int t50_ws = g_t49_winstart.load(std::memory_order_relaxed);
	int t50_vs = g_t48_vsync.load(std::memory_order_relaxed);
	return t50_ws >= 0 && t50_vs >= t50_ws;
}
// Silent per-tag tap (chain + MFIFO drain): remembers the tag being streamed.
void t50b_tag_tap(u32 tag_at, u32 id, u32 mod)
{
	g_t50b_tag_at = tag_at; g_t50b_tag_id = id; g_t50b_tag_mod = mod; g_t50b_tag_valid = true;
}
// VIF1 MPG with imm=0 (dest 0): log the DMA fetch pointer at command time.
void t50b_mpg(u32 code)
{
	if ((code & 0xffff) != 0) return; // imm != 0: not a dest-0 upload.
	if (!t50b_gate()) return;
	if (g_t50b_mpg_n >= 2000)
	{
		if (g_t50b_mpg_n == 2000)
		{
			g_t50b_mpg_n++;
			Console.WriteLn("T50_MPGPAY_CAP vsync=%d", g_t48_vsync.load(std::memory_order_relaxed));
		}
		return;
	}
	g_t50b_mpg_n++;
	u32 num = (code >> 16) & 0xff;
	u32 madr = vif1ch.madr;
	u32 masked = madr & 0x1fffffff;
	char mode[16], tagbuf[16];
	if (vif1ch.chcr.MOD == CHAIN_MODE && g_t50b_tag_valid && g_t50b_tag_mod == CHAIN_MODE)
	{
		snprintf(mode, sizeof(mode), "chain:%u", g_t50b_tag_id);
		snprintf(tagbuf, sizeof(tagbuf), "0x%x", g_t50b_tag_at);
	}
	else
	{
		snprintf(mode, sizeof(mode), "normal");
		snprintf(tagbuf, sizeof(tagbuf), "-");
	}
	Console.WriteLn("mpgpay vsync=%d imm=0 num=%u src=0x%08x&0x%08x mode=%s tag_at=%s",
		g_t48_vsync.load(std::memory_order_relaxed), num, madr, masked, mode, tagbuf);
}
// EE write to a D1 DMA register (applied writes only; hook sits past the busy-hack).
void t50b_dmareg(u32 mem, u32 value)
{
	const char* rn = nullptr;
	if (mem == 0x10009000) rn = "D1_CHCR";
	else if (mem == 0x10009010) rn = "D1_MADR";
	else if (mem == 0x10009020) rn = "D1_QWC";
	else if (mem == 0x10009030) rn = "D1_TADR";
	else return;
	if (!t50b_gate()) return;
	if (g_t50b_dm_n >= 256)
	{
		if (!g_t50b_dm_capped)
		{
			g_t50b_dm_capped = true;
			Console.WriteLn("T50_DMAREG_CAP vsync=%d", g_t48_vsync.load(std::memory_order_relaxed));
		}
		return;
	}
	g_t50b_dm_n++;
	Console.WriteLn("dmareg vsync=%d reg=%s value=0x%x pc=0x%x ra=0x%x a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x t0=%08x t1=%08x t2=%08x t3=%08x t4=%08x t5=%08x t6=%08x t7=%08x t8=%08x t9=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x",
		g_t48_vsync.load(std::memory_order_relaxed), rn, value, cpuRegs.pc, cpuRegs.GPR.r[31].UL[0],
		cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0],
		cpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0],
		cpuRegs.GPR.r[8].UL[0], cpuRegs.GPR.r[9].UL[0], cpuRegs.GPR.r[10].UL[0], cpuRegs.GPR.r[11].UL[0],
		cpuRegs.GPR.r[12].UL[0], cpuRegs.GPR.r[13].UL[0], cpuRegs.GPR.r[14].UL[0], cpuRegs.GPR.r[15].UL[0],
		cpuRegs.GPR.r[24].UL[0], cpuRegs.GPR.r[25].UL[0],
		cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0],
		cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0], cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0]);
}
"""

# --- hook-1 gate fallback (same file, exact text from t50-hook.py) ---
T50_FREE_DECL_FIND = "bool g_t50_armed = false;\n"
T50_FREE_DECL_ADD = "bool g_t50_free = false; // T50b: /tmp/t50-free fallback (statefile boots, no dump winstart).\n"
T50_FREE_GATE_FIND = "\tif (!g_t48_window.load(std::memory_order_relaxed)) return false;\n"
T50_FREE_GATE_REPL = (
    "\tif (!g_t50_free)\n"
    "\t{\n"
    "\t\tFILE* t50ff = fopen(\"/tmp/t50-free\", \"r\");\n"
    "\t\tif (t50ff) { fclose(t50ff); g_t50_free = true; }\n"
    "\t}\n"
    "\tif (!g_t50_free && !g_t48_window.load(std::memory_order_relaxed)) return false;\n"
)

T50B_TAP_CALL = "\n\tt50b_tag_tap(vif1ch.tadr, ptag->ID, vif1ch.chcr.MOD); // T50b: chain-tag tap (log-only)."

T50B_V1D_LOG_FIND = (
    "\tVIF_LOG(\"VIF1 Tag %8.8x_%8.8x size=%d, id=%d, madr=%lx, tadr=%lx\",\n"
    "\t\tptag[1]._u32, ptag[0]._u32, vif1ch.qwc, ptag->ID, vif1ch.madr, vif1ch.tadr);"
)

T50B_VC_EXTERN_FIND = "extern void t49_vif_mark_fn(); // T49: defined in VU1micro.cpp.\n"
T50B_VC_EXTERN_ADD = "extern void t50b_mpg(u32 code); // T50b: defined in Vif1_Dma.cpp.\n"

T50B_MPG_FIND = (
    "\t\tvifX.tag.size = vifNum ? (vifNum * 2) : 512;\n"
    "\t\tvifFlush(idx);\n"
    "\n"
    "\t\tif (vifX.waitforvu)\n"
    "\t\t{\n"
    "\t\t\tCPU_SET_DMASTALL(idx ? vif1InternalIrq() : DMAC_VIF0, true);\n"
    "\t\t\treturn 0;\n"
    "\t\t}\n"
    "\t\telse\n"
    "\t\t{\n"
    "\t\t\tvifX.pass = 1;\n"
    "\t\t\treturn 1;\n"
    "\t\t}"
)
T50B_MPG_REPL = (
    "\t\tvifX.tag.size = vifNum ? (vifNum * 2) : 512;\n"
    "\t\tvifFlush(idx);\n"
    "\n"
    "\t\tif (vifX.waitforvu)\n"
    "\t\t{\n"
    "\t\t\tCPU_SET_DMASTALL(idx ? vif1InternalIrq() : DMAC_VIF0, true);\n"
    "\t\t\treturn 0;\n"
    "\t\t}\n"
    "\t\telse\n"
    "\t\t{\n"
    "\t\t\tvifX.pass = 1;\n"
    "\t\t\tif (idx == 1) t50b_mpg(vifXRegs.code); // T50b: MPG-imm0 payload source (log-only).\n"
    "\t\t\treturn 1;\n"
    "\t\t}"
)

T50B_MF_FIND = (
    "\t\tvif1.done |= hwDmacSrcChainWithStack(vif1ch, ptag->ID);\n"
    "\n"
    "\t\tmfifoVifMaskMem(ptag->ID);"
)
T50B_MF_REPL = (
    "\t\tvif1.done |= hwDmacSrcChainWithStack(vif1ch, ptag->ID);\n"
    "\t\t{ extern void t50b_tag_tap(u32 tag_at, u32 id, u32 mod); t50b_tag_tap(vif1ch.tadr, ptag->ID, vif1ch.chcr.MOD); } // T50b: MFIFO-drain chain-tag tap (log-only).\n"
    "\n"
    "\t\tmfifoVifMaskMem(ptag->ID);"
)

T50B_DM_FIND = "\tallow_write:;\n\t}"
T50B_DM_REPL = (
    "\tallow_write:;\n"
    "\t}\n"
    "\t{ extern void t50b_dmareg(u32 mem, u32 value); t50b_dmareg(mem, value); } // T50b: D1 reg write watch (log-only)."
)


def check(text, find, name):
    n = text.count(find)
    assert n == 1, "%s: anchor count=%d, want 1" % (name, n)


def main():
    ri = open(RI, encoding="utf-8").read()
    v1d = open(V1D, encoding="utf-8").read()
    vc = open(VC, encoding="utf-8").read()
    mf = open(MF, encoding="utf-8").read()
    dm = open(DM, encoding="utf-8").read()
    assert "g_t50_free" not in ri, "T50b already applied to R5900OpcodeImpl.cpp"
    assert "t50b_mpg" not in v1d, "T50b already applied to Vif1_Dma.cpp"
    assert "t50b_mpg" not in vc, "T50b already applied to Vif_Codes.cpp"
    assert "t50b_tag_tap" not in mf, "T50b already applied to Vif1_MFIFO.cpp"
    assert "t50b_dmareg" not in dm, "T50b already applied to Dmac.cpp"
    # Validate every anchor before writing anything.
    check(ri, T50_FREE_DECL_FIND, "T50b-RI0")
    check(ri, T50_FREE_GATE_FIND, "T50b-RI1")
    check(v1d, '#include "Vif_Dynarec.h"\n', "T50b-VD0")
    check(v1d, T50B_V1D_LOG_FIND, "T50b-VD1")
    check(vc, T50B_VC_EXTERN_FIND, "T50b-VC0")
    check(vc, T50B_MPG_FIND, "T50b-VC1")
    check(mf, T50B_MF_FIND, "T50b-MF0")
    check(dm, T50B_DM_FIND, "T50b-DM0")

    ri = apply_after_once(ri, T50_FREE_DECL_FIND, T50_FREE_DECL_ADD, "T50b-RI0")
    ri = replace_once(ri, T50_FREE_GATE_FIND, T50_FREE_GATE_REPL, "T50b-RI1")
    open(RI, "w", encoding="utf-8").write(ri)

    v1d = apply_after_once(v1d, '#include "Vif_Dynarec.h"\n', T50B_DECLS, "T50b-VD0")
    v1d = apply_after_once(v1d, T50B_V1D_LOG_FIND, T50B_TAP_CALL, "T50b-VD1")
    open(V1D, "w", encoding="utf-8").write(v1d)

    vc = apply_after_once(vc, T50B_VC_EXTERN_FIND, T50B_VC_EXTERN_ADD, "T50b-VC0")
    vc = replace_once(vc, T50B_MPG_FIND, T50B_MPG_REPL, "T50b-VC1")
    open(VC, "w", encoding="utf-8").write(vc)

    mf = replace_once(mf, T50B_MF_FIND, T50B_MF_REPL, "T50b-MF0")
    open(MF, "w", encoding="utf-8").write(mf)

    dm = replace_once(dm, T50B_DM_FIND, T50B_DM_REPL, "T50b-DM0")
    open(DM, "w", encoding="utf-8").write(dm)

    print("T50b hook applied: RI(2) + VD(2) + VC(2) + MF(1) + DM(1) ok")


if __name__ == "__main__":
    main()
