#!/usr/bin/env python3
"""Prepare/build one private strict-FP ThinLTO object replacement.

The baseline module and all production inputs stay untouched. Reuse the actual
production compiler/link recipe and replace only chunk 802197A0. Preparing is
read-only except for a new local artifact directory; building is explicit.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import time

if __package__:
    from .native_float_conversion_spike import split_helpers, verify_conversion_receipt
    from .native_module_opt_spike import module_flags, source_identity
else:
    from native_float_conversion_spike import split_helpers, verify_conversion_receipt
    from native_module_opt_spike import module_flags, source_identity

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT/'local/native/ssx3-module/build'
GENERATED = ROOT/'local/native/ssx3-module/codegen/generated'
CHUNK = GENERATED/'chunks/chunk_0134_text1_802197A0.c'
MODULE = BUILD/'gGXBE69_recomp.dylib'
PROFILE_MODULE_SHA256 = 'ca06dba7726f57547efe2508f9a2ebe437ad249568a30da9e127f51bdd37e547'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(path):
    path = Path(path).resolve()
    stat = path.stat()
    return dict(path=str(path), sha256=sha(path), bytes=stat.st_size, mtime_ns=stat.st_mtime_ns)


def local_output(path):
    result = Path(path).resolve()
    if not result.is_relative_to(ROOT/'local') or result == ROOT/'local':
        raise ValueError('Use a private output directory under local/')
    return result


def option_value(command, flag):
    if command.count(flag) != 1 or command.index(flag)+1 >= len(command):
        raise ValueError(f'Expected one argument for {flag}')
    return command[command.index(flag)+1]


def replace_option(command, flag, value):
    option_value(command, flag)
    command[command.index(flag)+1] = str(value)


def strip_link_shell(command):
    # CMake's actual rule has two no-op shell commands. Never execute an
    # arbitrary command string, or silently retain other shell operations.
    if command[:2] != [':', '&&'] or command[-2:] != ['&&', ':']:
        raise ValueError('Production linker shell wrapper changed')
    result = command[2:-2]
    if any(word in result for word in ('&&', ';', '|', '||', '>', '<')):
        raise ValueError('Unexpected shell operation in linker recipe')
    return result


def recipes():
    commands = subprocess.check_output(
        [str(ROOT/'local/tooling/ninja'), '-C', str(BUILD), '-t', 'commands', MODULE.name], text=True)
    lines = commands.splitlines()
    compile_rows = [shlex.split(line) for line in lines if str(CHUNK) in line and ' -c ' in line]
    if len(compile_rows) != 1:
        raise ValueError('Expected exactly one original hot-chunk compile command')
    compile_command = compile_rows[0]
    link_command = strip_link_shell(shlex.split(lines[-1]))
    if compile_command[0] != '/usr/bin/clang' or link_command[0] != compile_command[0]:
        raise ValueError('Expected the same production Apple Clang for compile and link')
    if Path(option_value(compile_command, '-c')) != CHUNK:
        raise ValueError('Original source does not match the requested hot chunk')
    if option_value(link_command, '-o') != MODULE.name:
        raise ValueError('Unexpected production module output')
    if '-flto=thin' not in link_command or '-dynamiclib' not in link_command:
        raise ValueError('Expected production ThinLTO dynamic-module link')
    options = [word for word in compile_command if re.fullmatch('-O[0-3]', word)]
    if not options or options[-1] != '-O2' or any(flag not in compile_command for flag in (
            '-flto=thin', '-ffp-contract=off', '-fno-fast-math')):
        raise ValueError('Hot-chunk compile no longer uses strict O2 and ThinLTO')
    if (any(word.startswith('@') for word in compile_command) or
            any(word.startswith('@') and (index == 0 or link_command[index-1] != '-install_name')
                for index, word in enumerate(link_command))):
        raise ValueError('Response files require a separately reviewed recipe reader')
    return compile_command, link_command


def private_commands(output, compile_command, link_command):
    """Change paths only; preserve every production compiler/link flag."""
    output = local_output(output)
    private_generated = output/'generated'
    original_object = (BUILD/option_value(compile_command, '-o')).resolve()
    candidate_object = output/'chunk_0134.o'
    candidate_compile = list(compile_command)
    for flag, value in (('-c', private_generated/'chunks'/CHUNK.name), ('-o', candidate_object),
                        ('-MF', output/'chunk_0134.d'), ('-MT', candidate_object)):
        replace_option(candidate_compile, flag, value)
    include = '-I'+str(GENERATED)
    if candidate_compile.count(include) != 1:
        raise ValueError('Original generated include root changed')
    candidate_compile[candidate_compile.index(include)] = '-I'+str(private_generated)
    candidate_link = list(link_command)
    replace_option(candidate_link, '-o', output/MODULE.name)
    replaced = 0
    for index, word in enumerate(candidate_link):
        if word.endswith('.o'):
            path = (BUILD/word).resolve()
            if path == original_object:
                replaced += 1
                candidate_link[index] = str(candidate_object)
            else:
                candidate_link[index] = str(path)
    if replaced != 1:
        raise ValueError('Expected one hot-object replacement')
    return candidate_compile, candidate_link


def prepare(output, expected_baseline=PROFILE_MODULE_SHA256, *, conversion_evidence):
    output = local_output(output)
    if output.exists():
        raise ValueError('Use a fresh output directory')
    conversion_evidence = Path(conversion_evidence).resolve()
    candidate_header_sha256 = verify_conversion_receipt(conversion_evidence)
    header = (GENERATED/'generated.h').read_text()
    candidate_header = split_helpers(header)
    if hashlib.sha256(candidate_header.encode()).hexdigest() != candidate_header_sha256:
        raise ValueError('Transformed candidate header differs from verified conversion evidence')
    evidence = dict(path=str(conversion_evidence), candidate_header_sha256=candidate_header_sha256,
                    build_receipt_sha256=sha(conversion_evidence/'build.json'),
                    check_receipt_sha256=sha(conversion_evidence/'check.json'))
    compile_command, link_command = recipes()
    baseline = identity(MODULE)
    if baseline['sha256'] != expected_baseline:
        raise ValueError('Baseline module differs from the requested/profiled identity')
    original_object = (BUILD/option_value(compile_command, '-o')).resolve()
    objects = [(BUILD/word).resolve() for word in link_command if word.endswith('.o')]
    if len(objects) != len(set(objects)) or objects.count(original_object) != 1:
        raise ValueError('Hot object is missing, duplicated, or ambiguously linked')
    if any(not path.is_relative_to(BUILD) for path in objects):
        raise ValueError('Expected every original object inside the production build')
    originals = [identity(path) for path in objects]
    if any(row['mtime_ns'] > baseline['mtime_ns'] for row in originals):
        raise ValueError('An object is newer than the profiled baseline; rebuild identity is ambiguous')
    guarded = source_identity()
    for path in (BUILD/'build.ninja', BUILD/'CMakeFiles/rules.ninja', BUILD/'CMakeCache.txt',
                 BUILD/'module_tables.inc', Path(__file__), ROOT/'tools/native_float_conversion_spike.py'):
        guarded[str(path.relative_to(ROOT))] = sha(path)
    compiler = Path(compile_command[0])
    actual_compiler = Path(subprocess.check_output(['xcrun', '-f', 'clang'], text=True).strip())
    linker = Path(subprocess.check_output(['xcrun', '-f', 'ld'], text=True).strip())
    toolchain = dict(driver=identity(compiler), compiler=identity(actual_compiler), linker=identity(linker),
                     version=subprocess.check_output([str(compiler), '--version'], text=True))
    flags = module_flags(BUILD/'build.ninja', 2)

    output.mkdir(parents=True)
    private_generated = output/'generated'
    (private_generated/'chunks').mkdir(parents=True)
    private_chunk = private_generated/'chunks'/CHUNK.name
    shutil.copyfile(CHUNK, private_chunk)
    (private_generated/'generated.h').write_text(candidate_header)
    # Guard/parser inputs remain original. These copies document precisely what
    # the unchanged module_tables.inc represents; no table regeneration here.
    for name in ('main.dol', 'generated_smc.txt'):
        shutil.copyfile(GENERATED/name, private_generated/name)
    candidate_object = output/'chunk_0134.o'
    candidate_module = output/MODULE.name
    candidate_compile, candidate_link = private_commands(output, compile_command, link_command)
    private_inputs = {str(path.relative_to(output)): sha(path) for path in private_generated.rglob('*')
                      if path.is_file()}
    report = dict(schema=2, status='prepared', output=str(output), baseline=baseline,
                  conversion_evidence=evidence,
                  original_object=str(original_object), original_objects=originals,
                  production_sources=guarded, toolchain=toolchain, flags=flags,
                  private_inputs=private_inputs,
                  original_compile=compile_command, original_link=link_command,
                  compile_command=candidate_compile, link_command=candidate_link,
                  candidate_object=str(candidate_object), candidate_module=str(candidate_module),
                  original_object_count=len(objects), reused_object_count=len(objects)-1,
                  module_tables_sha256=sha(BUILD/'module_tables.inc'),
                  limits='One source object changes. A fresh ThinLTO link can still optimize all modules; '
                         'the original command has no cache. No runtime benefit or phone validation claimed.')
    (output/'manifest.json').write_text(json.dumps(report, indent=2)+'\n')
    verify_inputs(report)
    return report


def verify_inputs(report):
    # Historical schema-1 reports predate the evidence binding. Their archived
    # tools/receipts remain historical artifacts; new prepares always use v2.
    if report.get('schema', 1) >= 2:
        evidence = report['conversion_evidence']
        directory = Path(evidence['path'])
        if (sha(directory/'build.json') != evidence['build_receipt_sha256'] or
                sha(directory/'check.json') != evidence['check_receipt_sha256'] or
                verify_conversion_receipt(directory) != evidence['candidate_header_sha256']):
            raise ValueError('Bound conversion evidence changed since preparation')
        if sha(Path(report['output'])/'generated/generated.h') != evidence['candidate_header_sha256']:
            raise ValueError('Private candidate header differs from bound conversion evidence')
    for item in [report['baseline'], *report['original_objects'], *report['toolchain'].values()]:
        if isinstance(item, dict) and sha(item['path']) != item['sha256']:
            raise ValueError('Original binary or toolchain changed: '+item['path'])
    for relative, expected in report['production_sources'].items():
        if sha(ROOT/relative) != expected:
            raise ValueError('Production source/recipe changed: '+relative)
    output = local_output(report['output'])
    for relative, expected in report['private_inputs'].items():
        if sha(output/relative) != expected:
            raise ValueError('Private candidate input changed: '+relative)


def build(output):
    output = local_output(output)
    manifest = output/'manifest.json'
    report = json.loads(manifest.read_text())
    if report.get('schema') != 2 or report['status'] != 'prepared' or report['output'] != str(output):
        raise ValueError('Expected an unchanged prepared manifest with bound conversion evidence')
    verify_inputs(report)
    # Re-derive allowed substitutions so editing a manifest cannot redirect an
    # output to a production object/module or introduce an extra build command.
    original_compile, original_link = recipes()
    if original_compile != report['original_compile'] or original_link != report['original_link']:
        raise ValueError('Actual production commands changed since preparation')
    expected_compile, expected_link = private_commands(output, original_compile, original_link)
    if report['compile_command'] != expected_compile or report['link_command'] != expected_link:
        raise ValueError('Private commands differ from the allowed production path substitutions')
    for name, command in (('compile', report['compile_command']), ('link', report['link_command'])):
        started = time.monotonic()
        print('Starting private '+name, flush=True)
        with (output/(name+'.log')).open('w') as log:
            completed = subprocess.run(command, cwd=BUILD, stdout=log, stderr=subprocess.STDOUT)
        report[name+'_wall_seconds'] = time.monotonic()-started
        report[name+'_exit_code'] = completed.returncode
        if completed.returncode:
            report['status'] = name+'_failed'
            manifest.write_text(json.dumps(report, indent=2)+'\n')
            raise RuntimeError('Private '+name+' failed; see '+name+'.log')
        if name == 'compile':
            report['candidate_object_identity'] = identity(report['candidate_object'])
        manifest.write_text(json.dumps(report, indent=2)+'\n')
    verify_inputs(report)
    candidate = Path(report['candidate_module'])
    report['candidate'] = identity(candidate)
    report['baseline_exports'] = subprocess.check_output(['nm', '-gU', str(MODULE)], text=True).splitlines()
    report['candidate_exports'] = subprocess.check_output(['nm', '-gU', str(candidate)], text=True).splitlines()
    names = lambda rows: sorted(row.split()[-1] for row in rows if row.split())
    if names(report['baseline_exports']) != names(report['candidate_exports']):
        raise ValueError('Module ABI exports changed')
    report['baseline_size'] = subprocess.check_output(['size', '-m', str(MODULE)], text=True)
    report['candidate_size'] = subprocess.check_output(['size', '-m', str(candidate)], text=True)
    report['production_inputs_unchanged'] = True
    report['status'] = 'built'
    manifest.write_text(json.dumps(report, indent=2)+'\n')
    return report


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'build'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline-sha256', default=PROFILE_MODULE_SHA256)
    parser.add_argument('--conversion-evidence', type=Path,
                        help='Passing conversion artifact directory; required for prepare')
    args = parser.parse_args(argv)
    if args.action == 'prepare' and args.conversion_evidence is None:
        parser.error('prepare requires --conversion-evidence')
    if args.action == 'build' and args.conversion_evidence is not None:
        parser.error('build uses the conversion evidence already bound during prepare')
    return args


def main():
    args = parse_args()
    report = prepare(args.output, args.baseline_sha256, conversion_evidence=args.conversion_evidence) if args.action == 'prepare' else build(args.output)
    print(json.dumps({key: report[key] for key in ('status', 'output', 'original_object_count',
                                                  'reused_object_count', 'limits')}, indent=2))


if __name__ == '__main__':
    main()
