#!/usr/bin/env python3
"""VR4: identical-tick windows between Odin legs, from [vsync-rate] epoch lines
(linear interpolation between samples). Usage: ticks.py LEG [LEG ...]"""
import re, sys
W = [(1714, 2400), (2400, 3000), (3000, 4000), (4000, 4500), (1714, 4500)]
def pts(leg):
    p = []
    for line in open(f'logs/{leg}/logcat.txt', errors='replace'):
        m = re.search(r'^\s*(\d+\.\d+).*\[vsync-rate\] tick=(\d+)', line)
        if m: p.append((float(m.group(1)), int(m.group(2))))
    return p
def at(p, tick):
    for (w0, t0), (w1, t1) in zip(p, p[1:]):
        if t0 <= tick <= t1 and t1 > t0: return w0 + (w1 - w0) * (tick - t0) / (t1 - t0)
legs = sys.argv[1:]
print('window        ' + ''.join(f'{l:>22s}' for l in legs))
for a, b in W:
    row = f'{a:>5d}->{b:<5d}  '
    for l in legs:
        p = pts(l); s = at(p, b) - at(p, a)
        row += f'{s:7.2f} s {(b - a) / s:6.2f}/s {(b-a)/s/59.94:5.3f}x'.rjust(22)
    print(row)
