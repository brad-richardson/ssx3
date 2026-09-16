#!/usr/bin/env python3
"""Guest-time-aligned gameplay parity between two probe traces of one movie.

VI retrace paces update ticks to one per 1/60 guest second in every arm, and
same-movie runs share the boot timebase epoch, so the ABSOLUTE guest
timebase (tb_start) is the alignment grid — no per-run normalization (a
host-window edge can fall on different guest ticks per arm, which
normalization would misalign). End states compare by body_hash_after of
the tick's LAST body (the repeat row when a tick re-enters, the ordinary
row otherwise). HALF_CADENCE skip rows never ran a body and are left off
the grid, reported as skipped_rows_a/b.

Usage:
  gamecube_parity_compare.py A.jsonl B.jsonl [--telemetry A-rider.jsonl B-rider.jsonl]
      [--start 145] [--end 170] [--out report.json]

Exit 0 with a JSON report on stdout. Telemetry summaries are host-timed and
coarse; the hash alignment is the strict gate.
"""
import argparse
import json
import math
import statistics
import sys

TB_TICK = 40500000 // 60  # guest ticks per VI-paced update tick


def load_updates(path, start, end):
    rows = []
    with open(path) as fh:
        for line in fh:
            r = json.loads(line)
            if r['event'] == 'update' and start <= r['wall'] <= end:
                rows.append(r)
    return rows


def group_ticks(rows):
    """Ordinary row plus its immediately following repeats = one tick.

    A HALF_CADENCE skip row carries repeat=0 like an ordinary update, but the
    guest body never ran, so its end state is its start state. Counting one as
    a tick of its own would put a no-op on the alignment grid opposite a base
    tick that did advance, and the wrong-control arm would read as divergent
    for a bookkeeping reason rather than a simulation one. They are dropped
    from the grid and counted, so the surviving ticks keep their real tb_start.
    """
    ticks, skipped = [], 0
    for r in rows:
        if r.get('skipped_update'):
            skipped += 1
        elif not r['repeat']:
            ticks.append([r])
        elif ticks:
            ticks[-1].append(r)
    return ticks, skipped


def tick_key(tick):
    return tick[0]['tb_start']


def compare(a_path, b_path, start=145, end=170, telemetry=()):
    a_ticks, a_skipped = group_ticks(load_updates(a_path, start, end))
    b_ticks, b_skipped = group_ticks(load_updates(b_path, start, end))
    report = {'ticks_a': len(a_ticks), 'ticks_b': len(b_ticks),
              'skipped_rows_a': a_skipped, 'skipped_rows_b': b_skipped}
    if not a_ticks or not b_ticks:
        return dict(report, verdict='no-ticks')
    b_keys = [tick_key(t) for t in b_ticks]
    import bisect
    matched = exact = 0
    first_div = None
    for i, ta in enumerate(a_ticks):
        ka = tick_key(ta)
        j = bisect.bisect_left(b_keys, ka)
        cands = [k for k in (j - 1, j) if 0 <= k < len(b_keys)]
        if not cands:
            continue
        j = min(cands, key=lambda k: abs(b_keys[k] - ka))
        if abs(b_keys[j] - ka) > TB_TICK // 2:
            continue
        matched += 1
        ha, hb = ta[-1]['body_hash_after'], b_ticks[j][-1]['body_hash_after']
        if ha == hb:
            exact += 1
        elif first_div is None:
            first_div = dict(tick_a=i, tick_b=j, tb_a=ta[0]['tb_start'],
                             tb_b=b_ticks[j][0]['tb_start'],
                             offsets_a=sorted({o for r in ta for o in r['body_offsets']}),
                             offsets_b=sorted({o for r in b_ticks[j] for o in r['body_offsets']}))
            wa, wb = ta[-1].get('body_words'), b_ticks[j][-1].get('body_words')
            if isinstance(wa, list) and isinstance(wb, list):
                div = [4 * k for k, (x, y) in enumerate(zip(wa, wb)) if x != y]
                first_div['diverged_word_offsets'] = div[:64]
                first_div['diverged_word_count'] = len(div)
    report.update(matched_ticks=matched, exact_ticks=exact,
                  match_rate=exact / matched if matched else None,
                  first_divergence=first_div)
    report['verdict'] = ('parity' if matched and exact == matched
                         else 'divergent' if first_div else 'unmatched')
    for label, path in zip(('a', 'b'), telemetry):
        rows = [json.loads(l) for l in open(path)]
        w = [r for r in rows if start <= r['t'] <= end]
        dist = sum(math.dist((p['x'], p['y'], p['z']), (q['x'], q['y'], q['z']))
                   for p, q in zip(w, w[1:]))
        speeds = sorted(math.dist((p['x'], p['y'], p['z']), (q['x'], q['y'], q['z'])) / (q['t'] - p['t'])
                        for p, q in zip(w, w[1:]) if q['t'] > p['t'])
        report[f'telemetry_{label}'] = dict(
            samples=len(w), path_units=dist,
            end_xyz=[w[-1]['x'], w[-1]['y'], w[-1]['z']] if w else None,
            median_speed=statistics.median(speeds) if speeds else None)
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('a')
    ap.add_argument('b')
    ap.add_argument('--telemetry', nargs=2, default=())
    ap.add_argument('--start', type=float, default=145)
    ap.add_argument('--end', type=float, default=170)
    ap.add_argument('--out')
    args = ap.parse_args()
    report = compare(args.a, args.b, args.start, args.end, args.telemetry)
    text = json.dumps(report, indent=2)
    if args.out:
        open(args.out, 'w').write(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
