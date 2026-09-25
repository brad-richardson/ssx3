#!/usr/bin/env python3
"""GB8: wait for a truly quiet host, then run both speed boots back-to-back.

Trigger (polled every 3 s): all 4 P-lane slots free AND no foreign
ps2EntryRunner (exact argv[0] match) AND no compile running (clang++/ninja/
cmake) AND 1-min load < 4. On trigger: claim exclusive, snapshot ps/load
evidence, run speed-parallel then speed-cpu2 with GB8_HELD_SLOT=both (one
contiguous hold so a competing lane can't interleave), release, print results.

Usage: gb8_watch.py TIMEOUT_S
Exit 0: both boots ran (check their rc). Exit 2: timeout, nothing ran.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, '/Users/brad/dev/ssx3/local/tooling')
from p_lane_lease import claim, release, status  # noqa: E402

WORK = Path('/Users/brad/dev/ssx3-work/GB8')
SCRIPT = '/Users/brad/dev/ssx3/local/research/GB8/gb8_boot.py'


def foreign_runners():
    out = subprocess.run(['ps', 'aux'], capture_output=True, text=True).stdout
    hits = []
    for line in out.splitlines():
        f = line.split()
        if len(f) > 10 and f[10].endswith('/ps2EntryRunner'):
            hits.append(line.strip()[:160])
    return hits


def builds_running():
    out = subprocess.run(['ps', 'aux'], capture_output=True, text=True).stdout
    n = 0
    for line in out.splitlines():
        f = line.split()
        if len(f) > 10 and f[10].split('/')[-1] in ('clang', 'clang++', 'ninja', 'cmake',
                                                    'c++', 'cc', 'swiftc', 'ld'):
            n += 1
    return n


def quiet():
    st = status()
    if any(v is not None for v in st.values()):
        return False, 'slots %s' % st
    fr = foreign_runners()
    if fr:
        return False, 'runners %d' % len(fr)
    b = builds_running()
    if b:
        return False, 'builds %d' % b
    load1 = os.getloadavg()[0]
    if load1 >= 4.0:
        return False, 'load %.1f' % load1
    return True, 'load %.1f' % load1


def main():
    timeout = float(sys.argv[1])
    t0 = time.monotonic()
    last = ''
    while time.monotonic() - t0 < timeout:
        ok, why = quiet()
        if ok:
            # stability: require a second clean poll 3 s later
            time.sleep(3)
            ok2, why2 = quiet()
            if ok2:
                break
            last = why2
        else:
            if why != last:
                print('waiting: %s' % why, flush=True)
                last = why
            time.sleep(3)
    else:
        print('TIMEOUT: no quiet window in %.0fs' % timeout, flush=True)
        return 2
    print('TRIGGER: quiet (%s); claiming exclusive' % why2, flush=True)
    slot = claim('GB8-speedpair', exclusive=True)
    if slot is None:
        print('TRIGGER-LOST: exclusive claim failed', flush=True)
        return 2
    (WORK / 'run' / 'speedpair-claim.txt').write_text(
        json.dumps({'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                    'slot': slot, 'load': os.getloadavg()}) + '\n')
    try:
        print('--- ps snapshot at claim ---', flush=True)
        ps = subprocess.run(['ps', 'aux'], capture_output=True, text=True).stdout
        (WORK / 'run' / 'speedpair-ps-at-claim.txt').write_text(ps)
        print('\n'.join(ps.splitlines()[:5]), flush=True)
        env = dict(os.environ, GB8_HELD_SLOT='both')
        rcs = []
        for backend, label in (('parallel', 'speed-parallel'), ('cpu', 'speed-cpu2')):
            log = (WORK / 'run' / (label + '-driver.log')).open('w')
            rc = subprocess.run(
                ['python3', SCRIPT, '--mode', 'speed', '--backend', backend,
                 '--runner', str(WORK / 'bin' / 'runner-clean'), '--label', label,
                 '--stop-tick', '2400'],
                cwd=WORK, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
            log.close()
            rcs.append(rc)
            print('%s rc=%d' % (label, rc), flush=True)
            if rc != 0:
                break
        return 0 if all(r == 0 for r in rcs) and len(rcs) == 2 else 1
    finally:
        release(slot)
        print('released exclusive', flush=True)


if __name__ == '__main__':
    sys.exit(main())
