#!/usr/bin/env python3
"""VR1: run speed boots under one exclusive mini lease hold.

Plain exclusive claims starve while other lanes cycle single slots, so this
claims each slot as it frees (poll 5 s) until it holds all four, then runs the
given candidates back to back (each a vr1_boot.py --mode speed run with
VR1_HELD_SLOTS set), then releases every slot. Keep one hold <= 5 min (brief):
two ~90 s boots per hold.

Usage: speed_hold.py LABEL_PREFIX START CAND [CAND ...]   (labels s<N>-<cand>)
"""
import os, signal, subprocess, sys, time
sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
import p_lane_lease as L

signal.signal(signal.SIGTERM, lambda *_: sys.exit(1))  # run finally: release slots
prefix, start, cands = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
text = 'VR1-%s pid=%d utc=%s\n' % (prefix, os.getpid(), time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
held = []
t0 = time.time()
try:
    while len(held) < len(L.SLOTS):
        for n, path in L.SLOTS.items():
            if n not in held and L._try(path, text):
                held.append(n)
        if len(held) < len(L.SLOTS):
            time.sleep(5)
    # Never measure while this lane's own build runs (build.sh callers touch BUILDING).
    while os.path.exists('/Users/brad/dev/ssx3-work/VR1/BUILDING'):
        time.sleep(5)
    print('holding all slots after %.0f s' % (time.time() - t0), flush=True)
    h0 = time.time()
    env = dict(os.environ, VR1_HELD_SLOTS=prefix)
    n = start
    for c in cands:
        n += 1
        label = 's%d-%s' % (n, c)
        with open('/Users/brad/dev/ssx3-work/VR1/boot-%s.txt' % label, 'w') as out:
            rc = subprocess.call(['python3', '/Users/brad/dev/ssx3/local/research/VR1/vr1_boot.py',
                                  '--mode', 'speed', '--runner', 'bin/runner-%s-speed' % c,
                                  '--label', label, '--stop-tick', '2400'],
                                 cwd='/Users/brad/dev/ssx3-work/VR1', env=env, stdout=out,
                                 stderr=subprocess.STDOUT)
        print('%s rc=%d %s load=%s' % (label, rc, time.strftime('%H:%M:%S'), os.getloadavg()), flush=True)
    print('hold %.0f s' % (time.time() - h0), flush=True)
finally:
    for n in held:
        L.release(n)
