#!/usr/bin/env python3
"""Deterministic-movie A/B CPU harness for sub-noise module comparisons.

Host-timed inputs give +/-6% trajectory noise that swallows helper-level
(~1%) effects. Under SSX3_MOVIE_PLAY every guest input poll receives the
recorded pad state and the guest clock is fixed, so two plays of one movie
are the same trajectory: per-callback CPU (thread CPU seconds, robust to
ordinary host contention) becomes comparable toward the ~1% level, with the
measured pair noise setting the working floor.

  run       alternating A/B movie plays via gamecube_course_check.py
  compare   trajectory gate + per-arm CPU stats + resolved/unresolved verdict
  calibrate run+compare with the known idle-skip on/off delta

Trajectory gate: probe callbacks aligned by guest ordinal (not host wall
time). Riding callbacks (state_before == 0, same rider/view, no repeat)
must match in count-prefix, state, and watched-state hashes/flags across
all runs. CPU metric: sum of cpu_duration_ms over the common riding-prefix.
Dispatch counts are NOT compared: host-side knobs (idle skip) legitimately
change dispatch counts while keeping the guest trajectory identical.

Provenance follows native_determinism_check.py (movie/player/module/world
shas, normalized core config, clean runtime counters). Core configs must
match modulo Analytics ID plus exactly the ini lines the arm envs imply
(StaticRecompIdlePC when the arms differ in SSX3_IDLE_PC).
"""
import argparse
import configparser
import contextlib
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / 'tools') not in sys.path:
    sys.path.insert(0, str(ROOT / 'tools'))
import gamecube_course_check as course
from native_determinism_check import execution_status, finish, rider_observations


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_env(entries):
    """KEY=VALUE sets (empty value allowed); trailing KEY! unsets."""
    env, unset = {}, []
    for entry in entries or []:
        if entry.endswith('!') and '=' not in entry:
            unset.append(entry[:-1])
        elif '=' in entry:
            key, _, value = entry.partition('=')
            env[key] = value
        else:
            raise ValueError(f'Env entry must be KEY=VALUE or KEY!: {entry!r}')
    return env, unset


def merge_env(shared, arm):
    """Arm entries override shared ones; an arm set cancels a shared unset."""
    env = {**shared[0], **arm[0]}
    unset = [k for k in arm[1] + shared[1] if k not in arm[0]]
    return env, unset


def apply_env(base, env, unset):
    merged = dict(base)
    for key in unset:
        merged.pop(key, None)
    merged.update(env)
    return merged


def check_player(directory):
    """Verify an isolated diagnostic player against its build receipt."""
    directory = Path(directory).resolve()
    if not directory.is_relative_to(ROOT / 'local'):
        raise ValueError('Use an isolated diagnostic player under local/')
    receipt = json.loads((directory / 'build.json').read_text())
    for name, expected in [('player', receipt.get('player_sha256')),
                           ('run_native.py', (receipt.get('launchers') or {}).get('run_native.py'))]:
        if not expected or sha256(directory / name) != expected:
            raise ValueError(f'Player {name} does not match its build receipt')
    return receipt


@contextlib.contextmanager
def swapped_player(directory):
    """Route course_check's runtime launch through an isolated player."""
    original = course.subprocess.Popen

    def launch(command, *pos, **kw):
        command = list(command)
        target = str(ROOT / 'tools/native_gamecube.py')
        if target in command:
            command[command.index(target)] = str(Path(directory).resolve() / 'run_native.py')
        return original(command, *pos, **kw)

    course.subprocess.Popen = launch
    try:
        yield
    finally:
        course.subprocess.Popen = original


def host_sample():
    """One host-context sample: load, concurrent emulators/compilers, thermal."""
    def count(pattern):
        try:
            out = subprocess.run(['pgrep', '-c', '-f', pattern], capture_output=True,
                                 text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            return None
        return int(out.stdout.strip()) if out.returncode == 0 else 0
    try:
        thermal = subprocess.run(['pmset', '-g', 'therm'], capture_output=True,
                                 text=True, timeout=10)
        therm = (thermal.stdout + thermal.stderr).strip().replace('\n', ' | ')
    except (OSError, subprocess.TimeoutExpired):
        therm = None
    # Isolated players run as `.../player/player --game ...`, not
    # moderngekko-run: match both or the concurrency gate is blind.
    emulator = 'moderngekko-run|/player( |$)'
    return dict(t=time.time(), loadavg=list(os.getloadavg()),
                moderngekko=count(emulator),
                compilers=count('[c]lang|[x]codebuild|[s]wiftc|Xcode\\.app|[c]c1plus|[l]d\\.real'),
                thermal=therm)


@contextlib.contextmanager
def host_monitor(path, interval=30):
    """Sample host context to path every interval seconds until exit.

    The run directory appears when course_check starts, so the sampler
    waits for its parent instead of failing a thread nobody watches.
    """
    stop = threading.Event()

    def sample():
        deadline = time.time() + 180
        while not Path(path).parent.exists():
            if stop.is_set() or time.time() > deadline:
                return
            time.sleep(0.1)
        with open(path, 'w') as stream:
            while not stop.wait(interval):
                stream.write(json.dumps(host_sample()) + '\n')
                stream.flush()

    worker = threading.Thread(target=sample, daemon=True)
    worker.start()
    try:
        yield
    finally:
        stop.set()
        worker.join(timeout=interval + 5)


def one_run(args, output, profile, arm_env, label):
    """One bounded movie play; returns the course_check exit code.

    Invokes course_check in-process (like gamecube_schedule_check.py) so the
    isolated-player launch swap applies; a subprocess would not inherit it.
    """
    env_extra = dict(SSX3_MOVIE_PLAY=str(args.movie.resolve()),
                     SSX_NATIVE_QUIET='1' if args.quiet else '0')
    if 'SSX3_IDLE_PC' not in arm_env[0] and 'SSX3_IDLE_PC' not in arm_env[1]:
        # Pin the default explicitly so provenance shows the knob state.
        env_extra['SSX3_IDLE_PC'] = '0x80288ED4'
    paths = {}
    if args.probe:
        paths['SSX_NATIVE_PROBE'] = str(output / 'probe.jsonl')
    if args.signposts:
        paths['SSX_NATIVE_SIGNPOSTS'] = str(output / 'signposts.json')
    if args.pc_hist:
        paths['SSX_NATIVE_PC_HIST'] = str(output / 'pc_hist.txt')
    for key, path in paths.items():
        if Path(path).exists():
            raise ValueError(f'Preserving existing {path}')
        env_extra[key] = path
    env = apply_env(os.environ, {**env_extra, **arm_env[0]}, arm_env[1])
    argv = ['gamecube_course_check.py',
           '--game', str(args.game.resolve()), '--profile', profile,
           '--output', str(output), '--seconds', str(args.seconds),
           '--metal-validation', 'off']
    if args.course_manifest:
        argv += ['--course-manifest', str(args.course_manifest.resolve())]
    if args.screenshot_seconds:
        argv += ['--screenshot-seconds', str(args.screenshot_seconds)]
    if args.module:
        argv += ['--module', str(Path(args.module).resolve())]
    print(f'+ [{label}]', ' '.join(argv), flush=True)
    old_argv, old_environ = sys.argv, dict(os.environ)
    os.environ.clear()
    os.environ.update(env)
    sys.argv = argv
    try:
        with host_monitor(output / 'host.jsonl'):
            if args.player_dir:
                with swapped_player(args.player_dir):
                    course.main()
            else:
                course.main()
    except SystemExit as stop:
        return stop.code or 0
    finally:
        sys.argv = old_argv
        os.environ.clear()
        os.environ.update(old_environ)
    return 0


def run(args):
    output = args.output.resolve()
    if output.exists():
        raise ValueError('Preserving existing output; choose a fresh directory')
    if not args.movie.exists():
        raise ValueError(f'Missing movie {args.movie}')
    if args.probe and not args.player_dir:
        raise ValueError('--probe needs --player-dir: production runners emit no probe trace')
    if not 1 <= args.rounds <= 4:
        raise ValueError('Use 1-4 alternating rounds')
    free = shutil.disk_usage(output.parent).free
    if free < args.min_disk_bytes:
        raise ValueError(f'Only {free / 1e9:.2f} GB free; need '
                         f'{args.min_disk_bytes / 1e9:.2f} GB to run without ENOSPC-mangled traces')
    output.mkdir(parents=True)
    shared = parse_env(args.env)
    arms_env = [merge_env(shared, parse_env(entries)) for entries in (args.env_a, args.env_b)]
    env_a, env_b = arms_env
    player_receipt = check_player(args.player_dir) if args.player_dir else None
    manifest = dict(schema=1, movie=str(args.movie.resolve()), movie_sha256=sha256(args.movie),
                    game=str(args.game.resolve()), seconds=args.seconds, rounds=args.rounds,
                    env_shared=args.env or [], env_a=args.env_a or [], env_b=args.env_b or [],
                    module=str(Path(args.module).resolve()) if args.module else None,
                    player=str(Path(args.player_dir).resolve()) if args.player_dir else None,
                    player_receipt=player_receipt, quiet=bool(args.quiet), runs=[])
    order = []
    for index in range(args.rounds):
        order += [('a', env_a), ('b', env_b)] if index % 2 == 0 else [('b', env_b), ('a', env_a)]
    failed = None
    for position, (arm, arm_env) in enumerate(order):
        name = f'round{position // 2}-{arm}'
        profile = f'{args.profile_prefix}-{name}'
        run_dir = output / name
        try:
            code = one_run(args, run_dir, profile, arm_env, name)
        except Exception as error:
            # A crashed run still leaves a manifest behind: the attempted
            # comparison stays analyzable instead of vanishing.
            code, crashed = 1, f'{type(error).__name__}: {error}'
        else:
            crashed = None
        entry = dict(name=name, arm=arm, profile=profile, exit_code=code)
        if crashed:
            entry['crashed'] = crashed
        try:
            finish(run_dir, args.movie.resolve())
            entry['determinism'] = json.loads((run_dir / 'determinism.json').read_text())
        except (RuntimeError, OSError, ValueError) as error:
            entry['finish_error'] = str(error)
        manifest['runs'].append(entry)
        (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        if code:
            failed = name
            break
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    if failed:
        raise SystemExit(f'Comparison stopped at failed run {failed}')
    print(json.dumps({k: manifest[k] for k in ('movie_sha256', 'rounds')}, indent=2))
    return manifest


def trace_has_hashes(trace_path):
    """True when the trace carries watched-state hashes (non-quiet probe).

    Quiet rows zero the hash columns instead of omitting them, so absence
    means all-zero over the first callback rows, not nulls.
    """
    seen = 0
    with open(trace_path) as stream:
        for line in stream:
            row = json.loads(line)
            if row.get('event') not in ('update', 'render'):
                continue
            if row.get('body_hash_before'):
                return True
            seen += 1
            if seen >= 5:
                return False
    return False


def riding_series(trace_path, want_hashes, states=(0,)):
    """Callbacks in guest order at the given state_before values.

    State 0 is riding; other states select other guest phases from the same
    runs (useful when a knob concentrates in one phase). Fingerprints still
    gate trajectory equality.
    """
    series = []
    for line in Path(trace_path).read_text().splitlines():
        row = json.loads(line)
        if row.get('event') not in ('update', 'render') or row.get('repeat'):
            continue
        if row.get('state_before') not in states or not row.get('same_rider'):
            continue
        cpu = row.get('cpu_duration_ms')
        if cpu is None:
            raise ValueError(f'{trace_path}: probe row lacks cpu_duration_ms')
        key = (row.get('state_before'), row.get('state_after'),
               1 if row.get('position_changed') else 0, 1 if row.get('rng_changed') else 0)
        if want_hashes:
            key += (row.get('body_hash_before'), row.get('body_hash_after'))
        series.append(dict(class_=row['event'], cpu_ms=cpu, key=key))
    return series


def normalized_core_config(profile, allow_idle_line):
    """Dolphin.ini hash ignoring Analytics ID (+ idle line when declared)."""
    path = Path(profile) / 'Config/Dolphin.ini'
    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str
    config.read_string(path.read_text())
    if config.has_section('Analytics'):
        config.remove_option('Analytics', 'ID')
    if allow_idle_line and config.has_option('Core', 'StaticRecompIdlePC'):
        config.remove_option('Core', 'StaticRecompIdlePC')
    return hashlib.sha256(json.dumps({s: dict(config.items(s)) for s in config.sections()},
                                     sort_keys=True).encode()).hexdigest()


def stats(values):
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / max(1, len(values) - 1)
    return dict(n=len(values), mean=mean, stdev=math.sqrt(variance) if len(values) > 1 else 0.0,
                min=min(values), max=max(values))


def compare(args):
    output = args.output.resolve()
    manifest = json.loads((output / 'manifest.json').read_text())
    runs = manifest['runs']
    if not runs or any(r.get('exit_code') != 0 for r in runs):
        raise SystemExit('All runs must have exited 0 before comparison')
    allow_idle_line = ('SSX3_IDLE_PC' in
                       ' '.join(manifest.get('env_shared', []) + manifest['env_a'] + manifest['env_b']))
    issues, series, totals, details = [], {}, {}, {}
    # Weakest-link gate: a quiet arm carries no hashes, so states/flags
    # fingerprint every run when any trace lacks them.
    probed = [output / r['name'] / 'probe.jsonl' for r in runs]
    present = [p for p in probed if p.exists()]
    hashes = bool(present) and all(trace_has_hashes(p) for p in present)
    gate_strength = ('states+hashes' if hashes else
                     'unmeasurable (no probe traces)' if not present else
                     'states+flags (a quiet arm carries no hashes)')
    movie_sha = manifest['movie_sha256']
    for run in runs:
        run_dir = output / run['name']
        summary = run.get('determinism') or {}
        if summary.get('movie_sha256') != movie_sha:
            issues.append(f"{run['name']}: movie hash mismatch")
        evidence = summary.get('evidence') or {}
        counters = evidence.get('shutdown_counters') or {}
        status = execution_status(summary)
        if status.get('exit_code') != 0 or status.get('stopped_on_fault') is not None:
            issues.append(f"{run['name']}: clean exit without fault not established")
        if evidence.get('module_loaded') is not True:
            issues.append(f"{run['name']}: native module execution not established")
        if evidence.get('fallback_jit_runs') != 0:
            issues.append(f"{run['name']}: fallback_jit_runs nonzero")
        for key, value in [(k, evidence.get(k)) for k in ('invalid_memory_accesses', 'gpu_command_errors',
                                                         'unknown_guest_instructions')]:
            if value != 0:
                issues.append(f"{run['name']}: {key} missing or nonzero")
        host_path = run_dir / 'host.jsonl'
        if host_path.exists():
            hosts = [json.loads(line) for line in host_path.read_text().splitlines()]
            details.setdefault(run['name'], {})['host_samples'] = len(hosts)
            if hosts:
                details[run['name']]['max_moderngekko'] = max(h.get('moderngekko') or 0 for h in hosts)
                details[run['name']]['max_compilers'] = max(h.get('compilers') or 0 for h in hosts)
                details[run['name']]['max_load1'] = max(h['loadavg'][0] for h in hosts)
            if any((h.get('moderngekko') or 0) > 1 for h in hosts):
                issues.append(f"{run['name']}: another emulator ran concurrently (host contaminated)")
        trace = run_dir / 'probe.jsonl'
        if not trace.exists():
            issues.append(f"{run['name']}: probe trace missing (CPU is unmeasurable)")
            continue
        try:
            series[run['name']] = riding_series(trace, want_hashes=hashes,
                                               states=tuple(args.states))
        except ValueError as error:
            issues.append(f"{run['name']}: {error}")
    # Ordinal-aligned common prefix: same trajectory progress in every run.
    prefix = min((len(s) for s in series.values()), default=0)
    if prefix < args.min_callbacks:
        issues.append(f'Common riding prefix {prefix} < required {args.min_callbacks}')
    fingerprint_ok = True
    if series and prefix:
        keys = [[(r['class_'], r['key']) for r in s[:prefix]] for s in series.values()]
        if any(k != keys[0] for k in keys[1:]):
            fingerprint_ok = False
            issues.append('Riding-callback fingerprints diverge over the common prefix')
    gate_passed = not issues and fingerprint_ok and prefix >= args.min_callbacks
    for name, run_series in series.items():
        trimmed = run_series[:prefix]
        totals[name] = sum(r['cpu_ms'] for r in trimmed)
        details.setdefault(name, {}).update(
            riding_callbacks=len(run_series), prefix=prefix,
            update_ms=sum(r['cpu_ms'] for r in trimmed if r['class_'] == 'update'),
            render_ms=sum(r['cpu_ms'] for r in trimmed if r['class_'] == 'render'))
    arms = {}
    for arm in ('a', 'b'):
        names = [r['name'] for r in runs if r['arm'] == arm and r['name'] in totals]
        arms[arm] = stats([totals[n] for n in names]) if names else None
    # Config + provenance equality across runs.
    profiles = [ROOT / 'local/native/profiles' / r['profile'] for r in runs]
    try:
        normalized = [normalized_core_config(p, allow_idle_line) for p in profiles]
        if len(set(normalized)) != 1:
            issues.append('Core configs differ beyond the declared knob lines')
            gate_passed = False
    except OSError as error:
        issues.append(f'Core config unreadable: {error}')
        gate_passed = False
    modules = {json.loads((output / r['name'] / 'determinism.json').read_text()).get('module_sha256')
               for r in runs if (output / r['name'] / 'determinism.json').exists()}
    if len(modules) != 1:
        issues.append(f'Module changed across runs: {sorted(modules, key=str)}')
        gate_passed = False
    host_warnings = [f"{name}: compiler activity overlapped this run "
                     f"(max {info['max_compilers']} clang/xcodebuild; "
                     f"cache/memory contention is not excluded)"
                     for name, info in details.items()
                     if info.get('max_compilers')]
    result = dict(manifest=str(output / 'manifest.json'), runs=details, totals_ms=totals,
                  arms=arms, common_prefix=prefix, min_callbacks=args.min_callbacks,
                  gate_strength=gate_strength,
                  fingerprint_match=fingerprint_ok, issues=issues, gate_passed=gate_passed,
                  host_warnings=host_warnings,
                  observed_transitions={r['name']: (rider_observations(output / r['name']) or {}).get('state_transitions')
                                        for r in runs})
    if gate_passed and arms['a'] and arms['b']:
        mean_a, mean_b = arms['a']['mean'], arms['b']['mean']
        delta = mean_b - mean_a
        pairs = []
        for index in range(manifest['rounds']):
            pair = {}
            for arm in ('a', 'b'):
                name = f'round{index}-{arm}'
                if name in totals:
                    pair[arm] = totals[name]
            if len(pair) == 2:
                pairs.append(dict(round=index, delta_ms=pair['b'] - pair['a'],
                                  delta_pct=100 * (pair['b'] - pair['a']) / pair['a']))
        signs = {1 if p['delta_ms'] > 0 else -1 if p['delta_ms'] < 0 else 0 for p in pairs}
        sign_consistent = len(signs) == 1 and 0 not in signs
        noise_floor = max((a['max'] - a['min']) / 2 for a in arms.values())
        if manifest['rounds'] < 2 and not getattr(args, 'allow_single_round', False):
            # One pair cannot replicate its sign: a contaminated tail resolves
            # here and means nothing. Require --allow-single-round to proceed.
            result.update(delta_ms=delta, delta_pct=100 * delta / mean_a, round_pairs=pairs,
                          sign_consistent=sign_consistent, noise_floor_ms=noise_floor,
                          resolved=False,
                          confidence='provisional: single round without --allow-single-round')
        else:
            confidence = ('single round accepted via --allow-single-round'
                          if manifest['rounds'] < 2 else
                          'sign replicated across rounds' if sign_consistent else
                          'signs disagree across rounds')
            if host_warnings:
                confidence += '; compiler overlap recorded (see host_warnings)'
            result.update(delta_ms=delta, delta_pct=100 * delta / mean_a, round_pairs=pairs,
                          sign_consistent=sign_consistent, noise_floor_ms=noise_floor,
                          resolved=bool(sign_consistent and abs(delta) > noise_floor),
                          confidence=confidence)
    else:
        result.update(resolved=False)
        if gate_passed:
            issues.append('Both arms need measured totals before the delta resolves')
            result['issues'] = issues
    (output / 'ab_report.json').write_text(json.dumps(result, indent=2) + '\n')
    brief = {k: result[k] for k in ('gate_passed', 'common_prefix', 'fingerprint_match',
                                    'delta_ms', 'delta_pct', 'sign_consistent',
                                    'resolved') if k in result}
    print(json.dumps(brief, indent=2))
    if result.get('issues'):
        print(json.dumps({'issues': result['issues']}, indent=2))
    if not result.get('resolved'):
        raise SystemExit(1)
    return result


def calibrate(args):
    """Resolve the known idle-skip delta: arm A skip on, arm B skip off."""
    args.env_a = ['SSX3_IDLE_PC=0x80288ED4']
    args.env_b = ['SSX3_IDLE_PC=']
    args.profile_prefix = (args.profile_prefix or 'dctx-cal') + ''
    manifest = run(args)
    return compare(args)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('run', 'calibrate'):
        p = sub.add_parser(name, help=f'{name} alternating A/B movie plays')
        p.add_argument('--movie', type=Path, required=True)
        p.add_argument('--game', type=Path, required=True)
        p.add_argument('--output', type=Path, required=True)
        p.add_argument('--rounds', type=int, default=2)
        p.add_argument('--seconds', type=int, default=200)
        p.add_argument('--player-dir', type=Path)
        p.add_argument('--module', type=Path)
        p.add_argument('--course-manifest', type=Path)
        p.add_argument('--screenshot-seconds', type=int)
        p.add_argument('--profile-prefix', default='dctx-ab')
        p.add_argument('--probe', action='store_true', help='Capture per-run probe CPU traces')
        p.add_argument('--signposts', action='store_true')
        p.add_argument('--pc-hist', action='store_true')
        p.add_argument('--quiet', action='store_true',
                       help='Quiet probe rows (timing exact; hashes off, weaker gate)')
        p.add_argument('--min-callbacks', type=int, default=1000,
                       help='Common riding prefix required by calibrate-compare')
        p.add_argument('--min-disk-bytes', type=int, default=500_000_000,
                       help='Refuse to run below this free space (default 500MB)')
        p.add_argument('--states', type=int, nargs='*', default=[0],
                       help='state_before values selecting the metric window')
        p.add_argument('--env', nargs='*', default=[],
                       help='KEY=VALUE (or KEY!) applied to both arms; arm flags override')
        if name == 'run':
            p.add_argument('--env-a', nargs='*', default=[])
            p.add_argument('--env-b', nargs='*', default=[])
    p = sub.add_parser('compare')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--min-callbacks', type=int, default=1000)
    p.add_argument('--states', type=int, nargs='*', default=[0],
                   help='state_before values selecting the metric window (default: riding 0)')
    p.add_argument('--allow-single-round', action='store_true',
                   help='Resolve from one unreplicated pair (provisional; contamination can pass)')
    args = parser.parse_args()
    try:
        {'run': run, 'compare': compare, 'calibrate': calibrate}[args.command](args)
    except ValueError as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
