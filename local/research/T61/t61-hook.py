#!/usr/bin/env python3
"""T61 hook (pcsx2-g7, on T60's tree): value-filtered rerun + censuses.

1. Mode filter: tpl emits only when new tw0 has mode bits (new&0x3C0!=0;
   shadow still tracks everything); tpl gains tw0=/tw1= post-write
   snapshots (old/new of the unchanged word equal their snapshots). app
   emits only when sampled tw0 has mode bits. Caps 200 each (same
   T60_CAPAPP/T60_CAPTPL names).
2. appsum: t61_app_account runs on EVERY 0x3797ec execution;
   `appsum vsync n_app n_tpl mode_hist=m:count,...` (m=(tw0>>6)&0xF),
   flushed on vsync change (VIF1-packet tick + app path converge), cap 3000
   (T61_CAPSUM once). Trailing partial flushed at dump via t61_flush_all.
3. apc: every EE store folded (T59) into [0x809670,+0x80*64) records its pc;
   `apc vsync pc=0x<>:count,...` (pc-sorted) flushed per vsync the same way
   (store + tick paths). 4096 distinct-pc bound (documented; realistic max
   is dozens). DMA into the area is out of scope (no pc).

TUs: Interpreter.cpp (filter + appsum), R5900OpcodeImpl.cpp (apc + dump
call), Vif_Transfer.cpp (tick). Validates before writing.
"""

INTERP = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Interpreter.cpp"
RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"
VXFER = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Vif_Transfer.cpp"

T61_SUM = """
// T61: value filter + per-vsync appsum census (log-only).
static int g_t61_sum_vs = -1;
static u32 g_t61_sum_app = 0, g_t61_sum_tpl = 0;
static u32 g_t61_sum_hist[16] = {0,};
static u32 g_t61_sum_n = 0;
static bool g_t61_sum_cap = false;
#define T61_SUM_MAX 3000
static void t61_sum_reset(int vs)
{
\tg_t61_sum_vs = vs; g_t61_sum_app = 0; g_t61_sum_tpl = 0;
\tfor (int m = 0; m < 16; m++) g_t61_sum_hist[m] = 0;
}
static void t61_sum_emit(int vs)
{
\tif (g_t61_sum_n >= T61_SUM_MAX)
\t{
\t\tif (!g_t61_sum_cap) { g_t61_sum_cap = true; Console.WriteLn("T61_CAPSUM vsync=%d", vs); }
\t\treturn;
\t}
\tg_t61_sum_n++;
\tchar hb[256]; int o = 0; int first = 1;
\tfor (int m = 0; m < 16; m++)
\t{
\t\tif (!g_t61_sum_hist[m]) continue;
\t\to += snprintf(hb + (u32)o, sizeof(hb) - (u32)o, "%s%d:%u", first ? "" : ",", m, g_t61_sum_hist[m]);
\t\tfirst = 0;
\t}
\tConsole.WriteLn("appsum vsync=%d n_app=%u n_tpl=%u mode_hist=%s", vs, g_t61_sum_app, g_t61_sum_tpl, first ? "-" : hb);
}
void t61_apc_tick(int vs); // T61: defined in R5900OpcodeImpl.cpp.
void t61_apc_flush(); // T61: defined in R5900OpcodeImpl.cpp.
void t61_vsync_tick() // T61: per-VIF1-packet vsync tick (log-only).
{
\tint v = g_t48_vsync.load(std::memory_order_relaxed);
\tif (g_t61_sum_vs < 0) { t61_sum_reset(v); t61_apc_tick(v); return; }
\tif (v == g_t61_sum_vs) return;
\tt61_sum_emit(g_t61_sum_vs);
\tt61_sum_reset(v);
\tt61_apc_tick(v);
}
void t61_app_account(u32 m) // T61: every 0x3797ec execution (log-only).
{
\tint v = g_t48_vsync.load(std::memory_order_relaxed);
\tif (g_t61_sum_vs < 0) t61_sum_reset(v);
\telse if (v != g_t61_sum_vs) { t61_sum_emit(g_t61_sum_vs); t61_sum_reset(v); }
\tg_t61_sum_app++;
\tif (m < 16) g_t61_sum_hist[m]++;
}
void t61_flush_all() // T61: dump-time forced flush (log-only).
{
\tif (g_t61_sum_vs >= 0 && (g_t61_sum_app || g_t61_sum_tpl))
\t{
\t\tt61_sum_emit(g_t61_sum_vs);
\t\tt61_sum_reset(g_t61_sum_vs);
\t}
\tt61_apc_flush();
}
"""

T61_APC = """
// T61: appender-pc census over [0x809670,+0x80*64) (log-only; 4096-pc bound).
struct t61_apc { u32 pc; u32 n; };
static t61_apc g_t61_apc[4096] = {};
static int g_t61_apc_n = 0;
static int g_t61_apc_vs = -1;
void t61_flush_all(void); // T61: defined in Interpreter.cpp.
static void t61_apc_emit(int vs)
{
\tfor (int i = 1; i < g_t61_apc_n; i++)
\t{
\t\tt61_apc t = g_t61_apc[i]; int j = i - 1;
\t\twhile (j >= 0 && g_t61_apc[j].pc > t.pc) { g_t61_apc[j + 1] = g_t61_apc[j]; j--; }
\t\tg_t61_apc[j + 1] = t;
\t}
\tstatic char lb[32768];
\tint o = snprintf(lb, sizeof(lb), "apc vsync=%d", vs);
\tfor (int i = 0; i < g_t61_apc_n && o < 30000; i++)
\t\to += snprintf(lb + (u32)o, sizeof(lb) - (u32)o, "%spc=0x%x:%u", i ? "," : " ", g_t61_apc[i].pc, g_t61_apc[i].n);
\tConsole.WriteLn("%s", lb);
}
void t61_apc_tick(int vs) // T61: vsync-change flush (log-only).
{
\tif (vs == g_t61_apc_vs) return;
\tif (g_t61_apc_vs >= 0) t61_apc_emit(g_t61_apc_vs);
\tg_t61_apc_vs = vs; g_t61_apc_n = 0;
}
void t61_apc_flush() // T61: dump-time forced flush (log-only).
{
\tif (g_t61_apc_vs >= 0 && g_t61_apc_n > 0) t61_apc_emit(g_t61_apc_vs);
\tg_t61_apc_n = 0;
}
"""

T61_APC_RECORD = """t61_apc_tick(g_t48_vsync.load(std::memory_order_relaxed)); // T61: flush on change.
\tif (lo < 0x80B670u && hi > 0x809670u) // T61: list item area (log-only).
\t{
\t\tint k;
\t\tfor (k = 0; k < g_t61_apc_n; k++) if (g_t61_apc[k].pc == cpuRegs.pc) break;
\t\tif (k == g_t61_apc_n && g_t61_apc_n < 4096) { g_t61_apc[k].pc = cpuRegs.pc; g_t61_apc[k].n = 0; g_t61_apc_n++; }
\t\tif (k < g_t61_apc_n) g_t61_apc[k].n++;
\t}"""


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
    interp = open(INTERP, encoding="utf-8").read()
    ri = open(RI, encoding="utf-8").read()
    vx = open(VXFER, encoding="utf-8").read()

    # ---- validation pass ----
    assert "t61_" not in interp and "T61_CAPSUM" not in interp, "T61 already in INTERP"
    assert "t61_" not in ri and "appsum" not in ri, "T61 already in RI"
    assert "t61_" not in vx, "T61 already in VXFER"
    assert "t60_app" in interp and "t58_store_watch" in ri, "T60/T58 baseline missing"
    check(interp, "void t60_app() // T60: called from execI at pc 0x3797ec (log-only).", 1, "I-appdef")
    check(interp, "\tif (g_t60_napp >= 300)", 1, "I-appcap")
    check(interp, "\tu32 tw0 = memRead32(t0), tw1 = memRead32(t0 + 4), tw2 = memRead32(t0 + 8), tw3 = memRead32(t0 + 12), tw4 = memRead32(t0 + 16);", 1, "I-appreads")
    check(interp, "\tg_t60_napp++;", 1, "I-appcount")
    check(interp, "\tt60_arm(t0);", 1, "I-apparm")
    check(interp, "\tif (val == g_t60_tw[idx]) return;", 1, "I-tplsame")
    check(interp, "\tif (g_t60_ntpl >= 300)", 1, "I-tplcap")
    check(interp, "\tg_t60_tw[idx] = val;", 1, "I-tplupdate")
    check(interp, "old=0x%x new=0x%x pc=0x%x ra=0x%x a0=%08x", 1, "I-tplfmt")
    check(interp, "old, val, cpuRegs.pc,", 1, "I-tplargs")
    check(ri, "void t60_store_tpl(u32 vaddr, u32 lo, u32 hi); // T60: defined in Interpreter.cpp.", 1, "RI-t60decl")
    check(ri, "\tu32 hi = lo + size;", 1, "RI-storefold")
    check(ri, "\t\tmemRead32(0x80809b70u), memRead32(0x80809b74u), memRead32(0x80809b78u), memRead32(0x80809b7cu));", 1, "RI-dump")
    check(vx, "void t57_vif0_count(u32 cmd); // T57: defined in VU0micro.cpp.", 1, "VX-decl")
    check(vx, "if (idx == 0) t57_vif0_count(vifX.cmd & 0x7f); // T57: VIF0 command census (log-only).", 1, "VX-site")

    # ---- Interpreter.cpp ----
    interp = interp.replace(
        "void t60_app() // T60: called from execI at pc 0x3797ec (log-only).",
        T61_SUM + "void t60_app() // T60: called from execI at pc 0x3797ec (log-only).", 1)
    interp = interp.replace("\tif (g_t60_napp >= 300)", "\tif (g_t60_napp >= 200)", 1)
    interp = interp.replace(
        "\tu32 tw0 = memRead32(t0), tw1 = memRead32(t0 + 4), tw2 = memRead32(t0 + 8), tw3 = memRead32(t0 + 12), tw4 = memRead32(t0 + 16);",
        "\tu32 tw0 = memRead32(t0), tw1 = memRead32(t0 + 4), tw2 = memRead32(t0 + 8), tw3 = memRead32(t0 + 12), tw4 = memRead32(t0 + 16);\n\tt61_app_account((tw0 >> 6) & 0xFu); // T61: census every execution.\n\tt60_arm(t0); // T61: arm before the mode filter (moved up).\n\tif ((tw0 & 0x3C0u) == 0) return; // T61: mode filter.\n\tg_t60_napp++; // T61: count emitted rows only.", 1)
    interp = interp.replace("\tg_t60_napp++;", "", 1)
    interp = interp.replace("\tt60_arm(t0);", "", 1)
    interp = interp.replace("\tif (g_t60_ntpl >= 300)", "\tif (g_t60_ntpl >= 200)", 1)
    interp = interp.replace(
        "\tif (val == g_t60_tw[idx]) return;",
        "\tif (val == g_t60_tw[idx]) return;\n\tu32 ntw0 = (idx == 0) ? val : g_t60_tw[0];\n\tif ((ntw0 & 0x3C0u) == 0) { g_t60_tw[idx] = val; return; } // T61: mode filter (shadow still tracks).", 1)
    interp = interp.replace("\tg_t60_tw[idx] = val;",
                            "\tg_t60_tw[idx] = val;\n\tg_t61_sum_tpl++; // T61: count emitted tpl.", 1)
    interp = interp.replace("old=0x%x new=0x%x pc=0x%x ra=0x%x a0=%08x",
                            "old=0x%x new=0x%x tw0=0x%x tw1=0x%x pc=0x%x ra=0x%x a0=%08x", 1)
    interp = interp.replace("old, val, cpuRegs.pc,",
                            "old, val, g_t60_tw[0], g_t60_tw[1], cpuRegs.pc,", 1)
    open(INTERP, "w", encoding="utf-8").write(interp)

    # ---- RI ----
    ri = ri.replace(
        "void t60_store_tpl(u32 vaddr, u32 lo, u32 hi); // T60: defined in Interpreter.cpp.",
        T61_APC + "void t60_store_tpl(u32 vaddr, u32 lo, u32 hi); // T60: defined in Interpreter.cpp.", 1)
    ri = insert_after_line(ri, "\tu32 hi = lo + size;", T61_APC_RECORD, "RI-apc-record")
    ri = insert_after_line(
        ri, "\t\tmemRead32(0x80809b70u), memRead32(0x80809b74u), memRead32(0x80809b78u), memRead32(0x80809b7cu));",
        "t61_flush_all(); // T61: flush census tails at dump.", "RI-dump-call")
    open(RI, "w", encoding="utf-8").write(ri)

    # ---- Vif_Transfer.cpp ----
    vx = vx.replace(
        "void t57_vif0_count(u32 cmd); // T57: defined in VU0micro.cpp.",
        "void t57_vif0_count(u32 cmd); // T57: defined in VU0micro.cpp.\nvoid t61_vsync_tick(); // T61: defined in Interpreter.cpp.", 1)
    vx = insert_after_line(
        vx, "if (idx == 0) t57_vif0_count(vifX.cmd & 0x7f); // T57: VIF0 command census (log-only).",
        "if (idx == 1) t61_vsync_tick(); // T61: per-vsync census tick (log-only).", "VX-tick")
    open(VXFER, "w", encoding="utf-8").write(vx)

    print("T61 hook applied: INTERP(9) + RI(3) + VXFER(2) ok")


if __name__ == "__main__":
    main()
