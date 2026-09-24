#!/usr/bin/env python3
"""N5: per-phase guest vsyncs/s from [vsync-rate] lines (logcat -v epoch) + SF present rates.
Usage: phases.py <launch dir>. Phase tick boundaries come from the E33 route anchors
(guest ms x 5994/100000) and the L1 screencaps (see REPORT)."""
import re, sys, json, bisect
d = sys.argv[1]
T0 = json.load(open(f'{d}/meta.json'))['T0']
pts = [(0.0, 0)]
for line in open(f'{d}/logcat.txt', errors='replace'):
    m = re.search(r'^\s*(\d+\.\d+).*\[vsync-rate\] tick=(\d+)', line)
    if m:
        pts.append((float(m.group(1)) - T0, int(m.group(2))))
PH = [('title', 0, 621), ('main menu', 621, 1238), ('Select Character', 1238, 1852),
      ('Select Mode + Select Event', 1852, 3892), ('loading + Rival Challenge dialog', 3892, 7089),
      ('race (from start)', 7089, 10**9)]
def wall_at(tick):
    for (w0, t0), (w1, t1) in zip(pts, pts[1:]):
        if t0 <= tick <= t1 and t1 > t0:
            return w0 + (w1 - w0) * (tick - t0) / (t1 - t0)
    return None
# SF polls: per-poll unique present timestamps -> rate over the ring span
polls, cur = [], None
for line in open(f'{d}/sf-latency.txt', errors='replace'):
    if line.startswith('POLL'):
        m = re.match(r'POLL t=([\d.]+) tick=(\d+)', line); cur = [float(m.group(1)), int(m.group(2)), set()]; polls.append(cur)
    elif cur and '\t' in line:
        try:
            v = int(line.split('\t')[1])
            if 0 < v < 2**62: cur[2].add(v)
        except (ValueError, IndexError): pass
last_tick = pts[-1][1]
print(f'samples={len(pts)-1} last=t+{pts[-1][0]:.1f}s tick={last_tick}')
print('| Phase | Ticks | Wall (s) | Guest vsyncs/s | Ratio (÷59.94) | SF presents/s (polls) |')
print('|---|---|---|---|---|---|')
for name, a, b in PH:
    b = min(b, last_tick)
    wa, wb = wall_at(a), wall_at(b)
    if wa is None or wb is None or wb <= wa: continue
    r = (b - a) / (wb - wa)
    pr = []
    for pw, pt, ts in polls:
        if a <= pt < b and len(ts) > 2:
            s = sorted(ts); span = (s[-1] - s[0]) / 1e9
            if span > 0: pr.append((len(s) - 1) / span)
    prs = f'{min(pr):.1f}–{max(pr):.1f} (n={len(pr)})' if pr else '—'
    print(f'| {name} | {a}→{b} | {wb-wa:.1f} | {r:.2f} | {r/59.94:.3f}× | {prs} |')
wa = wall_at(7089)
if wa:
    print('race per-5s:', ' '.join(f'{(t1-t0)/(w1-w0):.1f}' for (w0,t0),(w1,t1) in zip(pts,pts[1:]) if t0 >= 7089))
