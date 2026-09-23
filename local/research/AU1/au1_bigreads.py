#!/usr/bin/env python3
"""AU1: map CD reads inside a BIGF archive to its entries.
Usage: au1_bigreads.py <cdread.txt> <iso-lbn-map.txt> <extracted cd root> <ISO path e.g. /DATA/AUDIO/MUSIC2.BIG>"""
import re, struct, sys, collections
trace, lbnmap, root, isopath = sys.argv[1:5]
base = next(int(l.split()[0], 16) for l in open(lbnmap) if l.split()[3] == isopath)
f = open(root + isopath, "rb"); h = f.read(16); n, ds = struct.unpack(">II", h[8:16]); d = f.read(ds); q = 0; ents = []
for _ in range(n):
    o, s = struct.unpack(">II", d[q:q+8]); q += 8; e = d.index(b"\0", q); ents.append((o, s, d[q:e].decode())); q = e + 1
agg = collections.OrderedDict()
for ln in open(trace):
    m = re.search(r"vsync=(\d+) lbn=0x([0-9a-f]+) sectors=(\d+)", ln)
    if not m: continue
    v, lbn, secs = int(m[1]), int(m[2], 16), int(m[3])
    off = (lbn - base) * 2048
    if off < 0 or off >= f.seek(0, 2): continue
    lo, hi = off, off + secs * 2048
    hit = [nm for o, s, nm in ents if o < hi and lo < o + s] or (["(directory)"] if lo < 16 + ds else ["(gap)"])
    for nm in hit:
        a = agg.setdefault(nm, [0, 0, v, v]); a[0] += 1; a[1] += secs; a[3] = v
print(f"{isopath}: base lbn {base:#x}, {len(ents)} entries")
for nm, (r, s, v0, v1) in agg.items(): print(f"  {nm}: reads={r} sectors={s} vsync {v0}..{v1}")
