#!/usr/bin/env python3
"""Compare two native rider traces of the same course, one archive change apart.

Two host-timed runs are not guaranteed to sample the same guest instants, so
this reports the alignment it used and treats separation, not equality, as the
measurement.

Absolute guest time is the wrong key: the harness repeats its start request
until riding is observed, so two runs of the same archive leave the gate tens
of guest seconds apart. The default alignment re-bases each trace at its own
race start — the first sample that has moved more than --motion world units
from the spawn — and pairs by time since then. `--absolute-time` keeps raw `t`
and `--by-index` pairs row n with row n. Rows with no position (the harness
records zeros before the rider exists) are excluded from every statistic.

A separation beyond the tolerance means the two runs took different paths. It
does not by itself say why: only a control pair of runs on the *same* archive
establishes this harness's run-to-run floor, and `floor` in the report is that
number when a control run is supplied with --floor.
"""
import argparse
import json
from pathlib import Path
from statistics import median

POSITION = ('x', 'y', 'z')


def load(path):
    """Rider samples with a position, from a run directory or a rider.jsonl."""
    path = Path(path)
    trace = path / 'rider.jsonl' if path.is_dir() else path
    rows = [json.loads(line) for line in trace.read_text().splitlines() if line.strip()]
    placed = [r for r in rows if any(r.get(k) for k in POSITION)]
    return rows, placed


def separation(a, b):
    return sum((a[k] - b[k]) ** 2 for k in POSITION) ** .5


def motion_start(rows, motion=1.):
    """Index of the first sample that has left the spawn position."""
    if not rows:
        raise ValueError('No positioned samples to find a race start in')
    spawn = rows[0]
    for i, row in enumerate(rows):
        if separation(row, spawn) > motion:
            return i
    raise ValueError('The rider never moved from its spawn position')


def rebase(rows, motion):
    """Samples from the race start, with `t` measured from it."""
    start = motion_start(rows, motion)
    origin = rows[start]['t']
    return [dict(row, t=row['t'] - origin) for row in rows[start:]]


def pair_by_time(left, right, window):
    """Nearest-in-guest-time pairs, each right sample used at most once."""
    pairs, used, j = [], 0, 0
    for row in left:
        while j + 1 < len(right) and abs(right[j + 1]['t'] - row['t']) <= abs(right[j]['t'] - row['t']):
            j += 1
        if j >= used and abs(right[j]['t'] - row['t']) <= window:
            pairs.append((row, right[j]))
            used = j + 1
    return pairs


def compare(a_run, b_run, tolerance=10., window=.25, align='motion', motion=1.):
    a_rows, a = load(a_run)
    b_rows, b = load(b_run)
    if not a or not b:
        raise ValueError('A trace has no positioned rider samples')
    if align == 'motion':
        a, b = rebase(a, motion), rebase(b, motion)
    pairs = (list(zip(a, b)) if align == 'index' else pair_by_time(a, b, window))
    if not pairs:
        raise ValueError('No sample pairs; traces do not overlap in guest time')
    gaps = [separation(x, y) for x, y in pairs]
    beyond = [(i, g) for i, g in enumerate(gaps) if g > tolerance]
    report = {
        'a': str(a_run), 'b': str(b_run),
        'alignment': {'index': 'row index',
                      'time': f'absolute guest time within {window}s',
                      'motion': f'guest time from each race start, within {window}s'}[align],
        'tolerance_world_units': tolerance,
        'samples': {'a': len(a_rows), 'b': len(b_rows),
                    'a_aligned': len(a), 'b_aligned': len(b), 'paired': len(pairs)},
        'start_separation_world_units': separation(a[0], b[0]),
        'guest_seconds_paired': round(pairs[-1][0]['t'] - pairs[0][0]['t'], 3),
        'separation_world_units': {
            'max': max(gaps), 'median': median(gaps),
            'within_tolerance': len(gaps) - len(beyond),
            'beyond_tolerance': len(beyond),
        },
        'identical': max(gaps) == 0,
        'first_beyond_tolerance': None if not beyond else {
            'paired_sample': beyond[0][0],
            'guest_t': pairs[beyond[0][0]][0]['t'],
            'separation': beyond[0][1],
            'a': {k: pairs[beyond[0][0]][0][k] for k in POSITION},
            'b': {k: pairs[beyond[0][0]][1][k] for k in POSITION},
        },
    }
    for name, run in (('a', a_run), ('b', b_run)):
        observations = Path(run) / 'observations.json'
        if observations.is_file():
            record = json.loads(observations.read_text())
            report[name + '_run'] = {k: record.get(k) for k in
                                     ('game', 'profile', 'course_manifest', 'module', 'cpu_thread',
                                      'riding_observed_after_start', 'complete_hazard_resets')}
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('a', help='Run directory or rider.jsonl')
    ap.add_argument('b', help='Run directory or rider.jsonl')
    ap.add_argument('--tolerance', type=float, default=10.,
                    help='World units of separation treated as the same path (default 10)')
    ap.add_argument('--time-window', type=float, default=.25,
                    help='Guest seconds a time-aligned pair may differ by (default 0.25)')
    ap.add_argument('--absolute-time', dest='align', action='store_const', const='time',
                    default='motion', help='Pair on raw guest time instead of time from the race start')
    ap.add_argument('--by-index', dest='align', action='store_const', const='index',
                    help='Pair row n with row n instead')
    ap.add_argument('--motion', type=float, default=1.,
                    help='World units from the spawn that count as the race start (default 1)')
    ap.add_argument('--floor', nargs=2, metavar=('A', 'B'),
                    help='A control pair on one archive, to report the run-to-run floor')
    ap.add_argument('--output', type=Path, help='Write the JSON report here as well')
    args = ap.parse_args()
    report = compare(args.a, args.b, args.tolerance, args.time_window, args.align, args.motion)
    if args.floor:
        control = compare(*args.floor, args.tolerance, args.time_window, args.align, args.motion)
        report['floor'] = {'a': control['a'], 'b': control['b'],
                           'separation_world_units': control['separation_world_units'],
                           'identical': control['identical']}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
