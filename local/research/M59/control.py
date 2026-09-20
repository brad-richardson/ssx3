#!/usr/bin/env python3
"""M59 control C-SIGN: known bin signs on a synthetic plane (offline).

Pure-synthetic (no dumps): bin/column sign helpers operate on
(plane, sites, deltas), so a synthetic plane + site list + delta dict
exercises the identical m59 code path (bin_sign_rows, col_sign_rows,
col_mode_rows, seat_of deciles) with zero dump coupling.

Synthetic plane 8x12 (DESIGN.md pinned): cols 0-5 dec 9 (mode block),
cols 6-7 dec 3 (off-mode block), col 8 dec 0, col 9 dec 1, col 10
dec 4, col 11 dec 5. Sites + deltas: dec-1 all-pos bin (N=4) + dec-0
split (N=2) + dec-3 split (N=3) + dec-9 split (N=3); bins 2/4/5/6/7/8
empty.
Tables, no verdicts.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m59 import bin_sign_rows, col_mode_rows, col_sign_rows, seat_of  # noqa: E402

PLANE = np.zeros((8, 12), np.int32)
PLANE[:, 0:6] = 9
PLANE[:, 6:8] = 3
PLANE[:, 8] = 0
PLANE[:, 9] = 1
PLANE[:, 10] = 4
PLANE[:, 11] = 5

# (row, col) -> delta; known signs per DESIGN.md.
DELTAS = {
    (0, 9): 9, (1, 9): 10, (2, 9): 22, (3, 9): 29,  # dec-1 all-pos
    (0, 8): 20, (1, 8): -9,  # dec-0 split
    (0, 6): 22, (1, 6): -18, (2, 7): 14,  # dec-3 split
    (0, 0): 19, (1, 1): -16, (2, 2): 8,  # dec-9 split
}
SITES = sorted(DELTAS)

WANT_BIN = {
    0: {"n": 2, "pos": 1, "neg": 1, "posshare": 0.5,
        "min": -9, "max": 20, "sum": 11,
        "counts": {-9: 1, 20: 1}},
    1: {"n": 4, "pos": 4, "neg": 0, "posshare": 1.0,
        "min": 9, "max": 29, "sum": 70,
        "counts": {9: 1, 10: 1, 22: 1, 29: 1}},
    2: {"n": 0, "pos": 0, "neg": 0, "posshare": None,
        "min": None, "max": None, "sum": 0, "counts": {}},
    3: {"n": 3, "pos": 2, "neg": 1, "posshare": 2 / 3,
        "min": -18, "max": 22, "sum": 18,
        "counts": {-18: 1, 14: 1, 22: 1}},
    4: {"n": 0, "pos": 0, "neg": 0, "posshare": None,
        "min": None, "max": None, "sum": 0, "counts": {}},
    5: {"n": 0, "pos": 0, "neg": 0, "posshare": None,
        "min": None, "max": None, "sum": 0, "counts": {}},
    6: {"n": 0, "pos": 0, "neg": 0, "posshare": None,
        "min": None, "max": None, "sum": 0, "counts": {}},
    7: {"n": 0, "pos": 0, "neg": 0, "posshare": None,
        "min": None, "max": None, "sum": 0, "counts": {}},
    8: {"n": 0, "pos": 0, "neg": 0, "posshare": None,
        "min": None, "max": None, "sum": 0, "counts": {}},
    9: {"n": 3, "pos": 2, "neg": 1, "posshare": 2 / 3,
        "min": -16, "max": 19, "sum": 11,
        "counts": {-16: 1, 8: 1, 19: 1}},
}

WANT_COL = {
    0: {"n": 1, "pos": 1, "neg": 0, "posshare": 1.0,
        "min": 19, "max": 19, "sum": 19},
    1: {"n": 1, "pos": 0, "neg": 1, "posshare": 0.0,
        "min": -16, "max": -16, "sum": -16},
    2: {"n": 1, "pos": 1, "neg": 0, "posshare": 1.0,
        "min": 8, "max": 8, "sum": 8},
    6: {"n": 2, "pos": 1, "neg": 1, "posshare": 0.5,
        "min": -18, "max": 22, "sum": 4},
    7: {"n": 1, "pos": 1, "neg": 0, "posshare": 1.0,
        "min": 14, "max": 14, "sum": 14},
    8: {"n": 2, "pos": 1, "neg": 1, "posshare": 0.5,
        "min": -9, "max": 20, "sum": 11},
    9: {"n": 4, "pos": 4, "neg": 0, "posshare": 1.0,
        "min": 9, "max": 29, "sum": 70},
}

WANT_MODE = {
    0: {"n": 1, "modedec": 9, "modedec_n": 1, "modedec_share": 1.0,
        "modesign": "pos", "modesign_n": 1, "modesign_share": 1.0},
    1: {"n": 1, "modedec": 9, "modedec_n": 1, "modedec_share": 1.0,
        "modesign": "neg", "modesign_n": 1, "modesign_share": 1.0},
    2: {"n": 1, "modedec": 9, "modedec_n": 1, "modedec_share": 1.0,
        "modesign": "pos", "modesign_n": 1, "modesign_share": 1.0},
    6: {"n": 2, "modedec": 3, "modedec_n": 2, "modedec_share": 1.0,
        "modesign": "tie", "modesign_n": 1, "modesign_share": 0.5},
    7: {"n": 1, "modedec": 3, "modedec_n": 1, "modedec_share": 1.0,
        "modesign": "pos", "modesign_n": 1, "modesign_share": 1.0},
    8: {"n": 2, "modedec": 0, "modedec_n": 2, "modedec_share": 1.0,
        "modesign": "tie", "modesign_n": 1, "modesign_share": 0.5},
    9: {"n": 4, "modedec": 1, "modedec_n": 4, "modedec_share": 1.0,
        "modesign": "pos", "modesign_n": 4, "modesign_share": 1.0},
}

WANT_DEC = {(0, 9): 1, (1, 9): 1, (2, 9): 1, (3, 9): 1,
            (0, 8): 0, (1, 8): 0,
            (0, 6): 3, (1, 6): 3, (2, 7): 3,
            (0, 0): 9, (1, 1): 9, (2, 2): 9}


def _close(a, b):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) < 1e-12


def main():
    ok = True
    # per-site deciles (seat_of on the synthetic plane)
    for (r, c) in SITES:
        st = seat_of(r, c, None, PLANE, None)
        m = st["dec"] == WANT_DEC[(r, c)]
        print(f"C-SIGN dec rc=({r},{c}): dec={st['dec']} "
              f"(want {WANT_DEC[(r, c)]}) match={m}")
        if not m:
            ok = False
    # bin-sign rows (all 10 bins incl. empties)
    brows = bin_sign_rows(SITES, PLANE, DELTAS)
    for dci in range(10):
        b, w = brows[dci], WANT_BIN[dci]
        m = (b["n"] == w["n"] and b["pos"] == w["pos"]
             and b["neg"] == w["neg"] and _close(b["posshare"], w["posshare"])
             and b["min"] == w["min"] and b["max"] == w["max"]
             and b["sum"] == w["sum"] and b["counts"] == w["counts"])
        print(f"C-SIGN bin dec={dci}: n={b['n']} pos={b['pos']} "
              f"neg={b['neg']} posshare={b['posshare']} min={b['min']} "
              f"max={b['max']} sum={b['sum']} match={m}")
        if not m:
            ok = False
    # column-sign rows
    crows = col_sign_rows(SITES, DELTAS)
    m_keys = sorted(crows) == sorted(WANT_COL)
    print(f"C-SIGN colkeys: {sorted(crows)} "
          f"(want {sorted(WANT_COL)}) match={m_keys}")
    if not m_keys:
        ok = False
    for col in sorted(WANT_COL):
        b, w = crows[col], WANT_COL[col]
        m = (b["n"] == w["n"] and b["pos"] == w["pos"]
             and b["neg"] == w["neg"] and _close(b["posshare"], w["posshare"])
             and b["min"] == w["min"] and b["max"] == w["max"]
             and b["sum"] == w["sum"])
        print(f"C-SIGN col c={col}: n={b['n']} pos={b['pos']} "
              f"neg={b['neg']} posshare={b['posshare']} min={b['min']} "
              f"max={b['max']} sum={b['sum']} match={m}")
        if not m:
            ok = False
    # column-mode rows
    mrows = col_mode_rows(SITES, PLANE, DELTAS)
    m_mkeys = sorted(mrows) == sorted(WANT_MODE)
    print(f"C-SIGN modekeys: {sorted(mrows)} "
          f"(want {sorted(WANT_MODE)}) match={m_mkeys}")
    if not m_mkeys:
        ok = False
    for col in sorted(WANT_MODE):
        b, w = mrows[col], WANT_MODE[col]
        m = (b["n"] == w["n"] and b["modedec"] == w["modedec"]
             and b["modedec_n"] == w["modedec_n"]
             and _close(b["modedec_share"], w["modedec_share"])
             and b["modesign"] == w["modesign"]
             and b["modesign_n"] == w["modesign_n"]
             and _close(b["modesign_share"], w["modesign_share"]))
        print(f"C-SIGN mode c={col}: n={b['n']} modedec={b['modedec']} "
              f"({b['modedec_n']}) modesign={b['modesign']} "
              f"({b['modesign_n']}) match={m}")
        if not m:
            ok = False
    print(f"C-SIGN pass={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
