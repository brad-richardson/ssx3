#!/usr/bin/env python3
"""RR1: per drawing tick, prims per class (tme, tbp0, psm, fst); report classes that
drop to zero on some drawing ticks between their first and last appearance (pop-in/out).
Usage: rr1_flash.py <gs.cap> <from> <to>"""
import sys, os
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(__file__))
import rr1_census as rc, rr1_cap as cap
g = rc.g


def main():
    path, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    per = defaultdict(Counter)
    for t in range(a, b + 1):
        gs, _ = cap.load(path, t, t)
        for p in gs.prims:
            if p.get('adc'):
                continue
            tf = g.tex0_fields(p['tex0'])
            k = (p['tme'], tf['tbp0'] if p['tme'] else -1, tf['psm'] if p['tme'] else -1, p['fst'])
            per[t][k] += 1
    draw = [t for t in range(a, b + 1) if sum(per[t].values()) > 1000]
    print('drawing ticks', len(draw), 'of', b - a + 1, 'prims/tick min/max',
          min(sum(per[t].values()) for t in draw), max(sum(per[t].values()) for t in draw))
    keys = set(k for t in draw for k in per[t])
    gaps = []
    for k in keys:
        seen = [t for t in draw if per[t][k] > 0]
        if len(seen) < 3:
            continue
        span = [t for t in draw if seen[0] <= t <= seen[-1]]
        missing = [t for t in span if per[t][k] == 0]
        if missing:
            gaps.append((len(missing), len(span), k, sum(per[t][k] for t in seen) // len(seen)))
    gaps.sort(reverse=True)
    print('classes with gaps (missing drawing ticks / span, key=(tme,tbp,psm,fst), mean prims when present):', len(gaps))
    for m, s, k, mean in gaps[:15]:
        print(f'  {k} missing {m}/{s} mean {mean}')
    fst = [sum(n for k, n in per[t].items() if k[3] == 1) for t in draw]
    print('FST (2D/HUD-style) prims per drawing tick: min', min(fst), 'max', max(fst))

if __name__ == '__main__':
    main()
