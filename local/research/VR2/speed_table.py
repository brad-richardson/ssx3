#!/usr/bin/env python3
"""VR2 (VB1's table, shared-driver run dirs): race-window speed from [vsync-rate].

Window: 5 s samples whose end tick is in (1800, 2400]; per run the mean of those
rates, per candidate the mean over runs, as guest vsyncs per wall second and as
x of 59.94. Run dirs: run/<hold>-<n>-<cand>.
"""
import glob
import json
import re
import sys
from collections import defaultdict

LO, HI = 1800, 2400
RATE = re.compile(r'\[vsync-rate\] tick=(\d+) rate=([\d.]+)/s')
root = sys.argv[1] if len(sys.argv) > 1 else 'run'
per = defaultdict(list)
for d in sorted(glob.glob(root + '/H*-*-*')):
    if d.endswith('.txt'):
        continue
    label = d.rsplit('/', 1)[1]
    try:
        res = json.load(open(d + '/result.json'))
    except OSError:
        continue
    cand = label.split('-', 2)[2]
    rows = [(int(t), float(r)) for t, r in RATE.findall(open(d + '/boot.log', errors='replace').read())]
    win = [r for t, r in rows if LO < t <= HI]
    if not win:
        print('%-12s no race-window samples (bound=%s)' % (label, res.get('bound')))
        continue
    mean = sum(win) / len(win)
    per[cand].append(mean)
    print('%-12s n=%d samples=%s mean=%6.2f vs/s = %.3fx bound=%s load=%s runner=%s' % (
        label, len(win), [round(x, 2) for x in win], mean, mean / 59.94, res['bound'],
        [round(x, 1) for x in res['load_start']], res['sha_reads'][0][res['runner']][:12]))
base = sum(per['base']) / len(per['base']) if per.get('base') else None
for cand in sorted(per):
    v = per[cand]
    m = sum(v) / len(v)
    print('%-5s runs=%d mean=%6.2f vs/s = %.3fx%s' % (
        cand, len(v), m, m / 59.94, '' if base is None else '  (%.3fx of base)' % (m / base)))
