#!/usr/bin/env python3
"""Isolated, fresh-process FastDiscSpeed A/B startup measurements.

Builds one private startup observer from existing native archives; never changes
the production player, game module, phone defaults or vendor sources. Timings
are Mac menu-startup evidence, not cold-storage, course-load or phone results.
"""
import argparse
import configparser
import contextlib
import json
import os
from pathlib import Path
import platform
import re
import resource
import shlex
import statistics
import subprocess
import time

import gamecube_startup as startup
from gamecube_draw_trace import BUILD, ROOT, VENDOR, compile_copy, sha
import native_gamecube as native

ORDER = (False, True, True, False, False, True)
REQUIRED = ('frontend_update', 'startup_movies_skipped', 'title_loading',
            'title_assets_ready', 'title_ready', 'main_menu_loading', 'main_menu_ready')


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def thermal_context():
    result = subprocess.run(['/usr/bin/pmset', '-g', 'therm'],
                            text=True, capture_output=True, timeout=5)
    return dict(exit_code=result.returncode, text=result.stdout + result.stderr)


def inject_config_observer(header):
    marker = '  std::fflush(output);'
    if header.count(marker) != 1:
        raise ValueError('Startup event emission seam changed')
    observation = r'''  std::fprintf(output,"{\"event\":\"loading_config\",\"startup_event\":\"%s\",\"fast_disc_speed\":%s}\n",
      event,Config::Get(Config::MAIN_FAST_DISC_SPEED)?"true":"false");
'''
    return ('#include "Common/Config/Config.h"\n#include "Core/Config/MainSettings.h"\n' +
            header.replace(marker, observation + marker))


def build(args):
    native.check_pins()
    native.check_patches()
    if sha(args.game / 'sys/main.dol') != native.PINS['dol_sha256']:
        raise ValueError('Startup addresses require the pinned GXBE69 executable')
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / 'local'):
        raise ValueError('Use an isolated output under local/')
    out.mkdir(parents=True, exist_ok=False)
    original = VENDOR / 'vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp'
    header = ROOT / 'native/diagnostics/startup_skip.h'
    copied = out / header.name
    copied.write_text(inject_config_observer(header.read_text()))
    marker = '          const u32 runtime_dispatch_address = m_guest.pc;'
    source = original.read_text()
    if source.count(marker) != 1:
        raise ValueError('Startup dispatch seam changed')
    source = '#include "' + str(copied) + '"\n' + source.replace(
        marker, '          StartupBoot::Step(m_guest);\n' + marker)
    target = out / 'Startup_Run.cpp'
    target.write_text(source)
    commands = subprocess.check_output([str(ROOT / 'local/tooling/ninja'), '-C',
        str(BUILD), '-t', 'commands', 'moderngekko-run'], text=True).splitlines()
    compile = compile_copy(next(c for c in commands if c.endswith('/StaticRecompCore_Run.cpp')),
                           target, out / 'startup.o')
    link = shlex.split(next(c for c in commands if ' -o moderngekko-run ' in c))
    link = link[2:link.index('&&', 2)]
    link[link.index('-o') + 1] = str(out / 'player')
    link.insert(link.index('libmoderngekko.a'), str(out / 'startup.o'))
    receipt = dict(schema=1, source_sha256=sha(original), header_sha256=sha(header),
        copied_header_sha256=sha(copied), injected_source_sha256=sha(target),
        dol_sha256=sha(args.game / 'sys/main.dol'), game=str(args.game.resolve()),
        module_sha256=sha(native.MODULE / 'build/gGXBE69_recomp.dylib'),
        world_sha256=sha(args.game / 'files/data/worlds/bam.big'),
        production_sha256=sha(BUILD / 'moderngekko-run'), commands=[compile, link],
        tool_sha256=sha(Path(__file__)), startup_runner_sha256=sha(Path(startup.__file__)))
    before = time.monotonic()
    for command in receipt['commands']:
        subprocess.run(command, cwd=BUILD, check=True)
    receipt['build_wall_seconds'] = time.monotonic() - before
    receipt['player_sha256'] = sha(out / 'player')
    if sha(BUILD / 'moderngekko-run') != receipt['production_sha256']:
        raise RuntimeError('Production player changed during isolated build')
    save(out / 'build.json', receipt)
    print(out / 'player')


def canonical_config(text):
    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str
    config.read_string(text)
    if config.has_option('Analytics', 'ID'):
        config.remove_option('Analytics', 'ID')
    return {section: dict(config[section]) for section in config.sections()}


def analyze_events(rows, expected_fast):
    phases = [r for r in rows if r.get('event') != 'loading_config']
    errors = []
    if [r.get('event') for r in phases] != list(REQUIRED):
        errors.append('missing, duplicate, failed or out-of-order startup phase')
    observed = [r for r in rows if r.get('event') == 'loading_config']
    if ([r.get('startup_event') for r in observed] != list(REQUIRED) or
            any(type(r.get('fast_disc_speed')) is not bool or
                r['fast_disc_speed'] != expected_fast for r in observed)):
        errors.append('missing or mismatched effective FastDiscSpeed observation')
    times = [r.get('elapsed_seconds') for r in phases]
    clocks = [r.get('guest_timebase') for r in phases]
    if (any(type(t) not in (int, float) or not 0 <= t <= 180 for t in times) or
            any(b < a for a, b in zip(times, times[1:]))):
        errors.append('invalid startup wall clock')
    if (any(type(t) is not int or t < 0 for t in clocks) or
            any(b < a for a, b in zip(clocks, clocks[1:]))):
        errors.append('invalid startup guest clock')
    if errors:
        return dict(accepted=False, errors=errors)
    mapped = {r['event']: r for r in phases}
    intervals = {}
    for a, b in (('frontend_update', 'title_assets_ready'),
                 ('title_ready', 'main_menu_loading'),
                 ('main_menu_loading', 'main_menu_ready')):
        intervals[a + '_to_' + b] = dict(
            wall_seconds=mapped[b]['elapsed_seconds'] - mapped[a]['elapsed_seconds'],
            guest_seconds=(mapped[b]['guest_timebase'] - mapped[a]['guest_timebase']) / 40500000)
    return dict(accepted=True, errors=[],
                phase_seconds={r['event']: r['elapsed_seconds'] for r in phases},
                intervals=intervals)


def run(args):
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / 'local') or out.exists():
        raise ValueError('Use a fresh evidence directory under local/')
    if not 30 <= args.seconds <= 60:
        raise ValueError('Use a bounded 30–60 second menu-only run')
    if Path(args.profile_prefix).name != args.profile_prefix or args.profile_prefix in ('.', '..'):
        raise ValueError('Profile prefix must be a single directory name')
    player = args.player.resolve()
    receipt = json.loads((player.parent / 'build.json').read_text())
    if sha(player) != receipt['player_sha256']:
        raise ValueError('Player receipt mismatch')
    if sha(player.parent / 'startup_skip.h') != receipt['copied_header_sha256']:
        raise ValueError('Copied observer receipt mismatch')
    if sha(Path(startup.__file__)) != receipt['startup_runner_sha256']:
        raise ValueError('Startup runner changed since build receipt')
    if sha(args.game / 'files/data/worlds/bam.big') != receipt['world_sha256']:
        raise ValueError('World identity changed')
    if sha(native.MODULE / 'build/gGXBE69_recomp.dylib') != receipt['module_sha256']:
        raise ValueError('Module identity changed')
    out.mkdir(parents=True)
    save(out / 'build-receipt.json', receipt)
    results = dict(schema=1, order=list(ORDER), seconds=args.seconds,
        machine=platform.platform(), load_before=os.getloadavg(),
        thermal_before=thermal_context(), run_tool_sha256=sha(Path(__file__)), cases=[],
        limits=['Fresh processes/profiles; OS storage cache is not cleared.',
                'Mac startup to menu only; no phone/course-loading/card-save acceptance.',
                'Metal validation and identical software rendering configuration retained.',
                'Child CPU covers the whole bounded run, including time after menu readiness and launcher verification subprocesses.',
                'Only Analytics.ID is excluded when comparing post-run config files.'])
    for index, fast in enumerate(ORDER, 1):
        name = f'{args.profile_prefix}-{index}-' + ('fast' if fast else 'control')
        profile = ROOT / 'local/native/profiles' / name
        case = out / name
        case.mkdir()
        original_launch = startup.native.launch
        def launch(config_args):
            config = profile / 'Config'
            config.mkdir(parents=True, exist_ok=False)
            core = ('[Core]\nCPUThread = False\nDSPHLE = True\nSkipIPL = True\n'
                    f'FastDiscSpeed = {str(fast)}\n[DSP]\nEnableJIT = False\n'
                    '[Interface]\nConfirmStop = False\n')
            (config / 'Dolphin.ini').write_text(core)
            (case / 'Dolphin-before.ini').write_text(core)
            (config / 'GFX.ini').write_text('[Settings]\nInternalResolution = 1\n')
            (profile / 'config.ini').write_text('[Video]\nresolution=640x528\n'
                'backend=Vulkan\nfullscreen=false\nshow_fps_in_title=true\n')
            return original_launch(config_args)
        startup.native.launch = launch
        before_reports = set((ROOT / 'local/reports/native-runs').glob('*.json'))
        before_cpu = resource.getrusage(resource.RUSAGE_CHILDREN)
        before_wall = time.monotonic()
        error = None
        try:
            with (case / 'launch.log').open('w') as log, contextlib.redirect_stdout(log):
                startup.run(argparse.Namespace(player=player, game=args.game, profile=name,
                                               seconds=args.seconds, skip=True))
        except Exception as exc:
            error = str(exc)
        finally:
            startup.native.launch = original_launch
        after_cpu = resource.getrusage(resource.RUSAGE_CHILDREN)
        item = dict(index=index, fast_disc_speed=fast, profile=str(profile), error=error,
                    wall_seconds=time.monotonic()-before_wall,
                    child_user_seconds=after_cpu.ru_utime-before_cpu.ru_utime,
                    child_system_seconds=after_cpu.ru_stime-before_cpu.ru_stime)
        trace = player.parent / (name + '.jsonl')
        try:
            rows = [json.loads(line) for line in trace.read_text().splitlines()]
            (case / 'startup.jsonl').write_bytes(trace.read_bytes())
            item['startup'] = analyze_events(rows, fast)
        except (OSError, ValueError) as exc:
            item['startup'] = dict(accepted=False, errors=[str(exc)])
        new_reports = set((ROOT / 'local/reports/native-runs').glob('*.json')) - before_reports
        matches = [json.loads(p.read_text()) for p in new_reports
                   if json.loads(p.read_text()).get('profile') == str(profile)]
        if len(matches) == 1:
            runtime = matches[0]
            save(case / 'runtime.json', runtime)
            raw_log = Path(runtime['log']).read_text(errors='replace')
            (case / 'runtime.log').write_text(raw_log)
            item['runtime'] = runtime
            item['observer_warnings'] = raw_log.count('MemoryWatcher')
            item['warning_lines'] = [line for line in raw_log.splitlines()
                if re.search(r'\bwarning\b|\bpanic\b|invalid address', line, re.I)]
            if (runtime.get('runner_sha256') != receipt['player_sha256'] or
                    runtime.get('module_sha256') != receipt['module_sha256'] or
                    runtime.get('world_archive_sha256') != receipt['world_sha256']):
                item['error'] = item['error'] or 'runtime player/module/world identity mismatch'
        else:
            item['error'] = item['error'] or 'missing unique runtime receipt'
        if (profile / 'Config/Dolphin.ini').exists():
            after = (profile / 'Config/Dolphin.ini').read_text()
            (case / 'Dolphin-after.ini').write_text(after)
            item['post_config'] = canonical_config(after)
        item['other_config_sha256'] = {}
        for relative in ('Config/GFX.ini', 'Config/GCPadNew.ini', 'config.ini'):
            source = profile / relative
            if source.is_file():
                (case / (relative.replace('/', '-') + '.after')).write_bytes(source.read_bytes())
                item['other_config_sha256'][relative] = sha(source)
        if (player.parent / (name + '-check.json')).exists():
            (case / 'input-check.json').write_bytes((player.parent / (name + '-check.json')).read_bytes())
        item['captures'] = []
        for source in sorted((profile / 'ScreenShots').rglob('*.png')):
            copied = case / source.name
            copied.write_bytes(source.read_bytes())
            item['captures'].append(dict(source=str(source), copied=str(copied), sha256=sha(copied)))
        if not item['captures']:
            item['error'] = item['error'] or 'missing rendered screenshot evidence'
        item['accepted'] = (not item['error'] and item['startup']['accepted'] and
                            item.get('observer_warnings') == 0)
        results['cases'].append(item)
        save(out / 'report.json', results)
        print(f'{name}: accepted={item["accepted"]}, phases={item["startup"].get("phase_seconds")}', flush=True)
    comparable = []
    for case in results['cases']:
        config = json.loads(json.dumps(case.get('post_config', {})))
        config.get('Core', {}).pop('FastDiscSpeed', None)
        comparable.append(config)
    results['post_configs_equal_except_fast_and_analytics_id'] = all(
        c == comparable[0] for c in comparable[1:])
    other_configs = [c['other_config_sha256'] for c in results['cases']]
    results['other_configs_equal'] = (all(len(c) == 3 for c in other_configs) and
                                     all(c == other_configs[0] for c in other_configs[1:]))
    results['accepted'] = (all(c['accepted'] for c in results['cases']) and
                          results['post_configs_equal_except_fast_and_analytics_id'] and
                          results['other_configs_equal'])
    results['menu_seconds'] = {}
    for fast in (False, True):
        values = [c['startup']['phase_seconds']['main_menu_ready'] for c in results['cases']
                  if c['fast_disc_speed'] == fast and c['startup']['accepted']]
        results['menu_seconds']['fast' if fast else 'control'] = dict(
            values=values, median=statistics.median(values) if values else None)
    results['load_after'] = os.getloadavg()
    results['thermal_after'] = thermal_context()
    save(out / 'report.json', results)
    if not results['accepted']:
        raise RuntimeError('Loading comparison lacks complete acceptance; inspect report.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('build', 'run'):
        child = sub.add_parser(name)
        child.add_argument('--game', type=Path, default=ROOT / 'local/game/gc-gari-027')
        child.add_argument('--output', type=Path, required=True)
        if name == 'run':
            child.add_argument('--player', type=Path, required=True)
            child.add_argument('--profile-prefix', required=True)
            child.add_argument('--seconds', type=float, default=40)
    args = parser.parse_args()
    {'build': build, 'run': run}[args.command](args)
