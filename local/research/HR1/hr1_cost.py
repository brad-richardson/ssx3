#!/usr/bin/env python3
"""HR1 cost table from a boot/console log: race-window ([lo, hi] ticks) guest vsyncs/s
(mean of [vsync-rate] 5 s samples) and per-thread CPU % over the same window from the
paired [thread-cpu] lines (cumulative ms; delta / (5 s x intervals)). Also main-thread
latch-wait and upload ms per latched frame, and the backend's last periodic line.
Usage: hr1_cost.py LABEL=LOG [...] [--lo 1800 --hi 2400]"""
import re, sys

lo, hi = 1800, 2450
args = []
it = iter(sys.argv[1:])
for a in it:
    if a == '--lo': lo = int(next(it))
    elif a == '--hi': hi = int(next(it))
    else: args.append(a)

RATE = re.compile(r'\[vsync-rate\] tick=(\d+) rate=([\d.]+)/s')
TCPU = re.compile(r'\[thread-cpu\] tick=(\d+) (.*) \| main_latch_ms=(\d+) main_upload_ms=(\d+) uploads=(\d+)')
PER = re.compile(r'\[gs:parallel\] periodic .*present_ms_avg=([\d.]+) readback_ms_avg=([\d.]+) copy_ms_avg=([\d.]+)')

def group(name):
    base = name.split('#')[0]
    if base in ('GameThread', 'GsWorker'): return base
    if name == 't#0': return 'main'
    return 'other'

print('| Run | race vs/s (x) | n | GameThread % | GsWorker % | main % | other % | latch ms/frame | upload ms/frame | present/readback/copy ms (backend avg) |')
print('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
for spec in args:
    label, path = spec.split('=', 1)
    text = open(path, errors='replace').read()
    rates = [(int(t), float(r)) for t, r in RATE.findall(text) if lo < int(t) <= hi]
    tc = []
    for m in TCPU.finditer(text):
        tick = int(m.group(1))
        th = {}
        for tok in m.group(2).split():
            n, _, v = tok.rpartition('=')
            th[group(n)] = th.get(group(n), 0.0) + float(v)
        tc.append((tick, th, int(m.group(3)), int(m.group(4)), int(m.group(5))))
    # window: thread-cpu samples whose tick falls in [lo, hi]; first one is the baseline
    w = [x for x in tc if lo <= x[0] <= hi]
    cells = ['-'] * 6
    if len(w) >= 2:
        a, b = w[0], w[-1]
        wall_ms = 5000.0 * (len(w) - 1)
        pct = {k: 100.0 * (b[1].get(k, 0) - a[1].get(k, 0)) / wall_ms for k in ('GameThread', 'GsWorker', 'main', 'other')}
        up = max(1, b[4] - a[4])
        cells = ['%.0f' % pct['GameThread'], '%.0f' % pct['GsWorker'], '%.0f' % pct['main'], '%.0f' % pct['other'],
                 '%.2f' % ((b[2] - a[2]) / up), '%.2f' % ((b[3] - a[3]) / up)]
    per = PER.findall(text)
    mean = sum(r for _, r in rates) / len(rates) if rates else 0.0
    print('| %s | %.2f (%.3fx) | %d | %s | %s |' % (label, mean, mean / 59.94, len(rates), ' | '.join(cells),
          '/'.join(per[-1]) if per else '-'))
