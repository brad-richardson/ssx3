#!/usr/bin/env python3
"""M55 positive control C-P1: known medians + known drift (offline, synthetic).

Usage: control.py  (run from the work dir; importable m55 nearby)

Synthetic truth with KNOWN medians + KNOWN drift, N=4 pseudo-columns
x frames A/B (pure-synthetic row->d lists exercising m55's identical
median/drift code path — see DESIGN.md). Recover the median + drift
tables exactly. Tables only.
"""
import time

import m55

# Listed profiles: name -> ((rowsA, deltasA), (rowsB, deltasB)).
LISTED = {
    "P1": (((26, 27, 28, 29, 30), (8, 10, 12, 10, 8)),
           ((26, 27, 28, 29, 30), (9, 12, 14, 12, 9))),
    "P2": (((26, 27, 28, 29), (8, 10, 12, 14)),
           ((26, 27, 28, 29), (9, 11, 13, 15))),
    "P3": (((26, 27), (-31, -26)),
           ((25, 26, 27, 289), (-22, -34, -26, -15))),
    "P4": (((23, 24, 25, 26, 27, 28, 29, 30, 31, 32),
            (17, 28, 30, 29, 29, 29, 29, 28, 23, 13)),
           ((23, 24, 25, 26, 27, 28, 29, 30, 31, 32),
            (12, 18, 20, 20, 19, 20, 20, 19, 16, 8))),
}

# Hand-computed wants (DESIGN.md pinned).
WANT = {
    "P1": {"medA": 10, "medB": 12, "drift": 2, "abs": 2, "rank": 3},
    "P2": {"medA": 11, "medB": 12, "drift": 1, "abs": 1, "rank": 4},
    "P3": {"medA": -29, "medB": -24, "drift": 5, "abs": 5, "rank": 2},
    "P4": {"medA": 29, "medB": 19, "drift": -10, "abs": 10, "rank": 1},
}


def main():
    t0 = time.time()
    got = {}
    for name, ((_, dA), (_, dB)) in LISTED.items():
        mA = m55.const_median(list(dA))
        mB = m55.const_median(list(dB))
        d, a = m55.median_drift(mA, mB)
        got[name] = {"medA": mA, "medB": mB, "drift": d, "abs": a}
    # Rank by |d| desc; ties -> name order (control-local tie rule).
    order = sorted(got, key=lambda n: (-got[n]["abs"], n))
    ranks = {n: i + 1 for i, n in enumerate(order)}
    allok = True
    for name in ("P1", "P2", "P3", "P4"):
        w = WANT[name]
        g = got[name]
        checks = {
            "medA": g["medA"] == w["medA"],
            "medB": g["medB"] == w["medB"],
            "drift": g["drift"] == w["drift"],
            "abs": g["abs"] == w["abs"],
            "rank": ranks[name] == w["rank"],
        }
        ok = all(checks.values())
        allok = allok and ok
        print(f"control C-P1 {name}: dA={LISTED[name][0][1]} "
              f"dB={LISTED[name][1][1]}")
        print(f"  med got={g['medA']}/{g['medB']} "
              f"want={w['medA']}/{w['medB']} "
              f"match={checks['medA'] and checks['medB']}")
        print(f"  drift got={g['drift']:+d} want={w['drift']:+d} "
              f"match={checks['drift']}")
        print(f"  abs got={g['abs']} want={w['abs']} "
              f"match={checks['abs']}")
        print(f"  rank got={ranks[name]} want={w['rank']} "
              f"match={checks['rank']}")
        print(f"  {name} pass={ok}")
    print(f"control C-P1 pooled: pass={allok} (want True)")
    print(f"control wall: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
