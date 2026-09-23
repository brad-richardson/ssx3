#!/usr/bin/env python3
"""T62 hook (pcsx2-g7, on T61's tree): exact-mode-6 post-K window.

1. Appender copy sites 0x3797ec(site0)/0x37ad44(site1)/0x37b474(site2):
   t62_ax() on every execution (v1=GPR3=count, t0=GPR8, tw via memRead32,
   ra=GPR31). Always: template globals + per-site census (site!=0 also feeds
   t61_app_account, so n_app/hist become all-sites; site 0 already counted
   via t60_app). Emits (vsync>=1025 only): `axfirst` (first 2/site, wide
   regs, register-map insurance) + `appx` (count<=1 or mode==6, cap 300).
2. Exact-value store watch: t62_store_v1b0() called from t58_store_watch
   (all EE store widths 1/2/4/8/16, post-write so memRead32 lanes are new
   values; RAM mirrors only, same fold as T58/T60). Per 32-bit lane: hit if
   (v&0x3FF)==0x1b0 anywhere, or template-target [t0p,t0p+20) with mode 6.
   `v1b0` rows, cap 200. Gated vsync>=1025.
3. appsum extended with ax= triple (per-site counts since last emit; reset
   in the emit). n_app/hist now cover all 3 sites (redefined, documented).

TUs: Interpreter.cpp (block + execI sites + appsum format), R5900OpcodeImpl.cpp
(proto + 1 call). Vif_Transfer untouched. Validates before writing.
"""

INTERP = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Interpreter.cpp"
RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"

T62_BLOCK = """
// T62: exact-mode-6 post-K window (log-only; emits only vsync>=1025).
void t61_app_account(u32 m); // T62: fwd (defined in the T61 block below).
#define T62_VSYNC_MIN 1025
#define T62_CAPAX 300
#define T62_CAPV 200
static u32 g_t62_t0v = 0, g_t62_t0p = 0; // template vaddr + folded phys (appx).
static u32 g_t62_ax[3] = {0, 0, 0}; // per-site execs since last appsum emit.
static u32 g_t62_axfirst[3] = {0, 0, 0}; // post-window diagnostic rows/site.
static u32 g_t62_nax = 0, g_t62_nv = 0;
static bool g_t62_capax = false, g_t62_capv = false;
void t62_ax(int site) // T62: appender copy-site census (log-only).
{
\tu32 v1 = cpuRegs.GPR.r[3].UL[0];
\tu32 t0 = cpuRegs.GPR.r[8].UL[0];
\tu32 tw0 = memRead32(t0);
\tu32 m = (tw0 >> 6) & 0xFu;
\tg_t62_t0v = t0;
\tu32 t0p;
\tif (t60_phys(t0, &t0p)) g_t62_t0p = t0p;
\tif (site != 0) t61_app_account(m); // T62: site 0 already counted via t60_app.
\tg_t62_ax[site]++;
\tint v = g_t48_vsync.load(std::memory_order_relaxed);
\tif (v < T62_VSYNC_MIN) return;
\tu32 sitepc = site == 0 ? 0x3797ecu : (site == 1 ? 0x37ad44u : 0x37b474u);
\tif (g_t62_axfirst[site] < 2)
\t{
\t\tg_t62_axfirst[site]++;
\t\tConsole.WriteLn("axfirst vsync=%d site=0x%x v1=%u t0=0x%x tw0=0x%x tw1=0x%x tw2=0x%x s0=0x%x a0=0x%x ra=0x%x", v, sitepc, v1, t0, tw0, memRead32(t0 + 4), memRead32(t0 + 8), cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[31].UL[0]);
\t}
\tif (g_t62_nax >= T62_CAPAX)
\t{
\t\tif (!g_t62_capax) { g_t62_capax = true; Console.WriteLn("T62_CAPAX vsync=%d", v); }
\t\treturn;
\t}
\tif (v1 <= 1 || m == 6)
\t{
\t\tg_t62_nax++;
\t\tConsole.WriteLn("appx vsync=%d site=0x%x count=%u t0=0x%x tw0=0x%x tw1=0x%x tw2=0x%x tw3=0x%x tw4=0x%x ra=0x%x", v, sitepc, v1, t0, tw0, memRead32(t0 + 4), memRead32(t0 + 8), memRead32(t0 + 12), memRead32(t0 + 16), cpuRegs.GPR.r[31].UL[0]);
\t}
}
void t62_store_v1b0(u32 vaddr, u32 lo, u32 hi) // T62: called from t58_store_watch (log-only).
{
\tif (g_t62_nv >= T62_CAPV) return;
\tint v = g_t48_vsync.load(std::memory_order_relaxed);
\tif (v < T62_VSYNC_MIN) return;
\tu32 size = hi - lo;
\tu32 a0 = vaddr & ~3u;
\tu32 a1 = (vaddr + size - 1u) & ~3u;
\tfor (u32 a = a0; ; a += 4)
\t{
\t\tu32 val = memRead32(a);
\t\tu32 ap = lo - (vaddr - a0) + (a - a0);
\t\tbool Gray = ((val & 0x3FFu) == 0x1B0u);
\t\tbool tmpl = (g_t62_t0p != 0 && ap >= g_t62_t0p && ap < g_t62_t0p + 20u && ((val >> 6) & 0xFu) == 6u);
\t\tif (Gray || tmpl)
\t\t{
\t\t\tif (g_t62_nv >= T62_CAPV)
\t\t\t{
\t\t\t\tif (!g_t62_capv) { g_t62_capv = true; Console.WriteLn("T62_CAPV vsync=%d", v); }
\t\t\t\treturn;
\t\t\t}
\t\t\tg_t62_nv++;
\t\t\tConsole.WriteLn("v1b0 vsync=%d addr=0x%x vaddr=0x%x value=0x%x pc=0x%x ra=0x%x a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x",
\t\t\t\tv, ap, a, val, cpuRegs.pc, cpuRegs.GPR.r[31].UL[0], cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0], cpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0], cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0], cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0], cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0]);
\t\t}
\t\tif (a == a1) break;
\t}
}
"""


def check(text, find, want, name):
    n = text.count(find)
    assert n == want, "%s: anchor count=%d, want %d" % (name, n, want)


def main():
    interp = open(INTERP, encoding="utf-8").read()
    ri = open(RI, encoding="utf-8").read()

    # ---- validation pass ----
    assert "t62_" not in interp and "T62_CAP" not in interp, "T62 already in INTERP"
    assert "t62_" not in ri, "T62 already in RI"
    check(interp, "static int t60_phys(u32 vaddr, u32* out)", 1, "I-fold")
    check(interp, "void t61_app_account(u32 m)", 1, "I-accountdef")
    check(interp, "// T61: appsum counters hoisted above first use (log-only).\nstatic u32 g_t61_sum_app = 0, g_t61_sum_tpl = 0;\nstatic void t60_check(int idx, u32 val)", 1, "I-hoist")
    check(interp, "\tif (pc == 0x3797ec) t60_app(); // T60: render-list append (log-only).", 1, "I-execsite")
    check(interp, '\tConsole.WriteLn("appsum vsync=%d n_app=%u n_tpl=%u mode_hist=%s", vs, g_t61_sum_app, g_t61_sum_tpl, first ? "-" : hb);', 1, "I-sumfmt")
    check(ri, "void t60_store_tpl(u32 vaddr, u32 lo, u32 hi); // T60: defined in Interpreter.cpp.", 1, "RI-t60decl")
    check(ri, "\tt60_store_tpl(vaddr, lo, hi); // T60: template-word watch (log-only).", 1, "RI-t60call")

    # ---- Interpreter.cpp: T62 block before t60_check (fwd decl covers later T61 defs) ----
    interp = interp.replace(
        "// T61: appsum counters hoisted above first use (log-only).\nstatic u32 g_t61_sum_app = 0, g_t61_sum_tpl = 0;\nstatic void t60_check(int idx, u32 val)",
        "// T61: appsum counters hoisted above first use (log-only).\nstatic u32 g_t61_sum_app = 0, g_t61_sum_tpl = 0;" + T62_BLOCK + "static void t60_check(int idx, u32 val)", 1)
    # ---- appsum format += ax triple + per-emit site reset ----
    interp = interp.replace(
        '\tConsole.WriteLn("appsum vsync=%d n_app=%u n_tpl=%u mode_hist=%s", vs, g_t61_sum_app, g_t61_sum_tpl, first ? "-" : hb);',
        '\tConsole.WriteLn("appsum vsync=%d n_app=%u n_tpl=%u mode_hist=%s ax=%u,%u,%u", vs, g_t61_sum_app, g_t61_sum_tpl, first ? "-" : hb, g_t62_ax[0], g_t62_ax[1], g_t62_ax[2]);\n\tg_t62_ax[0] = g_t62_ax[1] = g_t62_ax[2] = 0; // T62: per-site counts live between emits.', 1)
    # ---- execI: three site hooks (t60_app line untouched) ----
    interp = interp.replace(
        "\tif (pc == 0x3797ec) t60_app(); // T60: render-list append (log-only).",
        "\tif (pc == 0x3797ec) t60_app(); // T60: render-list append (log-only).\n"
        "\tif (pc == 0x3797ec) t62_ax(0); // T62: site-0 census (log-only).\n"
        "\tif (pc == 0x37ad44) t62_ax(1); // T62: SC appender copy site (log-only).\n"
        "\tif (pc == 0x37b474) t62_ax(2); // T62: SC appender copy site (log-only).", 1)
    open(INTERP, "w", encoding="utf-8").write(interp)

    # ---- RI: prototype + call ----
    ri = ri.replace(
        "void t60_store_tpl(u32 vaddr, u32 lo, u32 hi); // T60: defined in Interpreter.cpp.",
        "void t60_store_tpl(u32 vaddr, u32 lo, u32 hi); // T60: defined in Interpreter.cpp.\nvoid t62_store_v1b0(u32 vaddr, u32 lo, u32 hi); // T62: defined in Interpreter.cpp.", 1)
    ri = ri.replace(
        "\tt60_store_tpl(vaddr, lo, hi); // T60: template-word watch (log-only).",
        "\tt60_store_tpl(vaddr, lo, hi); // T60: template-word watch (log-only).\n\tt62_store_v1b0(vaddr, lo, hi); // T62: exact-0x1b0 value watch (log-only).", 1)
    open(RI, "w", encoding="utf-8").write(ri)

    print("T62 hook applied: INTERP(block+fmt+3sites) + RI(proto+call) ok")


if __name__ == "__main__":
    main()
