#!/usr/bin/env python3
"""MT1 stage 2': two-timeline model of the threaded unit from a census log.

Input: the PS2X_MTVU_CENSUS_OUT file of a synchronous census run:
  J <tau> <unit_ns> <d|f>   unit job submitted at EE time tau, unit_ns of work
  S <tau> <reason> [detail] a sync hit (EE waits for the unit unless the
                            scenario frees that reason)
  V <tau> <tick>            VBlankStart (a sync; frame boundary)
tau = EE host ns with all unit work removed, so the synchronous wall between
two events is d_tau + the unit work in between.

Model (threaded): the EE clock E advances by d_tau; a job starts on the unit
at max(U, E + submit) and ends unit_ns * slow + wake later; a sync sets
E = max(E, U). Per-frame wall = E at V(k) - E at V(k-1). Host costs the
census cannot see (thread wake/cache/GS-worker contention) are the
--submit/--wake/--slow knobs; the default is the ideal case.

Output: per-window totals and wait time by sync reason. Model numbers, not
speed measurements.
"""
import argparse
import collections
import sys


def load(path):
    ev = []
    with open(path) as f:
        for line in f:
            p = line.split()
            if not p:
                continue
            if p[0] == "J" and len(p) >= 4:
                ev.append(("J", int(p[1]), int(p[2]), p[3]))
            elif p[0] == "S" and len(p) >= 3:
                ev.append(("S", int(p[1]), p[2], p[3] if len(p) > 3 else ""))
            elif p[0] == "V" and len(p) >= 3:
                ev.append(("V", int(p[1]), int(p[2])))
    return ev


def simulate(ev, lo, hi, submit_ns, wake_ns, slow, free=(), vlag=None):
    E = 0.0            # EE clock (threaded)
    U = 0.0            # unit free time
    last = None
    frames = {}        # tick -> (sync_wall_ns, threaded_wall_ns, unit_ns, jobs)
    cur = [0.0, 0.0, 0]  # sync wall, unit ns, jobs since the last V
    e_at_v = None
    pending = []       # (reason, wait) since the last V
    wait_by = collections.Counter()
    hits_by = collections.Counter()
    vcount = 0
    ends = []          # (frame index at submit, unit end time), in order
    for e in ev:
        t = e[1]
        if last is not None:
            E += t - last
            cur[0] += t - last
        last = t
        if e[0] == "J":
            d = e[2]
            E += submit_ns
            U = max(U, E) + d * slow + wake_ns
            ends.append((vcount, U))
            cur[0] += d
            cur[1] += d
            cur[2] += 1
            continue
        reason = "vblank" if e[0] == "V" else e[2]
        if e[0] == "S" and reason in free:
            pending.append((reason, 0.0))
            continue
        if e[0] == "V" and vlag is not None:
            # bounded lag L: jobs of frame index f (V events seen before the
            # submit) must be done by the V that ends frame f + L.
            target = max([u for f, u in ends if f <= vcount - vlag] or [0.0])
            w = max(0.0, target - E)
            E = max(E, target)
        else:
            w = max(0.0, U - E)
            E = max(E, U)
        pending.append((reason, w))
        if e[0] == "V":
            tick = e[2]
            if e_at_v is not None and lo < tick <= hi:
                frames[tick] = (cur[0], E - e_at_v, cur[1], cur[2])
                for r, pw in pending:
                    wait_by[r] += pw
                    hits_by[r] += 1
            pending = []
            e_at_v = E
            vcount += 1
            ends = [x for x in ends if x[1] > E]
            cur = [0.0, 0.0, 0]
    return frames, wait_by, hits_by


SCENARIOS = [
    ("S0 as hooked", ()),
    ("S1 masked CSR reads free", ("gsprivread-masked",)),
    ("S2 S1 + GS priv writes queued", ("gsprivread-masked", "gsprivwrite")),
    ("S3 S2 + no VBlank sync, unit may trail 1 frame (non-det builds)", ("gsprivread-masked", "gsprivwrite", "vblank", "vblank@1")),
]


def report(name, ev, a, free):
    vlag = None
    for f in free:
        if f.startswith("vblank@"):
            vlag = int(f.split("@")[1])
    frames, wait_by, hits_by = simulate(ev, a.lo, a.hi, a.submit, a.wake, a.slow, free, vlag)
    if not frames:
        sys.exit("no frames in window")
    n = len(frames)
    sync = sum(f[0] for f in frames.values())
    thr = sum(f[1] for f in frames.values())
    unit = sum(f[2] for f in frames.values())
    jobs = sum(f[3] for f in frames.values())
    ee = sync - unit
    print(f"== {name}")
    print(f"sync wall/frame     {sync / n / 1e6:8.3f} ms  (EE {ee / n / 1e6:.3f} + unit {unit / n / 1e6:.3f}; jobs/frame {jobs / n:.2f})")
    print(f"threaded wall/frame {thr / n / 1e6:8.3f} ms  (model)")
    print(f"predicted speedup   {sync / thr:8.3f}x   ideal bound max(EE,unit): {sync / max(ee, unit):.3f}x")
    print(f"EE wait/frame       {sum(wait_by.values()) / n / 1e6:8.3f} ms; sync hits by reason:")
    for r in sorted(hits_by, key=lambda k: -wait_by[k]):
        tag = " (free)" if r in free else ""
        print(f"  {r:18s} wait {wait_by[r] / n / 1e6:7.3f} ms/frame  hits {hits_by[r] / n:6.2f}/frame{tag}")
    worst = sorted(frames, key=lambda k: -frames[k][1])[:3]
    print("  worst: " + ", ".join(f"t{k} {frames[k][1] / 1e6:.2f}ms (sync {frames[k][0] / 1e6:.2f})" for k in worst))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("census")
    ap.add_argument("--from", dest="lo", type=int, default=1800, help="window: ticks (lo, hi]")
    ap.add_argument("--to", dest="hi", type=int, default=2400)
    ap.add_argument("--submit", type=float, default=0.0, help="EE ns per job submit")
    ap.add_argument("--wake", type=float, default=0.0, help="unit ns per job (wake/handoff)")
    ap.add_argument("--slow", type=float, default=1.0, help="unit work multiplier (cache/contention)")
    a = ap.parse_args()
    ev = load(a.census)
    print(f"window ({a.lo},{a.hi}] submit={a.submit:.0f}ns wake={a.wake:.0f}ns slow={a.slow}")
    for name, free in SCENARIOS:
        report(name, ev, a, free)


if __name__ == "__main__":
    main()
