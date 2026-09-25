#!/usr/bin/env python3
"""RP1: draw-level diff of one tick between two PS2XGSC1 captures (before/after a fix).
Prims are compared in order: state key (rd1_draws.key) and per-vertex XYZ/ST/Q/RGBA/fog.
Prints totals, which fields differ, and the differing prims grouped by (TBP, PSM, TEST, FBA, type).
Usage: rp1_primdiff.py <before.cap> <after.cap> <tick>"""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'RD1'))
import rd1_draws as rd
g = rd.g

a_path, b_path, tick = sys.argv[1], sys.argv[2], int(sys.argv[3])
A = [p for p in rd.load_cap(a_path, tick, tick).prims if not p.get('adc')]
B = [p for p in rd.load_cap(b_path, tick, tick).prims if not p.get('adc')]
print('prims before %d after %d' % (len(A), len(B)))
if len(A) != len(B):
    print('prim counts differ: structure changed')
fields = Counter()
groups = Counter()
rgba_zero_before = rgba_zero_after = 0
for pa, pb in zip(A, B):
    diff = []
    if rd.key(pa) != rd.key(pb):
        diff.append('state')
    for va, vb in zip(pa['verts'], pb['verts']):
        for f in ('x', 'y', 'z', 's', 't', 'q', 'u', 'v', 'fog'):
            if va.get(f) != vb.get(f) and f not in diff:
                diff.append(f)
        if (va['rgba'] & 0xFFFFFFFF) != (vb['rgba'] & 0xFFFFFFFF) and 'rgba' not in diff:
            diff.append('rgba')
    if diff:
        for f in diff:
            fields[f] += 1
        t = g.tex0_fields(pa['tex0'])
        groups[(t['tbp0'] if pa['tme'] else -1, t['psm'] if pa['tme'] else -1, pa['test'], pa['fba'], pa['type'],
                tuple(diff))] += 1
        if all((v['rgba'] & 0xFFFFFFFF) == 0 for v in pa['verts']):
            rgba_zero_before += 1
        if all((v['rgba'] & 0xFFFFFFFF) == 0 for v in pb['verts']):
            rgba_zero_after += 1
print('differing prims %d; by field %s' % (sum(groups.values()), dict(fields)))
print('of those, all-zero RGBA: before %d after %d' % (rgba_zero_before, rgba_zero_after))
for (tbp, psm, test, fba, typ, diff), n in groups.most_common(40):
    print('  n=%5d tbp=%s psm=%s test=%#x fba=%d type=%d fields=%s' % (n, tbp, hex(psm) if psm >= 0 else '-', test, fba,
                                                                    typ, ','.join(diff)))
