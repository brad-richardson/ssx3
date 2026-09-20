#!/usr/bin/env python3
"""M54 positive control C-P1: known quadratics (offline, synthetic).

Usage: control.py  (run from the work dir; importable m54 nearby)

Synthetic truth with KNOWN quadratics, N=2 parabolic + N=2
non-parabolic pseudo-columns (pure-synthetic row->d lists exercising
m54's identical quad/residual/seat/census/depth code path — see
DESIGN.md). Recover the fit + residual tables exactly. Tables only.
"""
import sys
import time

import numpy as np

import m54

# Listed profiles: name -> (rows, deltas).
LISTED = {
    "P1": ([26, 27, 28, 29, 30], [8, 11, 12, 11, 8]),
    "P2": ([26, 27, 28, 29, 30], [16, 19, 20, 19, 16]),
    "T1": ([26, 27, 28, 29, 30], [8, 10, 12, 10, 8]),
    "T2": ([26, 27, 28, 29, 30], [8, 9, 12, 10, 8]),
}

# Hand-computed wants (DESIGN.md pinned).
WANT = {
    "P1": {"abc": (-1.0, 56.0, -772.0),
           "pred": [8, 11, 12, 11, 8],
           "res": [0, 0, 0, 0, 0],
           "hits": 5, "census": [],
           "seats": ["edge", "interior", "peak", "interior", "edge"],
           "holes": [False] * 5, "depth": 16.0},
    "P2": {"abc": (-1.0, 56.0, -764.0),
           "pred": [16, 19, 20, 19, 16],
           "res": [0, 0, 0, 0, 0],
           "hits": 5, "census": [],
           "seats": ["edge", "interior", "peak", "interior", "edge"],
           "holes": [False] * 5, "depth": 16.0},
    "T1": {"abc": (-6 / 7, 48.0, -23124 / 35),
           "pred": [8, 10, 11, 10, 8],
           "res": [0, 0, 1, 0, 0],
           "hits": 4, "census": [],
           "seats": ["edge", "interior", "peak", "interior", "edge"],
           "holes": [False] * 5, "depth": 96 / 7},
    "T2": {"abc": (-11 / 14, 44.1, -607.8285714285714),
           "pred": [8, 10, 11, 10, 8],
           "res": [0, -1, 1, 0, 0],
           "hits": 3, "census": [],
           "seats": ["edge", "interior", "peak", "interior", "edge"],
           "holes": [False] * 5, "depth": 88 / 7},
}

ABC_TOL = 1e-6
DEPTH_TOL = 1e-4


def main():
    t0 = time.time()
    allok = True
    for name, (rows, dd) in LISTED.items():
        r = np.array(rows, np.int64)
        d = np.array(dd, np.int64)
        w = WANT[name]
        qf = m54.quadfit(r, d)
        const = m54.int_median(d)
        t = m54.quad_residual_table(r, d, qf, const)
        dep = m54.quad_depth(r, qf)
        got_census = [(rr, rs) for rr, rs, a in
                      zip(t["rows"], t["res"], t["abs"]) if a in (2, 3)]
        abc_ok = (qf is not None and all(
            abs(g - x) <= ABC_TOL for g, x in zip(qf, w["abc"])))
        dep_ok = dep is not None and abs(dep - w["depth"]) <= DEPTH_TOL
        checks = {
            "abc": abc_ok,
            "pred": t["pred"] == w["pred"],
            "res": t["res"] == w["res"],
            "hits": t["hits"] == w["hits"],
            "census": got_census == w["census"],
            "seats": t["seats"] == w["seats"],
            "holes": t["holes"] == w["holes"],
            "depth": dep_ok,
        }
        ok = all(checks.values())
        allok = allok and ok
        print(f"control C-P1 {name}: rows={rows} d={dd}")
        print(f"  abc got={qf} want={w['abc']} match={checks['abc']}")
        print(f"  pred got={t['pred']} want={w['pred']} "
              f"match={checks['pred']}")
        print(f"  res got={t['res']} want={w['res']} "
              f"match={checks['res']}")
        print(f"  hits got={t['hits']} want={w['hits']} "
              f"match={checks['hits']}")
        print(f"  census got={got_census} want={w['census']} "
              f"match={checks['census']}")
        print(f"  seats got={t['seats']} match={checks['seats']}")
        print(f"  holes got={t['holes']} match={checks['holes']}")
        print(f"  depth got={dep} want={w['depth']} "
              f"match={checks['depth']}")
        print(f"  {name} pass={ok}")
    print(f"control C-P1 pooled: pass={allok} (want True)")
    print(f"control wall: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
