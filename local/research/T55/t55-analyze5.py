#!/usr/bin/env python3
"""T55 analyze-5: pass-2 stores=1 rows; ret-set parity (in)dependence."""
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "/home/brad/pcsx2-t4/t55-trace.txt"
pat = re.compile(
    r"^h394 vsync=(\d+) tgt=(0x[0-9a-f]+) a0=(0x[0-9a-f]+) s1=(0x[0-9a-f]+) "
    r"w0=(0x[0-9a-f]+) w1=(0x[0-9a-f]+) w2=(0x[0-9a-f]+) w3=(0x[0-9a-f]+) "
    r"hash=(0x[0-9a-f]+) ret=(0x[0-9a-f]+) stores=([01])$")
vs = {}
for line in open(path):
    m = pat.match(line.strip())
    if m:
        g = m.groups()
        vs.setdefault(int(g[0]), []).append(g[1:])
for v in (0, 1):
    print("vsync %d pass-2 stores=1 rows:" % v)
    for r in vs[v][112:]:
        if r[9] == "1":
            print("  s1=%s w0=%s w1=%s w2=%s w3=%s hash=%s ret=%s" % r[2:9])
# ret per (s1) across parity: same slot?
r0 = {r[2]: r[8] for r in vs[0][:112]}
r1 = {r[2]: r[8] for r in vs[1][:112]}
same = sum(1 for k in r0 if r0[k] == r1[k])
print("pass-1 items with identical ret even-vs-odd: %d/112" % same)
print("differing:")
for k in sorted(r0):
    if r0[k] != r1[k]:
        print("  s1=%s even_ret=%s odd_ret=%s" % (k, r0[k], r1[k]))
print("T55_ANALYZE5_DONE")
