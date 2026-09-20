#!/usr/bin/env python3
"""M61 control C-PAIR: known column pair on a synthetic plane (offline).

Pure-synthetic (no dumps): pair-join helpers operate on
(plane, sites, deltas, cols), so a synthetic plane + site list + delta
dict + synthetic cols exercises the identical m61 code path
(unanimity_rows, span_rows, runs_rows, dprof_rows, decpair_rows,
rowgeom_rows, seatdist_rows) with zero dump coupling.

Synthetic plane 10x2 (DESIGN.md pinned): (1,0) dec 0; (2,0) dec 1;
(5,0) dec 0; (1,1) dec 0; (2,1) dec 1; (5,1) dec 0; (6,1) dec 4;
rest dec 9 (unused).
Sites + deltas: c0 unanimous-pos (N=3) + c1 split 2/2 (N=4).
Tables, no verdicts.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m61 import (decpair_rows, dprof_rows, rowgeom_rows, runs_rows,  # noqa: E402
                 seatdist_rows, span_rows, unanimity_rows)

PLANE = np.full((10, 2), 9, np.int32)
PLANE[1, 0] = 0
PLANE[2, 0] = 1
PLANE[5, 0] = 0
PLANE[1, 1] = 0
PLANE[2, 1] = 1
PLANE[5, 1] = 0
PLANE[6, 1] = 4

# (row, col) -> delta; known pair per DESIGN.md.
DELTAS = {
    (1, 0): 10, (2, 0): 12, (5, 0): 14,  # c0 unanimous-pos
    (1, 1): 9, (2, 1): -8, (5, 1): -9, (6, 1): 11,  # c1 split
}
SITES = sorted(DELTAS)
SITES0 = sorted((r, c) for (r, c) in SITES if c == 0)
SITES1 = sorted((r, c) for (r, c) in SITES if c == 1)
COLS = {0: {"rows": [1, 2, 5], "deltas": [10, 12, 14]},
        1: {"rows": [1, 2, 5, 6], "deltas": [9, -8, -9, 11]}}

WANT_UNAN = {
    0: {"n": 3, "pos": 3, "neg": 0, "posshare": 1.0,
        "min": 10, "max": 14, "sum": 36, "uclass": "all-pos"},
    1: {"n": 4, "pos": 2, "neg": 2, "posshare": 0.5,
        "min": -9, "max": 11, "sum": 3, "uclass": "split"},
}

WANT_SPAN = {
    0: {"n": 3, "rowmin": 1, "rowmax": 5, "rowspan": 4,
        "decspan": 2, "dechist": {0: 2, 1: 1}, "decmaxshare": 2.0 / 3.0},
    1: {"n": 4, "rowmin": 1, "rowmax": 6, "rowspan": 5,
        "decspan": 3, "dechist": {0: 2, 1: 1, 4: 1},
        "decmaxshare": 0.5},
}

WANT_RUNS = {
    0: [("pos", 1, 5, 3)],
    1: [("pos", 1, 1, 1), ("neg", 2, 5, 2), ("pos", 6, 6, 1)],
}

WANT_DPROF = {
    0: {"n": 3, "dhist": {1: 2, 3: 1}, "na": 0, "dmax": 3, "dmode": 1},
    1: {"n": 4, "dhist": {1: 4}, "na": 0, "dmax": 1, "dmode": 1},
}

WANT_DEPAIR = {
    0: {"A_n": 2, "B_n": 2, "A_deltas": [10, 14],
        "B_deltas": [-9, 9]},
    1: {"A_n": 1, "B_n": 1, "A_deltas": [12], "B_deltas": [-8]},
    2: {"A_n": 0, "B_n": 0, "A_deltas": [], "B_deltas": []},
    3: {"A_n": 0, "B_n": 0, "A_deltas": [], "B_deltas": []},
    4: {"A_n": 0, "B_n": 1, "A_deltas": [], "B_deltas": [11]},
    5: {"A_n": 0, "B_n": 0, "A_deltas": [], "B_deltas": []},
    6: {"A_n": 0, "B_n": 0, "A_deltas": [], "B_deltas": []},
    7: {"A_n": 0, "B_n": 0, "A_deltas": [], "B_deltas": []},
    8: {"A_n": 0, "B_n": 0, "A_deltas": [], "B_deltas": []},
    9: {"A_n": 0, "B_n": 0, "A_deltas": [], "B_deltas": []},
}

WANT_ROWGEOM = {"A_rows": [1, 2, 5], "B_rows": [1, 2, 5, 6],
                "A_span": 4, "B_span": 5,
                "A_gaps": [1, 3], "B_gaps": [1, 3, 1],
                "intersection": [1, 2, 5], "union_n": 4,
                "overlap_range": (1, 5), "nested": True,
                "merged_labels": [(1, "both"), (2, "both"),
                                  (5, "both"), (6, "B")],
                "label_runs": [("both", 3), ("B", 1)]}

WANT_SEATDIST = {
    0: {"n": 3, "bandhist": {0: 3}, "streakhist": {"other": 3},
        "carrierhist": None, "split701hist": None,
        "peak": 5, "atpeak_n": 1},
    1: {"n": 4, "bandhist": {0: 4}, "streakhist": {"other": 4},
        "carrierhist": None, "split701hist": None,
        "peak": 6, "atpeak_n": 1},
}


def _close(a, b):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) < 1e-12


def main():
    ok = True
    # unanimity rows (2 cols)
    urows = unanimity_rows(SITES, DELTAS)
    m_keys = sorted(urows) == sorted(WANT_UNAN)
    print(f"C-PAIR unankeys: {sorted(urows)} "
          f"(want {sorted(WANT_UNAN)}) match={m_keys}")
    if not m_keys:
        ok = False
    for col in sorted(WANT_UNAN):
        b, w = urows[col], WANT_UNAN[col]
        m = (b["n"] == w["n"] and b["pos"] == w["pos"]
             and b["neg"] == w["neg"] and _close(b["posshare"], w["posshare"])
             and b["min"] == w["min"] and b["max"] == w["max"]
             and b["sum"] == w["sum"] and b["uclass"] == w["uclass"])
        print(f"C-PAIR unan c={col}: n={b['n']} pos={b['pos']} "
              f"neg={b['neg']} posshare={b['posshare']} min={b['min']} "
              f"max={b['max']} sum={b['sum']} class={b['uclass']} "
              f"match={m}")
        if not m:
            ok = False
    # span rows
    srows = span_rows(SITES, PLANE)
    m_skeys = sorted(srows) == sorted(WANT_SPAN)
    print(f"C-PAIR spankeys: {sorted(srows)} "
          f"(want {sorted(WANT_SPAN)}) match={m_skeys}")
    if not m_skeys:
        ok = False
    for col in sorted(WANT_SPAN):
        b, w = srows[col], WANT_SPAN[col]
        m = (b["n"] == w["n"] and b["rowmin"] == w["rowmin"]
             and b["rowmax"] == w["rowmax"] and b["rowspan"] == w["rowspan"]
             and b["decspan"] == w["decspan"] and b["dechist"] == w["dechist"]
             and _close(b["decmaxshare"], w["decmaxshare"]))
        print(f"C-PAIR span c={col}: n={b['n']} rows={b['rowmin']}-"
              f"{b['rowmax']} rowspan={b['rowspan']} "
              f"decspan={b['decspan']} dechist={b['dechist']} match={m}")
        if not m:
            ok = False
    # runs rows
    for col in sorted(WANT_RUNS):
        rows = sorted((r, c) for (r, c) in SITES if c == col)
        got = runs_rows(rows, DELTAS)
        m = got == WANT_RUNS[col]
        print(f"C-PAIR runs c={col}: runs={got} "
              f"(want {WANT_RUNS[col]}) match={m}")
        if not m:
            ok = False
    # d-profile rows
    drows = dprof_rows(SITES)
    m_dkeys = sorted(drows) == sorted(WANT_DPROF)
    print(f"C-PAIR dprofkeys: {sorted(drows)} "
          f"(want {sorted(WANT_DPROF)}) match={m_dkeys}")
    if not m_dkeys:
        ok = False
    for col in sorted(WANT_DPROF):
        b, w = drows[col], WANT_DPROF[col]
        m = (b["n"] == w["n"] and b["dhist"] == w["dhist"]
             and b["na"] == w["na"] and b["dmax"] == w["dmax"]
             and b["dmode"] == w["dmode"])
        print(f"C-PAIR dprof c={col}: n={b['n']} dhist={b['dhist']} "
              f"na={b['na']} dmax={b['dmax']} dmode={b['dmode']} "
              f"match={m}")
        if not m:
            ok = False
    # decpair rows (all 10 deciles)
    dp = decpair_rows(SITES0, SITES1, PLANE, DELTAS)
    m_dpkeys = sorted(dp) == sorted(WANT_DEPAIR)
    print(f"C-PAIR decpairkeys: {sorted(dp)} "
          f"(want {sorted(WANT_DEPAIR)}) match={m_dpkeys}")
    if not m_dpkeys:
        ok = False
    for dci in sorted(WANT_DEPAIR):
        b, w = dp[dci], WANT_DEPAIR[dci]
        m = (b["A_n"] == w["A_n"] and b["B_n"] == w["B_n"]
             and b["A_deltas"] == w["A_deltas"]
             and b["B_deltas"] == w["B_deltas"])
        print(f"C-PAIR decpair d{dci}: A_n={b['A_n']} "
              f"A={b['A_deltas']} B_n={b['B_n']} "
              f"B={b['B_deltas']} match={m}")
        if not m:
            ok = False
    # rowgeom (A=c0 rows, B=c1 rows)
    g = rowgeom_rows([1, 2, 5], [1, 2, 5, 6])
    m_g = all(g[k] == WANT_ROWGEOM[k] for k in WANT_ROWGEOM)
    print(f"C-PAIR rowgeom: A_rows={g['A_rows']} B_rows={g['B_rows']} "
          f"A_gaps={g['A_gaps']} B_gaps={g['B_gaps']} "
          f"A_span={g['A_span']} B_span={g['B_span']} "
          f"inter={g['intersection']} union_n={g['union_n']} "
          f"overlap={g['overlap_range']} nested={g['nested']} "
          f"merged={g['merged_labels']} runs={g['label_runs']} "
          f"match={m_g}")
    if not m_g:
        ok = False
    # seatdist rows (masks None -> carrier/split701 None)
    sd = seatdist_rows(SITES, PLANE, None, COLS)
    m_sdkeys = sorted(sd) == sorted(WANT_SEATDIST)
    print(f"C-PAIR seatkeys: {sorted(sd)} "
          f"(want {sorted(WANT_SEATDIST)}) match={m_sdkeys}")
    if not m_sdkeys:
        ok = False
    for col in sorted(WANT_SEATDIST):
        b, w = sd[col], WANT_SEATDIST[col]
        m = (b["n"] == w["n"] and b["bandhist"] == w["bandhist"]
             and b["streakhist"] == w["streakhist"]
             and b["carrierhist"] == w["carrierhist"]
             and b["split701hist"] == w["split701hist"]
             and b["peak"] == w["peak"]
             and b["atpeak_n"] == w["atpeak_n"])
        print(f"C-PAIR seats c={col}: n={b['n']} band={b['bandhist']} "
              f"streak={b['streakhist']} carrier={b['carrierhist']} "
              f"split701={b['split701hist']} peak={b['peak']} "
              f"atpeak_n={b['atpeak_n']} match={m}")
        if not m:
            ok = False
    print(f"C-PAIR pass={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
