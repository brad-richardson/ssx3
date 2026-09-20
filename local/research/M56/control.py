#!/usr/bin/env python3
"""M56 control C-P1: known far sites on synthetic row->delta lists (offline).

Pure-synthetic (no dumps): far census operates on row->delta lists, so
synthetic lists exercise the identical m56 code path (far_info, aux_dist,
pooled_d, hump_metrics, ROW_BAND) with zero dump coupling. Gaps/decile/
carrier N/A synthetic (disclosed, no expectation).

Pseudo-columns (DESIGN.md pinned):
  F1 col 343 rows [25,26,27,289] d [-22,-34,-26,-15]: far [289] d262
  F2 col 257 rows [30,31,200] d [20,22,-18]: far [200] d169
  B1 col 301 rows [23,24,25,26,27] d [10,12,14,12,10]: far []
  S1 col 372 rows [100] d [12]: singleton N/A
Tables, no verdicts.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m56 import FAR_THRESH, ROW_BAND, aux_dist, far_info, hump_metrics, pooled_d

PSEUDO = {
    "F1": {"col": 343, "rows": [25, 26, 27, 289],
           "deltas": [-22, -34, -26, -15]},
    "F2": {"col": 257, "rows": [30, 31, 200],
           "deltas": [20, 22, -18]},
    "B1": {"col": 301, "rows": [23, 24, 25, 26, 27],
           "deltas": [10, 12, 14, 12, 10]},
    "S1": {"col": 372, "rows": [100], "deltas": [12]},
}

WANT = {
    "F1": {"d": [1, 1, 1, 262], "far": [289], "lo": [None, 25, 26, 27],
           "hi": [26, 27, 289, None], "band": [0, 0, 0, 1],
           "peak": 289, "atpeak": {289: True},
           "holes": {289: (28, 288, 261)}},
    "F2": {"d": [1, 1, 169], "far": [200], "lo": [None, 30, 31],
           "hi": [31, 200, None], "band": [0, 0, 1],
           "peak": 31, "atpeak": {200: False},
           "holes": {200: (32, 199, 168)}},
    "B1": {"d": [1, 1, 1, 1, 1], "far": [], "lo": [None, 23, 24, 25, 26],
           "hi": [24, 25, 26, 27, None], "band": [0, 0, 0, 0, 0],
           "peak": 25, "atpeak": {}, "holes": {}},
    "S1": {"d": [None], "far": [], "lo": [None], "hi": [None],
           "band": [0], "peak": 100, "atpeak": {}, "holes": {}},
}


def main():
    ok = True
    allfar = []
    allnon = []
    for name in ("F1", "F2", "B1", "S1"):
        p = PSEUDO[name]
        w = WANT[name]
        rows, deltas = p["rows"], p["deltas"]
        col = p["col"]
        dd, lo, hi = far_info(rows)
        band = [int(ROW_BAND[r]) for r in rows]
        hm = hump_metrics(np.array(rows, np.int64),
                          np.array(deltas, np.int64))
        far = [r for r, d in zip(rows, dd)
               if d is not None and d >= FAR_THRESH]
        print(f"C-P1 {name} col={col}: rows={rows} deltas={deltas}")
        print(f"C-P1 {name} d={dd} (want {w['d']}) match={dd == w['d']}")
        print(f"C-P1 {name} lo={lo} (want {w['lo']}) match={lo == w['lo']}")
        print(f"C-P1 {name} hi={hi} (want {w['hi']}) match={hi == w['hi']}")
        print(f"C-P1 {name} far={far} (want {w['far']}) "
              f"match={far == w['far']}")
        print(f"C-P1 {name} band={band} (want {w['band']}) "
              f"match={band == w['band']}")
        print(f"C-P1 {name} peak={hm['peakrow']} (want {w['peak']}) "
              f"match={hm['peakrow'] == w['peak']}")
        if dd != w["d"] or lo != w["lo"] or hi != w["hi"]:
            ok = False
        if far != w["far"] or band != w["band"]:
            ok = False
        if hm["peakrow"] != w["peak"]:
            ok = False
        for r in far:
            atp = (r == hm["peakrow"])
            print(f"C-P1 {name} r={r} atpeak={atp} "
                  f"(want {w['atpeak'][r]}) match={atp == w['atpeak'][r]}")
            if atp != w["atpeak"][r]:
                ok = False
            i = rows.index(r)
            l, h = lo[i], hi[i]
            if l is not None and h is None:
                hole = (l + 1, r - 1, r - l - 1)
            elif l is None and h is not None:
                hole = (r + 1, h - 1, h - r - 1)
            else:
                hole = None
            print(f"C-P1 {name} r={r} hole={hole} "
                  f"(want {w['holes'][r]}) match={hole == w['holes'][r]}")
            if hole != w["holes"][r]:
                ok = False
            d_out, d_lim = aux_dist(r, rows)
            d_pool = pooled_d(r, rows)
            print(f"C-P1 {name} r={r} aux: d_out={d_out} d_lim={d_lim} "
                  f"d_pool={d_pool}")
            allfar.append((name, col, r))
        for r, d in zip(rows, dd):
            if d is not None and d < FAR_THRESH:
                allnon.append(((name, col, r, d)))
        # |delta| lists
        ads = [abs(x) for x in deltas]
        print(f"C-P1 {name} absdelta={ads}")
    allfar_sorted = sorted(allfar)
    want_far = sorted([("F1", 343, 289), ("F2", 257, 200)])
    print(f"C-P1 pooled far n={len(allfar_sorted)} (want 2) "
          f"match={len(allfar_sorted) == 2}")
    print(f"C-P1 pooled far set={allfar_sorted} (want {want_far}) "
          f"match={allfar_sorted == want_far}")
    if allfar_sorted != want_far:
        ok = False
    fcols = sorted({c for _, c, _ in allfar_sorted})
    print(f"C-P1 distinct far cols={fcols} (want [257, 343]) "
          f"match={fcols == [257, 343]}")
    if fcols != [257, 343]:
        ok = False
    allnon_sorted = sorted(allnon, key=lambda q: (-q[3], q[0], q[1], q[2]))
    top5d = [d for _, _, _, d in allnon_sorted[:5]]
    print(f"C-P1 null top5 d={top5d} (want [1, 1, 1, 1, 1]) "
          f"match={top5d == [1, 1, 1, 1, 1]}")
    if top5d != [1, 1, 1, 1, 1]:
        ok = False
    print("C-P1 decile/carrier: N/A synthetic (no dumps, disclosed)")
    print(f"C-P1 pass={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
