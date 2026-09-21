#!/usr/bin/env python3
"""G13: window the capture-side trace by G12_VSYNC; per-window DRAW tables.

Prints: total line counts; per-window DRAW/RASTER counts + FBP/PRIM/TME
histograms for windows containing G12_DRAW lines (the dump window);
n-gap analysis (Merge bumps); DISPFB0_FBP values.
"""
import re
import sys
from collections import Counter

trace = open(sys.argv[1]).read().splitlines()
wins = []  # ([draw_lines], [raster_lines], vsync_line); draws precede closer
pend_d, pend_r = [], []
for l in trace:
    if 'G12_VSYNC' in l:
        wins.append((pend_d, pend_r, l))
        pend_d, pend_r = [], []
    elif 'G12_DRAW' in l:
        pend_d.append(l)
    elif 'G12_RASTER' in l:
        pend_r.append(l)

print(f"windows={len(wins)}")
# find windows with draws
dw = [(i, w) for i, w in enumerate(wins) if w[1]]
print(f"windows_with_draws={len(dw)} idx={[i for i, _ in dw]}")
for i, (ds, rs, v) in dw:
    fbp = Counter(re.search(r'FBP=(\d+)', l).group(1) for l in ds)
    prim = Counter(re.search(r'PRIM=(\d+)', l).group(1) for l in ds)
    tme = Counter(re.search(r'TME=(\d+)', l).group(1) for l in ds)
    ns = [int(re.search(r'n=(\d+)', l).group(1)) for l in ds]
    rns = set(int(re.search(r'n=(\d+)', l).group(1)) for l in rs)
    unrast = [x for x in ns if x not in rns]
    print(f"win#{i} {v[v.index('G12_VSYNC'):]}")
    print(f"  draws={len(ds)} rasters={len(rs)} n=[{ns[0]}..{ns[-1]}] unrastered={unrast}")
    print(f"  FBP={dict(sorted(fbp.items()))} PRIM={dict(sorted(prim.items()))} TME={dict(sorted(tme.items()))}")
# n-gap check across the draw windows (Merge-IncDraw bumps)
alln = []
for _, (ds, _, _) in dw:
    alln += [int(re.search(r'n=(\d+)', l).group(1)) for l in ds]
gaps = [b - a - 1 for a, b in zip(alln, alln[1:]) if b - a - 1 > 0]
print(f"total_draws={len(alln)} gaps_inside={gaps}")
