#!/usr/bin/env python3
"""M62 control C-INTERVAL: known interval contents, synthetic (offline).

Pure-synthetic (no dumps): interval helpers operate on
(rows, cols, status), so a synthetic status map + synthetic ref
counts exercises the identical m62 code path (interval_census,
holejoin_compare) with zero dump coupling.

Synthetic interval rows 3-6 x cols 0-1 (DESIGN.md pinned):
(3,0) bulk +2 d3 b2; (4,0) noncell None d0 b2; (5,0) tail +9
d1 b2; (6,0) bulk -1 d3 b2; (3,1) noncell None d5 b2;
(4,1) bulk +1 d1 b2; (5,1) noncell None d0 b2; (6,1) noncell
None d7 b2.
Tables, no verdicts.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m62 import holejoin_compare, interval_census  # noqa: E402

STATUS = {
    (3, 0): {"kind": "bulk", "delta": 2, "dec": 3, "band": 2},
    (4, 0): {"kind": "noncell", "delta": None, "dec": 0, "band": 2},
    (5, 0): {"kind": "tail", "delta": 9, "dec": 1, "band": 2},
    (6, 0): {"kind": "bulk", "delta": -1, "dec": 3, "band": 2},
    (3, 1): {"kind": "noncell", "delta": None, "dec": 5, "band": 2},
    (4, 1): {"kind": "bulk", "delta": 1, "dec": 1, "band": 2},
    (5, 1): {"kind": "noncell", "delta": None, "dec": 0, "band": 2},
    (6, 1): {"kind": "noncell", "delta": None, "dec": 7, "band": 2},
}

WANT_CEN = {
    0: {"rows": [3, 4, 5, 6],
        "bulk": [(3, 2, 3), (6, -1, 3)],
        "noncell": [4],
        "tail": [(5, 9, 1)],
        "counts": {"bulk": 2, "noncell": 1, "tail": 1},
        "deciles": [3, 0, 1, 3],
        "decspan": 3,
        "dechist": {0: 1, 1: 1, 3: 2}},
    1: {"rows": [3, 4, 5, 6],
        "bulk": [(4, 1, 1)],
        "noncell": [3, 5, 6],
        "tail": [],
        "counts": {"bulk": 1, "noncell": 3, "tail": 0},
        "deciles": [5, 1, 0, 7],
        "decspan": 4,
        "dechist": {0: 1, 1: 1, 5: 1, 7: 1}},
}

WANT_JOIN = {
    "gap": {"bulk": 2, "noncell": 1, "tail": 1, "n": 4,
            "bulkshare": 0.5, "tailshare": 0.25},
    "ref": {"bulk": 1, "noncell": 2, "tail": 1, "n": 4,
            "bulkshare": 0.25, "tailshare": 0.25},
}


def main():
    ok = True
    cen = interval_census(3, 6, [0, 1], STATUS)
    m_keys = sorted(cen) == sorted(WANT_CEN)
    print(f"C-INTERVAL cenkeys: {sorted(cen)} "
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
        print(f"C-INTERVAL cen c={col}: rows={b['rows']} "
              f"bulk={b['bulk']} noncell={b['noncell']} "
              f"tail={b['tail']} counts={b['counts']} "
              f"deciles={b['deciles']} decspan={b['decspan']} "
              f"dechist={b['dechist']} probes={m_probes} match={m}")
        if not m:
            ok = False
    gap = {"gap": {"bulk": 2, "noncell": 1, "tail": 1, "n": 4}}
    ref = {"ref": {"bulk": 1, "noncell": 2, "tail": 1, "n": 4}}
    j = holejoin_compare(gap, ref)
    m_jkeys = sorted(j) == sorted(WANT_JOIN)
    print(f"C-INTERVAL joinkeys: {sorted(j)} "
          f"(want {sorted(WANT_JOIN)}) match={m_jkeys}")
    if not m_jkeys:
        ok = False
    for lab in sorted(WANT_JOIN):
        m = j[lab] == WANT_JOIN[lab]
        print(f"C-INTERVAL join {lab}: {j[lab]} "
              f"(want {WANT_JOIN[lab]}) match={m}")
        if not m:
            ok = False
    print(f"C-INTERVAL pass={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
