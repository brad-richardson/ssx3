#!/usr/bin/env python3
"""T53b: tag each tagaddrwrite line with its originating TU (ri/swc1/sqc2).

T53 capture #1 proved single-pc writers but all three TUs armed, so the path
(SW vs SWC1 vs SQC2) is undetermined. Appends one trailing field ` tu=XX` to
the three tagaddrwrite format literals (prefix-compatible with the T53
grammar). Log-only. Idempotent: aborts if applied.
"""

RI = "/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp"
FPU = "/home/brad/pcsx2-g7/pcsx2/pcsx2/FPU.cpp"
VU0 = "/home/brad/pcsx2-g7/pcsx2/pcsx2/VU0.cpp"

HEAD = 'Console.WriteLn("tagaddrwrite vsync='


def tag(path, tu):
    text = open(path, encoding="utf-8").read()
    assert " tu=%s" % tu not in text, "T53b already in %s" % path
    n = text.count(HEAD)
    assert n == 1, "%s: head count=%d, want 1" % (path, n)
    i = text.index(HEAD)
    j = text.index('",\n', i)
    assert j - i < 600, "%s: format literal longer than 600 chars" % path
    text = text[:j] + " tu=" + tu + text[j:]
    open(path, "w", encoding="utf-8").write(text)
    print("tagged %s tu=%s" % (path, tu))


tag(RI, "ri")
tag(FPU, "swc1")
tag(VU0, "sqc2")
print("T53b applied ok")
