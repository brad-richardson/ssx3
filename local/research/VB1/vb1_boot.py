#!/usr/bin/env python3
"""VB1 (copied from VR1) bounded boot (E57 driver + F2 Mac paraLLEl env + --env passthrough): I26-FAST to the race, deterministic, empty cards.

Modes:
  hash   det-hash runner (PS2X_ENABLE_DET_HASH_TAP=ON): PS2X_DET_HASH_EVERY=1 and a
         GS stream capture (PS2X_GS_CAPTURE, closed at PS2X_GS_CAPTURE_STOP_TICK).
         Stops once the det-hash tick reaches --stop-tick and the capture closed.
  speed  diagnostics-off runner: PS2X_VSYNC_RATE_LOG=1 ([vsync-rate] every 5 s);
         takes the EXCLUSIVE mini lease (all slots). Stops at --stop-tick.
  profile  like speed (one slot, not a speed number) plus `sample <pid>` for
         --sample-s seconds once the tick passes --sample-at.

Both modes: PS2X_DETERMINISTIC=1, PS2X_SKIP_MOVIE=1 (dev-only), vsync pad clock,
empty mc0/mc1 under the run dir, no frame dump. Wall cap 500 s, no-progress cap
120 s, log cap 16 MiB. Only the recorded runner PID is signalled; the lease is
released on every path.

Usage: vr1_boot.py --mode hash|speed|profile --runner PATH --label NAME [--stop-tick N]
"""
import argparse
import signal
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

WORK = Path('/Users/brad/dev/ssx3-work/VB1')
VULKAN_LIB = '/opt/homebrew/lib/libvulkan.1.dylib'
ELF = Path('/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72')
ISO = Path('/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso')
ISO_SHA = '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'

# I26-FAST (local/research/I26/ROUTES.md), race HUD at tick ~1714.
ROUTE = ('10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,'
         '19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,'
         '28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,'
         '30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,'
         '33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,'
         '35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,'
         '38522:down:30000')

WALL_CAP_S = 500
PROGRESS_CAP_S = 120
LOG_CAP_BYTES = 16 * 1024 * 1024

HASH_TICK = re.compile(rb'\[det-hash:v1\] tick=(\d+)\b')
RATE_TICK = re.compile(rb'\[vsync-rate\] tick=(\d+)\b')
CAPTURE_STOP = b'[gs:capture] stopped at marker'


def sha_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    # SIGTERM -> SystemExit so the finally below kills the runner and releases the lease.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=('hash', 'speed', 'profile'), required=True)
    ap.add_argument('--runner', required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--stop-tick', type=int, default=2400)
    ap.add_argument('--sample-at', type=int, default=1900)
    ap.add_argument('--sample-s', type=int, default=30)
    ap.add_argument('--backend', choices=('cpu', 'parallel'), default='parallel')
    ap.add_argument('--env', action='append', default=[], help='extra KEY=VALUE (PS2X_VU1_RECOMP*)')
    args = ap.parse_args()

    runner = Path(args.runner).resolve()
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

    env = {k: v for k, v in os.environ.items() if not k.startswith('PS2X_')}
    env.update(PS2X_CD_IMAGE=str(ISO), PS2X_SKIP_MOVIE='1', PS2X_DETERMINISTIC='1',
               PS2X_PAD_SCRIPT_CLOCK='vsync', PS2X_PAD_SCRIPT=ROUTE,
               PS2X_MC_ROOT=str(lane / 'mc0'), PS2X_MISSING_FUNCTION_POLICY='stop',
               COPYFILE_DISABLE='1')
    if args.backend == 'parallel':
        env.update(PS2X_GS_BACKEND='parallel', GRANITE_VULKAN_LIBRARY=VULKAN_LIB,
                   PGS_HIER_BINNING='force')
    for kv in args.env:
        k, v = kv.split('=', 1)
        env[k] = v
    if args.mode == 'hash':
        env.update(PS2X_DET_HASH_EVERY='1', PS2X_GS_CAPTURE=str(lane / 'gs.cap'),
                   PS2X_GS_CAPTURE_STOP_TICK=str(args.stop_tick))
        tick_re = HASH_TICK
    else:
        env.update(PS2X_VSYNC_RATE_LOG='1')
        tick_re = RATE_TICK

    exclusive = args.mode == 'speed'
    held = os.environ.get('VB1_HELD_SLOTS')
    if held:
        slot = None  # all four slots pre-held by speed_hold.py; it releases them
        print(json.dumps({'event': 'using-held-slots', 'holder': held}), flush=True)
    else:
        slot = claim('VB1-' + args.label, exclusive=exclusive)
    while slot is None and not held:
        print('lease busy; retrying in 30 s', flush=True)
        time.sleep(30)
        slot = claim('VB1-' + args.label, exclusive=exclusive)

    result = {'label': args.label, 'mode': args.mode, 'runner': str(runner),
              'sha_reads': reads, 'stop_tick': args.stop_tick, 'slot': slot,
              'env': {k: v for k, v in env.items() if k.startswith(('PS2X_', 'GRANITE_', 'PGS_'))},
              'load_start': os.getloadavg()}
    proc = None
    sampler = None
    try:
        t0 = time.monotonic()
        with log.open('wb') as out:
            proc = subprocess.Popen([str(runner), str(ELF)], cwd=lane, env=env,
                                    stdout=out, stderr=subprocess.STDOUT)
            result['runner_pid'] = proc.pid
            print(json.dumps({'event': 'boot', 'label': args.label, 'pid': proc.pid,
                              'slot': slot}), flush=True)
            last_tick, last_progress, bound = 0, t0, None
            while True:
                now = time.monotonic()
                if proc.poll() is not None:
                    bound = 'exit'
                    break
                if now - t0 >= WALL_CAP_S:
                    bound = 'wall_cap'
                    break
                if log.stat().st_size > LOG_CAP_BYTES:
                    bound = 'log_cap'
                    break
                tail = log.read_bytes()[-65536:]
                m = tick_re.findall(tail)
                if m and int(m[-1]) > last_tick:
                    last_tick, last_progress = int(m[-1]), now
                if now - last_progress >= PROGRESS_CAP_S:
                    bound = 'progress_cap'
                    break
                if args.mode == 'profile' and sampler is None and last_tick >= args.sample_at:
                    sampler = subprocess.Popen(
                        ['sample', str(proc.pid), str(args.sample_s), '-file',
                         str(lane / 'sample.txt')],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    result['sample_start_tick'] = last_tick
                if last_tick >= args.stop_tick:
                    if args.mode != 'hash' or CAPTURE_STOP in log.read_bytes():
                        if sampler is None or sampler.poll() is not None:
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
                      load_end=os.getloadavg())
        (lane / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({k: v for k, v in result.items() if k not in ('env', 'sha_reads')}),
              flush=True)
        return 0 if bound == 'target' else 1
    finally:
        if sampler is not None and sampler.poll() is None:
            sampler.wait(timeout=120)
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        if not held:
            release(slot)


if __name__ == '__main__':
    sys.exit(main())
