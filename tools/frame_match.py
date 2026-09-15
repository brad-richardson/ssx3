#!/usr/bin/env python3
"""Pair screenshots from two replays of one movie by where the rider was.

A visual A/B of two texture packs needs the *same moment* in both arms.
Screenshots are taken on a wall-clock cadence, and two arms do not run at the
same speed - a pack that loads 8,000 files paces differently from stock - so
the same screenshot index is not the same moment. Guest time does not help
either: the arms reach the start gate at different guest times, and the
pre-start hold defeats any "seconds since the race began" estimate.

What is identical in both arms is the trajectory: the same movie drives the
same inputs, so the rider passes through the same positions. This pairs frames
by that position, using each run's own rider trace (`rider.jsonl`) to look up
where the rider was when a screenshot was written.

    python3 tools/frame_match.py RUN_A PROFILE_A RUN_B PROFILE_B [COUNT]

Each line of output is a pair with the distance between the two riders in guest
units; anything under a couple of hundred units is the same view. A fine
screenshot cadence (`--screenshot-seconds 1`) makes close pairs much more
likely, because the pairing can only choose among the frames that exist.
"""

import datetime, json, sys
from pathlib import Path

def samples(run):
    rows = [json.loads(l) for l in (Path(run)/'rider.jsonl').read_text().splitlines() if l.strip()]
    return [r for r in rows if (r['x'] or r['y'] or r['z'])]

def moving(rows, threshold=500.0):
    """Drop the pre-start hold: samples before the rider leaves the gate."""
    first = rows[0]
    for index, r in enumerate(rows):
        if ((r['x']-first['x'])**2 + (r['y']-first['y'])**2 + (r['z']-first['z'])**2) > threshold**2:
            return rows[index:]
    return rows

def shots(profile):
    out = []
    for p in sorted((Path('local/native/profiles')/profile/'ScreenShots/GXBE69').glob('*.png')):
        dt = datetime.datetime.strptime(p.stem.split('_', 1)[1], '%Y-%m-%d_%H-%M-%S')
        out.append((p, dt.timestamp()))
    return out

def frames(run, profile):
    rows = moving(samples(run))
    out = []
    for path, wall in shots(profile):
        near = min(rows, key=lambda r: abs(r['wall_time'] - wall))
        if abs(near['wall_time'] - wall) > 1.5:
            continue
        out.append((path, (near['x'], near['y'], near['z']), near['t'] - rows[0]['t']))
    return out

def pairs(run_a, prof_a, run_b, prof_b, count=3, spread=2000.0):
    fa, fb = frames(run_a, prof_a), frames(run_b, prof_b)
    cand = []
    for pa, xa, ea in fa:
        for pb, xb, eb in fb:
            d = sum((xa[i]-xb[i])**2 for i in range(3)) ** 0.5
            cand.append((d, xa, ea, pa, pb))
    cand.sort(key=lambda c: c[0])
    picked = []
    for d, xa, ea, pa, pb in cand:
        if all(sum((xa[i]-q[i])**2 for i in range(3)) ** 0.5 > spread for _, q, _, _, _ in picked):
            picked.append((d, xa, ea, pa, pb))
        if len(picked) == count:
            break
    return picked

if __name__ == '__main__':
    a, pa, b, pb = sys.argv[1:5]
    for d, x, e, fa, fb in pairs(a, pa, b, pb, count=int(sys.argv[5]) if len(sys.argv) > 5 else 3):
        print(json.dumps({'units_apart': round(d, 1), 'seconds_into_run': round(e, 1),
                          'a': str(fa), 'b': str(fb)}))
