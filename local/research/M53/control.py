#!/usr/bin/env python3
"""M53 positive control C-P1: known plateaus (offline, synthetic).

Usage: control.py  (run from the work dir; importable m53 nearby)

Synthetic truth with KNOWN plateaus, N=2 singleton + N=2 run + N=2
scattered-tie pseudo-columns (pure-synthetic row->d lists exercising
m53's identical tie/rule code path — see DESIGN.md). Recover the
first-tie + all-tie + run-center tables exactly. Tables only.
"""
import sys
import time

import numpy as np

import m53

# Listed profiles: name -> (rows, deltas).
LISTED = {
    "S1": ([20, 21, 22, 23, 24], [10, 14, 18, 14, 10]),
    "S2": ([40, 41, 42], [-20, -12, -15]),
    "R1": ([50, 51, 52, 53, 54], [9, 15, 15, 15, 11]),
    "R2": ([60, 61, 62, 63, 64], [8, 12, 20, 20, 12]),
    "T1": ([70, 71, 75, 76], [30, 22, 30, 25]),
    "T2": ([80, 81, 82, 83, 84, 85], [40, 40, 31, 40, 40, 33]),
}

# Hand-computed wants (DESIGN.md pinned).
WANT = {
    # ft=(peak,k,n,third) tie=(max,T,rows) shape census rc1 rc2
    "S1": {"ft": (22, 2, 5, "mid"), "tie": (18, 1, [22]),
           "shape": "singleton", "census": [],
           "rc1": (22, 2, "mid"), "rc2": (22, True, 2, "mid")},
    "S2": {"ft": (41, 1, 3, "mid"), "tie": (-12, 1, [41]),
           "shape": "singleton", "census": [],
           "rc1": (41, 1, "mid"), "rc2": (41, True, 1, "mid")},
    "R1": {"ft": (51, 1, 5, "top"), "tie": (15, 3, [51, 52, 53]),
           "shape": "run", "census": [(51, 53, 15, 3)],
           "rc1": (52, 2, "mid"), "rc2": (52, True, 2, "mid")},
    "R2": {"ft": (62, 2, 5, "mid"), "tie": (20, 2, [62, 63]),
           "shape": "run", "census": [(62, 63, 20, 2)],
           "rc1": (62, 2, "mid"), "rc2": (63, True, 3, "mid")},
    "T1": {"ft": (70, 0, 4, "top"), "tie": (30, 2, [70, 75]),
           "shape": "scattered", "census": [],
           "rc1": (70, 0, "top"), "rc2": (73, False, 2, "mid")},
    "T2": {"ft": (80, 0, 6, "top"), "tie": (40, 4, [80, 81, 83, 84]),
           "shape": "multirun",
           "census": [(80, 81, 40, 2), (83, 84, 40, 2)],
           "rc1": (80, 0, "top"), "rc2": (82, True, 2, "mid")},
}


def main():
    t0 = time.time()
    allok = True
    for name, (rows, dd) in LISTED.items():
        r = np.array(rows, np.int64)
        d = np.array(dd, np.int64)
        w = WANT[name]
        hm = m53.hump_metrics(r, d)
        got_ft = (hm["peakrow"], hm["k"], hm["n"], hm["third"])
        ti = m53.tie_info(r, d)
        got_tie = (ti["max"], ti["T"], ti["rows"])
        cen = m53.plateau_census(r, d)
        p1, k1, t1 = m53.runcenter_r1(r, ti)
        p2, pres2, k2, t2 = m53.runcenter_r2(r, ti)
        checks = {
            "firsttie": got_ft == w["ft"],
            "alltie": got_tie == w["tie"],
            "shape": ti["shape"] == w["shape"],
            "census": cen == w["census"],
            "rc1": (p1, k1, t1) == w["rc1"],
            "rc2": (p2, pres2, k2, t2) == w["rc2"],
        }
        ok = all(checks.values())
        allok = allok and ok
        print(f"control C-P1 {name}: rows={rows} d={dd}")
        print(f"  firsttie got={got_ft} want={w['ft']} "
              f"match={checks['firsttie']}")
        print(f"  alltie got={got_tie} want={w['tie']} "
              f"match={checks['alltie']}")
        print(f"  shape got={ti['shape']} want={w['shape']} "
              f"match={checks['shape']}")
        print(f"  census got={cen} want={w['census']} "
              f"match={checks['census']}")
        print(f"  rc1 got={(p1, k1, t1)} want={w['rc1']} "
              f"match={checks['rc1']}")
        print(f"  rc2 got={(p2, pres2, k2, t2)} want={w['rc2']} "
              f"match={checks['rc2']}")
        print(f"  {name} pass={ok}")
    print(f"control C-P1 pooled: pass={allok} (want True)")
    print(f"control wall: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
