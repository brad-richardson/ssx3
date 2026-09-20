#!/usr/bin/env python3
"""M60 control C-UNAN: known column signs on a synthetic plane (offline).

Pure-synthetic (no dumps): unanimity/span helpers operate on
(plane, sites, deltas), so a synthetic plane + site list + delta dict
exercises the identical m60 code path (unanimity_rows, span_rows,
runs_rows, dprof_rows) with zero dump coupling.

Synthetic plane 10x6 (DESIGN.md pinned): col 0 dec 9; col 1 dec 3;
col 2 rows 1-2 dec 0, rows 5-6 dec 1 (rest dec 9, unused); (7,3)
dec 9; (0,4) and (5,4) dec 9; col 5 dec 9 (empty, no sites).
Sites + deltas: c0 unanimous-pos (N=3) + c1 unanimous-neg (N=2) +
c2 split 2/2 (N=4) + c3 singleton-neg (N=1) + c4 unanimous-pos
gapped (N=2, d=5); c5 empty.
Tables, no verdicts.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m60 import dprof_rows, runs_rows, span_rows, unanimity_rows  # noqa: E402

PLANE = np.full((10, 6), 9, np.int32)
PLANE[:, 0] = 9
PLANE[:, 1] = 3
PLANE[1, 2] = 0
PLANE[2, 2] = 0
PLANE[5, 2] = 1
PLANE[6, 2] = 1
PLANE[7, 3] = 9
PLANE[0, 4] = 9
PLANE[5, 4] = 9
PLANE[:, 5] = 9

# (row, col) -> delta; known signs per DESIGN.md.
DELTAS = {
    (2, 0): 12, (3, 0): 18, (4, 0): 20,  # c0 unanimous-pos
    (5, 1): -8, (6, 1): -16,  # c1 unanimous-neg
    (1, 2): 9, (2, 2): 10, (5, 2): -9, (6, 2): -8,  # c2 split
    (7, 3): -9,  # c3 singleton-neg
    (0, 4): 10, (5, 4): 14,  # c4 unanimous-pos gapped
}
SITES = sorted(DELTAS)

WANT_UNAN = {
    0: {"n": 3, "pos": 3, "neg": 0, "posshare": 1.0,
        "min": 12, "max": 20, "sum": 50, "uclass": "all-pos"},
    1: {"n": 2, "pos": 0, "neg": 2, "posshare": 0.0,
        "min": -16, "max": -8, "sum": -24, "uclass": "all-neg"},
    2: {"n": 4, "pos": 2, "neg": 2, "posshare": 0.5,
        "min": -9, "max": 10, "sum": 2, "uclass": "split"},
    3: {"n": 1, "pos": 0, "neg": 1, "posshare": 0.0,
        "min": -9, "max": -9, "sum": -9, "uclass": "all-neg"},
    4: {"n": 2, "pos": 2, "neg": 0, "posshare": 1.0,
        "min": 10, "max": 14, "sum": 24, "uclass": "all-pos"},
}

WANT_SPAN = {
    0: {"n": 3, "rowmin": 2, "rowmax": 4, "rowspan": 2,
        "decspan": 1, "dechist": {9: 3}, "decmaxshare": 1.0},
    1: {"n": 2, "rowmin": 5, "rowmax": 6, "rowspan": 1,
        "decspan": 1, "dechist": {3: 2}, "decmaxshare": 1.0},
    2: {"n": 4, "rowmin": 1, "rowmax": 6, "rowspan": 5,
        "decspan": 2, "dechist": {0: 2, 1: 2}, "decmaxshare": 0.5},
    3: {"n": 1, "rowmin": 7, "rowmax": 7, "rowspan": 0,
        "decspan": 1, "dechist": {9: 1}, "decmaxshare": 1.0},
    4: {"n": 2, "rowmin": 0, "rowmax": 5, "rowspan": 5,
        "decspan": 1, "dechist": {9: 2}, "decmaxshare": 1.0},
}

WANT_RUNS = {
    0: [("pos", 2, 4, 3)],
    1: [("neg", 5, 6, 2)],
    2: [("pos", 1, 2, 2), ("neg", 5, 6, 2)],
    3: [("neg", 7, 7, 1)],
    4: [("pos", 0, 5, 2)],
}

WANT_DPROF = {
    0: {"n": 3, "dhist": {1: 3}, "na": 0, "dmax": 1, "dmode": 1},
    1: {"n": 2, "dhist": {1: 2}, "na": 0, "dmax": 1, "dmode": 1},
    2: {"n": 4, "dhist": {1: 4}, "na": 0, "dmax": 1, "dmode": 1},
    3: {"n": 1, "dhist": {}, "na": 1, "dmax": None, "dmode": None},
    4: {"n": 2, "dhist": {5: 2}, "na": 0, "dmax": 5, "dmode": 5},
}


def _close(a, b):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) < 1e-12


def main():
    ok = True
    # unanimity rows (5 cols + empty-c5 absence)
    urows = unanimity_rows(SITES, DELTAS)
    m_keys = sorted(urows) == sorted(WANT_UNAN)
    print(f"C-UNAN unankeys: {sorted(urows)} "
          f"(want {sorted(WANT_UNAN)}) match={m_keys}")
    if not m_keys:
        ok = False
    for col in sorted(WANT_UNAN):
        b, w = urows[col], WANT_UNAN[col]
        m = (b["n"] == w["n"] and b["pos"] == w["pos"]
             and b["neg"] == w["neg"] and _close(b["posshare"], w["posshare"])
             and b["min"] == w["min"] and b["max"] == w["max"]
             and b["sum"] == w["sum"] and b["uclass"] == w["uclass"])
        print(f"C-UNAN unan c={col}: n={b['n']} pos={b['pos']} "
              f"neg={b['neg']} posshare={b['posshare']} min={b['min']} "
              f"max={b['max']} sum={b['sum']} class={b['uclass']} "
              f"match={m}")
        if not m:
            ok = False
    # span rows
    srows = span_rows(SITES, PLANE)
    m_skeys = sorted(srows) == sorted(WANT_SPAN)
    print(f"C-UNAN spankeys: {sorted(srows)} "
          f"(want {sorted(WANT_SPAN)}) match={m_skeys}")
    if not m_skeys:
        ok = False
    for col in sorted(WANT_SPAN):
        b, w = srows[col], WANT_SPAN[col]
        m = (b["n"] == w["n"] and b["rowmin"] == w["rowmin"]
             and b["rowmax"] == w["rowmax"] and b["rowspan"] == w["rowspan"]
             and b["decspan"] == w["decspan"] and b["dechist"] == w["dechist"]
             and _close(b["decmaxshare"], w["decmaxshare"]))
        print(f"C-UNAN span c={col}: n={b['n']} rows={b['rowmin']}-"
              f"{b['rowmax']} rowspan={b['rowspan']} "
              f"decspan={b['decspan']} dechist={b['dechist']} match={m}")
        if not m:
            ok = False
    # runs rows
    for col in sorted(WANT_RUNS):
        rows = sorted((r, c) for (r, c) in SITES if c == col)
        got = runs_rows(rows, DELTAS)
        m = got == WANT_RUNS[col]
        print(f"C-UNAN runs c={col}: runs={got} "
              f"(want {WANT_RUNS[col]}) match={m}")
        if not m:
            ok = False
    # d-profile rows
    drows = dprof_rows(SITES)
    m_dkeys = sorted(drows) == sorted(WANT_DPROF)
    print(f"C-UNAN dprofkeys: {sorted(drows)} "
          f"(want {sorted(WANT_DPROF)}) match={m_dkeys}")
    if not m_dkeys:
        ok = False
    for col in sorted(WANT_DPROF):
        b, w = drows[col], WANT_DPROF[col]
        m = (b["n"] == w["n"] and b["dhist"] == w["dhist"]
             and b["na"] == w["na"] and b["dmax"] == w["dmax"]
             and b["dmode"] == w["dmode"])
        print(f"C-UNAN dprof c={col}: n={b['n']} dhist={b['dhist']} "
              f"na={b['na']} dmax={b['dmax']} dmode={b['dmode']} "
              f"match={m}")
        if not m:
            ok = False
    print(f"C-UNAN pass={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
