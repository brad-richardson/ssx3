import sys
p = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/GSState.cpp"
t = open(p, encoding="utf-8").read()
start_mark = "// T51: GS SIGNAL/FINISH/LABEL event tap (log-only; GS thread, free-gate only)."
assert t.count(start_mark) == 1, "block count"
si = t.index(start_mark)
assert t[si-1] == "\n"
si -= 1
end_mark = '\tConsole.WriteLn("gsreg vsync=%d reg=%s", t51_vs, t51rn);\n}\n'
assert t.count(end_mark) == 1, "end count"
ei = t.index(end_mark) + len(end_mark)
block = t[si:ei]
t = t[:si] + t[ei:]
anchor = '#include "common/Console.h"\n'
assert t.count(anchor) == 1, "anchor count=%d" % t.count(anchor)
t = t.replace(anchor, anchor + block, 1)
open(p, "w", encoding="utf-8").write(t)
print("GS block relocated ok")
