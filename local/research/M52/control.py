#!/usr/bin/env python3
"""M52 positive control C-P1: known peaks + known agreeing sites (offline).

Usage: control.py  (run from the work dir; importable m52 nearby; no inputs)

Listed-truth logic control: two pseudo-frames A/B over pseudo-columns
901-904 with KNOWN peaks, KNOWN d-agreeing sites at KNOWN distances,
and KNOWN residual agreements. Runs m52's exact Task-1/Task-2 join
functions (xframe_match_lines, agree_site_lines, xshape_lines,
peakjoin_lines, resid_lines, dist_table, dist_lines, xres_lines) on
the listed profiles and requires exact recovery. Tables only.

Listed truth (DESIGN.md pinned):
  c901 rows 26-30: A=10,14,20,14,10 (peak 28/20);
                   B=10,12,20,12,8  (peak 28/20).
    d-agrees r26+r28 (d 2/2, 0/0); res-agrees r26+r28.
  c902 rows 26-29: A=18,12,10,8 (peak 26/18);
                   B=10,20,12,8 (peak 27/20).
    d-agrees r29 (d_A 3, d_B 2); res-agrees r28 (other site).
  c903 rows 26-28: A=-10,-20,-12 (peak 26/-10);
                   B=-12,-22,-16 (peak 26/-12).
    d-agrees none; res-agrees r26+r27 (residual rises above d).
  c904 rows 26-28: A=15,15,10 (peak 26/15 first-tie);
                   B=12,15,15 (peak 27/15 first-tie).
    d-agrees r27 (d_A 1, d_B 0); res-agrees r27.
Pooled want: shared 15; d-agrees 4/15 at (901,26),(901,28),
(902,29),(904,27); peak agree 2/4 (901,903); res-agrees 6/15 at
(901,26),(901,28),(902,28),(903,26),(903,27),(904,27).
"""
import time

import numpy as np

import m52

COLS = (901, 902, 903, 904)
LISTED = {
    901: {"rows": [26, 27, 28, 29, 30],
          "A": [10, 14, 20, 14, 10], "B": [10, 12, 20, 12, 8]},
    902: {"rows": [26, 27, 28, 29],
          "A": [18, 12, 10, 8], "B": [10, 20, 12, 8]},
    903: {"rows": [26, 27, 28],
          "A": [-10, -20, -12], "B": [-12, -22, -16]},
    904: {"rows": [26, 27, 28],
          "A": [15, 15, 10], "B": [12, 15, 15]},
}
WANT_PEAK = {901: ((28, 20), (28, 20)), 902: ((26, 18), (27, 20)),
             903: ((26, -10), (26, -12)), 904: ((26, 15), (27, 15))}
WANT_PEAKAGREE = {901: True, 902: False, 903: True, 904: False}
WANT_DAGREE = {901: [26, 28], 902: [29], 903: [], 904: [27]}
WANT_RESAGREE = {901: [26, 28], 902: [28], 903: [26, 27], 904: [27]}
WANT_DIST = {(901, 26): (2, 2), (901, 28): (0, 0), (902, 29): (3, 2),
             (904, 27): (1, 0)}
WANT_RES = {
    901: {"A": [-10, -6, 0, -6, -10], "B": [-10, -8, 0, -8, -12]},
    902: {"A": [0, -6, -8, -10], "B": [-10, 0, -8, -12]},
    903: {"A": [0, -10, -2], "B": [0, -10, -4]},
    904: {"A": [0, 0, -5], "B": [-3, 0, 0]},
}


def mkart(frame):
    profs = {}
    for c in COLS:
        rows = np.array(LISTED[c]["rows"], np.int64)
        d = np.array(LISTED[c][frame], np.int64)
        profs[c] = {"rows": rows, "d": d,
                    "hump": m52.hump_metrics(rows, d)}
    return {"profs": profs}


def main():
    t0 = time.time()
    artA, artB = mkart("A"), mkart("B")

    # Peaks (m52.hump_metrics code path) + first-tie check.
    peak_ok = True
    for c in COLS:
        g0 = (artA["profs"][c]["hump"]["peakrow"],
              artA["profs"][c]["hump"]["peakval"])
        g1 = (artB["profs"][c]["hump"]["peakrow"],
              artB["profs"][c]["hump"]["peakval"])
        ok = (g0, g1) == WANT_PEAK[c]
        peak_ok = peak_ok and ok
        print(f"control C-P1: peak c={c}: A={g0[0]}/{g0[1]} "
              f"B={g1[0]}/{g1[1]} want={WANT_PEAK[c]} exact={ok}")

    # Residual quads via m52.resid_lines (exact code path).
    res_ok = True
    for tag, art, fr in (("A", artA, "A"), ("B", artB, "B")):
        for ln in m52.resid_lines(tag, art, COLS):
            print(f"control C-P1: {ln}")
    for c in COLS:
        for fr, art in (("A", artA), ("B", artB)):
            _, res, _, _ = m52.peak_residual(art["profs"][c]["rows"],
                                             art["profs"][c]["d"])
            ok = res.tolist() == WANT_RES[c][fr]
            res_ok = res_ok and ok
            if not ok:
                print(f"control C-P1: RES MISMATCH c={c} {fr}: "
                      f"got={res.tolist()} want={WANT_RES[c][fr]}")
    print(f"control C-P1: residuals exact={res_ok}")

    # H5 join via m52.xframe_match_lines + agree_site_lines.
    for ln in m52.xframe_match_lines(artA, artB, COLS):
        print(f"control C-P1: {ln}")
    LA, agsites = m52.agree_site_lines(artA, artB, COLS)
    for ln in LA:
        print(f"control C-P1: {ln}")
    dag_ok = True
    for c in COLS:
        got = sorted(r for (cc, r) in agsites if cc == c)
        ok = got == WANT_DAGREE[c]
        dag_ok = dag_ok and ok
        print(f"control C-P1: dagree c={c}: got={got} "
              f"want={WANT_DAGREE[c]} exact={ok}")
    want_all = sorted((c, r) for c in COLS for r in WANT_DAGREE[c])
    dag_ok = dag_ok and sorted(agsites) == want_all
    print(f"control C-P1: pooled dagree shared=15 agree={len(agsites)} "
          f"want=4 exact={sorted(agsites) == want_all}")

    # Peak-agree join via m52.xshape_lines + peakjoin_lines.
    for ln in m52.xshape_lines(artA, artB, COLS):
        print(f"control C-P1: {ln}")
    for ln in m52.peakjoin_lines(artA, artB, agsites, COLS):
        print(f"control C-P1: {ln}")
    pa_ok = True
    for c in COLS:
        h0 = artA["profs"][c]["hump"]
        h1 = artB["profs"][c]["hump"]
        got = h0["peakrow"] == h1["peakrow"]
        ok = got == WANT_PEAKAGREE[c]
        pa_ok = pa_ok and ok
        print(f"control C-P1: peakagree c={c}: got={got} "
              f"want={WANT_PEAKAGREE[c]} exact={ok}")

    # Distance + residual-agreement via m52.dist_table/xres_lines.
    dtab = m52.dist_table(artA, artB, COLS)
    for ln in m52.dist_lines(dtab):
        print(f"control C-P1: {ln}")
    dist_ok = True
    for (c, r), (w0, w1) in WANT_DIST.items():
        t = next(t for t in dtab if t["c"] == c and t["r"] == r)
        ok = (t["q0"], t["q1"]) == (w0, w1)
        dist_ok = dist_ok and ok
        print(f"control C-P1: dist c={c} r={r}: got=({t['q0']},{t['q1']}) "
              f"want=({w0},{w1}) exact={ok}")
    for ln in m52.xres_lines(artA, artB, dtab, COLS):
        print(f"control C-P1: {ln}")
    rag_ok = True
    for c in COLS:
        got = sorted(t["r"] for t in dtab
                     if t["c"] == c and t["agr"])
        ok = got == WANT_RESAGREE[c]
        rag_ok = rag_ok and ok
        print(f"control C-P1: resagree c={c}: got={got} "
              f"want={WANT_RESAGREE[c]} exact={ok}")
    nrag = sum(1 for t in dtab if t["agr"])
    rag_ok = rag_ok and nrag == 6 and len(dtab) == 15
    print(f"control C-P1: pooled resagree shared={len(dtab)} "
          f"agree={nrag} want=6 exact={nrag == 6 and len(dtab) == 15}")

    overall = peak_ok and res_ok and dag_ok and pa_ok and dist_ok and rag_ok
    print(f"control C-P1: wall={time.time() - t0:.1f}s pass={overall}")


if __name__ == "__main__":
    main()
