#!/usr/bin/env python3
"""T48 shared analyzer: draws/vsync by path (via G12_VSYNC s_n brackets),
top tuples, VU1 cycle/xgkick stats, PATHS window table. Usage: t48-anAB.py A|B"""
import re, statistics as S, sys
from collections import Counter

TAG = sys.argv[1] if len(sys.argv) > 1 else "A"
P = "t48%s-" % TAG.lower()

draw_re = re.compile(r"G12_DRAW n=(\d+) FBP=(\d+) FBW=(\d+) FPSM=(\d+) TBP0=(\d+) TBW=(\d+) TPSM=(\d+) TME=(\d+) PRIM=(\d+) verts=(\d+) path=(-?\d+)")
vsync_re = re.compile(r"G12_VSYNC field=(\d+) idle=(\d+) n=(\d+)")
vu_re = re.compile(r"T48_VU1 vsync=(\d+) start_pc=0x([0-9a-f]+) cycles=(\d+) xgkicks=(\d+) end=(\w+)")
p_re = re.compile(r"T48_PATHS vsync=(\d+) p1_pkts=(\d+) p1_bytes=(\d+) p2_pkts=(\d+) p2_bytes=(\d+) p3_pkts=(\d+) p3_bytes=(\d+) p0_pkts=(\d+) p0_bytes=(\d+)")
q_re = re.compile(r"T48_DUMP_QUEUED vsync=(\d+)")

draws = [m.groups() for l in open(P + "draw.txt") for m in [draw_re.search(l)] if m]
vs = [(int(m.group(3)), int(m.group(1))) for l in open(P + "vsync.txt") for m in [vsync_re.search(l)] if m]
vus = [m.groups() for l in open(P + "vu1.txt") for m in [vu_re.search(l)] if m]
ps = [m.groups() for l in open(P + "paths.txt") for m in [p_re.search(l)] if m]
qs = [int(m.group(1)) for l in open(P + "markers.txt") for m in [q_re.search(l)] if m]
Q = qs[0] if qs else None
print("dump_queued_vs=%s window=%s..%s" % (Q, Q + 1 if Q is not None else None, Q + 8 if Q is not None else None))

# draws per vsync: DRAW n in (vs_n[i], vs_n[i+1]] -> live-vsync i+1; align to dump window via PATHS span
vs_sorted = sorted(vs)
def vsync_of(n):
    import bisect
    keys = [k for k, f in vs_sorted]
    i = bisect.bisect_left(keys, n)
    return i
per_vs = Counter()
per_vs_path = Counter()
for d in draws:
    i = vsync_of(int(d[0]))
    per_vs[i] += 1
    per_vs_path[(i, d[10])] += 1
print("draws=%d path=%s" % (len(draws), Counter(d[10] for d in draws)))
verts = [int(d[9]) for d in draws]
print("verts max=%d mean=%.2f n0=%d miss(path=-2)=%d" % (max(verts), sum(verts) / len(verts), sum(1 for v in verts if v == 0), sum(1 for d in draws if d[10] == '-2')))
print("PRIM:", Counter(d[8] for d in draws))
print("top tuples:", Counter((d[1], d[4], d[8], d[7]) for d in draws).most_common(10))
print("per-live-vsync draws (last 12):", dict(sorted(per_vs.items())[-12:]))

cyc = sorted(int(v[2]) for v in vus)
def pct(q):
    if not cyc:
        return 0
    i = (len(cyc) - 1) * q / 100.0
    lo, hi = int(i), min(int(i) + 1, len(cyc) - 1)
    return cyc[lo] + (cyc[hi] - cyc[lo]) * (i - lo)
print("\nvu1 n=%d ends=%s" % (len(vus), Counter(v[4] for v in vus)))
if cyc:
    print("cycles min=%d med=%s p99=%.1f max=%d over65536=%d" % (cyc[0], S.median(cyc), pct(99), cyc[-1], sum(1 for c in cyc if c > 65536)))
    print("start_pc:", Counter(v[1] for v in vus).most_common(10))
    xg = [int(v[3]) for v in vus]
    print("xg max=%d mean=%.2f n0=%d" % (max(xg), sum(xg) / len(xg), sum(1 for x in xg if x == 0)))
    print("vsync span:", min(int(v[0]) for v in vus), max(int(v[0]) for v in vus))

if Q is not None:
    win = [p for p in ps if Q + 1 <= int(p[0]) <= Q + 8]
    print("\nwindow PATHS rows=%d vsyncs=%s" % (len(win), sorted(set(int(p[0]) for p in win))))
    for p in win:
        print(" vsync=%s p1=%s/%s p2=%s/%s p3=%s/%s p0=%s/%s" % p)
