#!/usr/bin/env python3
"""M63 control C-NEIGHBOR: known row bulk, synthetic (offline).

Pure-synthetic (no dumps): neighborhood helpers operate on
(rows, cols, status), so a synthetic status map exercises the
identical m63 code path (interval_census, row_slice) with zero
dump coupling.

Synthetic neighborhood rows 5-6 x cols 0-1-2 (DESIGN.md pinned):
(5,0) bulk +3 d0 b2; (6,0) bulk +1 d0 b2; (5,1) noncell None
d3 b2; (6,1) noncell None d3 b2; (5,2) tail +9 d1 b2;
(6,2) noncell None d0 b2.
Tables, no verdicts.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m63 import interval_census, row_slice  # noqa: E402

STATUS = {
    (5, 0): {"kind": "bulk", "delta": 3, "dec": 0, "band": 2},
    (6, 0): {"kind": "bulk", "delta": 1, "dec": 0, "band": 2},
    (5, 1): {"kind": "noncell", "delta": None, "dec": 3, "band": 2},
    (6, 1): {"kind": "noncell", "delta": None, "dec": 3, "band": 2},
    (5, 2): {"kind": "tail", "delta": 9, "dec": 1, "band": 2},
    (6, 2): {"kind": "noncell", "delta": None, "dec": 0, "band": 2},
}

WANT_CEN = {
    0: {"rows": [5, 6],
        "bulk": [(5, 3, 0), (6, 1, 0)],
        "noncell": [],
        "tail": [],
        "counts": {"bulk": 2, "noncell": 0, "tail": 0},
        "deciles": [0, 0],
        "decspan": 1,
        "dechist": {0: 2}},
    1: {"rows": [5, 6],
        "bulk": [],
        "noncell": [5, 6],
        "tail": [],
        "counts": {"bulk": 0, "noncell": 2, "tail": 0},
        "deciles": [3, 3],
        "decspan": 1,
        "dechist": {3: 2}},
    2: {"rows": [5, 6],
        "bulk": [],
        "noncell": [6],
        "tail": [(5, 9, 1)],
        "counts": {"bulk": 0, "noncell": 1, "tail": 1},
        "deciles": [1, 0],
        "decspan": 2,
        "dechist": {0: 1, 1: 1}},
}

WANT_SLICE = {
    5: {0: {"kind": "bulk", "delta": 3, "dec": 0, "band": 2},
        1: {"kind": "noncell", "delta": None, "dec": 3, "band": 2},
        2: {"kind": "tail", "delta": 9, "dec": 1, "band": 2}},
    6: {0: {"kind": "bulk", "delta": 1, "dec": 0, "band": 2},
        1: {"kind": "noncell", "delta": None, "dec": 3, "band": 2},
        2: {"kind": "noncell", "delta": None, "dec": 0, "band": 2}},
}


def main():
    ok = True
    cen = interval_census(5, 6, [0, 1, 2], STATUS)
    m_keys = sorted(cen) == sorted(WANT_CEN)
    print(f"C-NEIGHBOR cenkeys: {sorted(cen)} "
          f"(want {sorted(WANT_CEN)}) match={m_keys}")
    if not m_keys:
        ok = False
    for col in sorted(WANT_CEN):
        b, w = cen[col], WANT_CEN[col]
        m_probes = all(b["probes"][r] == STATUS[(r, col)]
                       for r in w["rows"])
        m = (m_probes and b["rows"] == w["rows"]
             and b["bulk"] == w["bulk"]
             and b["noncell"] == w["noncell"]
             and b["tail"] == w["tail"]
             and b["counts"] == w["counts"]
             and b["deciles"] == w["deciles"]
             and b["decspan"] == w["decspan"]
             and b["dechist"] == w["dechist"])
        print(f"C-NEIGHBOR cen c={col}: rows={b['rows']} "
              f"bulk={b['bulk']} noncell={b['noncell']} "
              f"tail={b['tail']} counts={b['counts']} "
              f"deciles={b['deciles']} decspan={b['decspan']} "
              f"dechist={b['dechist']} probes={m_probes} match={m}")
        if not m:
            ok = False
    for row in sorted(WANT_SLICE):
        sl = row_slice(row, [0, 1, 2], STATUS)
        m = sl == WANT_SLICE[row]
        print(f"C-NEIGHBOR slice r={row}: {sl} "
              f"(want {WANT_SLICE[row]}) match={m}")
        if not m:
            ok = False
    print(f"C-NEIGHBOR pass={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
