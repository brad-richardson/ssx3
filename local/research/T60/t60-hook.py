#!/usr/bin/env python3
"""T60 hook (pcsx2-g7, on T59's tree): render-list append trace + template watch.

sub_00376938 (0x379784-0x379820) appends one item per execution; item w0 is
template w0 at append time. At every EE execution of pc 0x3797ec (hooked in
execI next to T55's pc checks):

  app vsync=<n> count=<*a3> t0=0x<> tw0=0x<> .. tw4=0x<> s4=0x<> t1=0x<> ra=0x<>
(a3=GPR7 list header, t0=GPR8 template, s4=GPR20, t1=GPR9, ra=GPR31 raw.)

The template watch arms at the first app (shadow tw[5] via memRead32) and
re-arms when t0 changes (tplrearm line). Every store/DMA range (T58/T59
fold) is also checked against [t0phys,t0phys+20); writes changing tw0/tw1:

  tpl vsync addr old new pc ra a0..a3 v0 v1 s0..s7   (14 regs, E44 format)
  tplrearm vsync old new                              (t0 changed)

Caps: first 300 app (T60_CAPAPP once); tpl+tplrearm share 300
(T60_CAPTPL once). Log-only. Idempotent; validates before writing.
"""

INTERP = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Interpreter.cpp"
RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"

T60_CORE = """
// T60: render-list append trace + render-state template watch (log-only).
static u32 g_t60_napp = 0, g_t60_ntpl = 0;
static bool g_t60_capapp = false, g_t60_captpl = false;
static u32 g_t60_t0v = 0, g_t60_t0p = 0;
static bool g_t60_armed = false;
static u32 g_t60_tw[5] = {0, 0, 0, 0, 0};
static int t60_phys(u32 vaddr, u32* out) // T60: same RAM fold as T59 t58_phys.
{
\tu32 seg = vaddr >> 24;
\tif ((seg == 0x00u || seg == 0x20u || seg == 0x30u || seg == 0x80u || seg == 0xA0u) &&
\t\t(vaddr & 0x00FFFFFFu) < 0x02000000u)
\t{
\t\t*out = vaddr & 0x01FFFFFFu;
\t\treturn 1;
\t}
\treturn 0;
}
static void t60_arm(u32 t0v)
{
\tu32 t0p;
\tif (!t60_phys(t0v, &t0p)) { g_t60_armed = false; return; }
\tif (g_t60_armed && t0v == g_t60_t0v) return;
\tif (g_t60_armed && g_t60_ntpl < 300)
\t{
\t\tg_t60_ntpl++;
\t\tConsole.WriteLn("tplrearm vsync=%d old=0x%x new=0x%x",
\t\t\tg_t48_vsync.load(std::memory_order_relaxed), g_t60_t0v, t0v);
\t}
\tg_t60_t0v = t0v; g_t60_t0p = t0p; g_t60_armed = true;
\tfor (int i = 0; i < 5; i++) g_t60_tw[i] = memRead32(t0v + (u32)(i * 4));
}
static void t60_check(int idx, u32 val)
{
\tif (!g_t60_armed || idx < 0 || idx > 1) return;
\tif (val == g_t60_tw[idx]) return;
\tif (g_t60_ntpl >= 300)
\t{
\t\tif (!g_t60_captpl) { g_t60_captpl = true; Console.WriteLn("T60_CAPTPL vsync=%d", g_t48_vsync.load(std::memory_order_relaxed)); }
\t\treturn;
\t}
\tg_t60_ntpl++;
\tu32 old = g_t60_tw[idx];
\tg_t60_tw[idx] = val;
\tConsole.WriteLn("tpl vsync=%d addr=0x%x old=0x%x new=0x%x pc=0x%x ra=0x%x a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x",
\t\tg_t48_vsync.load(std::memory_order_relaxed), g_t60_t0p + (u32)(idx * 4), old, val, cpuRegs.pc, cpuRegs.GPR.r[31].UL[0], cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0], cpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0], cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0], cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0], cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0]);
}
void t60_app() // T60: called from execI at pc 0x3797ec (log-only).
{
\tif (g_t60_napp >= 300)
\t{
\t\tif (!g_t60_capapp) { g_t60_capapp = true; Console.WriteLn("T60_CAPAPP vsync=%d", g_t48_vsync.load(std::memory_order_relaxed)); }
\t\treturn;
\t}
\tg_t60_napp++;
\tu32 a3 = cpuRegs.GPR.r[7].UL[0];
\tu32 t0 = cpuRegs.GPR.r[8].UL[0];
\tu32 tw0 = memRead32(t0), tw1 = memRead32(t0 + 4), tw2 = memRead32(t0 + 8), tw3 = memRead32(t0 + 12), tw4 = memRead32(t0 + 16);
\tConsole.WriteLn("app vsync=%d count=%u t0=0x%x tw0=0x%x tw1=0x%x tw2=0x%x tw3=0x%x tw4=0x%x s4=0x%x t1=0x%x ra=0x%x",
\t\tg_t48_vsync.load(std::memory_order_relaxed), memRead32(a3), t0, tw0, tw1, tw2, tw3, tw4, cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[9].UL[0], cpuRegs.GPR.r[31].UL[0]);
\tt60_arm(t0);
}
void t60_store_tpl(u32 vaddr, u32 lo, u32 hi) // T60: called from t58_store_watch (log-only).
{
\tif (!g_t60_armed) return;
\tfor (int i = 0; i < 5; i++)
\t{
\t\tu32 w = g_t60_t0p + (u32)(i * 4);
\t\tif (w + 4 <= lo || w >= hi) continue;
\t\tt60_check(i, memRead32(vaddr + (w - lo)));
\t}
}
void t60_dma_tpl(const u8* host, u32 base, u32 bytes) // T60: called from t58_dma_watch (log-only).
{
\tif (!g_t60_armed) return;
\tu32 end = base + bytes;
\tfor (int i = 0; i < 5; i++)
\t{
\t\tu32 w = g_t60_t0p + (u32)(i * 4);
\t\tif (w + 4 <= base || w >= end) continue;
\t\tu32 o = w - base;
\t\tu32 v = (u32)host[o] | ((u32)host[o + 1] << 8) | ((u32)host[o + 2] << 16) | ((u32)host[o + 3] << 24);
\t\tt60_check(i, v);
\t}
}
"""

T60_RI_DECLS = """void t60_store_tpl(u32 vaddr, u32 lo, u32 hi); // T60: defined in Interpreter.cpp.
void t60_dma_tpl(const u8* host, u32 base, u32 bytes); // T60: defined in Interpreter.cpp.
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
    interp = open(INTERP, encoding="utf-8").read()
    ri = open(RI, encoding="utf-8").read()

    # ---- validation pass ----
    assert "t60_" not in interp and "T60" not in interp, "T60 already in Interpreter.cpp"
    assert "t60_" not in ri and "T60_CAPTPL" not in ri, "T60 already in RI"
    assert "t55_mark" in interp, "T55 baseline missing in Interpreter.cpp"
    check(interp, "using namespace R5900;", 1, "INTERP-using")
    check(interp, "\telse if (pc >= 0x394fdc && pc <= 0x394fe8) t55_mark(); // T55: store cluster (log-only).", 1, "INTERP-execI")
    check(ri, "void t58_store_watch(u32 vaddr, u32 size)", 1, "RI-store-def")
    check(ri, "\tu32 hi = lo + size;", 1, "RI-store-fold")
    check(ri, "void t58_dma_watch(u32 base, const u8* host, u32 bytes, const char* via, u32 src)", 1, "RI-dma-def")
    check(ri, "\tu32 end = base + bytes;", 1, "RI-dma-range")

    # ---- write pass: Interpreter.cpp ----
    interp = interp.replace("using namespace R5900;",
                            T60_CORE + "using namespace R5900;", 1)
    interp = insert_after_line(interp,
                               "\telse if (pc >= 0x394fdc && pc <= 0x394fe8) t55_mark(); // T55: store cluster (log-only).",
                               "if (pc == 0x3797ec) t60_app(); // T60: render-list append (log-only).",
                               "INTERP-execI")
    open(INTERP, "w", encoding="utf-8").write(interp)

    # ---- write pass: RI ----
    ri = ri.replace("void t58_store_watch(u32 vaddr, u32 size)",
                    T60_RI_DECLS + "void t58_store_watch(u32 vaddr, u32 size)", 1)
    ri = insert_after_line(ri, "\tu32 hi = lo + size;",
                           "t60_store_tpl(vaddr, lo, hi); // T60: template-word watch (log-only).",
                           "RI-store-tpl")
    ri = insert_after_line(ri, "\tu32 end = base + bytes;",
                           "t60_dma_tpl(host, base, end - base); // T60: template-word watch (log-only).",
                           "RI-dma-tpl")
    open(RI, "w", encoding="utf-8").write(ri)

    print("T60 hook applied: INTERP(2) + RI(3) ok")


if __name__ == "__main__":
    main()
