#!/usr/bin/env python3
"""T59 hook (pcsx2-g7, on T58's tree): fix the store fold + end-state dump.

T58's `& 0x1FFFFFFF` fold maps a UCAB store to 0x30809670 -> 0x10809670
(never matches). Per the brief, resolve RAM aliases segment-aware:
  seg = addr>>24 in {0x00,0x20,0x30,0x80,0xA0} and addr below seg-base+32MiB
  -> phys = addr & 0x01FFFFFF; otherwise unmatched.
(KSEG2/supervisor and kuseg>=32MiB stay unmatched: genuinely unknown.)

Also: log the original virtual address as vaddr= in ebw lines (DMA passes
its madr as vaddr), and add a one-shot /tmp/t59-dump-gated end dump
(`ebwend vsync b0=.. b1=..` via memRead32 x8). The gate is checked at most
once per vsync at the top of t58_store_watch/t58_dma_watch (hot paths stay
cheap: one cached vsync compare, fopen only on vsync change).

One TU touched (R5900OpcodeImpl.cpp). Validates before writing.
"""

RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"

OLD_FOLD = """void t58_store_watch(u32 vaddr, u32 size)
{
\tu32 lo = vaddr & 0x1fffffffu;
\tu32 hi = lo + size;
\tfor (int i = 0; i < 8; i++)
\t{
\t\tu32 w = g_t58_off[i];
\t\tif (w + 4 <= lo || w >= hi) continue;
\t\tt58_emit(i, memRead32(vaddr + (w - lo)), "store", 0);
\t}
}"""

NEW_FOLD = """static int t58_phys(u32 vaddr, u32* out) // T59: segment-aware RAM fold.
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
static bool g_t59_dumped = false;
static int g_t59_gate_vs = -1;
static void t59_maybe_dump() // T59: one-shot /tmp/t59-dump end dump (<=1 fopen per vsync).
{
\tif (g_t59_dumped) return;
\tint vs = g_t48_vsync.load(std::memory_order_relaxed);
\tif (vs == g_t59_gate_vs) return;
\tg_t59_gate_vs = vs;
\tFILE* f = fopen("/tmp/t59-dump", "r");
\tif (!f) return;
\tfclose(f);
\tg_t59_dumped = true;
\tConsole.WriteLn("ebwend vsync=%d b0=0x%x 0x%x 0x%x 0x%x b1=0x%x 0x%x 0x%x 0x%x", vs,
\t\tmemRead32(0x80809670u), memRead32(0x80809674u), memRead32(0x80809678u), memRead32(0x8080967cu),
\t\tmemRead32(0x80809b70u), memRead32(0x80809b74u), memRead32(0x80809b78u), memRead32(0x80809b7cu));
}
void t58_store_watch(u32 vaddr, u32 size)
{
\tt59_maybe_dump(); // T59: end-dump gate.
\tu32 lo;
\tif (!t58_phys(vaddr, &lo)) return;
\tu32 hi = lo + size;
\tfor (int i = 0; i < 8; i++)
\t{
\t\tu32 w = g_t58_off[i];
\t\tif (w + 4 <= lo || w >= hi) continue;
\t\tt58_emit(i, memRead32(vaddr + (w - lo)), "store", 0, vaddr);
\t}
}"""

OLD_DMA = """void t58_dma_watch(u32 base, const u8* host, u32 bytes, const char* via, u32 src)
{
\tu32 end = base + bytes;"""

NEW_DMA = """void t58_dma_watch(u32 base, const u8* host, u32 bytes, const char* via, u32 src)
{
\tt59_maybe_dump(); // T59: end-dump gate.
\tu32 end = base + bytes;"""

OLD_EMIT_SIG = "static void t58_emit(int i, u32 val, const char* via, u32 src)"
NEW_EMIT_SIG = "static void t58_emit(int i, u32 val, const char* via, u32 src, u32 vaddr)"

OLD_EMIT_LINE = '\tConsole.WriteLn("ebw vsync=%d addr=0x%x value=0x%x via=%s src=0x%x pc=0x%x ra=0x%x a0=%08x'
NEW_EMIT_LINE = '\tConsole.WriteLn("ebw vsync=%d addr=0x%x value=0x%x via=%s src=0x%x vaddr=0x%x pc=0x%x ra=0x%x a0=%08x'

OLD_EMIT_ARGS = "\t\tvs, w, val, via, src, cpuRegs.pc,"
NEW_EMIT_ARGS = "\t\tvs, w, val, via, src, vaddr, cpuRegs.pc,"

OLD_DMA_CALL = "\t\tt58_emit(i, v, via, src);"
NEW_DMA_CALL = "\t\tt58_emit(i, v, via, src, base); // T59: DMA vaddr is the madr itself."


def check(text, find, want, name):
    n = text.count(find)
    assert n == want, "%s: anchor count=%d, want %d" % (name, n, want)


def main():
    body = open(RI, encoding="utf-8").read()
    assert "t59_maybe_dump" not in body and "t58_phys" not in body and "ebwend" not in body, \
        "T59 already applied"
    assert "t58_store_watch" in body, "T58 baseline missing"
    check(body, OLD_FOLD, 1, "fold")
    check(body, OLD_DMA, 1, "dma")
    check(body, OLD_EMIT_SIG, 1, "emit-sig")
    check(body, OLD_EMIT_LINE, 1, "emit-line")
    check(body, OLD_EMIT_ARGS, 1, "emit-args")
    check(body, OLD_DMA_CALL, 1, "dma-call")
    body = body.replace(OLD_FOLD, NEW_FOLD, 1)
    body = body.replace(OLD_DMA, NEW_DMA, 1)
    body = body.replace(OLD_EMIT_SIG, NEW_EMIT_SIG, 1)
    body = body.replace(OLD_EMIT_LINE, NEW_EMIT_LINE, 1)
    body = body.replace(OLD_EMIT_ARGS, NEW_EMIT_ARGS, 1)
    body = body.replace(OLD_DMA_CALL, NEW_DMA_CALL, 1)
    open(RI, "w", encoding="utf-8").write(body)
    print("T59 hook applied: RI(5) ok")


if __name__ == "__main__":
    main()
