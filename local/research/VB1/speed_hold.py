#!/usr/bin/env python3
"""VR1: run speed boots under one exclusive mini lease hold.

Plain exclusive claims starve while other lanes cycle single slots, so this
claims each slot as it frees (poll 5 s) until it holds all four, then runs the
given candidates back to back (each a vr1_boot.py --mode speed run with
VB1_HELD_SLOTS set), then releases every slot. Two ~90 s boots per hold keep
one hold <= 5 min (brief).

Host load: other lanes' builds aren't leased (a 70-130 load spike voided hold F,
NOTEBOOK 11:14). The holder starts claiming only when the 1-min load is < 8.
Inside the hold, each boot starts only when the load is < 8; if that takes more
than 120 s, the hold is abandoned (slots released) and retried from the start.
It never measures while this lane's own build runs (VB1/BUILDING exists).

'<cand>off' runs bin/runner-<cand>-speed with PS2X_VU1_RECOMP=0 (interpreter only).

Usage: speed_hold.py LABEL_PREFIX START CAND [CAND ...]   (labels s<N>-<cand>)
"""
import os, signal, subprocess, sys, time
sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
import p_lane_lease as L

signal.signal(signal.SIGTERM, lambda *_: sys.exit(1))  # run finally: release slots
prefix, start, cands = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
WORK = '/Users/brad/dev/ssx3-work/VB1'
LOAD_MAX, LOAD_WAIT_MAX = 8.0, 120


def quiet():
    return os.getloadavg()[0] < LOAD_MAX and not os.path.exists(WORK + '/BUILDING')


def one_hold():
    held = []
    text = 'VB1-%s pid=%d utc=%s\n' % (prefix, os.getpid(),
                                       time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    t0 = time.time()
    child = None
    try:
        while not quiet():
            time.sleep(10)
        while len(held) < len(L.SLOTS):
            for n, path in L.SLOTS.items():
                if n not in held and L._try(path, text):
                    held.append(n)
            if len(held) < len(L.SLOTS):
                time.sleep(5)
        print('holding all slots after %.0f s' % (time.time() - t0), flush=True)
        h0 = time.time()
        env = dict(os.environ, VB1_HELD_SLOTS=prefix)
        n = start
        for c in cands:
            n += 1
            label = 's%d-%s' % (n, c)
            w0 = time.time()
            while not quiet():
                if time.time() - w0 > LOAD_WAIT_MAX:
                    print('abandon hold: load %s for %d s before %s' % (os.getloadavg(), LOAD_WAIT_MAX, label), flush=True)
                    return False
                time.sleep(10)
            runner = c[:-3] if c.endswith('off') else c
            extra = ['--env', 'PS2X_VU1_RECOMP=0'] if c.endswith('off') else []
            with open('%s/boot-%s.txt' % (WORK, label), 'w') as out:
                child = subprocess.Popen(
                    ['python3', '/Users/brad/dev/ssx3/local/research/VB1/vb1_boot.py',
                     '--mode', 'speed', '--runner', 'bin/runner-%s-speed' % runner,
                     '--label', label, '--stop-tick', '2400'] + extra,
                    cwd=WORK, env=env, stdout=out, stderr=subprocess.STDOUT)
                rc = child.wait()
                child = None
            print('%s rc=%d %s load=%s' % (label, rc, time.strftime('%H:%M:%S'), os.getloadavg()), flush=True)
        print('hold %.0f s' % (time.time() - h0), flush=True)
        return True
    finally:
        if child is not None and child.poll() is None:
            child.terminate()  # vr1_boot.py kills its runner on SIGTERM
            child.wait()
        for n in held:
            L.release(n)


for attempt in range(6):
    if one_hold():
        break
    # an abandoned hold may have left a partial run dir; the next attempt needs fresh labels
    start += 100
