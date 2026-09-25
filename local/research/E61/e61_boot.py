#!/usr/bin/env python3
"""E61 bounded boot: I26-FAST to tick 1750, deterministic, empty cards.

Modes:
  speed    diagnostics-off runner + PS2X_VSYNC_RATE_LOG=1 ([vsync-rate] every
           5 s); takes the EXCLUSIVE mini lease (all 4 slots). --sound adds
           PS2X_SOUND=1. Stops at --stop-tick. Wall cap 300 s.
  profile  like speed with PS2X_SOUND=1 fixed, ONE lease slot (not a speed
           number). Takes --samples SPEC triggers of `sample <pid>` driven by
           interpolated tick estimates (last rate line tick + rate * elapsed,
           polled every 0.5 s), plus `ps -M` per-thread CPU snapshots at each
           sample start/end. SPEC: "trig,dur,name;..." e.g.
           "730,5,s1;1050,10,s2;1620,10,s3". Wall cap 500 s.

Both modes: PS2X_DETERMINISTIC=1, PS2X_SKIP_MOVIE=1 (dev-only), vsync pad
clock, I26-FAST route (race HUD ~1714), empty mc0/mc1 under the run dir, no
frame dump. Log cap 16 MiB, no-progress cap 120 s. Only the recorded runner
PID is signalled; the lease is released on every path.

Usage:
  e61_boot.py --mode speed --runner PATH --label NAME [--sound]
  e61_boot.py --mode profile --runner PATH --label NAME [--samples SPEC]
  e61_boot.py --self-check   (no boot, no lease)
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
from p_lane_lease import claim, release  # noqa: E402

WORK = Path('/Users/brad/dev/ssx3-work/E61')
ELF = Path('/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72')
ISO = Path('/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso')
ISO_SHA = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'

# I26-FAST (local/research/I26/ROUTES.md), race HUD at tick ~1714.
ROUTE = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,'
         '18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,'
         '22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,'
         '29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,'
         '31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,'
         '33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,'
         '35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,'
         '37521:cross:200,37772:down:700,38522:down:30000')
I26_FAST_CANON = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,'
                  '18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,'
                  '22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,'
                  '29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,'
                  '31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,'
                  '33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,'
                  '35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,'
                  '37521:cross:200,37772:down:700,38522:down:30000')

SPEED_WALL_CAP_S = 300
PROFILE_WALL_CAP_S = 500
PROGRESS_CAP_S = 120
LOG_CAP_BYTES = 16 * 1024 * 1024

RATE = re.compile(rb'\[vsync-rate\] tick=(\d+) rate=([\d.]+)/s')
DEFAULT_SAMPLES = '730,5,s1;1050,10,s2;1620,10,s3'


def sha_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def parse_samples(spec):
    out = []
    for part in spec.split(';'):
        trig, dur, name = part.split(',')
        out.append((int(trig), int(dur), name))
    trigs = [t for t, _, _ in out]
    assert trigs == sorted(trigs), 'sample triggers must ascend'
    assert all(d > 0 for _, d, _ in out), 'durations must be positive'
    return out


def self_check():
    cases = []

    def record(name, ok, detail=''):
        cases.append((name, ok))
        print('%s %s %s' % ('ok' if ok else 'MISMATCH', name, detail))

    record('route_is_i26_fast', ROUTE == I26_FAST_CANON)
    record('route_31_entries', len(ROUTE.split(',')) == 31, str(len(ROUTE.split(','))))
    record('route_first_start', ROUTE.split(',')[0] == '10611:start:250')
    record('route_last_tuck', ROUTE.split(',')[-1] == '38522:down:30000')
    try:
        specs = parse_samples(DEFAULT_SAMPLES)
        record('default_samples_parse', [n for _, _, n in specs] == ['s1', 's2', 's3'])
        record('default_samples_ascend', True)
    except AssertionError as exc:
        record('default_samples_parse', False, str(exc))
    try:
        parse_samples('100,5,a;50,5,b')
        record('samples_reject_descending', False, 'no assertion raised')
    except AssertionError:
        record('samples_reject_descending', True)
    record('speed_wall_le_300', SPEED_WALL_CAP_S <= 300, str(SPEED_WALL_CAP_S))
    record('profile_wall_le_600', PROFILE_WALL_CAP_S <= 600, str(PROFILE_WALL_CAP_S))
    record('progress_cap_120', PROGRESS_CAP_S == 120, str(PROGRESS_CAP_S))
    record('log_cap_16mib', LOG_CAP_BYTES == 16 * 1024 * 1024, str(LOG_CAP_BYTES))
    m = RATE.search(b'[vsync-rate] tick=1234 rate=32.46/s (0.541x of 59.94)\n')
    record('rate_re', m is not None and m.group(1) == b'1234' and m.group(2) == b'32.46')
    return 0 if all(ok for _, ok in cases) else 1


def thread_snapshot(pid):
    """Per-thread CPU% via ps -M; returns text (never raises)."""
    try:
        r = subprocess.run(['ps', '-M', str(pid)], capture_output=True, text=True, timeout=15)
        return r.stdout + r.stderr
    except Exception as exc:  # noqa: BLE001
        return 'ps -M failed: %r' % exc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=('speed', 'profile'), required=True)
    ap.add_argument('--runner', required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--stop-tick', type=int, default=1750)
    ap.add_argument('--sound', action='store_true')
    ap.add_argument('--samples', default=DEFAULT_SAMPLES)
    args = ap.parse_args()

    runner = Path(args.runner).resolve()
    if not runner.exists():
        raise SystemExit('missing runner: %s' % runner)
    lane = WORK / 'run' / args.label
    if lane.exists():
        raise SystemExit('refusing to reuse %s' % lane)
    lane.mkdir(parents=True)
    (lane / 'mc0').mkdir()
    (lane / 'mc1').mkdir()
    log = lane / 'boot.log'

    reads = [{str(p): sha_of(p) for p in (runner, ISO, ELF)} for _ in range(2)]
    if reads[0] != reads[1]:
        raise SystemExit('two SHA reads differ')
    if reads[0][str(ISO)] != ISO_SHA or reads[0][str(ELF)] != ELF_SHA:
        raise SystemExit('ISO/ELF SHA mismatch')

    if args.mode == 'profile':
        specs = parse_samples(args.samples)
        wall_cap = PROFILE_WALL_CAP_S
    else:
        specs = []
        wall_cap = SPEED_WALL_CAP_S

    env = {k: v for k, v in os.environ.items() if not k.startswith('PS2X_')}
    env.update(PS2X_CD_IMAGE=str(ISO), PS2X_SKIP_MOVIE='1', PS2X_DETERMINISTIC='1',
               PS2X_PAD_SCRIPT_CLOCK='vsync', PS2X_PAD_SCRIPT=ROUTE,
               PS2X_VSYNC_RATE_LOG='1',
               PS2X_MC_ROOT=str(lane / 'mc0'), PS2X_MISSING_FUNCTION_POLICY='stop',
               COPYFILE_DISABLE='1')
    if args.sound or args.mode == 'profile':
        env['PS2X_SOUND'] = '1'

    exclusive = args.mode == 'speed'
    slot = claim('E61-' + args.label, exclusive=exclusive)
    while slot is None:
        print('lease busy; retrying in 30 s', flush=True)
        time.sleep(30)
        slot = claim('E61-' + args.label, exclusive=exclusive)

    result = {'label': args.label, 'mode': args.mode, 'runner': str(runner),
              'sha_reads': reads, 'stop_tick': args.stop_tick, 'slot': slot,
              'sound': bool(args.sound or args.mode == 'profile'),
              'samples_spec': args.samples if specs else None,
              'env': {k: v for k, v in env.items() if k.startswith('PS2X_')},
              'load_start': os.getloadavg()}
    proc = None
    samplers = []  # (name, Popen, start_wall, start_est)
    fired = set()
    try:
        t0 = time.monotonic()
        with log.open('wb') as out:
            proc = subprocess.Popen([str(runner), str(ELF)], cwd=lane, env=env,
                                    stdout=out, stderr=subprocess.STDOUT)
            result['runner_pid'] = proc.pid
            print(json.dumps({'event': 'boot', 'label': args.label, 'pid': proc.pid,
                              'slot': slot}), flush=True)
            last_tick, last_rate, last_line_wall = 0, 0.0, t0
            last_progress, bound = t0, None
            sample_events = []
            while True:
                now = time.monotonic()
                if proc.poll() is not None:
                    bound = 'exit'
                    break
                if now - t0 >= wall_cap:
                    bound = 'wall_cap'
                    break
                if log.stat().st_size > LOG_CAP_BYTES:
                    bound = 'log_cap'
                    break
                tail = log.read_bytes()[-65536:]
                for mtick, mrate in RATE.findall(tail):
                    vt = int(mtick)
                    if vt > last_tick:
                        last_tick, last_rate, last_line_wall = vt, float(mrate), now
                        last_progress = now
                if now - last_progress >= PROGRESS_CAP_S:
                    bound = 'progress_cap'
                    break
                est_tick = last_tick + last_rate * (now - last_line_wall)
                if specs:
                    for trig, dur, name in specs:
                        if name not in fired and est_tick >= trig:
                            fired.add(name)
                            pre = thread_snapshot(proc.pid)
                            (lane / ('psm-%s-pre.txt' % name)).write_text(pre)
                            sp = subprocess.Popen(
                                ['sample', str(proc.pid), str(dur), '-file',
                                 str(lane / ('sample-%s.txt' % name))],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            samplers.append((name, sp, now, est_tick))
                            sample_events.append(
                                {'name': name, 'trigger': trig, 'dur_s': dur,
                                 'start_wall_s': round(now - t0, 1),
                                 'start_est_tick': round(est_tick, 1),
                                 'last_rate_tick': last_tick})
                            print(json.dumps({'event': 'sample-start', 'name': name,
                                              'est_tick': round(est_tick, 1)}), flush=True)
                    for name, sp, swall, _ in samplers:
                        if sp.poll() is not None and 'end_wall_s' not in next(
                                e for e in sample_events if e['name'] == name):
                            post = thread_snapshot(proc.pid)
                            (lane / ('psm-%s-post.txt' % name)).write_text(post)
                            next(e for e in sample_events if e['name'] == name).update(
                                end_wall_s=round(time.monotonic() - t0, 1))
                if last_tick >= args.stop_tick:
                    if all(sp.poll() is not None for _, sp, _, _ in samplers):
                        bound = 'target'
                        break
                time.sleep(0.5)
            if proc.poll() is None:
                proc.terminate()
                try:
                    result['runner_rc'] = proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    result['runner_rc'] = proc.wait(timeout=10)
                    bound += '+kill'
            else:
                result['runner_rc'] = proc.returncode
        result.update(bound=bound, elapsed_s=round(time.monotonic() - t0, 3),
                      last_tick=last_tick, log_bytes=log.stat().st_size,
                      load_end=os.getloadavg(), sample_events=sample_events)
        (lane / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({k: v for k, v in result.items() if k not in ('env', 'sha_reads')}),
              flush=True)
        return 0 if bound == 'target' else 1
    finally:
        for _, sp, _, _ in samplers:
            if sp.poll() is None:
                try:
                    sp.wait(timeout=120)
                except subprocess.TimeoutExpired:
                    sp.kill()
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        release(slot)


if __name__ == '__main__':
    if '--self-check' in sys.argv:
        sys.exit(self_check())
    sys.exit(main())
