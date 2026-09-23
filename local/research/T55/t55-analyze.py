#!/usr/bin/env python3
"""T55 analyze: per-vsync call counts, field distributions, first-5-vsync table."""
import re
import sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "/home/brad/pcsx2-t4/t55-trace.txt"
pat = re.compile(
    r"^h394 vsync=(\d+) tgt=(0x[0-9a-f]+) a0=(0x[0-9a-f]+) s1=(0x[0-9a-f]+) "
    r"w0=(0x[0-9a-f]+) w1=(0x[0-9a-f]+) w2=(0x[0-9a-f]+) w3=(0x[0-9a-f]+) "
    r"hash=(0x[0-9a-f]+) ret=(0x[0-9a-f]+) stores=([01])$")
rows = []
windows = []
cap = None
for line in open(path):
    line = line.strip()
    m = pat.match(line)
    if m:
        rows.append(m.groups())
        continue
    if line.startswith("T51C_WINDOW"):
        windows.append(int(line.split("=")[1]))
    elif line.startswith("T55_CAP"):
        cap = int(line.split("=")[1].split()[0])

print("rows=%d first_vsync=%s last_vsync=%s cap_vsync=%s cwindow=%s" % (
    len(rows), rows[0][0] if rows else None, rows[-1][0] if rows else None,
    cap, windows[:1]))
by_vs = Counter(r[0] for r in rows)
vss = sorted(by_vs, key=int)
print("n_vsyncs=%d" % len(vss))
c = Counter(by_vs.values())
print("calls-per-vsync distribution (calls: n_vsyncs): %s" % sorted(c.items()))
print("first 10 vsyncs: %s" % [(v, by_vs[v]) for v in vss[:10]])
print("last 5 vsyncs: %s" % [(v, by_vs[v]) for v in vss[-5:]])
for i, name in [(1, "tgt"), (2, "a0"), (3, "s1"), (8, "hash"), (9, "ret"), (10, "stores")]:
    print("%s distinct=%d top=%s" % (name, len(set(r[i] for r in rows)),
                                     Counter(r[i] for r in rows).most_common(8)))
print("distinct (s1,w0,w1,w2,w3,hash) tuples=%d" % len(set((r[3], r[4], r[5], r[6], r[7], r[8]) for r in rows)))
print("distinct full rows=%d" % len(set(rows)))
print("stores=1 frac=%.4f" % (sum(1 for r in rows if r[10] == "1") / max(len(rows), 1)))
# stores by hash
sh = Counter((r[8], r[10]) for r in rows)
print("(hash,stores) combos=%d top=%s" % (len(sh), sh.most_common(10)))
# first-5-vsync table
print("=== first 5 vsyncs ===")
for v in vss[:5]:
    _sq = [r for r in rows if r[0] == v]
    print("-- vsync %s n=%d" % (v, len(_sq)))
    for r in _sq[:60]:
        print("  tgt=%s a0=%s s1=%s w0=%s w1=%s w2=%s w3=%s hash=%s ret=%s stores=%s" % r[1:])
    if len(_sq) > 60:
        print("  ... (%d more)" % (len(_sq) - 60))
print("T55_ANALYZE_DONE")
