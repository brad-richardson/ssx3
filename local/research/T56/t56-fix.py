#!/usr/bin/env python3
"""T56 fix (authoring misses in t56-hook.py, applied tree only).

1. RI call lines rendered as `t56_watch(<args>), "<via>");` (via outside the
   parens). Fix to `t56_watch(<args-minus-paren>, "<via>");` — 9 lines.
2. SPR emit decl rendered as `const char* viau32 srcmadr, )`. Fix to
   `const char* via, u32 srcmadr)`.

Idempotent: aborts if already fixed. Asserts counts.
"""
import re

RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"
SPR = "/home/brad/pcsx2-g7/pcsx2/pcsx2/SPR.cpp"


def main():
    ri = open(RI, encoding="utf-8").read()
    spr = open(SPR, encoding="utf-8").read()

    assert "t56_spr_watch" in spr, "T56 SPR hook missing"
    bad_ri = [ln for ln in ri.split("\n") if "t56_watch(" in ln and "static void" not in ln]
    assert len(bad_ri) == 9, "RI t56 lines=%d, want 9" % len(bad_ri)
    assert all('), "' in ln for ln in bad_ri), "unexpected RI line shape"
    assert "viau32 srcmadr" in spr, "SPR decl already fixed?"

    fixed = 0
    out = []
    for ln in ri.split("\n"):
        if "t56_watch(" in ln and "static void" not in ln and '), "' in ln:
            ln = ln.replace('), "', ', "', 1)
            fixed += 1
        out.append(ln)
    assert fixed == 9, "fixed=%d, want 9" % fixed
    open(RI, "w", encoding="utf-8").write("\n".join(out))

    assert spr.count("const char* viau32 srcmadr, )") == 1
    spr = spr.replace("const char* viau32 srcmadr, )", "const char* via, u32 srcmadr)", 1)
    open(SPR, "w", encoding="utf-8").write(spr)

    print("T56 fix applied: RI 9 call lines + SPR emit decl ok")


if __name__ == "__main__":
    main()
