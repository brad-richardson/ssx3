#!/usr/bin/env python3
"""T61 fix2: hoist decls above first use + restore moved-up arm.

1. Interpreter.cpp: `g_t61_sum_tpl++` (t60_check) precedes the T61_SUM block
   that defines it -> move the counters' definition above t60_check.
2. Interpreter.cpp: applier's `("\\tg_t60_napp++;", "", 1)`-style cleanup ate
   the moved-up `t60_arm(t0);` (first occurrence), leaving the trailing one ->
   restore the moved-up arm, drop the trailing double-arm (exactly one arm).
3. R5900OpcodeImpl.cpp: `t61_flush_all()` call in t59_maybe_dump precedes the
   prototype inside the T61_APC block -> move prototype to file scope above
   t59_maybe_dump (global scope: block is above line 744 namespaces).
Validates every anchor before writing.
"""

INTERP = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Interpreter.cpp"
RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"


def check(text, find, want, name):
    n = text.count(find)
    assert n == want, "%s: anchor count=%d, want %d" % (name, n, want)


def main():
    interp = open(INTERP, encoding="utf-8").read()
    ri = open(RI, encoding="utf-8").read()

    # ---- validation pass (anchors verified against view-t61/view2 output) ----
    check(interp, "static u32 g_t61_sum_app = 0, g_t61_sum_tpl = 0;\n", 1, "I-sumdef")
    check(interp, "static void t60_check(int idx, u32 val)", 1, "I-checkdef")
    check(interp, "t61_app_account((tw0 >> 6) & 0xFu); // T61: census every execution.\n // T61: arm before the mode filter (moved up).", 1, "I-brokenarm")
    check(interp, "cpuRegs.GPR.r[31].UL[0]);\n\tt60_arm(t0);\n}", 1, "I-trailarm")
    check(ri, "static int g_t61_apc_vs = -1;\nvoid t61_flush_all(void); // T61: defined in Interpreter.cpp.\nstatic void t61_apc_emit", 1, "RI-apcproto")
    check(ri, "static bool g_t59_dumped = false;", 1, "RI-dumphead")

    # ---- Interpreter.cpp: hoist counters above template watch ----
    interp = interp.replace("static u32 g_t61_sum_app = 0, g_t61_sum_tpl = 0;\n", "", 1)
    interp = interp.replace(
        "static void t60_check(int idx, u32 val)",
        "// T61: appsum counters hoisted above first use (log-only).\n"
        "static u32 g_t61_sum_app = 0, g_t61_sum_tpl = 0;\n"
        "static void t60_check(int idx, u32 val)", 1)
    # ---- Interpreter.cpp: restore moved-up arm, drop trailing double-arm ----
    interp = interp.replace(
        "t61_app_account((tw0 >> 6) & 0xFu); // T61: census every execution.\n // T61: arm before the mode filter (moved up).",
        "t61_app_account((tw0 >> 6) & 0xFu); // T61: census every execution.\n\tt60_arm(t0); // T61: arm before the mode filter (moved up).", 1)
    interp = interp.replace(
        "cpuRegs.GPR.r[31].UL[0]);\n\tt60_arm(t0);\n}",
        "cpuRegs.GPR.r[31].UL[0]);\n}", 1)
    check(interp, "\tt60_arm(t0);", 1, "I-armfinal")

    # ---- RI: move prototype to file scope above t59_maybe_dump ----
    ri = ri.replace(
        "static int g_t61_apc_vs = -1;\nvoid t61_flush_all(void); // T61: defined in Interpreter.cpp.\nstatic void t61_apc_emit",
        "static int g_t61_apc_vs = -1;\nstatic void t61_apc_emit", 1)
    ri = ri.replace(
        "static bool g_t59_dumped = false;",
        "void t61_flush_all(void); // T61: hoisted prototype (defined in Interpreter.cpp).\nstatic bool g_t59_dumped = false;", 1)
    check(ri, "void t61_flush_all(void);", 1, "RI-protofinal")

    open(INTERP, "w", encoding="utf-8").write(interp)
    open(RI, "w", encoding="utf-8").write(ri)
    print("T61 fix2 applied: INTERP(hoist+arm) + RI(proto-move) ok")


if __name__ == "__main__":
    main()
