#!/usr/bin/env python3
"""T64 analyzer: non-churn w0 writers + t2 census around the change."""
import re, sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "t64-trace.txt"
K = int(sys.argv[2]) if len(sys.argv) > 2 else 930
TW = re.compile(r"^tw vsync=(\d+) addr=(0x[0-9a-f]+) vaddr=(0x[0-9a-f]+) old=(0x[0-9a-f]+) new=(0x[0-9a-f]+) via=([A-Za-z0-9-]+) pc=(0x[0-9a-f]+) ra=(0x[0-9a-f]+) (.*)")
T2 = re.compile(r"^t2 vsync=(\d+) w0=(0x[0-9a-f]+) n=(\d+) pcs=(\S+)")

tw, t2 = [], []
for ln in open(path, encoding="utf-8"):
    ln = ln.rstrip("\n")
    m = TW.match(ln)
    if m:
        tw.append(m.groups())
        continue
    m = T2.match(ln)
    if m:
        t2.append(m.groups())
        continue
print("tw=%d t2=%d" % (len(tw), len(t2)))
print("tw span %s..%s; new-values:" % (tw[0][0], tw[-1][0]), Counter(t[4] for t in tw))
print("tw per (pc,new):", Counter((t[6], t[4]) for t in tw).most_common())
print("tw per via:", Counter(t[5] for t in tw))
print("t2 span %s..%s" % (t2[0][0], t2[-1][0]))
nz = [t for t in t2 if int(t[2]) > 0]
print("t2 nonzero-n lines: %d (span %s..%s)" % (len(nz), nz[0][0], nz[-1][0]))
print("== t2 table: 5 before first-nonzero through +8 ==")
i0 = t2.index(nz[0])
for t in t2[max(0, i0 - 5):i0 + 9]:
    print("   vsync=%s(K%+d) w0=%s n=%s pcs=%s" % (t[0], int(t[0]) - K, t[1], t[2], t[3][:90]))
print("== t2 last 5 ==")
for t in t2[-5:]:
    print("   vsync=%s(K%+d) w0=%s n=%s pcs=%s" % (t[0], int(t[0]) - K, t[1], t[2], t[3][:90]))
print("== first 0x1b0 row full ==")
b = [t for t in tw if t[4] == "0x1b0"][0]
print("   vsync=%s(K%+d) old=%s via=%s pc=%s ra=%s" % (b[0], int(b[0]) - K, b[3], b[5], b[6], b[7]))
print("   regs: %s" % b[8][:220])
print("== distinct tw pcs and their ra ==")
for pc in sorted(set(t[6] for t in tw)):
    print("   pc=%s ra=%s" % (pc, set(t[7] for t in tw if t[6] == pc)))
