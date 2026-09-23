#!/usr/bin/env python3
"""T57 hook (pcsx2-g7, on top of the T56-end working tree = HEAD 9056c083 + T48-T56 hooks).

VU0 micro-program starts + VIF0 command census at Select Character settled,
EE interp + VU0 interp (dat-t57: EnableEE=false, EnableVU0=false).

Every VU0 start funnels through vu0ExecMicro() (VU0micro.cpp): COP2 VCALLMS/R
directly, VIF0 MSCAL/MSCALF/MSCNT via vifExecQueue(0) (Vif_Codes.cpp:44).
The hook arms a pending record at start (caller pc + via + startPC + VU0.cycle)
and emits the line at the E-bit stop in _vu0Exec (VU0microInterp.cpp, interp
only), with cycles-to-E-bit and post-run VI[1]/VI[2]:

  vu0call vsync=<n> caller_pc=0x<> via=<cop2|vif0> startPC=0x<byte> cycles=<n>
    vi1=0x<> vi2=0x<>[ ms=0x<14|15|17>][ mark=sub_0037D968][ end=abort]

- ms= records which VIF MS op queued a vif0 start (set in the 3 vifOp
  handlers, consumed at exec; cop2 lines never carry it).
- mark= flags the COP2 vcallmsr at EE 0x37deb8 (sub_0037D968) explicitly.
- end=abort marks a pending program that never reached E-bit (superseded,
  e.g. M-bit-stuck + new start, or VPU reset): cycles are approximate.
- A start that arrives while one is pending can only happen for an
  already-dead program (vu0ExecMicro stall-finishes a running one first),
  so pending is checked at entry (dead: VPU_STAT clear) and after the
  stall-finish (still pending: stuck) - both emit end=abort.

VIF0 census: every VIF0 command word passing through vifTransferLoop
(Vif_Transfer.cpp, next to T49's VIF1 hook) increments a per-op counter for
the current g_t48_vsync; on vsync change the previous vsync's nonzero counts
flush as:

  vif0op vsync=<n> op=<NAME> n=<count>

(Names: T49's t49_vif_name table, copied.) A vsync with zero VIF0 commands
produces no lines; the trailing vsync's counts are flushed opportunistically
when a later vu0call completes in a newer vsync (else unflushed - gap, noted).

Shared budget: first 2000 vu0call+vif0op lines, then one T57_CAP line.
Log-only. Idempotent: aborts if applied. Asserts every anchor count.
"""

VU0MICRO = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU0micro.cpp"
COP2 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/COP2.cpp"
VIFCODES = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Vif_Codes.cpp"
VIFXFER = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Vif_Transfer.cpp"
VU0INTERP = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU0microInterp.cpp"

T57_DECL = """
// T57: VU0 micro-program start/end watch + VIF0 command census (log-only).
#include <atomic>
extern std::atomic<int> g_t48_vsync; // T57: defined in GS.cpp (T48 vsync mirror).
#define T57_MAXL 2000
static u32 g_t57_n = 0;
static bool g_t57_capped = false;
static bool t57_budget()
{
\tif (g_t57_n >= T57_MAXL)
\t{
\t\tif (!g_t57_capped) { g_t57_capped = true; Console.WriteLn("T57_CAP vsync=%d", g_t48_vsync.load(std::memory_order_relaxed)); }
\t\treturn false;
\t}
\tg_t57_n++;
\treturn true;
}
static const char* t57_opname(u32 cmd) // T57: VIF code names (same table as T49 t49_vif_name).
{
\tswitch (cmd)
\t{
\t\tcase 0x00: return "NOP";
\t\tcase 0x01: return "STCYCL";
\t\tcase 0x02: return "OFFSET";
\t\tcase 0x03: return "BASE";
\t\tcase 0x04: return "ITOP";
\t\tcase 0x05: return "STMOD";
\t\tcase 0x06: return "MSKPATH3";
\t\tcase 0x07: return "MARK";
\t\tcase 0x10: return "FLUSHE";
\t\tcase 0x11: return "FLUSH";
\t\tcase 0x13: return "FLUSHA";
\t\tcase 0x14: return "MSCAL";
\t\tcase 0x15: return "MSCALF";
\t\tcase 0x17: return "MSCNT";
\t\tcase 0x20: return "STMASK";
\t\tcase 0x30: return "STROW";
\t\tcase 0x31: return "STCOL";
\t\tcase 0x4a: return "MPG";
\t\tcase 0x50: return "DIRECT";
\t\tcase 0x51: return "DIRECTHL";
\t\tdefault: break;
\t}
\tif (cmd >= 0x60 && cmd <= 0x7f) return "UNPACK";
\treturn "NULL";
}
static const char* t57_vianame(u32 v)
{
\treturn v == 0 ? "cop2" : (v == 1 ? "vif0" : "unknown");
}
static bool g_t57_pend = false;
static u32 g_t57_pcaller = 0, g_t57_pvia = 9, g_t57_pstart = 0, g_t57_pms = 0;
static u64 g_t57_pc0 = 0;
static u32 g_t57_ctx_via = 9, g_t57_ctx_caller = 0, g_t57_ctx_ms = 0;
static u32 g_t57_noebit = 0; // T57: E-bit stops with nothing pending (pre-window program).
void t57_cop2_ctx() { g_t57_ctx_via = 0; g_t57_ctx_caller = cpuRegs.pc; g_t57_ctx_ms = 0; }
void t57_vif0_ctx() { g_t57_ctx_via = 1; g_t57_ctx_caller = cpuRegs.pc; }
void t57_msop(u32 op) { g_t57_ctx_ms = op; }
static u32 g_t57c[128] = {0,};
static int g_t57c_vs = -1;
static void t57_vif0_flush(int vs)
{
\tfor (u32 c = 0; c < 128; c++)
\t{
\t\tif (!g_t57c[c]) continue;
\t\tif (!t57_budget()) return;
\t\tConsole.WriteLn("vif0op vsync=%d op=%s n=%u", vs, t57_opname(c), g_t57c[c]);
\t}
}
static void t57_vif0_sync()
{
\tif (g_t57c_vs < 0) return;
\tint v = g_t48_vsync.load(std::memory_order_relaxed);
\tif (v == g_t57c_vs) return;
\tt57_vif0_flush(g_t57c_vs);
\tfor (u32 c = 0; c < 128; c++) g_t57c[c] = 0;
\tg_t57c_vs = v;
}
void t57_vif0_count(u32 cmd)
{
\tint v = g_t48_vsync.load(std::memory_order_relaxed);
\tif (g_t57c_vs < 0) g_t57c_vs = v;
\tif (v != g_t57c_vs) { t57_vif0_flush(g_t57c_vs); for (u32 c = 0; c < 128; c++) g_t57c[c] = 0; g_t57c_vs = v; }
\tif (cmd < 128) g_t57c[cmd]++;
}
static void t57_emit(bool abort)
{
\tif (!t57_budget()) return;
\tt57_vif0_sync(); // T57: flush any stale census vsync before the vu0call line.
\tint vs = g_t48_vsync.load(std::memory_order_relaxed);
\tu32 vi1 = VU0.VI[1].UL, vi2 = VU0.VI[2].UL;
\tunsigned long long cyc = (unsigned long long)(VU0.cycle - g_t57_pc0);
\tconst char* via = t57_vianame(g_t57_pvia);
\tbool mark = (g_t57_pvia == 0 && g_t57_pcaller == 0x37deb8);
\tconst char* ab = abort ? " end=abort" : "";
\tif (g_t57_pvia == 1)
\t\tConsole.WriteLn("vu0call vsync=%d caller_pc=0x%x via=%s startPC=0x%x cycles=%llu vi1=0x%x vi2=0x%x ms=0x%x%s", vs, g_t57_pcaller, via, g_t57_pstart, cyc, vi1, vi2, g_t57_pms, ab);
\telse if (mark)
\t\tConsole.WriteLn("vu0call vsync=%d caller_pc=0x%x via=%s startPC=0x%x cycles=%llu vi1=0x%x vi2=0x%x mark=sub_0037D968%s", vs, g_t57_pcaller, via, g_t57_pstart, cyc, vi1, vi2, ab);
\telse
\t\tConsole.WriteLn("vu0call vsync=%d caller_pc=0x%x via=%s startPC=0x%x cycles=%llu vi1=0x%x vi2=0x%x%s", vs, g_t57_pcaller, via, g_t57_pstart, cyc, vi1, vi2, ab);
}
void t57_entry() // T57: top of vu0ExecMicro - previous program died without E-bit.
{
\tif (g_t57_pend && !(VU0.VI[REG_VPU_STAT].UL & 1))
\t{
\t\tt57_emit(true);
\t\tg_t57_pend = false;
\t}
}
void t57_arm() // T57: after the stall-finish, before the new setup clobbers TPC.
{
\tif (g_t57_pend)
\t{
\t\tt57_emit(true); // T57: superseded without E-bit (e.g. M-bit-stuck).
\t\tg_t57_pend = false;
\t}
\tg_t57_pcaller = g_t57_ctx_caller; g_t57_pvia = g_t57_ctx_via; g_t57_pms = g_t57_ctx_ms;
\tg_t57_pstart = (VU0.VI[REG_TPC].UL << 3);
\tg_t57_pc0 = VU0.cycle;
\tg_t57_pend = true;
\tg_t57_ctx_via = 9; g_t57_ctx_caller = 0; g_t57_ctx_ms = 0;
}
void t57_vu0_ebit() // T57: E-bit stop in _vu0Exec (VU0 interp only).
{
\tif (!g_t57_pend) { g_t57_noebit++; return; }
\tt57_emit(false);
\tg_t57_pend = false;
}
"""


def check(text, find, want, name):
    n = text.count(find)
    assert n == want, "%s: anchor count=%d, want %d" % (name, n, want)


def insert_after_line(text, anchor, add, name):
    lines = text.split("\n")
    idx = [i for i, ln in enumerate(lines) if anchor in ln]
    assert len(idx) == 1, "%s: line-anchor count=%d, want 1" % (name, len(idx))
    i = idx[0]
    indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
    lines[i] = lines[i] + "\n" + indent + add
    return "\n".join(lines)


def main():
    vu0m = open(VU0MICRO, encoding="utf-8").read()
    cop2 = open(COP2, encoding="utf-8").read()
    vc = open(VIFCODES, encoding="utf-8").read()
    vx = open(VIFXFER, encoding="utf-8").read()
    vi = open(VU0INTERP, encoding="utf-8").read()

    for name, body in (("VU0micro.cpp", vu0m), ("COP2.cpp", cop2),
                       ("Vif_Codes.cpp", vc), ("Vif_Transfer.cpp", vx),
                       ("VU0microInterp.cpp", vi)):
        assert "t57_" not in body and "T57" not in body, "T57 already in %s" % name
    assert "t56_spr_watch" in open("/home/brad/pcsx2-g7/pcsx2/pcsx2/SPR.cpp",
                                   encoding="utf-8").read(), "T56 baseline missing in SPR.cpp"

    # --- VU0micro.cpp: decl + entry + arm ---
    check(vu0m, "#include <cmath>", 1, "VU0M-include")
    vu0m = vu0m.replace("#include <cmath>", "#include <cmath>\n" + T57_DECL, 1)
    check(vu0m, "void vu0ExecMicro(u32 addr) {", 1, "VU0M-exec")
    vu0m = vu0m.replace("void vu0ExecMicro(u32 addr) {",
                        "void vu0ExecMicro(u32 addr) {\n\tt57_entry(); // T57: log a previous program that died without E-bit.", 1)
    check(vu0m, "\tCpuVU0->SetStartPC(VU0.VI[REG_TPC].UL << 3);", 1, "VU0M-startpc")
    vu0m = vu0m.replace("\tCpuVU0->SetStartPC(VU0.VI[REG_TPC].UL << 3);",
                        "\tt57_arm(); // T57: arm the pending-program record (log-only).\n\tCpuVU0->SetStartPC(VU0.VI[REG_TPC].UL << 3);", 1)
    open(VU0MICRO, "w", encoding="utf-8").write(vu0m)

    # --- COP2.cpp: decl + ctx at both VCALLMS/R ---
    check(cop2, '#include "VUmicro.h"', 1, "COP2-include")
    cop2 = cop2.replace('#include "VUmicro.h"',
                        '#include "VUmicro.h"\nvoid t57_cop2_ctx(); // T57: defined in VU0micro.cpp.', 1)
    check(cop2, "\tvu0ExecMicro(((cpuRegs.code >> 6) & 0x7FFF));", 1, "COP2-ms")
    cop2 = cop2.replace("\tvu0ExecMicro(((cpuRegs.code >> 6) & 0x7FFF));",
                        "\tt57_cop2_ctx(); // T57: COP2 vcallms start (log-only).\n\tvu0ExecMicro(((cpuRegs.code >> 6) & 0x7FFF));", 1)
    check(cop2, "\tvu0ExecMicro(VU0.VI[REG_CMSAR0].US[0]);", 1, "COP2-msr")
    cop2 = cop2.replace("\tvu0ExecMicro(VU0.VI[REG_CMSAR0].US[0]);",
                        "\tt57_cop2_ctx(); // T57: COP2 vcallmsr start (log-only).\n\tvu0ExecMicro(VU0.VI[REG_CMSAR0].US[0]);", 1)
    open(COP2, "w", encoding="utf-8").write(cop2)

    # --- Vif_Codes.cpp: decl + vif0 ctx in vifExecQueue + msop in 3 handlers ---
    check(vc, "extern void t49_vif_mark_fn(); // T49: defined in VU1micro.cpp.", 1, "VC-decl")
    vc = vc.replace("extern void t49_vif_mark_fn(); // T49: defined in VU1micro.cpp.",
                    "extern void t49_vif_mark_fn(); // T49: defined in VU1micro.cpp.\nvoid t57_vif0_ctx(); // T57: defined in VU0micro.cpp.\nvoid t57_msop(u32 op); // T57: defined in VU0micro.cpp.", 1)
    check(vc, "\tif (!idx)\n\t\tvu0ExecMicro(vif0.queued_pc);", 1, "VC-queue")
    vc = vc.replace("\tif (!idx)\n\t\tvu0ExecMicro(vif0.queued_pc);",
                    "\tif (!idx)\n\t{\n\t\tt57_vif0_ctx(); // T57: VIF0-queued program start (log-only).\n\t\tvu0ExecMicro(vif0.queued_pc);\n\t}", 1)
    check(vc, "\t\tvuExecMicro(idx, static_cast<u16>(vifXRegs.code), false);", 1, "VC-mscal")
    vc = vc.replace("\t\tvuExecMicro(idx, static_cast<u16>(vifXRegs.code), false);",
                    "\t\tif (!idx) t57_msop(0x14); // T57: MSCAL queued (log-only).\n\t\tvuExecMicro(idx, static_cast<u16>(vifXRegs.code), false);", 1)
    check(vc, "\t\tvuExecMicro(idx, static_cast<u16>(vifXRegs.code), true);", 1, "VC-mscalf")
    vc = vc.replace("\t\tvuExecMicro(idx, static_cast<u16>(vifXRegs.code), true);",
                    "\t\tif (!idx) t57_msop(0x15); // T57: MSCALF queued (log-only).\n\t\tvuExecMicro(idx, static_cast<u16>(vifXRegs.code), true);", 1)
    check(vc, "\t\tvuExecMicro(idx, -1, false);", 1, "VC-mscnt")
    vc = vc.replace("\t\tvuExecMicro(idx, -1, false);",
                    "\t\tif (!idx) t57_msop(0x17); // T57: MSCNT queued (log-only).\n\t\tvuExecMicro(idx, -1, false);", 1)
    open(VIFCODES, "w", encoding="utf-8").write(vc)

    # --- Vif_Transfer.cpp: decl + census call next to T49's VIF1 hook ---
    check(vx, "extern void t49_vif_record(u32 code, const u32* data, u32 avail, u32 cl, u32 wl, u32 mask, u32 tops, u32 itops); // T49: defined in VU1micro.cpp.", 1, "VX-decl")
    vx = vx.replace("extern void t49_vif_record(u32 code, const u32* data, u32 avail, u32 cl, u32 wl, u32 mask, u32 tops, u32 itops); // T49: defined in VU1micro.cpp.",
                    "extern void t49_vif_record(u32 code, const u32* data, u32 avail, u32 cl, u32 wl, u32 mask, u32 tops, u32 itops); // T49: defined in VU1micro.cpp.\nvoid t57_vif0_count(u32 cmd); // T57: defined in VU0micro.cpp.", 1)
    check(vx, "if (idx == 1) t49_vif_record(", 1, "VX-rec")
    vx = insert_after_line(vx, "if (idx == 1) t49_vif_record(",
                           "if (idx == 0) t57_vif0_count(vifX.cmd & 0x7f); // T57: VIF0 command census (log-only).",
                           "VX-count")
    open(VIFXFER, "w", encoding="utf-8").write(vx)

    # --- VU0microInterp.cpp: decl + ebit completion call ---
    check(vi, "extern void _vuFlushAll(VURegs* VU);", 1, "VI-decl")
    vi = vi.replace("extern void _vuFlushAll(VURegs* VU);",
                    "extern void _vuFlushAll(VURegs* VU);\nvoid t57_vu0_ebit(); // T57: defined in VU0micro.cpp.", 1)
    check(vi, "\t\t\tVU0.VI[REG_VPU_STAT].UL &= ~0x1; /* E flag */", 1, "VI-ebit")
    lines = vi.split("\n")
    ei = [i for i, ln in enumerate(lines)
          if ln == "\t\t\tVU0.VI[REG_VPU_STAT].UL &= ~0x1; /* E flag */"][0]
    assert lines[ei + 1] == "\t\t\tvif0Regs.stat.VEW = false;", \
        "VI-vew: next line=%r" % lines[ei + 1]
    lines[ei + 1] = lines[ei + 1] + "\n\t\t\tt57_vu0_ebit(); // T57: E-bit stop, emit the pending vu0call line (log-only)."
    vi = "\n".join(lines)
    open(VU0INTERP, "w", encoding="utf-8").write(vi)

    print("T57 hook applied: VU0micro(3) + COP2(3) + Vif_Codes(5) + Vif_Transfer(2) + VU0microInterp(2) ok")


if __name__ == "__main__":
    main()
