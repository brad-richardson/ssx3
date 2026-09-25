#!/usr/bin/env python3
"""E57 (copied for VR1): race-window speed from [vsync-rate] lines (speed runs only).

Window: 5 s samples whose end tick is in (LO, HI]; rate = sum(ticks)/sum(seconds) is
approximated as the mean of the 5 s rates (equal-length samples). Prints per run and per
candidate mean, in guest vsyncs per wall second and as x of 59.94.
"""
import glob
import json
import re
import sys
from collections import defaultdict

LO, HI = 1800, 2400
RATE = re.compile(r'\[vsync-rate\] tick=(\d+) rate=([\d.]+)/s')
per = defaultdict(list)
for d in sorted(glob.glob(sys.argv[1] + '/s*-*')):
    label = d.rsplit('/', 1)[1]
    try:
        open(d + '/result.json').close()
    except OSError:
        continue
    cand = label.split('-', 1)[1]
    rows = [(int(t), float(r)) for t, r in RATE.findall(open(d + '/boot.log').read())]
    win = [r for t, r in rows if LO < t <= HI]
    res = json.load(open(d + '/result.json'))
    if not win:
        continue
    mean = sum(win) / len(win)
    per[cand].append(mean)
    print('%-10s n=%2d mean=%6.2f vs/s = %.3fx  bound=%s load=%s runner=%s' % (
        label, len(win), mean, mean / 59.94, res['bound'],
        [round(x, 1) for x in res['load_start']], res['sha_reads'][0][res['runner']][:12]))
base = sum(per['base']) / len(per['base']) if per.get('base') else None
for cand, v in per.items():
    m = sum(v) / len(v)
    print('%-5s runs=%d mean=%6.2f vs/s = %.3fx%s' % (
        cand, len(v), m, m / 59.94, '' if base is None else '  (%.2fx of base)' % (m / base)))
