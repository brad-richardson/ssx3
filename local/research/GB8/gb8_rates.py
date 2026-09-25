#!/usr/bin/env python3
"""GB8 Q1: per-phase guest rates from speed runs.

Phases by guest tick: title [0,636), menus [636,1440), loading [1440,1714),
race-start [1714,1800], race (1800,2400]. Rate per phase = dtick/dwall from the
run's trace.jsonl (0.5 s polls) by linear interpolation at the boundaries.
Also prints the raw 5 s [vsync-rate] means per phase and hud_wall_s.

Usage: gb8_rates.py RUN_DIR [RUN_DIR ...]
"""
import json
import re
import sys
from pathlib import Path

PHASES = [('title', 0, 636), ('menus', 636, 1440), ('loading', 1440, 1714),
          ('race-start', 1714, 1800), ('race', 1800, 2400)]
RATE = re.compile(r'\[vsync-rate\] tick=(\d+) rate=([\d.]+)/s')


def wall_at(trace, tick):
    prev = None
    for wall, tick_now in trace:
        if tick_now >= tick:
            if prev is None:
                return wall
            pw, pt = prev
            if tick_now == pt:
                return wall
            f = (tick - pt) / (tick_now - pt)
            return pw + f * (wall - pw)
        prev = (wall, tick_now)
    return None


def main():
    for d in sys.argv[1:]:
        run = Path(d)
        res = json.load(open(run / 'result.json'))
        trace = [(json.loads(line)['wall_s'], json.loads(line)['tick'])
                 for line in open(run / 'trace.jsonl')]
        print('%s backend=%s bound=%s elapsed=%ss hud_wall=%ss' % (
            run.name, res.get('backend'), res['bound'], res['elapsed_s'],
            res.get('hud_wall_s')))
        rows = [(int(t), float(r)) for t, r in RATE.findall(open(run / 'boot.log').read())]
        for name, lo, hi in PHASES:
            w0, w1 = wall_at(trace, lo), wall_at(trace, hi)
            if w0 is not None and w1 is not None and w1 > w0:
                rate = (hi - lo) / (w1 - w0)
                s = 'trace %6.2f vs/s = %.3fx (wall %.1f->%.1f)' % (rate, rate / 59.94, w0, w1)
            else:
                s = 'trace n/a (w0=%s w1=%s)' % (w0, w1)
            win = [r for t, r in rows if lo < t <= hi] if name != 'title' else \
                [r for t, r in rows if t <= hi]
            r = 'raw n=%d mean=%.2f' % (len(win), sum(win) / len(win)) if win else 'raw none'
            print('  %-10s %s | %s' % (name, s, r))
        print('  load_start=%s load_end=%s runner=%s' % (
            [round(x, 1) for x in res['load_start']], [round(x, 1) for x in res['load_end']],
            res['sha_reads'][0][res['runner']][:12]))


if __name__ == '__main__':
    main()
