#!/usr/bin/env python3
"""Record one Mac ride as a Dolphin input movie, replay it against two modules,
and compare the runtime's periodic dispatch trace.

Under movie playback every guest input poll receives the recorded pad state and
the guest clock is fixed, so a single-core run is deterministic: the dispatch
trace (one row per 1,048,576 native dispatches with pc, lr, ctr, cr and the
guest timebase) must match row for row between a baseline module and a
candidate module. The first differing row is the first observable divergence.
This is an execution-equivalence gate for generated-code changes, not proof of
correctness against the original console.

  record  : course check with SSX3_MOVIE_RECORD, baseline module
  play    : course check with SSX3_MOVIE_PLAY and a chosen module
  compare : diff two play (or record/play) outputs
"""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def course_check(args, output, profile, env_extra, module):
    env = dict(os.environ, **env_extra)
    command = [sys.executable, str(ROOT / 'tools/gamecube_course_check.py'), '--game', str(args.game.resolve()),
               '--profile', profile, '--output', str(output), '--seconds', str(args.seconds),
               '--metal-validation', 'off']
    if module:
        command += ['--module', str(Path(module).resolve())]
    print('+', ' '.join(command), flush=True)
    result = subprocess.run(command, env=env, cwd=ROOT)
    return result.returncode


def latest_receipt(output):
    log = (output / 'runtime.log').read_text(errors='replace')
    for line in log.splitlines():
        if line.startswith('Log: '):
            log_path = Path(line[5:].strip())
            return log_path.with_suffix('.json'), log_path.with_name(log_path.stem + '-dispatch.csv')
    raise RuntimeError('Runtime receipt not found in runtime.log')


def finish(output, movie=None):
    receipt_path, dispatch_path = latest_receipt(output)
    receipt = json.loads(receipt_path.read_text())
    summary = dict(receipt=str(receipt_path), dispatch_trace=str(dispatch_path) if dispatch_path.exists() else None,
                   module=receipt.get('module_path'), module_sha256=receipt.get('module_sha256'),
                   evidence=receipt.get('evidence'), movie=str(movie) if movie else None)
    (output / 'determinism.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: summary[k] for k in ('module_sha256', 'dispatch_trace', 'movie')}, indent=2))


def record(args):
    output = args.output.resolve()
    movie = output.parent / (output.name + '.dtm')
    if movie.exists():
        raise SystemExit(f'Preserving existing movie {movie}')
    code = course_check(args, output, args.profile, {'SSX3_MOVIE_RECORD': str(movie)}, args.module)
    if not movie.exists():
        raise SystemExit('The runtime did not save a movie; see runtime.log')
    finish(output, movie)
    if code:
        raise SystemExit(code)


def play(args):
    output = args.output.resolve()
    movie = args.movie.resolve()
    if not movie.exists():
        raise SystemExit(f'Missing movie {movie}')
    code = course_check(args, output, args.profile, {'SSX3_MOVIE_PLAY': str(movie)}, args.module)
    finish(output, movie)
    if code:
        raise SystemExit(code)


def load_trace(path):
    rows = {}
    with open(path, newline='') as stream:
        for fields in csv.reader(stream):
            if len(fields) >= 6 and fields[0].isdigit():
                rows[int(fields[0])] = tuple(fields[1:6])  # pc, lr, ctr, cr, timebase
    return rows


def compare(args):
    summaries = [json.loads((p.resolve() / 'determinism.json').read_text()) for p in (args.a, args.b)]
    traces = [load_trace(s['dispatch_trace']) for s in summaries]
    # The runtime reopens the trace when its run loop is re-entered, so a file may
    # cover only the tail of a session. Align rows by dispatch count and compare
    # the overlap; report how much of each file that overlap covers.
    common = sorted(set(traces[0]) & set(traces[1]))
    first_divergence = None
    for dispatch in common:
        if traces[0][dispatch] != traces[1][dispatch]:
            first_divergence = dict(dispatch=dispatch, a=traces[0][dispatch], b=traces[1][dispatch])
            break
    identical = len(common) if first_divergence is None else common.index(first_divergence['dispatch'])
    result = dict(a=summaries[0], b=summaries[1], rows=[len(t) for t in traces],
                  first_dispatch=[min(t) if t else None for t in traces],
                  last_dispatch=[max(t) if t else None for t in traces],
                  compared_rows=len(common), identical_rows=identical, first_divergence=first_divergence,
                  verdict=('identical over the compared rows' if first_divergence is None and common else
                           'diverged' if first_divergence else 'no overlapping rows'),
                  note='Rows are one sample per 1,048,576 native dispatches: pc, lr, ctr, cr and guest '
                       'timebase, aligned by dispatch count. Equal rows mean both executions reached the '
                       'same state after the same number of dispatches at every compared sample; a differing '
                       'row locates the first observed divergence. Coverage is bounded by the overlap.')
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('rows', 'first_dispatch', 'last_dispatch', 'compared_rows',
                                              'identical_rows', 'first_divergence', 'verdict')}, indent=2))
    if first_divergence or not common:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    for name, fn in (('record', record), ('play', play)):
        p = sub.add_parser(name)
        p.add_argument('--game', type=Path, required=True)
        p.add_argument('--profile', required=True, help='Fresh isolated profile name')
        p.add_argument('--output', type=Path, required=True, help='Fresh output directory')
        p.add_argument('--seconds', type=int, default=200)
        p.add_argument('--module', type=Path, help='Module dylib; default is the current build')
        if name == 'play':
            p.add_argument('--movie', type=Path, required=True)
        p.set_defaults(fn=fn)
    p = sub.add_parser('compare')
    p.add_argument('a', type=Path)
    p.add_argument('b', type=Path)
    p.add_argument('--output', type=Path)
    p.set_defaults(fn=compare)
    args = parser.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
