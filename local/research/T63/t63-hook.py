#!/usr/bin/env python3
"""T63 hook (pcsx2-g7, on T62's tree): template-array change watch.

Watch words [0x61c8fc,0x61c94c) (4 templates x 0x14; template 2 w0 =
0x61c910) over every EE store path (t58_store_watch choke point, all
widths, post-write) + T58's DMA paths (t58_dma_watch, host-assembled).
`t63_emit`: tw vsync addr vaddr old new via pc ra + 14 regs. Change-only
vs a shadow baselined one-shot at first execI (pre-all-stores) + a 20-row
`twbase` receipt; 2000 lines total (T63_CAPTW once). Keeps T62's appx /
axfirst / v1b0 / censuses untouched.

TUs: Interpreter.cpp (block + execI baseline), R5900OpcodeImpl.cpp
(protos + 2 calls). Validates before writing.
"""

INTERP = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Interpreter.cpp"
RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"

T63_BLOCK = """
// T63: template-array change watch (log-only).
#define T63_BASE 0x61c8fcu
#define T63_WORDS 20
#define T63_CAPTW 2000
static u32 g_t63_tw[T63_WORDS];
static bool g_t63_based = false;
static u32 g_t63_ntw = 0;
static bool g_t63_captw = false;
static void t63_baseline() // T63: one-shot boot snapshot (log-only).
{
\tg_t63_based = true;
\tfor (int i = 0; i < T63_WORDS; i++)
\t{
\t\tg_t63_tw[i] = memRead32(T63_BASE + (u32)(i * 4));
\t\tConsole.WriteLn("twbase vsync=%d addr=0x%x value=0x%x", g_t48_vsync.load(std::memory_order_relaxed), T63_BASE + (u32)(i * 4), g_t63_tw[i]);
\t}
}
static void t63_emit(int vs, u32 addr, u32 vaddr, u32 old, u32 nw, const char* via, u32 pc) // T63 (log-only).
{
\tConsole.WriteLn("tw vsync=%d addr=0x%x vaddr=0x%x old=0x%x new=0x%x via=%s pc=0x%x ra=0x%x a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x",
\t\tvs, addr, vaddr, old, nw, via, pc, cpuRegs.GPR.r[31].UL[0], cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0], cpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0], cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0], cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0], cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0]);
}
static const char* t63_stvia(u32 size) // T63: store-width tag.
{
\treturn size == 1 ? "st1" : size == 2 ? "st2" : size == 4 ? "st4" : size == 8 ? "st8" : "st16";
}
void t63_store_tw(u32 vaddr, u32 lo, u32 hi) // T63: called from t58_store_watch (log-only).
{
\tif (!g_t63_based || g_t63_ntw >= T63_CAPTW) return;
\tint v = g_t48_vsync.load(std::memory_order_relaxed);
\tfor (int i = 0; i < T63_WORDS; i++)
\t{
\t\tu32 w = T63_BASE + (u32)(i * 4);
\t\tif (w + 4 <= lo || w >= hi) continue;
\t\tu32 nw = memRead32(vaddr + (w - lo));
\t\tif (nw == g_t63_tw[i]) continue;
\t\tif (g_t63_ntw >= T63_CAPTW)
\t\t{
\t\t\tif (!g_t63_captw) { g_t63_captw = true; Console.WriteLn("T63_CAPTW vsync=%d", v); }
\t\t\treturn;
\t\t}
\t\tg_t63_ntw++;
\t\tu32 old = g_t63_tw[i];
\t\tg_t63_tw[i] = nw;
\t\tt63_emit(v, w, vaddr + (w - lo), old, nw, t63_stvia(hi - lo), cpuRegs.pc);
\t}
}
void t63_dma_tw(const u8* host, u32 base, u32 bytes, const char* via) // T63: called from t58_dma_watch (log-only).
{
\tif (!g_t63_based || g_t63_ntw >= T63_CAPTW) return;
\tint v = g_t48_vsync.load(std::memory_order_relaxed);
\tu32 end = base + bytes;
\tfor (int i = 0; i < T63_WORDS; i++)
\t{
\t\tu32 w = T63_BASE + (u32)(i * 4);
\t\tif (w + 4 <= base || w >= end) continue;
\t\tu32 o = w - base;
\t\tu32 nw = (u32)host[o] | ((u32)host[o + 1] << 8) | ((u32)host[o + 2] << 16) | ((u32)host[o + 3] << 24);
\t\tif (nw == g_t63_tw[i]) continue;
\t\tif (g_t63_ntw >= T63_CAPTW)
\t\t{
\t\t\tif (!g_t63_captw) { g_t63_captw = true; Console.WriteLn("T63_CAPTW vsync=%d", v); }
\t\t\treturn;
\t\t}
\t\tg_t63_ntw++;
\t\tu32 old = g_t63_tw[i];
\t\tg_t63_tw[i] = nw;
\t\tt63_emit(v, w, base + o, old, nw, via, cpuRegs.pc);
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
    assert "t63_" not in interp and "T63_CAPTW" not in interp, "T63 already in INTERP"
    assert "t63_" not in ri, "T63 already in RI"
    check(interp, "static void t60_check(int idx, u32 val)", 1, "I-checkdef")
    check(interp, "\tif (pc == 0x37b474) t62_ax(2); // T62: SC appender copy site (log-only).", 1, "I-t62site2")
    check(ri, "void t62_store_v1b0(u32 vaddr, u32 lo, u32 hi); // T62: defined in Interpreter.cpp.", 1, "RI-t62proto")
    check(ri, "\tt62_store_v1b0(vaddr, lo, hi); // T62: exact-0x1b0 value watch (log-only).", 1, "RI-t62call")
    check(ri, "\tt60_dma_tpl(host, base, end - base); // T60: template-word watch (log-only).", 1, "RI-t60dmacall")

    # ---- Interpreter.cpp: T63 block before t60_check + execI baseline ----
    interp = interp.replace(
        "static void t60_check(int idx, u32 val)",
        T63_BLOCK + "static void t60_check(int idx, u32 val)", 1)
    interp = interp.replace(
        "\tif (pc == 0x37b474) t62_ax(2); // T62: SC appender copy site (log-only).",
        "\tif (pc == 0x37b474) t62_ax(2); // T62: SC appender copy site (log-only).\n\tif (!g_t63_based) t63_baseline(); // T63: boot snapshot of template array (log-only).", 1)
    open(INTERP, "w", encoding="utf-8").write(interp)

    # ---- RI: protos + store call + dma call ----
    ri = ri.replace(
        "void t62_store_v1b0(u32 vaddr, u32 lo, u32 hi); // T62: defined in Interpreter.cpp.",
        "void t62_store_v1b0(u32 vaddr, u32 lo, u32 hi); // T62: defined in Interpreter.cpp.\n"
        "void t63_store_tw(u32 vaddr, u32 lo, u32 hi); // T63: defined in Interpreter.cpp.\n"
        "void t63_dma_tw(const u8* host, u32 base, u32 bytes, const char* via); // T63: defined in Interpreter.cpp.", 1)
    ri = ri.replace(
        "\tt62_store_v1b0(vaddr, lo, hi); // T62: exact-0x1b0 value watch (log-only).",
        "\tt62_store_v1b0(vaddr, lo, hi); // T62: exact-0x1b0 value watch (log-only).\n"
        "\tt63_store_tw(vaddr, lo, hi); // T63: template-array change watch (log-only).", 1)
    ri = ri.replace(
        "\tt60_dma_tpl(host, base, end - base); // T60: template-word watch (log-only).",
        "\tt60_dma_tpl(host, base, end - base); // T60: template-word watch (log-only).\n"
        "\tt63_dma_tw(host, base, end - base, via); // T63: template-array change watch (log-only).", 1)
    open(RI, "w", encoding="utf-8").write(ri)

    print("T63 hook applied: INTERP(block+baseline) + RI(protos+2calls) ok")


if __name__ == "__main__":
    main()
