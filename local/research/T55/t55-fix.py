#!/usr/bin/env python3
"""T55 fix: move the T55 decl block from before void JAL() to before
static void execI() (execI calls t55_ret/enter/mark and is defined first).
Validate-all-then-write; aborts if already fixed.
"""
INTERP = "/home/brad/pcsx2-g7/pcsx2/pcsx2/Interpreter.cpp"

DECL_START = "\n// T55: func_394ED0 call inputs from jal @0x362f68 (log-only)."


def main():
    interp = open(INTERP, encoding="utf-8").read()
    assert "t55_call" in interp, "T55 decl missing entirely"
    assert interp.count("static void execI()\n{") == 1, "execI anchor count != 1"
    assert interp.count("void JAL()\n{") == 1, "JAL anchor count != 1"

    i = interp.find(DECL_START)
    assert i >= 0, "T55 decl start not found"
    j = interp.find("void JAL()\n{", i)
    assert j > i, "JAL not after decl"
    decl = interp[i:j]
    assert "static void t55_ret()" in decl, "decl slice wrong"
    assert "static void execI()" not in decl, "decl slice overrun"

    interp = interp[:i] + interp[j:]  # remove from JAL site
    assert "static void t55_call" not in interp, "decl removal incomplete"
    interp = interp.replace("static void execI()\n{",
                            decl + "static void execI()\n{", 1)
    open(INTERP, "w", encoding="utf-8").write(interp)
    print("T55 fix applied: decl moved above execI ok")


if __name__ == "__main__":
    main()
