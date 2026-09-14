#!/usr/bin/env python3
"""Isolated, source-receipted GXRuntime result-classifier experiment."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import re
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
GXRUNTIME = ROOT / 'third_party/ModernGekko/vendor/dolphin/GXRuntime'
HARNESS = ROOT / 'native/diagnostics/float_classify_harness.c'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def transform(source):
    """Only expose the existing normal-finite classifier result as a hot path."""
    for name, mask in [('classify_f32', '0x7F800000u'),
                       ('classify_f64', '0x7FF0000000000000ull')]:
        start = source.index('u32 ' + name + '(')
        end = source.index('\n}', start)
        body = source[start:end]
        marker = '    if (exponent == ' + mask + ')'
        if (body.count(marker) != 1 or '__builtin_expect' in body or
                'return sign ? 0x08u : 0x04u;' not in body):
            raise ValueError('Pinned classifier shape changed: ' + name)
        replacement = ('    if (__builtin_expect(exponent != 0 && exponent != ' + mask + ', 1))\n'
                       '        return 4u << sign;\n' + marker)
        source = source[:start] + body.replace(marker, replacement) + source[end:]
    return source


def transform_scoped(source):
    """Give only generated ppc_fma its own fast classifiers; preserve other users."""
    fast = transform(source)
    helpers = ''
    for name in ('classify_f32', 'classify_f64'):
        start = fast.index('u32 ' + name + '(')
        end = fast.index('\n}', start) + 2
        helpers += 'static ' + fast[start:end].replace(name + '(', 'generated_fma_' + name + '(', 1) + '\n\n'
    start = source.index('bool ppc_fma(')
    end = source.index('\n}', start) + 2
    body = source[start:end]
    marker = 'set_fprf(cpu, single ? classify_f32((f32)result) : classify_f64(result));'
    if body.count(marker) != 1:
        raise ValueError('Pinned generated FMA classification seam changed')
    replacement = marker.replace('classify_f32', 'generated_fma_classify_f32').replace('classify_f64', 'generated_fma_classify_f64')
    return source[:start] + helpers + body.replace(marker, replacement) + source[end:]


def checked(command, **kwargs):
    result = subprocess.run(command, text=True, capture_output=True, **kwargs)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def prepare(args):
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / 'local'):
        raise ValueError('Use a fresh isolated directory under local/')
    output.mkdir(parents=True, exist_ok=False)
    paths = ['src/core/cpu_interpreter_float.c', 'src/core/cpu_interpreter_private.h',
             'src/core/cpu_interpreter_table.c', 'include/core/cpu.h', 'include/core/types.h']
    receipt = dict(schema=2, sources={}, commands=[],
                   host=dict(system=platform.system(), release=platform.release(),
                             machine=platform.machine()),
                   changes=dict(candidate='Normal-finite early return in classify_f32 and classify_f64 only',
                                scoped='Private normal-finite classifiers called only by generated ppc_fma'))
    for relative in paths:
        original = GXRUNTIME / relative
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(original.read_bytes())
        receipt['sources'][relative] = sha(original)
    (output / 'harness.c').write_bytes(HARNESS.read_bytes())
    receipt['harness_sha256'] = sha(HARNESS)
    source = (output / paths[0]).read_text()
    names = re.findall(r'^\w+\s+(\w+)\([^;]*?\)\s*\{', source, re.MULTILINE)
    if len(names) < 40 or not {'classify_f32', 'classify_f64', 'ppc_fadds', 'ppc_fmuls', 'ppc_fma'} <= set(names):
        raise ValueError('Could not isolate the pinned floating-point definitions')
    for variant in ('reference', 'candidate', 'scoped'):
        macros = ''.join('#define ' + name + ' ' + variant + '_' + name + '\n' for name in names)
        transformed = source if variant == 'reference' else transform(source) if variant == 'candidate' else transform_scoped(source)
        (output / (variant + '.c')).write_text(macros + transformed)
    command = [args.compiler, '-O2', '-flto=thin', '-ffp-contract=off', '-fno-fast-math',
               '-fvisibility=hidden', '-std=gnu11', '-mmacosx-version-min=14.0',
               '-I' + str(output / 'include'), '-I' + str(output / 'src/core'),
               str(output / 'reference.c'), str(output / 'candidate.c'), str(output / 'scoped.c'),
               str(output / 'src/core/cpu_interpreter_table.c'), str(output / 'harness.c'),
               '-Wl,-dead_strip', '-lm', '-o', str(output / 'harness')]
    receipt['commands'].append(command)
    receipt['compiler'] = checked([args.compiler, '--version'])
    checked(command)
    receipt['generated'] = {name: sha(output / name) for name in ('reference.c', 'candidate.c', 'scoped.c', 'harness.c', 'harness')}
    (output / 'build.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(output / 'harness')


def run(args):
    output = args.output.resolve()
    receipt = json.loads((output / 'build.json').read_text())
    for name, digest in {**receipt['sources'], **receipt['generated']}.items():
        if sha(output / name) != digest:
            raise ValueError('Diagnostic receipt mismatch: ' + name)
    if args.command == 'check':
        result = json.loads(checked([str(output / 'harness'), 'check']))
        result['binary_sha256'] = receipt['generated']['harness']
        (output / 'check.json').write_text(json.dumps(result, indent=2) + '\n')
    else:
        if not (output / 'check.json').exists():
            raise ValueError('Run the differential check before benchmarking')
        check = json.loads((output / 'check.json').read_text())
        if not check.get('passed') or check['binary_sha256'] != receipt['generated']['harness']:
            raise ValueError('No passing differential check for this binary')
        if not 1 <= args.rounds <= 20 or not 1000 <= args.iterations <= 10000000:
            raise ValueError('Use 1–20 rounds and 1,000–10,000,000 calls per case')
        variants = ('reference', 'candidate', 'scoped') if receipt['schema'] >= 2 else ('reference', 'candidate')
        orders = list(itertools.permutations(variants))
        result = dict(schema=2, binary_sha256=receipt['generated']['harness'],
                      iterations=args.iterations, rounds=[])
        for index in range(args.rounds):
            for variant in orders[index % len(orders)]:
                row = json.loads(checked([str(output / 'harness'), 'bench', variant, str(args.iterations)]))
                row['round'] = index
                result['rounds'].append(row)
        for index in range(args.rounds):
            pair = [r for r in result['rounds'] if r['round'] == index]
            keys = ('operation', 'corpus', 'calls', 'checksum')
            if any([[r[k] for k in keys] for r in pair[0]['cases']] !=
                   [[r[k] for k in keys] for r in row['cases']] for row in pair[1:]):
                raise ValueError('Benchmark variants diverged')
        result['summary'] = []
        for case in result['rounds'][0]['cases']:
            values = {variant: [c['ns_per_call'] for row in result['rounds']
                                if row['variant'] == variant for c in row['cases']
                                if (c['operation'], c['corpus']) == (case['operation'], case['corpus'])]
                      for variant in variants}
            comparisons = {}
            for variant in variants[1:]:
                paired = [100 * (c / r - 1) for r, c in zip(values['reference'], values[variant])]
                comparisons[variant] = dict(median_ns=statistics.median(values[variant]),
                                            paired_change_percent=paired,
                                            paired_median_percent=statistics.median(paired),
                                            paired_range_percent=[min(paired), max(paired)])
            result['summary'].append(dict(operation=case['operation'], corpus=case['corpus'],
                                          reference_median_ns=statistics.median(values['reference']),
                                          comparisons=comparisons, ns_per_call=values))
        (output / 'benchmark.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare_parser = commands.add_parser('prepare')
    prepare_parser.add_argument('--output', type=Path, required=True)
    prepare_parser.add_argument('--compiler', default='/usr/bin/clang')
    check_parser = commands.add_parser('check')
    check_parser.add_argument('output', type=Path)
    bench_parser = commands.add_parser('bench')
    bench_parser.add_argument('output', type=Path)
    bench_parser.add_argument('--rounds', type=int, default=6)
    bench_parser.add_argument('--iterations', type=int, default=1000000)
    args = parser.parse_args()
    prepare(args) if args.command == 'prepare' else run(args)


if __name__ == '__main__':
    main()
