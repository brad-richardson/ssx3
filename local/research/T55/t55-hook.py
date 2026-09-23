#!/usr/bin/env python3
"""T55 hook (pcsx2-g7, on top of the T54 working tree = HEAD 9056c083 + T48-T54 hooks).

At the `jal func_394ED0` @0x362f68 (caller sub_00362DE8), per call:
  h394 vsync=<n> tgt=0x<> a0=0x<> s1=0x<> w0=0x.. w1=0x.. w2=0x.. w3=0x..
       hash=0x<a2 & 0xff> ret=0x<v0 at return> stores=<0|1>
  (tgt = jal target, validates 0x394ed0; a0 = s6 per the E43 read;
   s1/a1 = item pointer, w0..w3 = the 4 hashed words;
   stores = 1 if pcs 0x394fdc-0x394fe8 executed during the call.)

Mechanics (all Interpreter.cpp, log-only):
- JAL() entry: cpuRegs.pc == 0x362f6c is the jal @0x362f68 (execI
  pre-increments pc, same convention as T54) -> t55_call(_JumpTarget_)
  arms a pending flag (snapshot deferred to func entry so delay-slot
  arg setup is included).
- execI() entry: pc == 0x394ed0 -> t55_enter() snapshots regs+words;
  pc in [0x394fdc, 0x394fe8] -> t55_mark() sets the stores flag;
  pc == 0x362f70 (return address of the jal) -> t55_ret() logs v0.
- Cap: 8192 h394 lines, then one T55_CAP marker, then silence.

Log-only. Idempotent: aborts if applied. Asserts every anchor count.
"""

INTERP = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Interpreter.cpp"


def check(text, find, want, name):
    n = text.count(find)
    assert n == want, "%s: anchor count=%d, want %d" % (name, n, want)


T55_DECL = """
// T55: func_394ED0 call inputs from jal @0x362f68 (log-only).
static bool g_t55_pending = false; // jal seen, awaiting func entry
static bool g_t55_incall = false; // inside func_394ED0
static int g_t55_vs = -1;
static u32 g_t55_tgt = 0, g_t55_a0 = 0, g_t55_s1 = 0;
static u32 g_t55_w0 = 0, g_t55_w1 = 0, g_t55_w2 = 0, g_t55_w3 = 0;
static u32 g_t55_hash = 0;
static bool g_t55_stores = false;
static u32 g_t55_n = 0; // h394 lines emitted
static void t55_call(u32 tgt)
{
\tg_t55_vs = g_t48_vsync.load(std::memory_order_relaxed);
\tg_t55_tgt = tgt;
\tg_t55_pending = true; // snapshot at func entry (post-delay-slot regs)
}
static void t55_enter()
{
\tif (!g_t55_pending) return;
\tg_t55_pending = false;
\tg_t55_a0 = cpuRegs.GPR.r[4].UL[0];
\tg_t55_s1 = cpuRegs.GPR.r[5].UL[0];
\tu32 s1 = g_t55_s1;
\tg_t55_w0 = memRead32(s1);
\tg_t55_w1 = memRead32(s1 + 4);
\tg_t55_w2 = memRead32(s1 + 8);
\tg_t55_w3 = memRead32(s1 + 12);
\tg_t55_hash = cpuRegs.GPR.r[6].UL[0] & 0xffu;
\tg_t55_stores = false;
\tg_t55_incall = true;
}
static void t55_mark()
{
\tif (g_t55_incall) g_t55_stores = true;
}
static void t55_ret()
{
\tif (!g_t55_incall) return;
\tg_t55_incall = false;
\tif (g_t55_n >= 8192)
\t{
\t\tif (g_t55_n == 8192) Console.WriteLn("T55_CAP vsync=%d", g_t48_vsync.load(std::memory_order_relaxed));
\t\tg_t55_n++;
\t\treturn;
\t}
\tg_t55_n++;
\tConsole.WriteLn("h394 vsync=%d tgt=0x%x a0=0x%x s1=0x%x w0=0x%x w1=0x%x w2=0x%x w3=0x%x hash=0x%x ret=0x%x stores=%u",
\t\tg_t55_vs, g_t55_tgt, g_t55_a0, g_t55_s1, g_t55_w0, g_t55_w1, g_t55_w2, g_t55_w3,
\t\tg_t55_hash, cpuRegs.GPR.r[2].UL[0], g_t55_stores ? 1u : 0u);
}
"""

T55_JAL_HOOK = "\tif (cpuRegs.pc == 0x362f6c) t55_call(_JumpTarget_); // T55: func_394ED0 call site (log-only; jal @0x362f68)."

T55_EXEC_ANCHOR = "\tCBreakPoints::CommitClearSkipFirst(BREAKPOINT_EE);\n#endif\n\n\tconst u32 pc = cpuRegs.pc;"

T55_EXEC_HOOK = ("\n\tif (pc == 0x362f70) t55_ret(); // T55: func_394ED0 return (log-only; ra of jal @0x362f68)."
                 "\n\telse if (pc == 0x394ed0) t55_enter(); // T55: func entry snapshot (log-only)."
                 "\n\telse if (pc >= 0x394fdc && pc <= 0x394fe8) t55_mark(); // T55: store cluster (log-only).")


def main():
    interp = open(INTERP, encoding="utf-8").read()

    assert "t55_call" not in interp, "T55 already in Interpreter.cpp"
    assert "t54_census" in interp, "T54 baseline missing in Interpreter.cpp"
    assert "g_t48_vsync" in interp, "T48 vsync mirror missing in Interpreter.cpp"

    check(interp, "void JAL()\n{", 1, "Interp-JAL")
    check(interp,
          "if (cpuRegs.pc == 0x363cf8) t54_census(cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[19].UL[0]);",
          1, "Interp-T54line")
    check(interp, T55_EXEC_ANCHOR, 1, "Interp-execI")

    interp = interp.replace("void JAL()\n{",
                            T55_DECL + "void JAL()\n{", 1)
    interp = interp.replace(
        "if (cpuRegs.pc == 0x363cf8) t54_census(cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[19].UL[0]);",
        "if (cpuRegs.pc == 0x363cf8) t54_census(cpuRegs.GPR.r[5].UL[0], cpuRegs.GPR.r[19].UL[0]);\n" + T55_JAL_HOOK,
        1)
    interp = interp.replace(T55_EXEC_ANCHOR,
                            T55_EXEC_ANCHOR + T55_EXEC_HOOK, 1)
    open(INTERP, "w", encoding="utf-8").write(interp)

    print("T55 hook applied: Interp(decl + JAL call-site + execI entry/ret/stores) ok")


if __name__ == "__main__":
    main()
