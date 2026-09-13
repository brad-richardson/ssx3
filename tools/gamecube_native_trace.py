#!/usr/bin/env python3
"""Build an isolated native callback observer or summarize its JSONL events.

Research only. SSX_NATIVE_PROBE must name a new JSONL output file. Explicitly
setting SSX_NATIVE_DOUBLE_RENDER=1 attempts at most 120 extra renderer calls
after 140 host seconds while riding. Readiness gates remain intact; an attempted
call is not evidence of drawing or displaying another frame.
"""
import argparse
import collections
import json
from pathlib import Path
import shlex
import subprocess

from gamecube_draw_trace import BUILD, ROOT, VENDOR, compile_copy, sha

DOL_SHA256 = 'b92162d6c616be3ce46b4eb61d5ddbb49891bc387ea7ddb2fea5792842fa29ce'
HEADER = ROOT / 'native/diagnostics/native_callback_trace.h'


def build(args):
    game = args.game.resolve()
    if ((game / 'sys/boot.bin').read_bytes()[:6] != b'GXBE69' or
            sha(game / 'sys/main.dol') != DOL_SHA256):
        raise ValueError('Callback addresses require the pinned GXBE69 executable')
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / 'local'):
        raise ValueError('Diagnostic outputs must remain under local/')
    out.mkdir(parents=True, exist_ok=False)
    original = VENDOR / 'vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp'
    production = BUILD / 'moderngekko-run'
    receipt = dict(schema=1, dol_sha256=DOL_SHA256, game=str(game),
                   original_source_sha256=sha(original), probe_header_sha256=sha(HEADER),
                   production_runner_sha256=sha(production), commands=[])
    source = original.read_text()
    includes = 'namespace\n{'
    dispatch = '          const u32 runtime_dispatch_address = m_guest.pc;'
    for marker in (includes, dispatch):
        if source.count(marker) != 1:
            raise ValueError(f'Native diagnostic injection point changed: {marker!r}')
    # Snapshot the authored header too, so later edits cannot change a receipt.
    header_copy = out / HEADER.name
    header_copy.write_bytes(HEADER.read_bytes())
    source = source.replace(includes, f'#include "{header_copy}"\n' + includes)
    source = source.replace(dispatch, '          NativeProbe::Step(m_guest);\n' + dispatch)
    copy = out / 'Core_Run.cpp'
    copy.write_text(source)
    commands = subprocess.check_output(
        [str(ROOT / 'local/tooling/ninja'), '-C', str(BUILD), '-t', 'commands', 'moderngekko-run'],
        text=True).splitlines()

    def run(command):
        receipt['commands'].append(command)
        subprocess.run(command, cwd=BUILD, check=True)

    run(compile_copy(next(c for c in commands if c.endswith('/StaticRecompCore_Run.cpp')),
                     copy, out / 'probe.o'))
    link = shlex.split(next(c for c in commands if ' -o moderngekko-run ' in c))
    link = link[2:link.index('&&', 2)]
    link[link.index('-o') + 1] = str(out / 'player')
    link.insert(link.index('libmoderngekko.a'), str(out / 'probe.o'))
    run(link)
    if sha(production) != receipt['production_runner_sha256']:
        raise RuntimeError('Production runner changed during diagnostic build')
    receipt['player_sha256'] = sha(out / 'player')
    (out / 'build.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(out / 'player')


def summarize(rows, after=140):
    """Keep attempted repeats separate from observed scene-path coverage."""
    result = dict(schema=1, after_host_seconds=after, groups={})
    for label in ('update', 'render', 'repeat'):
        group = [r for r in rows if r['wall'] > after and r['rider'] and r['same_rider']
                 and (r['repeat'] if label == 'repeat' else
                      r['event'] == label and not r['repeat'])]
        counts = dict(calls=len(group))
        for field in ('position_changed', 'rng_changed', 'view_offsets', 'body_offsets', 'app_offsets'):
            counts[field] = sum(bool(r[field]) for r in group)
        counts['state_changed'] = sum(r['state_before'] != r['state_after'] for r in group)
        counts['view_pointer_changed'] = sum(not r['same_view'] for r in group)
        coverage = bool(group) and all('gate_calls' in r for r in group)
        counts['render_gate_instrumented'] = coverage
        if coverage and label != 'update':
            for field in ('view_matrix_calls', 'frame_end_calls', 'elapsed_calls', 'queue_calls',
                          'gate_calls', 'gate_ready'):
                if all(field in r for r in group):
                    counts[field] = sum(r[field] for r in group)
            counts['results'] = dict(collections.Counter(str(r['result']) for r in group))
        result['groups'][label] = counts
    repeats = [(i, r) for i, r in enumerate(rows) if r['repeat']]
    result['repeat_pairing_failures'] = sum(
        i == 0 or rows[i-1]['event'] != 'render' or rows[i-1]['repeat'] or
        rows[i-1]['app'] != r['app'] or rows[i-1]['rider'] != r['rider']
        for i, r in repeats)
    result['limits'] = ('Scoped entry/return comparisons, not whole-game determinism or a '
                        'presentation count. Dispatch counters must observe ordinary draws '
                        'before absent repeat calls are evidence of a skipped path. Guest '
                        'time and interrupts continue during repeated rendering.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('build')
    p.add_argument('--game', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('summarize')
    p.add_argument('trace', type=Path)
    p.add_argument('--after', type=float, default=140)
    p.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.command == 'build':
        build(args)
    else:
        rows = [json.loads(line) for line in args.trace.read_text().splitlines()]
        result = summarize(rows, args.after)
        result['trace_sha256'] = sha(args.trace)
        encoded = json.dumps(result, indent=2) + '\n'
        if args.output:
            args.output.write_text(encoded)
        else:
            print(encoded, end='')


if __name__ == '__main__':
    main()
