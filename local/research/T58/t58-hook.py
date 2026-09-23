#!/usr/bin/env python3
"""T58 hook (pcsx2-g7, on top of the T57-end working tree = HEAD 9056c083 + T48-T57 hooks).

Who builds the rider items' EE staging buffers (0x809670..0x80967c and
0x809b70..0x809b7c, all aliases) at scene build? Every write path into EE
RAM is watched for those 8 words:

- EE stores: the same 9 interpreter sites as T56 (SB/SH/SW/SWL/SWR/SD/SDL/
  SDR/SQ) + SWC1 (FPU) + SQC2 (VU0). Aliases folded with & 0x1FFFFFFF
  (kuseg/KSEG0/KSEG1; TLB-mapped access would miss, same caveat as T56).
- fromSPR DMA (ch8, SPR->EE): both memcpy_from_spr sites (_SPR0chain,
  _SPR0interleave NO_MFD branch). The MFIFO branch (hwMFIFOWrite) is
  deliberately excluded: it writes the VIF1/GIF MFIFO ring, a streaming
  FIFO consumed by VIF1 unpacks into VU memory, not the EE heap.
- SIF0 DMA (ch5, IOP->EE): WriteFifoToEE in Sif0.cpp (EE dest range).
- SIF2 DMA (ch7, IOP->EE): WriteFifoToEE in sif2.cpp (EE dest range).
- IPU-from DMA (ch3, IPU->EE): dmaIPU0 in IPUdma.cpp (EE dest range).
Excluded with reason: SIF1 (EE->IOP), IPU1/toIPU (EE->IPU), VIF0/VIF1/GIF/
toSPR (EE readers, not writers), USB/FW (no game heap use), EE CACHE ops
(not emulated, T56 precedent).

Line: ebw vsync addr value via=<store|spr-from|sif0|dma-ch7|dma-ch3>
  src=<EE xfer base, 0 for stores> pc ra a0..s7 (24 regs, T56 order).
For DMA, pc/ra/regs are EE interrupt-time state; SIF drains can run on the
IOP thread, where they are whatever the EE was doing concurrently (stated,
not gated). src is the EE-side transfer base (lets the reader verify
addr in [src,src+bytes)); the SPR sadr / IOP-side madr are not logged.

Plus the per-vsync last writer of each word:
  ebwlast vsync addr value via pc ra   (no src/regs by design)
flushed lazily on vsync change (same pattern as T57's census); only vsyncs
with >=1 write emit. Caps: first 64 ebw per word overall (T58_CAP per word),
first 400 ebwlast total (T58_CAPLAST once). T57's VU0/VIF0 hooks stay on
unchanged (own 2000-line budget). Log-only. Idempotent: aborts if applied.
Validates every anchor across all files BEFORE writing anything.
"""

RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"
FPU = "/home/brad/pcsx2-g7/pcsx2/pcsx2/FPU.cpp"
VU0 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU0.cpp"
SPR = "/home/brad/pcsx2-g7/pcsx2/pcsx2/SPR.cpp"
SIF0 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Sif0.cpp"
SIF2 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/sif2.cpp"
IPU = "/home/brad/pcsx2-g7/pcsx2/pcsx2/IPU/IPUdma.cpp"

T58_CORE = """
// T58: EE staging-buffer writer watch (log-only; 8 words + DMA paths).
#include <atomic>
extern std::atomic<int> g_t48_vsync; // T58: defined in GS.cpp (T48 vsync mirror).
static const u32 g_t58_off[8] = {0x809670u, 0x809674u, 0x809678u, 0x80967cu, 0x809b70u, 0x809b74u, 0x809b78u, 0x809b7cu};
static u32 g_t58_hits[8] = {0, 0, 0, 0, 0, 0, 0, 0};
struct t58_last { bool dirty; u32 val; char via[12]; u32 pc; u32 ra; };
static t58_last g_t58_last[8] = {};
static int g_t58_last_vs = -1;
static u32 g_t58_last_n = 0;
static bool g_t58_last_cap = false;
#define T58_MAXLAST 400
static void t58_flush(int vs)
{
\tfor (int i = 0; i < 8; i++)
\t{
\t\tif (!g_t58_last[i].dirty) continue;
\t\tif (g_t58_last_n >= T58_MAXLAST)
\t\t{
\t\t\tif (!g_t58_last_cap) { g_t58_last_cap = true; Console.WriteLn("T58_CAPLAST vsync=%d", vs); }
\t\t\treturn;
\t\t}
\t\tg_t58_last_n++;
\t\tConsole.WriteLn("ebwlast vsync=%d addr=0x%x value=0x%x via=%s pc=0x%x ra=0x%x", vs, g_t58_off[i], g_t58_last[i].val, g_t58_last[i].via, g_t58_last[i].pc, g_t58_last[i].ra);
\t}
}
static void t58_emit(int i, u32 val, const char* via, u32 src)
{
\tu32 w = g_t58_off[i];
\tu32 k = g_t58_hits[i]++;
\tif (k >= 64)
\t{
\t\tif (k == 64) Console.WriteLn("T58_CAP vsync=%d addr=0x%x", g_t48_vsync.load(std::memory_order_relaxed), w);
\t\treturn;
\t}
\tint vs = g_t48_vsync.load(std::memory_order_relaxed);
\tif (g_t58_last_vs < 0) g_t58_last_vs = vs;
\tif (vs != g_t58_last_vs) { t58_flush(g_t58_last_vs); for (int j = 0; j < 8; j++) g_t58_last[j].dirty = false; g_t58_last_vs = vs; }
\tConsole.WriteLn("ebw vsync=%d addr=0x%x value=0x%x via=%s src=0x%x pc=0x%x ra=0x%x a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x t0=%08x t1=%08x t2=%08x t3=%08x t4=%08x t5=%08x t6=%08x t7=%08x t8=%08x t9=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x",
\t\tvs, w, val, via, src, cpuRegs.pc, cpuRegs.GPR.r[31].UL[0], cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0], cpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0], cpuRegs.GPR.r[8].UL[0], cpuRegs.GPR.r[9].UL[0], cpuRegs.GPR.r[10].UL[0], cpuRegs.GPR.r[11].UL[0], cpuRegs.GPR.r[12].UL[0], cpuRegs.GPR.r[13].UL[0], cpuRegs.GPR.r[14].UL[0], cpuRegs.GPR.r[15].UL[0], cpuRegs.GPR.r[24].UL[0], cpuRegs.GPR.r[25].UL[0], cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0], cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0], cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0]);
\tg_t58_last[i].dirty = true; g_t58_last[i].val = val;
\tsnprintf(g_t58_last[i].via, sizeof(g_t58_last[i].via), "%s", via);
\tg_t58_last[i].pc = cpuRegs.pc; g_t58_last[i].ra = cpuRegs.GPR.r[31].UL[0];
}
void t58_store_watch(u32 vaddr, u32 size)
{
\tu32 lo = vaddr & 0x1fffffffu;
\tu32 hi = lo + size;
\tfor (int i = 0; i < 8; i++)
\t{
\t\tu32 w = g_t58_off[i];
\t\tif (w + 4 <= lo || w >= hi) continue;
\t\tt58_emit(i, memRead32(vaddr + (w - lo)), "store", 0);
\t}
}
void t58_dma_watch(u32 base, const u8* host, u32 bytes, const char* via, u32 src)
{
\tu32 end = base + bytes;
\tfor (int i = 0; i < 8; i++)
\t{
\t\tu32 w = g_t58_off[i];
\t\tif (w + 4 <= base || w >= end) continue;
\t\tu32 o = w - base;
\t\tu32 v = (u32)host[o] | ((u32)host[o + 1] << 8) | ((u32)host[o + 2] << 16) | ((u32)host[o + 3] << 24);
\t\tt58_emit(i, v, via, src);
\t}
}
"""

T58_DMA_DECL = "void t58_dma_watch(u32 base, const u8* host, u32 bytes, const char* via, u32 src); // T58: defined in R5900OpcodeImpl.cpp."
T58_STORE_DECL = "void t58_store_watch(u32 vaddr, u32 size); // T58: defined in R5900OpcodeImpl.cpp."

RI_SITES = [
    ('t56_watch(addr, 1, "sb");', "t58_store_watch(addr, 1);"),
    ('t56_watch(addr, 2, "sh");', "t58_store_watch(addr, 2);"),
    ('t56_watch(addr, 4, "sw");', "t58_store_watch(addr, 4);"),
    ('t56_watch(addr & ~3, 4, "swl");', "t58_store_watch(addr & ~3, 4);"),
    ('t56_watch(addr & ~3, 4, "swr");', "t58_store_watch(addr & ~3, 4);"),
    ('t56_watch(addr, 8, "sd");', "t58_store_watch(addr, 8);"),
    ('t56_watch(addr & ~7, 8, "sdl");', "t58_store_watch(addr & ~7, 8);"),
    ('t56_watch(addr & ~7, 8, "sdr");', "t58_store_watch(addr & ~7, 8);"),
    ('t56_watch(addr & ~0xf, 16, "sq");', "t58_store_watch(addr & ~0xf, 16);"),
]


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
    bodies = {}
    for key, path in (("RI", RI), ("FPU", FPU), ("VU0", VU0), ("SPR", SPR),
                      ("SIF0", SIF0), ("SIF2", SIF2), ("IPU", IPU)):
        bodies[key] = open(path, encoding="utf-8").read()

    # ---- validation pass: everything before anything is written ----
    for key, body in bodies.items():
        assert "t58_" not in body and "T58" not in body and "T58_CAPLAST" not in body, \
            "T58 already in %s" % key
    for key in ("RI", "FPU", "VU0"):
        assert "t56_watch" in bodies[key], "T56 baseline missing in %s" % key
    assert "t56_spr_watch" in bodies["SPR"], "T56 baseline missing in SPR"
    check(bodies["RI"], "static void t56_watch(u32 vaddr, u32 size, const char* via)", 1, "RI-core")
    for anchor, _new in RI_SITES:
        check(bodies["RI"], anchor, 1, "RI-site:%s" % anchor)
    check(bodies["FPU"], "static void t56_watch(u32 vaddr, u32 size, const char* via)", 1, "FPU-decl")
    check(bodies["FPU"], 't56_watch(addr, 4, "swc1");', 1, "FPU-site")
    check(bodies["VU0"], "static void t56_watch(u32 vaddr, u32 size, const char* via)", 1, "VU0-decl")
    check(bodies["VU0"], 't56_watch(addr, 16, "sqc2");', 1, "VU0-site")
    check(bodies["SPR"], "static const u32 g_t56s_fixed[8]", 1, "SPR-decl")
    check(bodies["SPR"], "memcpy_from_spr((u8*)pMem, spr0ch.sadr, partialqwc*16);", 1, "SPR-chain")
    check(bodies["SPR"], "memcpy_from_spr((u8*)pMem, spr0ch.sadr, spr0ch.qwc*16);", 1, "SPR-interleave")
    check(bodies["SIF0"], "static __fi bool WriteFifoToEE()", 1, "SIF0-decl")
    check(bodies["SIF0"], "sif0.fifo.read((u32*)ptag, readSize << 2);", 1, "SIF0-site")
    check(bodies["SIF2"], "static __fi bool WriteFifoToEE()", 1, "SIF2-decl")
    check(bodies["SIF2"], "sif2.fifo.read((u32*)ptag, readSize << 2);", 1, "SIF2-site")
    check(bodies["IPU"], "ipu_fifo.out.read(pMem, readsize);", 1, "IPU-site")
    # IPU decl anchor decided at write time (see below).

    # ---- write pass ----
    ri = bodies["RI"].replace(
        "static void t56_watch(u32 vaddr, u32 size, const char* via)",
        T58_CORE + "static void t56_watch(u32 vaddr, u32 size, const char* via)", 1)
    for anchor, new in RI_SITES:
        ri = insert_after_line(ri, anchor,
                               new + " // T58: EE staging-buffer writer watch (log-only).",
                               "RI-site:%s" % anchor)
    open(RI, "w", encoding="utf-8").write(ri)

    fpu = bodies["FPU"].replace(
        "static void t56_watch(u32 vaddr, u32 size, const char* via)",
        T58_STORE_DECL + "\nstatic void t56_watch(u32 vaddr, u32 size, const char* via)", 1)
    fpu = insert_after_line(fpu, 't56_watch(addr, 4, "swc1");',
                            't58_store_watch(addr, 4); // T58: EE staging-buffer writer watch (log-only).',
                            "FPU-site")
    open(FPU, "w", encoding="utf-8").write(fpu)

    vu0 = bodies["VU0"].replace(
        "static void t56_watch(u32 vaddr, u32 size, const char* via)",
        T58_STORE_DECL + "\nstatic void t56_watch(u32 vaddr, u32 size, const char* via)", 1)
    vu0 = insert_after_line(vu0, 't56_watch(addr, 16, "sqc2");',
                            't58_store_watch(addr, 16); // T58: EE staging-buffer writer watch (log-only).',
                            "VU0-site")
    open(VU0, "w", encoding="utf-8").write(vu0)

    spr = bodies["SPR"].replace(
        "static const u32 g_t56s_fixed[8]",
        T58_DMA_DECL + "\nstatic const u32 g_t56s_fixed[8]", 1)
    spr = insert_after_line(spr, "memcpy_from_spr((u8*)pMem, spr0ch.sadr, partialqwc*16);",
                            't58_dma_watch(spr0ch.madr, (const u8*)pMem, (u32)(partialqwc*16), "spr-from", spr0ch.sadr); // T58: fromSPR writer watch (log-only).',
                            "SPR-chain")
    spr = insert_after_line(spr, "memcpy_from_spr((u8*)pMem, spr0ch.sadr, spr0ch.qwc*16);",
                            't58_dma_watch(spr0ch.madr, (const u8*)pMem, (u32)(spr0ch.qwc*16), "spr-from", spr0ch.sadr); // T58: fromSPR writer watch (log-only).',
                            "SPR-interleave")
    open(SPR, "w", encoding="utf-8").write(spr)

    sif0 = bodies["SIF0"].replace(
        "static __fi bool WriteFifoToEE()",
        T58_DMA_DECL + "\nstatic __fi bool WriteFifoToEE()", 1)
    sif0 = insert_after_line(sif0, "sif0.fifo.read((u32*)ptag, readSize << 2);",
                             't58_dma_watch(sif0ch.madr, (const u8*)ptag, (u32)(readSize << 4), "sif0", 0); // T58: SIF0 writer watch (log-only).',
                             "SIF0-site")
    open(SIF0, "w", encoding="utf-8").write(sif0)

    sif2 = bodies["SIF2"].replace(
        "static __fi bool WriteFifoToEE()",
        T58_DMA_DECL + "\nstatic __fi bool WriteFifoToEE()", 1)
    sif2 = insert_after_line(sif2, "sif2.fifo.read((u32*)ptag, readSize << 2);",
                             't58_dma_watch(sif2dma.madr, (const u8*)ptag, (u32)(readSize << 4), "dma-ch7", 0); // T58: SIF2 writer watch (log-only).',
                             "SIF2-site")
    open(SIF2, "w", encoding="utf-8").write(sif2)

    ipu = bodies["IPU"]
    check(ipu, "static __fi int IPU1chain() {", 1, "IPU-decl")
    ipu = ipu.replace("static __fi int IPU1chain() {",
                      T58_DMA_DECL + "\nstatic __fi int IPU1chain() {", 1)
    ipu = insert_after_line(ipu, "ipu_fifo.out.read(pMem, readsize);",
                            't58_dma_watch(ipu0ch.madr, (const u8*)pMem, (u32)(readsize << 4), "dma-ch3", 0); // T58: IPU-from writer watch (log-only).',
                            "IPU-site")
    open(IPU, "w", encoding="utf-8").write(ipu)

    print("T58 hook applied: RI(10) + FPU(2) + VU0(2) + SPR(3) + SIF0(2) + SIF2(2) + IPU(2) ok")


if __name__ == "__main__":
    main()
