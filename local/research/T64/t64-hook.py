#!/usr/bin/env python3
"""T64 hook (pcsx2-g7, on T63's tree): churn-excluded w0 watch + t2 census.

1. Template-2 w0 (0x61c910) only: tw rows when new NOT in {0,c,cc};
   tw line gains 8 pre-pc instruction words. Cap 200 (T64_CAPTW once).
2. Uncapped per-vsync t2 line (w0 last, write count, distinct pcs) via
   rollover on every store-watch call + dump flush.
3. All other tw emission dropped; shadows kept updating.

Small anchored replaces on T63's block (decls, cap guards, loop bodies,
emit format) + one line in t61_flush_all. Validates before writing.
"""

INTERP = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Interpreter.cpp"
RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"

T64_STATE = """#define T64_CAPW0 200
#define T64W0 0x61c910u
static u32 g_t64_ntw = 0;
static bool g_t64_captw = false;
static int g_t64_vs = -1;
static u32 g_t64_last = 0;
static u32 g_t64_n = 0;
static u32 g_t64_pcs[32] = {0,};
static int g_t64_npc = 0;
static void t64_line(int vs) // T64: emit one t2 census line (log-only).
{
\tchar pb[320]; int o = 0;
\tfor (int i = 0; i < g_t64_npc && o < 300; i++)
\t\to += snprintf(pb + (u32)o, sizeof(pb) - (u32)o, "%s0x%x", i ? "," : "", g_t64_pcs[i]);
\tConsole.WriteLn("t2 vsync=%d w0=0x%x n=%u pcs=%s", vs, g_t64_last, g_t64_n, g_t64_npc ? pb : "-");
}
static void t64_roll(int v) // T64: rollover on vsync change (log-only).
{
\tif (g_t64_vs < 0) { g_t64_vs = v; g_t64_last = memRead32(T64W0); return; }
\tif (v == g_t64_vs) return;
\tt64_line(g_t64_vs);
\tg_t64_vs = v; g_t64_n = 0; g_t64_npc = 0;
}
static void t64_note(u32 nw, u32 pc) // T64: count one w0 write (log-only).
{
\tg_t64_last = nw; g_t64_n++;
\tfor (int k = 0; k < g_t64_npc; k++) if (g_t64_pcs[k] == pc) return;
\tif (g_t64_npc < 32) g_t64_pcs[g_t64_npc++] = pc;
}
static void t64_flush() // T64: dump-time trailing flush (log-only).
{
\tif (g_t64_vs < 0) return;
\tt64_line(g_t64_vs);
\tg_t64_n = 0; g_t64_npc = 0;
}
"""


def check(text, find, want, name):
    n = text.count(find)
    assert n == want, "%s: anchor count=%d, want %d" % (name, n, want)


def main():
    interp = open(INTERP, encoding="utf-8").read()

    # ---- validation pass ----
    assert "t64_" not in interp and "T64_CAPTW" not in interp, "T64 already in INTERP"
    check(interp, "#define T63_CAPTW 2000", 1, "I-t63capdef")
    check(interp, "static u32 g_t63_ntw = 0;\nstatic bool g_t63_captw = false;", 1, "I-t63capdecl")
    check(interp, "\tif (!g_t63_based || g_t63_ntw >= T63_CAPTW) return;\n\tint v = g_t48_vsync.load(std::memory_order_relaxed);", 2, "I-topguard")
    check(interp, "\t\tu32 nw = memRead32(vaddr + (w - lo));\n\t\tif (nw == g_t63_tw[i]) continue;", 1, "I-storerd")
    check(interp, "\t\tu32 nw = (u32)host[o] | ((u32)host[o + 1] << 8) | ((u32)host[o + 2] << 16) | ((u32)host[o + 3] << 24);\n\t\tif (nw == g_t63_tw[i]) continue;", 1, "I-dmard")
    check(interp, "\t\tif (g_t63_ntw >= T63_CAPTW)\n\t\t{\n\t\t\tif (!g_t63_captw) { g_t63_captw = true; Console.WriteLn(\"T63_CAPTW vsync=%d\", v); }\n\t\t\treturn;\n\t\t}", 2, "I-capguard")
    check(interp, "\t\tg_t63_ntw++;\n\t\tu32 old = g_t63_tw[i];\n\t\tg_t63_tw[i] = nw;\n\t\tt63_emit(v, w, vaddr + (w - lo), old, nw, t63_stvia(hi - lo), cpuRegs.pc);", 1, "I-storetail")
    check(interp, "\t\tg_t63_ntw++;\n\t\tu32 old = g_t63_tw[i];\n\t\tg_t63_tw[i] = nw;\n\t\tt63_emit(v, w, base + o, old, nw, via, cpuRegs.pc);", 1, "I-dmatail")
    check(interp, '"tw vsync=%d addr=0x%x vaddr=0x%x old=0x%x new=0x%x via=%s pc=0x%x ra=0x%x a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x",', 1, "I-emitfmt")
    check(interp, "\t\tvs, addr, vaddr, old, nw, via, pc, cpuRegs.GPR.r[31].UL[0], cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0], cpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0], cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0], cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0], cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0]);", 1, "I-emitargs")
    check(interp, "\tt61_apc_flush();", 1, "I-flush")

    # ---- decls: T63 cap -> T64 state ----
    interp = interp.replace("#define T63_CAPTW 2000", T64_STATE, 1)
    interp = interp.replace("static u32 g_t63_ntw = 0;\nstatic bool g_t63_captw = false;", "// T64: T63 2000-cap retired (w0-nonchurn cap is T64_CAPW0 in T64 state above).", 1)
    # ---- fn-top guards: uncap + rollover ----
    interp = interp.replace(
        "\tif (!g_t63_based || g_t63_ntw >= T63_CAPTW) return;\n\tint v = g_t48_vsync.load(std::memory_order_relaxed);",
        "\tif (!g_t63_based) return;\n\tint v = g_t48_vsync.load(std::memory_order_relaxed);\n\tt64_roll(v); // T64: per-vsync t2 line (uncapped).", 2)
    # ---- loop bodies: shadow kept, w0 counted, churn excluded ----
    interp = interp.replace(
        "\t\tu32 nw = memRead32(vaddr + (w - lo));\n\t\tif (nw == g_t63_tw[i]) continue;",
        "\t\tu32 nw = memRead32(vaddr + (w - lo));\n\t\tu32 olds = g_t63_tw[i];\n\t\tg_t63_tw[i] = nw; // T64: shadows kept; only w0-nonchurn emits.\n\t\tif (w != T64W0) continue;\n\t\tt64_note(nw, cpuRegs.pc); // T64: count every w0 write.\n\t\tif (nw == olds || nw == 0u || nw == 0xcu || nw == 0xccu) continue; // T64: churn-excluded.", 1)
    interp = interp.replace(
        "\t\tu32 nw = (u32)host[o] | ((u32)host[o + 1] << 8) | ((u32)host[o + 2] << 16) | ((u32)host[o + 3] << 24);\n\t\tif (nw == g_t63_tw[i]) continue;",
        "\t\tu32 nw = (u32)host[o] | ((u32)host[o + 1] << 8) | ((u32)host[o + 2] << 16) | ((u32)host[o + 3] << 24);\n\t\tu32 oldd = g_t63_tw[i];\n\t\tg_t63_tw[i] = nw;\n\t\tif (w != T64W0) continue;\n\t\tt64_note(nw, cpuRegs.pc);\n\t\tif (nw == oldd || nw == 0u || nw == 0xcu || nw == 0xccu) continue;", 1)
    # ---- cap guards -> T64 w0 cap ----
    interp = interp.replace(
        "\t\tif (g_t63_ntw >= T63_CAPTW)\n\t\t{\n\t\t\tif (!g_t63_captw) { g_t63_captw = true; Console.WriteLn(\"T63_CAPTW vsync=%d\", v); }\n\t\t\treturn;\n\t\t}",
        "\t\tif (g_t64_ntw >= T64_CAPW0)\n\t\t{\n\t\t\tif (!g_t64_captw) { g_t64_captw = true; Console.WriteLn(\"T64_CAPTW vsync=%d\", v); }\n\t\t\treturn;\n\t\t}", 2)
    # ---- tails: use hoisted old ----
    interp = interp.replace(
        "\t\tg_t63_ntw++;\n\t\tu32 old = g_t63_tw[i];\n\t\tg_t63_tw[i] = nw;\n\t\tt63_emit(v, w, vaddr + (w - lo), old, nw, t63_stvia(hi - lo), cpuRegs.pc);",
        "\t\tg_t64_ntw++;\n\t\tt63_emit(v, w, vaddr + (w - lo), olds, nw, t63_stvia(hi - lo), cpuRegs.pc);", 1)
    interp = interp.replace(
        "\t\tg_t63_ntw++;\n\t\tu32 old = g_t63_tw[i];\n\t\tg_t63_tw[i] = nw;\n\t\tt63_emit(v, w, base + o, old, nw, via, cpuRegs.pc);",
        "\t\tg_t64_ntw++;\n\t\tt63_emit(v, w, base + o, oldd, nw, via, cpuRegs.pc);", 1)
    # ---- emit format + args: 8 pre-pc words ----
    interp = interp.replace(
        '"tw vsync=%d addr=0x%x vaddr=0x%x old=0x%x new=0x%x via=%s pc=0x%x ra=0x%x a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x",',
        '"tw vsync=%d addr=0x%x vaddr=0x%x old=0x%x new=0x%x via=%s pc=0x%x ra=0x%x a0=%08x a1=%08x a2=%08x a3=%08x v0=%08x v1=%08x s0=%08x s1=%08x s2=%08x s3=%08x s4=%08x s5=%08x s6=%08x s7=%08x pre=0x%08x,0x%08x,0x%08x,0x%08x,0x%08x,0x%08x,0x%08x,0x%08x",', 1)
    interp = interp.replace(
        "\t\tvs, addr, vaddr, old, nw, via, pc, cpuRegs.GPR.r[31].UL[0], cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0], cpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0], cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0], cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0], cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0]);",
        "\t\tvs, addr, vaddr, old, nw, via, pc, cpuRegs.GPR.r[31].UL[0], cpuRegs.GPR.r[4].UL[0], cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[6].UL[0], cpuRegs.GPR.r[7].UL[0], cpuRegs.GPR.r[2].UL[0], cpuRegs.GPR.r[3].UL[0], cpuRegs.GPR.r[16].UL[0], cpuRegs.GPR.r[17].UL[0], cpuRegs.GPR.r[18].UL[0], cpuRegs.GPR.r[19].UL[0], cpuRegs.GPR.r[20].UL[0], cpuRegs.GPR.r[21].UL[0], cpuRegs.GPR.r[22].UL[0], cpuRegs.GPR.r[23].UL[0], memRead32(pc - 32u), memRead32(pc - 28u), memRead32(pc - 24u), memRead32(pc - 20u), memRead32(pc - 16u), memRead32(pc - 12u), memRead32(pc - 8u), memRead32(pc - 4u));", 1)
    # ---- dump flush ----
    interp = interp.replace(
        "\tt61_apc_flush();",
        "\tt61_apc_flush();\n\tt64_flush(); // T64: flush trailing t2 partial (log-only).", 1)
    open(INTERP, "w", encoding="utf-8").write(interp)

    print("T64 hook applied: INTERP(w0-filter+t2+pre+flush) ok (RI untouched)")


if __name__ == "__main__":
    main()
