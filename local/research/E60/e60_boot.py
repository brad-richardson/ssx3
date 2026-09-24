#!/usr/bin/env python3
"""E60 bounded I26-FAST race capture; one mini lease slot."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
from p_lane_lease import claim, release

WORK = Path('/Users/brad/dev/ssx3-work/E60')
DEFAULT_RUNNER = Path('/Users/brad/dev/ssx3-work/E60/build/ps2xRuntime/ps2EntryRunner')
ELF = Path('/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72')
ISO = Path('/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso')
ROUTE = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,'
         '18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,'
         '22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,'
         '29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,'
         '31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,'
         '33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,'
         '35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,'
         '37521:cross:200,37772:down:700,38522:down:30000')
RATE = re.compile(r'\[vsync-rate\] tick=(\d+) rate=([\d.]+)/s')
TICK = re.compile(r'\btick=(\d+)\b')


def bytes_in(path):
    return sum(p.stat().st_size for p in path.rglob('*') if p.is_file()) if path.exists() else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--label', required=True)
    ap.add_argument('--wall', type=int, default=500)
    ap.add_argument('--target', type=int, default=2100)
    ap.add_argument('--capture', action='store_true')
    ap.add_argument('--runner', type=Path, default=DEFAULT_RUNNER)
    ap.add_argument('--fpmode', choices=('ieee', 'ps2'), default='ps2')
    ap.add_argument('--exclusive', action='store_true')
    args = ap.parse_args()
    if args.wall > 600 or args.wall < 1:
        ap.error('wall must be 1..600 seconds')
    for p in (args.runner, ELF, ISO):
        if not p.exists():
            raise SystemExit(f'missing input: {p}')
    lane = WORK / 'run' / args.label
    lane.mkdir(parents=True, exist_ok=True)
    log = lane / 'boot.log'
    frames = lane / 'frames'
    if args.capture:
        frames.mkdir(exist_ok=True)
    slot = claim('E60-' + args.label, exclusive=args.exclusive)
    while slot is None:
        print('Both mini lease slots busy; polling in 60 s', flush=True)
        time.sleep(60)
        slot = claim('E60-' + args.label, exclusive=args.exclusive)
    result = {'label': args.label, 'slot': slot, 'capture': args.capture,
              'target_tick': args.target, 'wall_cap_s': args.wall,
              'runner': str(args.runner), 'cwd': str(lane), 'frames': {}}
    env = dict(os.environ)
    for k in tuple(env):
        if k.startswith('PS2X_'):
            env.pop(k)
    env.update(PS2X_CD_IMAGE=str(ISO), PS2X_SKIP_MOVIE='1',
               PS2X_PAD_SCRIPT_CLOCK='vsync', PS2X_PAD_SCRIPT=ROUTE,
               PS2X_VSYNC_RATE_LOG='1', PS2X_EE_FPMODE=args.fpmode, COPYFILE_DISABLE='1',
               PS2X_E60_TAP=str(lane / 'vu0.bin'))
    if args.capture:
        env['PS2X_FRAME_DUMP_DIR'] = str(frames)
    result['env'] = {k: env[k] for k in env if k.startswith('PS2X_')}
    result['load_start'] = os.getloadavg()
    result['other_jobs_start'] = subprocess.run(
        ['ps', '-axo', 'pid,comm'], text=True, capture_output=True).stdout
    proc = None
    try:
        t0 = time.monotonic()
        with log.open('wb') as out:
            proc = subprocess.Popen([str(args.runner), str(ELF)], cwd=lane, env=env,
                                    stdout=out, stderr=subprocess.STDOUT)
            result['pid'] = proc.pid
            print(json.dumps({'event': 'boot', 'pid': proc.pid, 'slot': slot}), flush=True)
            last_rate_tick = 0
            last_progress = t0
            snapshots = {'race1800': (1790, 1830), 'race1950': (1940, 1980),
                         'race2100': (2090, 2130)}
            bound = None
            while True:
                now = time.monotonic()
                ret = proc.poll()
                if ret is not None:
                    bound = 'exit'
                    result['rc'] = ret
                    break
                if now - t0 >= args.wall:
                    bound = 'wall'
                    break
                if log.exists() and log.stat().st_size > 64 * 1024 * 1024:
                    bound = 'log_cap'
                    break
                if args.capture and bytes_in(frames) > 256 * 1024 * 1024:
                    bound = 'frames_cap'
                    break
                if args.capture:
                    side = frames / 'upload-latest.txt'
                    if side.exists():
                        m = TICK.search(side.read_text(errors='replace'))
                        if m:
                            vt = int(m.group(1))
                            for name, (lo, hi) in snapshots.items():
                                if name not in result['frames'] and lo <= vt <= hi:
                                    src = frames / 'upload-latest.png'
                                    if src.exists():
                                        dst = lane / f'{name}-tick{vt}.png'
                                        shutil.copyfile(src, dst)
                                        result['frames'][name] = str(dst)
                if log.exists():
                    tail = log.read_bytes()[-32768:].decode(errors='replace')
                    matches = RATE.findall(tail)
                    if matches:
                        vt = int(matches[-1][0])
                        if vt > last_rate_tick:
                            last_rate_tick = vt
                            last_progress = now
                if now - last_progress >= 120:
                    bound = 'progress_cap'
                    break
                if last_rate_tick >= args.target and (not args.capture or len(result['frames']) == len(snapshots)):
                    bound = 'target'
                    break
                time.sleep(1)
            if proc.poll() is None:
                proc.terminate()
                try:
                    result['rc'] = proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    result['rc'] = proc.wait(timeout=10)
                    bound += '+kill'
            result['bound'] = bound
            result['elapsed_s'] = round(time.monotonic() - t0, 3)
            result['last_rate_tick'] = last_rate_tick
            result['log_bytes'] = log.stat().st_size
            result['load_end'] = os.getloadavg()
        (lane / 'result.json').write_text(json.dumps(result, indent=2))
        print(json.dumps({k: v for k, v in result.items() if k not in ('env', 'other_jobs_start')}), flush=True)
        return 0 if bound == 'target' else 1
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        release(slot)


if __name__ == '__main__':
    sys.exit(main())
