#!/usr/bin/env python3
"""E51 tables from e51_gif decoders. Usage:
  e51_tables.py census pcsx2 <dump.gs> | recomp <dump.bin>
"""
import sys, math
from collections import Counter, defaultdict
sys.path.insert(0, __import__('os').path.dirname(__file__))
import e51_gif as G


def census(prims, label):
    per = defaultdict(Counter)
    for p in prims:
        c = per[p['vsync']]
        if p.get('adc'):
            c['adc'] += 1
            continue
        cls, zero = G.classify(p)
        c[cls] += 1
        c['zero'] += zero
    print(f"### All-path prims per vsync, T65 definitions ({label})\n")
    print("| vsync | on | off | straddle | zero-area | adc |")
    print("|---|---|---|---|---|---|")
    for v in sorted(per):
        c = per[v]
        print(f"| {v} | {c['on']} | {c['off']} | {c['straddle']} | {c['zero']} | {c['adc']} |")
    print()


if __name__ == '__main__':
    if sys.argv[1] == 'census':
        if sys.argv[2] == 'pcsx2':
            gs, vram = G.load_pcsx2(sys.argv[3])
        else:
            gs = G.load_recomp(sys.argv[3])
        census(gs.prims, sys.argv[2])
        print('images', len(gs.images))
