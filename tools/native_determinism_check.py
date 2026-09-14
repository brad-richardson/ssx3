#!/usr/bin/env python3
"""Record one Mac ride as a Dolphin input movie, replay it against two modules,
and compare the runtime's periodic dispatch trace.

Under movie playback every guest input poll receives the recorded pad state and
the guest clock is fixed. Compare the sparse control-register trace (one row
per 1,048,576 native dispatches with pc, lr, ctr, cr and guest timebase).
Matching rows do not establish equal floating-point registers or gameplay
memory. Host-timed rider observations provide a separate smoke check, not a
guest-update-aligned gameplay equivalence test.

  record  : course check with SSX3_MOVIE_RECORD, baseline module
  play    : course check with SSX3_MOVIE_PLAY and a chosen module
  compare : diff two play (or record/play) outputs
"""
import argparse
import configparser
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DISPATCH_STRIDE = 1048576


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def comparable_config(receipt):
    """Ignore only the randomized Analytics ID, after verifying the saved file."""
    if not receipt.get('profile'):
        return None
    path = Path(receipt['profile']) / 'Config/Dolphin.ini'
    if not path.exists() or sha256(path) != receipt.get('core_config_sha256'):
        return None
    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str
    config.read_string(path.read_text())
    if config.has_section('Analytics'):
        config.remove_option('Analytics', 'ID')
    contents = {s: dict(config.items(s)) for s in config.sections()}
    return hashlib.sha256(json.dumps(contents, sort_keys=True).encode()).hexdigest()


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
                   evidence=receipt.get('evidence'), movie=str(movie) if movie else None,
                   movie_sha256=sha256(movie) if movie else None,
                   execution_status={k: receipt[k] for k in ('exit_code', 'stopped_on_fault') if k in receipt},
                   provenance={**{k: receipt.get(k) for k in ('cpu_thread', 'runner_sha256',
                               'world_archive_sha256', 'core_config_sha256')},
                               'comparable_config_sha256': comparable_config(receipt)})
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
                dispatch = int(fields[0])
                if dispatch in rows:
                    raise ValueError(f'Duplicate dispatch count {dispatch} in {path}')
                rows[dispatch] = tuple(fields[1:6])  # pc, lr, ctr, cr, timebase
    return rows


def rider_observations(folder):
    path = folder / 'rider.jsonl'
    if not path.exists():
        return None
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    transitions = []
    for row in rows:
        state = row.get('state')
        if not transitions or state != transitions[-1]:
            transitions.append(state)
    return dict(samples=len(rows), state_transitions=transitions,
                alignment='host time; not aligned to guest updates')


def provenance(summary):
    """Also read receipts from older runs that predate saved provenance."""
    result = dict(summary.get('provenance') or {})
    receipt = summary.get('receipt')
    if not result and receipt and Path(receipt).exists():
        data = json.loads(Path(receipt).read_text())
        result = {k: data.get(k) for k in ('cpu_thread', 'runner_sha256',
                  'world_archive_sha256', 'core_config_sha256')}
        result['comparable_config_sha256'] = comparable_config(data)
    result['movie_sha256'] = summary.get('movie_sha256')
    result['movie_hash_source'] = 'captured_at_run' if result['movie_sha256'] else 'unavailable'
    if result['movie_sha256'] is None and summary.get('movie') and Path(summary['movie']).exists():
        result['movie_sha256'] = sha256(summary['movie'])
        result['movie_hash_source'] = 'current_file_only'
    return result


def execution_status(summary):
    if 'execution_status' in summary:
        return summary['execution_status']
    receipt = summary.get('receipt')
    if receipt and Path(receipt).exists():
        data = json.loads(Path(receipt).read_text())
        return {k: data[k] for k in ('exit_code', 'stopped_on_fault') if k in data}
    return {}


def compare(args):
    summaries = [json.loads((p.resolve() / 'determinism.json').read_text()) for p in (args.a, args.b)]
    traces = [load_trace(s['dispatch_trace']) for s in summaries]
    # Older traces may contain only a tail. Keep overlap analysis available,
    # but the strict control-flow gate requires an uninterrupted prefix from 0.
    common = sorted(set(traces[0]) & set(traces[1]))
    first_divergence = None
    for dispatch in common:
        if traces[0][dispatch] != traces[1][dispatch]:
            first_divergence = dict(dispatch=dispatch, a=traces[0][dispatch], b=traces[1][dispatch])
            break
    identical = len(common) if first_divergence is None else common.index(first_divergence['dispatch'])
    prefix_complete = bool(common) and common == list(range(0, common[-1] + 1, DISPATCH_STRIDE))
    run_provenance = [provenance(s) for s in summaries]
    issues = []
    if not prefix_complete:
        issues.append('Compared rows are not an uninterrupted prefix from dispatch zero')
    for key in ('movie_sha256', 'runner_sha256', 'world_archive_sha256'):
        values = [p.get(key) for p in run_provenance]
        if any(v is None for v in values) or values[0] != values[1]:
            issues.append(f'Missing or mismatched {key}')
    raw_configs = [p.get('core_config_sha256') for p in run_provenance]
    normalized_configs = [p.get('comparable_config_sha256') for p in run_provenance]
    if not ((all(raw_configs) and raw_configs[0] == raw_configs[1]) or
            (all(normalized_configs) and normalized_configs[0] == normalized_configs[1])):
        issues.append('Missing or mismatched core_config_sha256 (excluding verified Analytics ID)')
    if any(p.get('cpu_thread') is not False for p in run_provenance):
        issues.append('Both runs must explicitly use single-core mode')
    if any(p.get('movie_hash_source') != 'captured_at_run' for p in run_provenance):
        issues.append('Both movie hashes must have been captured at run time; current files cannot verify legacy inputs')
    for i, summary in enumerate(summaries):
        evidence = summary.get('evidence') or {}
        counters = evidence.get('shutdown_counters') or {}
        status = execution_status(summary)
        if status.get('exit_code') != 0 or 'stopped_on_fault' not in status or status['stopped_on_fault'] is not None:
            issues.append(f'Run {i + 1}: successful exit without a fault is not established')
        if evidence.get('module_loaded') is not True or not isinstance(counters.get('native'), int) or counters['native'] <= 0:
            issues.append(f'Run {i + 1}: native module execution is not established')
        if evidence.get('fallback_jit_runs') != 0:
            issues.append(f'Run {i + 1}: fallback_jit_runs is missing or nonzero')
        for key, value in [(k, evidence.get(k)) for k in ('invalid_memory_accesses', 'gpu_command_errors',
                                                       'unknown_guest_instructions')] + [('smc_failed', counters.get('smc_failed'))]:
            if value != 0:
                issues.append(f'Run {i + 1}: {key} is missing or nonzero')
    observed = [rider_observations(p.resolve()) for p in (args.a, args.b)]
    result = dict(a=summaries[0], b=summaries[1], rows=[len(t) for t in traces],
                  first_dispatch=[min(t) if t else None for t in traces],
                  last_dispatch=[max(t) if t else None for t in traces],
                  compared_rows=len(common), identical_rows=identical, first_divergence=first_divergence,
                  coverage_fractions=[len(common) / len(t) if t else 0 for t in traces],
                  contiguous_prefix=prefix_complete, provenance=run_provenance,
                  control_flow_gate_issues=issues,
                  control_flow_gate_passed=not issues and first_divergence is None,
                  gameplay_equivalence_verified=False,
                  rider_observations=observed,
                  observed_state_transitions_equal=(observed[0]['state_transitions'] == observed[1]['state_transitions']
                                                     if all(o and o['samples'] for o in observed) else None),
                  verdict=('identical over the compared rows' if first_divergence is None and common else
                           'diverged' if first_divergence else 'no overlapping rows'),
                  note='Rows are one sample per 1,048,576 native dispatches: pc, lr, ctr, cr and guest '
                       'timebase, aligned by dispatch count. Equal rows establish equality only of those '
                       'five sampled control values, not FPRs or gameplay memory. Coverage is bounded by '
                       'the overlap. Rider state transitions are host-timed observations, not an exact '
                       'gameplay-state gate. Legacy movie hashes are computed from the current movie file.')
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('rows', 'first_dispatch', 'last_dispatch', 'compared_rows',
                                              'identical_rows', 'first_divergence', 'verdict',
                                              'control_flow_gate_passed', 'control_flow_gate_issues',
                                              'gameplay_equivalence_verified', 'observed_state_transitions_equal')}, indent=2))
    if first_divergence or not common or (getattr(args, 'strict', False) is True and issues):
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
    p.add_argument('--strict', action='store_true',
                   help='Require a contiguous prefix, matching provenance and clean runtime counters; '
                        'still only a sparse control-flow gate')
    p.set_defaults(fn=compare)
    args = parser.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
