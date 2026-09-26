#!/usr/bin/env python3
"""VR3 (VR2's holder, VR3 runners): speed boots under one exclusive mini lease hold (VB1's holder, repointed
at the shared driver local/tooling/boot/ssx3_boot.py).

Waits for the 1-min load < 8, claims each slot as it frees (poll 5 s) until it
holds all four, runs the candidates back to back with SSX3_HELD_SLOT=both
(`ssx3_boot.py --mode speed`, FR1-R1, paraLLEl, stop t2400), then releases every
slot. The hold is capped at 300 s: a boot that could not finish inside the cap
(estimate 80 s) is skipped and reported, never started.

Candidates: see RUNNERS.

Usage: speed_hold.py HOLD CAND [CAND ...]   (run dirs run/<HOLD>-<n>-<cand>)
"""
import os, signal, subprocess, sys, time
sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
import p_lane_lease as L

signal.signal(signal.SIGTERM, lambda *_: sys.exit(1))  # run finally: release slots
hold, cands = sys.argv[1], sys.argv[2:]
WORK = '/Users/brad/dev/ssx3-work/VR3'
DRIVER = '/Users/brad/dev/ssx3/local/tooling/boot/ssx3_boot.py'
LOAD_MAX, HOLD_CAP, BOOT_EST = 8.0, 300, 80


# VR3: c0 = fork tip d585e5c + census (off); c3 = vr3 d52e7f0 with the VU0 image
# compiled in: off = both knobs off, on = PS2X_VU0_RECOMP=1, dir = + PS2X_VU0_DIRECT=1.
RUNNERS = {'base': (WORK + '/bin/runner-c0-clean', []),
           'off': (WORK + '/bin/runner-c3-clean', []),
           'on': (WORK + '/bin/runner-c3-clean', ['--env', 'PS2X_VU0_RECOMP=1']),
           'dir': (WORK + '/bin/runner-c3-clean', ['--env', 'PS2X_VU0_RECOMP=1', '--env', 'PS2X_VU0_DIRECT=1'])}


def runner(c):
    return RUNNERS.get(c, ('%s/bin/runner-%s-clean' % (WORK, c), []))


held = []
child = None
text = 'VR3-%s pid=%d utc=%s\n' % (hold, os.getpid(), time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
t0 = time.time()
try:
    while os.getloadavg()[0] >= LOAD_MAX:
        time.sleep(10)
    while len(held) < len(L.SLOTS):
        for n, path in L.SLOTS.items():
            if n not in held and L._try(path, text):
                held.append(n)
        if len(held) < len(L.SLOTS):
            time.sleep(5)
    h0 = time.time()
    print('%s holding all slots after %.0f s at %s load=%s' % (
        hold, h0 - t0, time.strftime('%H:%M:%S'), [round(x, 1) for x in os.getloadavg()]), flush=True)
    env = dict(os.environ, SSX3_HELD_SLOT='both')
    for i, c in enumerate(cands, 1):
        label = '%s-%d-%s' % (hold, i, c)
        if time.time() - h0 + BOOT_EST > HOLD_CAP:
            print('%s SKIPPED (hold cap)' % label, flush=True)
            continue
        with open('%s/run/%s.txt' % (WORK, label), 'w') as out:
            child = subprocess.Popen(
                ['python3', DRIVER, '--mode', 'speed', '--backend', 'parallel', '--runner', runner(c)[0],
                 '--label', label, '--out', '%s/run/%s' % (WORK, label), '--route', 'fr1r1',
                 '--stop-tick', '2400', '--wall', '120'] + runner(c)[1],
                cwd=WORK, env=env, stdout=out, stderr=subprocess.STDOUT)
            rc = child.wait()
            child = None
        print('%s rc=%d %s load=%s' % (label, rc, time.strftime('%H:%M:%S'),
                                       [round(x, 1) for x in os.getloadavg()]), flush=True)
    print('%s hold %.0f s' % (hold, time.time() - h0), flush=True)
finally:
    if child is not None and child.poll() is None:
        child.terminate()  # the driver kills its runner by PID on SIGTERM
        child.wait()
    for n in held:
        L.release(n)
