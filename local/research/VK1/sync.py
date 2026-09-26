#!/usr/bin/env python3
"""VK1 Part 2A: race-window means of the backend's `[gs:parallel] sync` lines
(one line per 300 presents, values per present since the previous line) and
the whole-run race rate from F4's phases.py method. Lines count toward the
race when the last [vsync-rate] tick before them is >= --from (default 1800).
Usage: sync.py logs/A1 [logs/A2 ...]
"""
import re
import sys

SYNC = re.compile(r'\[gs:parallel\] sync presents=(\d+) frame_contexts=(\d+) flush_submits_per_present=([\d.e+-]+) '
                  r'frame_ctx_advances_per_present=([\d.e+-]+) frame_ctx_wait_ms_per_present=([\d.e+-]+) '
                  r'timeline_waits_per_present=([\d.e+-]+) timeline_wait_ms_per_present=([\d.e+-]+)'
                  r'(?: flush_submit_ms_per_present=([\d.e+-]+) iface_flush_ms_per_present=([\d.e+-]+) '
                  r'iface_vsync_ms_per_present=([\d.e+-]+))?')
RATE = re.compile(r'\[vsync-rate\] tick=(\d+)')
PRES = re.compile(r'present_ms_avg=([\d.e+-]+)')

args = [a for a in sys.argv[1:] if not a.startswith('--')]
start = 1800
for d in args:
    tick = 0
    rows = []
    fc = '?'
    for line in open(f'{d}/logcat.txt', errors='replace'):
        m = RATE.search(line)
        if m:
            tick = int(m.group(1))
        m = SYNC.search(line)
        if m:
            fc = m.group(2)
            if tick >= start:
                rows.append([float(x) if x is not None else float('nan') for x in m.groups()[2:]])
    if not rows:
        print(f'{d}: no race sync lines')
        continue
    n = len(rows)
    mean = [sum(r[i] for r in rows) / n for i in range(8)]
    print(f'{d}: frame_contexts={fc} race lines={n}: flush_submits/present {mean[0]:.2f}, '
          f'frame-ctx advances/present {mean[1]:.2f}, frame-ctx wait {mean[2]:.2f} ms/present, '
          f'timeline waits/present {mean[3]:.2f}, timeline wait {mean[4]:.2f} ms/present'
          + ('' if mean[5] != mean[5] else f', flush_submit wall {mean[5]:.1f} ms/present, '
             f'Present: iface flush {mean[6]:.1f} ms, vsync {mean[7]:.2f} ms'))
