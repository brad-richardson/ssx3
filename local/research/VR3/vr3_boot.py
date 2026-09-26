#!/usr/bin/env python3
"""VR3: one-slot diagnostic boot of a speed runner (NOT a speed number).

Claims one mini slot, runs local/tooling/boot/ssx3_boot.py --mode speed with
SSX3_HELD_SLOT=<slot> (the driver neither claims the exclusive lease nor
releases), FR1-R1 route. With --sample-s N, once the run's trace passes
--sample-at it runs macOS `sample <runner pid> N` into <run>/sample.txt.
Extra runner env via --env K=V (repeatable). Releases the slot on exit.
(VR2's vr2_profile.py with the runner path and env as arguments.)

Usage: vr3_boot.py LABEL RUNNER [--sample-at 1800] [--sample-s 0] [--stop-tick 2400] [--env K=V]...
"""
import argparse, json, os, signal, subprocess, sys, time
sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
from p_lane_lease import claim, release

signal.signal(signal.SIGTERM, lambda *_: sys.exit(1))
ap = argparse.ArgumentParser()
ap.add_argument('label')
ap.add_argument('runner')
ap.add_argument('--sample-at', type=int, default=1800)
ap.add_argument('--sample-s', type=int, default=0)
ap.add_argument('--stop-tick', type=int, default=2400)
ap.add_argument('--env', action='append', default=[])
args = ap.parse_args()
WORK = '/Users/brad/dev/ssx3-work/VR3'
lane = '%s/run/%s' % (WORK, args.label)
os.makedirs(WORK + '/run', exist_ok=True)
slot = claim('VR3-' + args.label)
while slot is None:
    time.sleep(15)
    slot = claim('VR3-' + args.label)
child = sampler = None
try:
    env = dict(os.environ, SSX3_HELD_SLOT=str(slot))
    extra = []
    for kv in args.env:
        extra += ['--env', kv]
    out = open('%s/run/%s.txt' % (WORK, args.label), 'w')
    child = subprocess.Popen(
        ['python3', '/Users/brad/dev/ssx3/local/tooling/boot/ssx3_boot.py', '--mode', 'speed',
         '--backend', 'parallel', '--runner', args.runner, '--label', args.label, '--out', lane,
         '--route', 'fr1r1', '--stop-tick', str(args.stop_tick), '--wall', '200'] + extra,
        cwd=WORK, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    pid = None
    for line in child.stdout:
        out.write(line)
        out.flush()
        if pid is None and line.startswith('{"event": "boot"'):
            pid = json.loads(line)['pid']
            break
    t0 = time.time()
    while args.sample_s > 0 and pid is not None and sampler is None and child.poll() is None \
            and time.time() - t0 < 200:
        tick = 0
        try:
            with open(lane + '/trace.jsonl') as f:
                rows = f.read().splitlines()
            if rows:
                tick = json.loads(rows[-1]).get('tick', 0) or 0
        except (OSError, ValueError):
            pass
        if tick >= args.sample_at:
            sampler = subprocess.Popen(['sample', str(pid), str(args.sample_s), '-file', lane + '/sample.txt'],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print('sampling pid %d from tick %d' % (pid, tick), flush=True)
            break
        time.sleep(0.5)
    for line in child.stdout:
        out.write(line)
    child.wait()
    child = None
    if sampler is not None:
        sampler.wait(timeout=120)
finally:
    if child is not None and child.poll() is None:
        child.terminate()
        child.wait()
    release(slot)
