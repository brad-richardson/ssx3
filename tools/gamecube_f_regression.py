#!/usr/bin/env python3
"""F-candidate regression battery over one probe trace of a movie run.

Checks the invariants a time-normalized 120 Hz arm must hold:
  counter_rate : rider body word 12 (+0x30, race tick stamp) advances at
                 most +1 per ordinary tick (the v3 invariant). A doubled
                 arm without counter normalization stamps +2 (fail). The
                 single 0->N creation jump and frozen pre-ride spans pass.
  repeat_count : with --expect-repeats N, the trace holds exactly N
                 repeats (guest-window driver check).
  restore      : with --rider and --close-t, median rider speed in the 10 s
                 after close must be within --restore-band (default 2x) of
                 the 10 s before (a half-speed tail reads ~0.5x: fail).
  drift        : with --baseline-ev/--baseline-rider, time-aligned cumulative
                 path ratios at deciles (report; --max-drift asserts a bound).

Exit 0 with a JSON verdict on stdout. verdict is pass/fail plus per-check
details; a check without its required inputs reports skipped, never pass.
"""
import argparse
import json
import math
import statistics
import sys
from pathlib import Path

COUNTER_WORD = 12


def load_updates(path):
    rows = []
    with open(path) as stream:
        for line in stream:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get('event') == 'update' and event.get('body_words'):
                rows.append(event)
    rows.sort(key=lambda e: e['tb_start'])
    return rows


def check_counter(rows):
    """Tick-stamp rate over ordinary updates; returns detail dict."""
    ords = [e for e in rows if not e.get('repeat')]
    violations = []
    seen_nonzero = False
    for i in range(1, len(ords)):
        before = ords[i - 1]['body_words'][COUNTER_WORD]
        after = ords[i]['body_words'][COUNTER_WORD]
        if before == 0 and not seen_nonzero:
            if after != 0:
                seen_nonzero = True  # creation jump 0->N: allowed once
            continue
        seen_nonzero = seen_nonzero or after != 0
        step = after - before
        if step < 0 or step > 1:
            violations.append({'tick': i, 'before': before, 'after': after})
            if len(violations) >= 5:
                break
    steps = [ords[i]['body_words'][COUNTER_WORD] - ords[i - 1]['body_words'][COUNTER_WORD]
             for i in range(1, len(ords))
             if not (ords[i - 1]['body_words'][COUNTER_WORD] == 0
                     and ords[i]['body_words'][COUNTER_WORD] != 0)]
    return {'violations': violations,
            'max_step': max(steps) if steps else 0,
            'ticks': len(ords),
            'verdict': 'fail' if violations else 'pass'}


def check_repeats(rows, expect):
    have = sum(1 for e in rows if e.get('repeat'))
    return {'have': have, 'expect': expect,
            'verdict': 'pass' if have == expect else 'fail'}


def load_rider(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    ride = [r for r in rows if r['x'] or r['y'] or r['z']]
    t0 = ride[0]['t']
    return [(r['t'] - t0, (r['x'], r['y'], r['z'])) for r in ride]


def speeds(rider):
    out = []
    for a, b in zip(rider, rider[1:]):
        dt = b[0] - a[0]
        if dt > 0:
            out.append((b[0], math.dist(a[1], b[1]) / dt))
    return out


def check_restore(rider_path, close_t, band):
    series = speeds(load_rider(rider_path))
    pre = [s for t, s in series if close_t - 12 < t < close_t - 2]
    post = [s for t, s in series if close_t + 2 < t < close_t + 12]
    if not pre or not post:
        return {'verdict': 'skipped', 'reason': 'empty pre/post window'}
    ratio = statistics.median(post) / statistics.median(pre)
    return {'pre_median': statistics.median(pre), 'post_median': statistics.median(post),
            'ratio': ratio, 'verdict': 'pass' if 1 / band <= ratio <= band else 'fail'}


def cumulative(rider):
    out, total = [], 0.0
    for a, b in zip(rider, rider[1:]):
        total += math.dist(a[1], b[1])
        out.append((b[0], total))
    return out


def at(series, t):
    prev = 0.0
    for tt, value in series:
        if tt > t:
            return prev
        prev = value
    return prev


def check_drift(rider_path, base_rider_path, bound):
    series, base = cumulative(load_rider(rider_path)), cumulative(load_rider(base_rider_path))
    span = min(series[-1][0], base[-1][0])
    ratios = {}
    for frac in (0.1, 0.25, 0.5, 0.75, 1.0):
        t = span * frac
        ratios[f't{frac}'] = at(series, t) / max(at(base, t), 1)
    worst = max(abs(r - 1) for r in ratios.values())
    detail = {'ratios': ratios, 'worst_deviation': worst}
    if bound is None:
        detail['verdict'] = 'skipped'
    else:
        detail.update(bound=bound, verdict='pass' if worst <= bound else 'fail')
    return detail


def run(args):
    rows = load_updates(args.events)
    report = {'events': str(args.events), 'checks': {}}
    report['checks']['counter_rate'] = check_counter(rows)
    if args.expect_repeats is not None:
        report['checks']['repeat_count'] = check_repeats(rows, args.expect_repeats)
    else:
        report['checks']['repeat_count'] = {'verdict': 'skipped'}
    if args.rider and args.close_t is not None:
        report['checks']['restore'] = check_restore(args.rider, args.close_t, args.restore_band)
    else:
        report['checks']['restore'] = {'verdict': 'skipped'}
    if args.rider and args.baseline_rider:
        report['checks']['drift'] = check_drift(args.rider, args.baseline_rider, args.max_drift)
    else:
        report['checks']['drift'] = {'verdict': 'skipped'}
    verdicts = [c['verdict'] for c in report['checks'].values()]
    report['verdict'] = 'fail' if 'fail' in verdicts else 'pass'
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('events')
    parser.add_argument('--rider', default=None)
    parser.add_argument('--close-t', type=float, default=None)
    parser.add_argument('--restore-band', type=float, default=2.0)
    parser.add_argument('--expect-repeats', type=int, default=None)
    parser.add_argument('--baseline-rider', default=None)
    parser.add_argument('--max-drift', type=float, default=None)
    args = parser.parse_args(argv)
    json.dump(run(args), sys.stdout, indent=2)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
