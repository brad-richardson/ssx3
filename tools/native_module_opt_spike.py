#!/usr/bin/env python3
"""Build and compare isolated O2/O3 AOT modules with strict FP and ThinLTO.

No production binaries, module paths, phone settings or game content are changed.
The optional rides retain native/course/watched-state checks. They are manually
timed workloads, so measured differences never establish a causal speedup.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT/'third_party/ModernGekko/vendor/dolphin'
GENERATED = ROOT/'local/native/ssx3-module/codegen/generated'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_identity():
    paths = set(GENERATED.rglob('*'))
    for directory in (CORE/'module-template', CORE/'GXRuntime/src/core', CORE/'GXRuntime/include',
                      CORE/'Source/Core/Core/PowerPC/StaticRecomp'):
        paths.update(directory.rglob('*.h'))
        paths.update(directory.rglob('*.c'))
    paths.update((CORE/'module-template').glob('*.py'))
    paths.add(CORE/'module-template/CMakeLists.txt')
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths) if p.is_file()}


def module_flags(ninja, level):
    flags = [re.search(r'^  FLAGS = (.*)$', block, re.M).group(1)
             for block in Path(ninja).read_text().split('\n\n')
             if 'CMakeFiles/gGXBE69_recomp.dir' in block and '  FLAGS = ' in block]
    if not flags:
        raise ValueError('No generated module object commands in Ninja recipe')
    for value in flags:
        opts = re.findall(r'(?:^| )-O([0-3])(?= |$)', value)
        if not opts or opts[-1] != str(level):
            raise ValueError('Effective compiler optimization does not match requested variant')
        if any(flag not in value.split() for flag in ('-flto=thin', '-ffp-contract=off', '-fno-fast-math')):
            raise ValueError('ThinLTO or strict floating-point flags missing')
        if '-ffast-math' in value.split() or '-Ofast' in value.split():
            raise ValueError('Relaxed floating-point optimization is forbidden in this comparison')
    return dict(object_count=len(flags), distinct_flags=sorted(set(flags)))


def compiler_identity(directory):
    cache = Path(directory)/'CMakeCache.txt'
    line = next(line for line in cache.read_text().splitlines() if line.startswith('CMAKE_C_COMPILER:'))
    compiler = Path(line.split('=', 1)[1])
    return dict(path=str(compiler), sha256=sha(compiler),
                version=subprocess.check_output([str(compiler), '--version'], text=True).splitlines()[0])


def thermal_context():
    try:
        result = subprocess.run(['pmset', '-g', 'therm'], capture_output=True, text=True, timeout=10)
        return dict(exit_code=result.returncode, output=result.stdout+result.stderr,
                    note='OS thermal/performance warning state, not a direct temperature measurement.')
    except (OSError, subprocess.TimeoutExpired) as error:
        return dict(unknown=str(error))


def runtime_receipt(case_directory, expected_module, expected_player):
    text = (Path(case_directory)/'runtime.log').read_text()
    match = re.search(r'^Log: (.+\.log)$', text, re.M)
    if not match:
        raise ValueError('Native run did not identify its runtime receipt')
    path = Path(match[1]).with_suffix('.json')
    if path.parent != ROOT/'local/reports/native-runs':
        raise ValueError('Runtime receipt is outside the native report directory')
    record = json.loads(path.read_text())
    if record['module_sha256'] != expected_module or record['runner_sha256'] != expected_player:
        raise ValueError('Actual executed module/player differs from the requested comparison variant')
    return dict(path=str(path), sha256=sha(path), evidence=record['evidence'],
                module_sha256=record['module_sha256'], runner_sha256=record['runner_sha256'],
                core_config_sha256=record['core_config_sha256'], world_archive_sha256=record['world_archive_sha256'])


def audit_callback_evidence(trace, runtime_log):
    if __package__:
        from .mobile_pacing_check import known_watched_state, read_jsonl
    else:
        from mobile_pacing_check import known_watched_state, read_jsonl
    rows, issues = read_jsonl(Path(trace))
    callbacks = [row for row in rows if row.get('event') in ('render', 'update')]
    unknown = [row for row in callbacks if not known_watched_state(row)]
    extras = [row for row in callbacks if row.get('event') == 'render' and row.get('repeat')]
    changes = [row for row in extras if known_watched_state(row) and
               (row['position_changed'] or row['rng_changed'] or not row['same_rider'] or
                not row['same_view'] or row['state_before'] != row['state_after'] or
                any(row[key] for key in ('body_offsets', 'app_offsets', 'view_offsets')))]
    warnings = re.findall(r'^.*Unable to resolve (?:read|write) address[^\n]*$', runtime_log, re.M)
    return dict(trace_issues=issues, callback_count=len(callbacks), extra_count=len(extras),
                unknown_watched_callbacks=len(unknown), changed_extra_callbacks=len(changes),
                unresolved_address_warning_count=len(warnings),
                unresolved_address_warning_messages=sorted(set(warnings)),
                limits='Full trace checked. Unresolved host-read warnings can perturb the observer; '
                       'they are separate from the existing guest-fault gate.')


def core_config_without_analytics_id(text):
    """Ignore only Dolphin's per-profile analytics nonce, retaining every setting."""
    lines, section = [], None
    for line in text.splitlines():
        if re.fullmatch(r'\s*\[[^]]+\]\s*', line):
            section = line.strip()[1:-1]
        if section == 'Analytics' and re.match(r'\s*ID\s*=', line):
            continue
        lines.append(line)
    return '\n'.join(lines)+'\n'


def audit(output):
    """Recheck completed artifacts without launching another game or benchmark."""
    output = Path(output).resolve()
    report = json.loads((output/'report.json').read_text())
    cases, core_hashes, world_hashes = [], set(), set()
    canonical_core_hashes, gfx_hashes, frontend_hashes = set(), set(), set()
    for case in report['cases']:
        variant = next(v for v in report['build']['variants'] if v['level'] == case['opt_level'])
        receipt = runtime_receipt(output/case['name'], variant['module_sha256'], report['build']['common_player_sha256'])
        if receipt['sha256'] != case['runtime']['sha256']:
            raise ValueError('Native runtime receipt changed after the comparison case')
        trace = output/(case['name']+'.jsonl')
        if sha(trace) != case['trace_sha256']:
            raise ValueError('Native callback trace changed after the comparison case')
        core_hashes.add(receipt['core_config_sha256'])
        world_hashes.add(receipt['world_archive_sha256'])
        runtime = json.loads(Path(receipt['path']).read_text())
        profile = Path(runtime['profile'])
        core = profile/'Config/Dolphin.ini'
        if sha(core) != receipt['core_config_sha256']:
            raise ValueError('Core configuration changed after the runtime receipt')
        canonical_core_hashes.add(hashlib.sha256(core_config_without_analytics_id(core.read_text()).encode()).hexdigest())
        gfx_hashes.add(sha(profile/'Config/GFX.ini'))
        frontend_hashes.add(sha(profile/'config.ini'))
        log = Path(receipt['path']).with_suffix('.log').read_text()
        evidence = audit_callback_evidence(trace, log)
        if evidence['changed_extra_callbacks'] or not case['accepted']:
            status = 'failed'
        elif (evidence['trace_issues'] or evidence['unknown_watched_callbacks'] or
              not evidence['callback_count'] or not evidence['extra_count'] or
              evidence['unresolved_address_warning_count']):
            status = 'inconclusive'
        else:
            status = 'passed'
        cases.append(dict(name=case['name'], bounded_integrity=status, **evidence))
    same_raw_config = bool(cases) and len(core_hashes) == len(world_hashes) == 1 and None not in core_hashes | world_hashes
    same_settings = bool(cases) and all(len(values) == 1 and None not in values for values in
                                      (world_hashes, canonical_core_hashes, gfx_hashes, frontend_hashes))
    result = dict(cases=cases, identical_world_and_raw_core_config=same_raw_config,
                  equivalent_world_and_settings_except_analytics_id=same_settings,
                  core_config_sha256=sorted(core_hashes, key=str), world_archive_sha256=sorted(world_hashes, key=str),
                  core_without_analytics_id_sha256=sorted(canonical_core_hashes),
                  graphics_config_sha256=sorted(gfx_hashes), frontend_config_sha256=sorted(frontend_hashes),
                  ignored_config_fields=['Analytics.ID: random per-profile analytics identifier'],
                  all_bounded_integrity_passed=same_settings and all(c['bounded_integrity'] == 'passed' for c in cases),
                  causal_speedup_established=False,
                  limits='Strict known watched fields and matching runtime receipts do not establish '
                         'identical trajectories, complete-course correctness or phone performance.')
    (output/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def build(output, game, jobs, compiler=Path('/usr/bin/clang')):
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT/'local') or not 1 <= jobs <= 8:
        raise ValueError('Use a fresh local/ output and 1–8 build jobs')
    output.mkdir(parents=True, exist_ok=False)
    identity = source_identity()
    report = dict(schema=1, source_sha256=identity, game=str(Path(game).resolve()),
                  game_dol_sha256=sha(Path(game)/'sys/main.dol'), variants=[], platform=platform.platform(),
                  defaults_changed=False, phone_verified=False)
    env = os.environ.copy()
    env.pop('CMAKE_NINJA_FORCE_RESPONSE_FILE', None)
    cmake = shutil.which('cmake')
    if cmake is None:
        raise ValueError('cmake is required')
    compiler = Path(compiler).resolve()
    if not compiler.is_file():
        raise ValueError('Choose an existing C compiler executable')
    for level in (2, 3):
        directory = output/f'o{level}'
        directory.mkdir()
        configure = [cmake, '-S', str(CORE/'module-template'), '-B', str(directory/'build'), '-G', 'Ninja',
                     '-DCMAKE_MAKE_PROGRAM='+str(ROOT/'local/tooling/ninja'), '-DCMAKE_BUILD_TYPE=Release',
                     '-DCMAKE_C_COMPILER='+str(compiler),
                     '-DCMAKE_OSX_DEPLOYMENT_TARGET=14.0', '-DCMAKE_OSX_ARCHITECTURES=arm64',
                     '-DGAME_ID=GXBE69', '-DGENERATED_DIR='+str(GENERATED),
                     '-DGXRUNTIME_DIR='+str(CORE/'GXRuntime'),
                     '-DCHASSIS_ABI_DIR='+str(CORE/'Source/Core/Core/PowerPC/StaticRecomp'),
                     '-DRECOMPCORE_MODULE_ENABLE_IPO=ON', '-DRECOMPCORE_MODULE_OPT_LEVEL='+str(level)]
        print('Configuring O'+str(level), flush=True)
        with (directory/'configure.log').open('w') as log:
            subprocess.run(configure, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        flags = module_flags(directory/'build/build.ninja', level)
        print('Building O'+str(level), flush=True)
        started = time.monotonic()
        command = [cmake, '--build', str(directory/'build'), '--target', 'gGXBE69_recomp', '-j', str(jobs)]
        with (directory/'build.log').open('w') as log:
            subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        module = directory/'build/gGXBE69_recomp.dylib'
        variant = dict(level=level, configure=configure, build_command=command, flags=flags,
                       build_wall_seconds=time.monotonic()-started, module=str(module),
                       module_sha256=sha(module), module_bytes=module.stat().st_size,
                       compiler=compiler_identity(directory/'build'),
                       module_tables_sha256=sha(directory/'build/module_tables.inc'))
        variant['size_output'] = subprocess.check_output(['size', '-m', str(module)], text=True)
        variant['exports'] = subprocess.check_output(['nm', '-gU', str(module)], text=True).splitlines()
        if not any(line.endswith(' _staticrecomp_get_module') for line in variant['exports']):
            raise ValueError('AOT module ABI export missing')
        report['variants'].append(variant)
        (output/'build.json').write_text(json.dumps(report, indent=2)+'\n')
        print('Finished O'+str(level)+': '+str(module.stat().st_size)+' bytes', flush=True)
    if source_identity() != identity:
        raise ValueError('Source inputs changed during module builds; comparison rejected')
    report['identical_source_inputs_verified'] = True
    base = output/'player-base'
    command = [sys.executable, str(ROOT/'tools/gamecube_native_trace.py'), 'build', '--game', str(Path(game).resolve()),
               '--output', str(base), '--scheduler', '--interpolation']
    print('Building common diagnostic player', flush=True)
    with (output/'player-build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    receipt = json.loads((base/'build.json').read_text())
    for variant in report['variants']:
        player = output/f"o{variant['level']}-player"
        variant_directory = output/f"o{variant['level']}"
        player.mkdir()
        shutil.copy2(base/'player', player/'player')
        launcher = ('import sys\nfrom pathlib import Path\n'
                    f'ROOT=Path({str(ROOT)!r})\nsys.path.insert(0,str(ROOT/"tools"))\n'
                    'import native_gamecube as native\noriginal=native.executable\n'
                    f'player=Path({str(player/"player")!r})\n'
                    'native.executable=lambda name: player if name=="moderngekko-run" else original(name)\n'
                    f'native.MODULE=Path({str(variant_directory)!r})\nnative.main()\n')
        (player/'run_native.py').write_text(launcher)
        private_receipt = dict(receipt, module_variant=variant,
                               launchers={'run_native.py': sha(player/'run_native.py')})
        (player/'build.json').write_text(json.dumps(private_receipt, indent=2)+'\n')
        variant['player_dir'] = str(player)
    report['common_player_sha256'] = sha(base/'player')
    (output/'build.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def run(output, rounds):
    from gamecube_schedule_trace import summarize
    from mobile_report import distribution
    output = Path(output).resolve()
    report = json.loads((output/'build.json').read_text())
    if not report.get('identical_source_inputs_verified') or rounds not in (1, 2):
        raise ValueError('Require verified shared sources and one or two alternating paired rounds')
    if source_identity() != report['source_sha256']:
        raise ValueError('Module sources changed since the comparison build')
    # Also supports a build already in flight when compiler receipts were added.
    identities, tables, normalized_flags = [], [], []
    for variant in report['variants']:
        directory = Path(variant['module']).parent
        current = compiler_identity(directory)
        if 'compiler' in variant and current != variant['compiler']:
            raise ValueError('Compiler identity changed since build')
        identities.append(current)
        tables.append(sha(directory/'module_tables.inc'))
        normalized_flags.append([re.sub(r'-O[0-3](?= |$)', '-OLEVEL', value)
                                 for value in module_flags(directory/'build.ninja', variant['level'])['distinct_flags']])
    if identities[0] != identities[1] or tables[0] != tables[1] or normalized_flags[0] != normalized_flags[1]:
        raise ValueError('Compiler, module tables or flags differ beyond optimization level')
    base = output/'player-base'
    player_receipt = json.loads((base/'build.json').read_text())
    if sha(base/'player') != report['common_player_sha256'] or player_receipt['player_sha256'] != report['common_player_sha256']:
        raise ValueError('Common diagnostic player changed')
    helper_hashes = dict(player_receipt['scheduler_headers'],
                         **{'native_callback_trace.h': player_receipt['probe_header_sha256'],
                            'callback_timing.h': player_receipt['callback_timing_sha256']})
    if any(sha(base/name) != expected for name, expected in helper_hashes.items()):
        raise ValueError('Common diagnostic helper receipt does not match copied source')
    for variant in report['variants']:
        if sha(variant['module']) != variant['module_sha256']:
            raise ValueError('Comparison module changed')
        player = Path(variant['player_dir'])
        receipt = json.loads((player/'build.json').read_text())
        if (sha(player/'player') != report['common_player_sha256'] or receipt['player_sha256'] != report['common_player_sha256'] or
                sha(player/'run_native.py') != receipt['launchers']['run_native.py']):
            raise ValueError('Private comparison player/launcher changed')
    results = dict(build=report, compiler_identity=identities[0], module_tables_sha256=tables[0],
                   cases=[], causal_speedup_established=False,
                   acceptance_scope='Native/course/watched-state checks; not sustained 120 Hz or a causal speedup.',
                   limits='Sequential host-timed rides are not identical trajectories. Mac results do not establish phone gains.')
    prefix = 'opt'+time.strftime('%H%M%S')
    for index in range(rounds):
        for level in ((2, 3) if index % 2 == 0 else (3, 2)):
            variant = next(v for v in report['variants'] if v['level'] == level)
            name = f'round{index}-o{level}'
            trace = output/(name+'.jsonl')
            env = {k: v for k, v in os.environ.items() if not k.startswith(('SSX_NATIVE_', 'STATICRECOMP_LOCKSTEP'))}
            env.pop('SSX3_IDLE_PC', None)
            env.update(SSX_NATIVE_PROBE=str(trace), SSX_NATIVE_SCHEDULE='1', SSX_NATIVE_COMPLETION_RELEASE='1',
                       SSX_NATIVE_SKIP_BOOKKEEPING='1', SSX_NATIVE_START_SPACING='1', SSX_NATIVE_SPEED_FLOOR='1',
                       SSX3_DISPATCH_SAMPLES='1', SSX3_RUSH_PRESENT='0', SSX3_HOST_HLE='1')
            command = [sys.executable, str(ROOT/'tools/gamecube_schedule_check.py'), '--player-dir', variant['player_dir'],
                       '--game', report['game'], '--profile', prefix+str(index)+str(level), '--output', str(output/name),
                       '--seconds', '180', '--immediate-xfb', '--resolution', '640x528', '--metal-validation', 'off']
            print('Starting '+name, flush=True)
            thermal_before = thermal_context()
            with (output/(name+'.log')).open('w') as log:
                status = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
            case = dict(name=name, opt_level=level, exit_code=status, command=command, accepted=False,
                        thermal_before=thermal_before, thermal_after=thermal_context())
            if status == 0:
                case['runtime'] = runtime_receipt(output/name, variant['module_sha256'], report['common_player_sha256'])
            if trace.exists():
                rows = [json.loads(line) for line in trace.read_text().splitlines()]
                case['measurements'] = summarize(rows)
                measured = case['measurements']
                for label, repeated in (('extra', True), ('regular', False)):
                    measured[label+'_callback_cpu_ms'] = distribution([row.get('cpu_duration_ms') for row in rows
                        if row.get('event') == 'render' and bool(row.get('repeat')) == repeated and 145 <= row['wall'] < 170])
                case['accepted'] = (status == 0 and measured['complete_renders'] > 0 and
                                    measured['complete_extras'] > 0 and not any(measured['extra_state_changes'].values()))
                case['trace_sha256'] = sha(trace)
            results['cases'].append(case)
            (output/'report.json').write_text(json.dumps(results, indent=2)+'\n')
            if status:
                raise ValueError('Correctness run failed; stopping comparison at '+name)
    results['artifact_audit'] = audit(output)
    (output/'report.json').write_text(json.dumps(results, indent=2)+'\n')
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('build')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--game', type=Path, required=True)
    p.add_argument('--jobs', type=int, default=4)
    p.add_argument('--compiler', type=Path, default=Path('/usr/bin/clang'),
                   help='explicit C compiler, default AppleClang matching production')
    p = sub.add_parser('run')
    p.add_argument('output', type=Path)
    p.add_argument('--rounds', type=int, choices=(1, 2), default=2)
    p = sub.add_parser('audit', help='Recheck completed trace fields, observer warnings and matching runtime receipts')
    p.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'build':
            result = build(args.output, args.game, args.jobs, args.compiler)
        elif args.command == 'run':
            result = run(args.output, args.rounds)
        else:
            result = audit(args.output)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
