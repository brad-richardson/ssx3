#!/usr/bin/env python3
"""FS2: race-window sync-line counters per present and per guest frame.

Reads a launch's logcat.txt: `[gs:parallel] sync presents=N key=value...` lines
(per-present deltas since the previous line) and `[vsync-rate] tick=T` lines
(for the tick at each sync line, interpolated on the logcat epoch). Prints, for
sync lines whose interval lies in ticks [lo, hi], the present-weighted mean of
each *_ms_per_present key and the same in ms per guest frame
(ms/present x presents / ticks over the interval).

usage: syncsum.py LOGDIR [--lo 1900] [--hi 4500]
"""
import argparse, re

ap = argparse.ArgumentParser()
ap.add_argument('logdir')
ap.add_argument('--lo', type=int, default=1900)
ap.add_argument('--hi', type=int, default=4500)
a = ap.parse_args()

ticks, syncs = [], []
for line in open(f'{a.logdir}/logcat.txt', errors='replace'):
    m = re.match(r'\s*(\d+\.\d+)\s.*\[vsync-rate\] tick=(\d+)', line)
    if m:
        ticks.append((float(m.group(1)), int(m.group(2))))
        continue
    m = re.match(r'\s*(\d+\.\d+)\s.*\[gs:parallel\] sync (.*)', line)
    if m:
        kv = dict(x.split('=', 1) for x in m.group(2).split() if '=' in x)
        syncs.append((float(m.group(1)), kv))


def tick_at(t):
    for (t0, k0), (t1, k1) in zip(ticks, ticks[1:]):
        if t0 <= t <= t1:
            return k0 + (k1 - k0) * (t - t0) / (t1 - t0)
    return None


rows = []
prev = None
for t, kv in syncs:
    k = tick_at(t)
    p = int(kv['presents'])
    if prev and k is not None and prev[1] is not None and prev[1] >= a.lo and k <= a.hi:
        rows.append((prev[1], k, p - prev[2], kv))
    prev = (t, k, p)

keys = [k for k in syncs[-1][1] if k.endswith('_per_present')] if syncs else []
tot_p = sum(r[2] for r in rows)
tot_k = sum(r[1] - r[0] for r in rows)
print(f'window ticks {rows[0][0]:.0f}->{rows[-1][1]:.0f} ({len(rows)} sync intervals, '
      f'{tot_p} presents, {tot_k:.0f} frames, {tot_p / tot_k:.3f} presents/frame)' if rows else 'no rows')
for key in keys:
    if not all(key in r[3] for r in rows):
        continue
    per_present = sum(float(r[3][key]) * r[2] for r in rows) / tot_p
    unit = 'ms' if '_ms_' in key else 'n'
    print(f'{key:36s} {per_present:10.4f} /present {per_present * tot_p / tot_k:10.4f} {unit}/frame')
