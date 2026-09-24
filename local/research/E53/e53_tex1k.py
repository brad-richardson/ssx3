#!/usr/bin/env python3
"""E53 Part 2: TEX1 K distribution from a PS2X_GIF_DUMP (E51 decoder).
K = TEX1 bits 32-43 (signed 7.4 fixed point). Counts per (path, VU1 startPC)
over textured prims, and the distinct K values."""
import sys, os
from collections import Counter, defaultdict
sys.path.insert(0, os.path.expanduser('~/dev/ssx3/local/research/E51'))
import e51_gif as G
gs = G.load_recomp(sys.argv[1])
def kval(tex1):
    k = (tex1 >> 32) & 0xFFF
    return k, (k - 0x1000 if k & 0x800 else k) / 16.0
allk = Counter(); per = defaultdict(Counter)
for p in gs.prims:
    if p.get('adc') or not p.get('tme'):
        continue
    k, _ = kval(p['tex1'])
    allk[k] += 1
    per[(p.get('path'), p.get('pc'))][k] += 1
print(f'textured prims: {sum(allk.values())}, distinct K: {len(allk)}')
print('| K (hex) | K (value) | prims |')
print('|---|---|---|')
for k, n in allk.most_common(20):
    print(f'| 0x{k:03x} | {kval(k << 32)[1]:.2f} | {n} |')
print('\n| path | VU1 startPC | prims | distinct K | top K |')
print('|---|---|---|---|---|')
for key, c in sorted(per.items(), key=lambda kv: -sum(kv[1].values()))[:12]:
    pth, pc = key
    top = ', '.join(f'0x{k:03x}×{n}' for k, n in c.most_common(4))
    print(f'| {pth} | {hex(pc) if pc is not None else "-"} | {sum(c.values())} | {len(c)} | {top} |')
