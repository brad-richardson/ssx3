#!/usr/bin/env python3
"""HR1: one exclusive mini hold (all four slots) around back-to-back speed boots.
Usage: hr1_hold.py LABEL:ARGS [LABEL:ARGS ...]   (ARGS = extra hr1_boot.py args, space-separated)
Brief rule: exclusive holds <= 5 min; the caller leaves a gap between holds."""
import json, os, subprocess, sys, time
sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
from p_lane_lease import claim, release  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER = '/Users/brad/dev/ssx3-work/HR1/bin/runner-hr1'
HOLD_CAP_S = 300

slot = claim('HR1-hold', exclusive=True)
while slot is None:
    print('exclusive lease busy; retrying in 20 s', flush=True)
    time.sleep(20)
    slot = claim('HR1-hold', exclusive=True)
t0 = time.monotonic()
print(json.dumps({'event': 'hold', 'slot': slot, 'load': os.getloadavg()}), flush=True)
try:
    env = dict(os.environ, HR1_HELD_SLOT=str(slot))
    for spec in sys.argv[1:]:
        if time.monotonic() - t0 > HOLD_CAP_S - 95:
            print(json.dumps({'event': 'skip-cap', 'spec': spec}), flush=True)
            continue
        label, _, extra = spec.partition(':')
        cmd = [sys.executable, os.path.join(HERE, 'hr1_boot.py'), '--mode', 'speed', '--backend',
               'parallel', '--runner', RUNNER, '--label', label, '--stop-tick', '2400'] + extra.split()
        print(json.dumps({'event': 'run', 'cmd': cmd[2:], 'load': os.getloadavg()}), flush=True)
        subprocess.run(cmd, env=env)
finally:
    release(slot)
    print(json.dumps({'event': 'released', 'held_s': round(time.monotonic() - t0, 1)}), flush=True)
