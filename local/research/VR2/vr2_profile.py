#!/usr/bin/env python3
"""VR2: diagnostic VU1 profile of one speed runner (one mini slot, NOT a speed number).

Claims one slot, runs local/tooling/boot/ssx3_boot.py --mode speed with
SSX3_HELD_SLOT=<slot> (so the driver neither claims the exclusive lease nor
releases), and once the run's trace passes --sample-at runs macOS
`sample <runner pid> <s>` into <run>/sample.txt. Releases the slot on exit.
Then: profile_share.py <run>/sample.txt (VB1's bucketer).

Usage: vr2_profile.py CAND [--sample-at 1800] [--sample-s 15]
"""
import argparse, json, os, signal, subprocess, sys, time
sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
from p_lane_lease import claim, release

signal.signal(signal.SIGTERM, lambda *_: sys.exit(1))
ap = argparse.ArgumentParser()
ap.add_argument('cand')
ap.add_argument('--sample-at', type=int, default=1800)
ap.add_argument('--sample-s', type=int, default=15)
args = ap.parse_args()
WORK = '/Users/brad/dev/ssx3-work/VR2'
runner = ('/Users/brad/dev/ssx3-work/F5/bin/runner-clean' if args.cand == 'base'
          else '%s/bin/runner-%s-clean' % (WORK, args.cand))
label = 'p-' + args.cand
lane = '%s/run/%s' % (WORK, label)
slot = claim('VR2-' + label)
while slot is None:
    time.sleep(15)
    slot = claim('VR2-' + label)
child = sampler = None
try:
    env = dict(os.environ, SSX3_HELD_SLOT=str(slot))
    out = open('%s/run/%s.txt' % (WORK, label), 'w')
    child = subprocess.Popen(
        ['python3', '/Users/brad/dev/ssx3/local/tooling/boot/ssx3_boot.py', '--mode', 'speed',
         '--backend', 'parallel', '--runner', runner, '--label', label, '--out', lane,
         '--route', 'fr1r1', '--stop-tick', '2400', '--wall', '150'],
        cwd=WORK, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    pid = None
    for line in child.stdout:
        out.write(line)
        out.flush()
        if pid is None and line.startswith('{"event": "boot"'):
            pid = json.loads(line)['pid']
            break
    t0 = time.time()
    while pid is not None and sampler is None and child.poll() is None and time.time() - t0 < 150:
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
