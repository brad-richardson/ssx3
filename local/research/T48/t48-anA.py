#!/usr/bin/env python3
"""T48 quick analysis of Capture A extracts."""
import re, statistics as S

W = {}
draw_re = re.compile(r"G12_DRAW n=(\d+) FBP=(\d+) FBW=(\d+) FPSM=(\d+) TBP0=(\d+) TBW=(\d+) TPSM=(\d+) TME=(\d+) PRIM=(\d+) verts=(\d+) path=(-?\d+)")
vu_re = re.compile(r"T48_VU1 vsync=(\d+) start_pc=0x([0-9a-f]+) cycles=(\d+) xgkicks=(\d+) end=(\w+)")
p_re = re.compile(r"T48_PATHS vsync=(\d+) p1_pkts=(\d+) p1_bytes=(\d+) p2_pkts=(\d+) p2_bytes=(\d+) p3_pkts=(\d+) p3_bytes=(\d+) p0_pkts=(\d+) p0_bytes=(\d+)")

draws = [m.groups() for l in open("t48a-draw.txt") for m in [draw_re.search(l)] if m]
print("DRAW n=%d" % len(draws))
from collections import Counter
print("path dist:", Counter(d[10] for d in draws))
verts = [int(d[9]) for d in draws]
print("verts: max=%d mean=%.2f n0=%d/%d" % (max(verts), sum(verts)/len(verts), sum(1 for v in verts if v==0), len(verts)))
print("PRIM dist:", Counter(d[8] for d in draws))
print("top (FBP,TBP0,PRIM,TME):", Counter((d[1],d[4],d[8],d[7]) for d in draws).most_common(8))

vus = [m.groups() for l in open("t48a-vu1.txt") for m in [vu_re.search(l)] if m]
print("\nVU1 n=%d" % len(vus))
print("end dist:", Counter(v[4] for v in vus))
cyc = sorted(int(v[2]) for v in vus)
def pct(q):
    i = (len(cyc)-1)*q/100.0
    lo, hi = int(i), min(int(i)+1, len(cyc)-1)
    return cyc[lo] + (cyc[hi]-cyc[lo])*(i-lo)
print("cycles: min=%d med=%s p99=%.1f max=%d over65536=%d" % (cyc[0], S.median(cyc), pct(99), cyc[-1], sum(1 for c in cyc if c>65536)))
print("start_pc dist:", Counter(v[1] for v in vus).most_common(10))
xg = [int(v[3]) for v in vus]
print("xgkicks: max=%d mean=%.2f n0=%d" % (max(xg), sum(xg)/len(xg), sum(1 for x in xg if x==0)))
print("vsync span:", min(int(v[0]) for v in vus), max(int(v[0]) for v in vus))
print("per-vsync VU1:", Counter(int(v[0]) for v in vus))

ps = [m.groups() for l in open("t48a-paths.txt") for m in [p_re.search(l)] if m]
print("\nPATHS n=%d span=%s..%s" % (len(ps), ps[0][0], ps[-1][0]))
win = [p for p in ps if 18808 <= int(p[0]) <= 18815]
print("window vsyncs present:", sorted(set(int(p[0]) for p in win)))
for p in win:
    print(" vsync=%s p1=%s/%s p2=%s/%s p3=%s/%s p0=%s/%s" % p)
