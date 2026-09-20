#!/usr/bin/env python3
"""M51 positive control C-P1: known triangles + known drift (offline).

Usage: control.py M16_DIR  (run from the work dir; importable m51 nearby)

Synthetic truth mid'_A + mid'_B on s0 (same v0/full/synth, different
mids): M25 union pool (interior-BULK gap>=17 + ENDPOINT gap>=32,
offset order), distinct rows 26..30, N=2 pseudo-columns x 5 sites:
X listed-A TRIANGLE delta = 8,10,12,10,8 (p=28,h=12,e=8,w=2);
X listed-B DRIFTED delta = 9,12,14,12,9 (p=28,h=14,e=9,w=2;
known drift 0/+2/+1/0);
Y listed-A TRIANGLE delta = 8,10,12,10,8 (p=28,h=12,e=8,w=2);
Y listed-B PEAK-SHIFTED delta = 8,8,10,12,10 (p=29,h=12,e=8,w=2;
known drift +1/0/0/0).
Recompute cell 7 + tail on both: each tail set must equal T_s0
union injected exactly (count 112 + values + map), originals
unchanged. Profile recovery + trifit per pseudo-col per frame
(4 fits) + drift per pseudo-col (2 drifts) must read the listed
+ known values exactly. Tables only.
"""
import sys
import time
from pathlib import Path

import numpy as np

import m51

ROWS = [26, 27, 28, 29, 30]
LISTED_A = {"X": [8, 10, 12, 10, 8], "Y": [8, 10, 12, 10, 8]}
LISTED_B = {"X": [9, 12, 14, 12, 9], "Y": [8, 8, 10, 12, 10]}
WANT_FIT_A = {"X": (28, 12, 8, 2), "Y": (28, 12, 8, 2)}
WANT_FIT_B = {"X": (28, 14, 9, 2), "Y": (29, 12, 8, 2)}
WANT_DRIFT = {"X": (0, 2, 1, 0), "Y": (1, 0, 0, 0)}
N_WANT = 10


def main():
    m16d = Path(sys.argv[1])
    t0 = time.time()
    rr, cc = m51.plane_coords()
    pl = m51.plane_of_byte()

    v0 = m51.load_dump(m16d / "m16-v0-s0000.bin")
    mid = m51.load_dump(m16d / "m16-mid-s0000.bin")
    full = m51.load_dump(m16d / "m16-full-s0000.bin")
    synth = m51.synth_w_bytes(v0, full, 0.5)
    sp = m51.interior_sites(v0, mid, full, synth)
    mask, delta = sp["mask"], sp["delta"]
    print(f"control C-P1: s0 cell7 n={sp['n']} (want 2475)")
    tail0, bulk0 = m51.tail_bulk_masks(mask, delta)
    print(f"control C-P1: s0 tail n={int(tail0.sum())} (want 102)")

    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    b = np.frombuffer(full, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    g = (a - b).astype(np.int16)
    ag = np.abs(g)
    moved = a != b
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)
    endpoint = moved & ((m == lo) | (m == hi))

    pool_bulk = np.flatnonzero(bulk0 & (ag >= 17))
    pool_endp = np.flatnonzero(endpoint & ~mask & (ag >= 32))
    pool = np.array(sorted(set(pool_bulk.tolist())
                           | set(pool_endp.tolist())), np.int64)
    print(f"control C-P1: pool bulk-gap>=17 n={len(pool_bulk)} + "
          f"endpoint-gap>=32 n={len(pool_endp)} union n={len(pool)}")

    # Choose N sites in offset order; one per row per pseudo-col.
    # Each offset must fit BOTH frames' listed delta strictly inside.
    want_a = {grp: dict(zip(ROWS, vals)) for grp, vals in LISTED_A.items()}
    want_b = {grp: dict(zip(ROWS, vals)) for grp, vals in LISTED_B.items()}
    chosen = {"X": {}, "Y": {}}  # grp -> {row: offset}
    skips = 0
    for o in pool.tolist():
        if all(len(chosen[grp]) == 5 for grp in ("X", "Y")):
            break
        r = int(rr[o])
        if r not in ROWS:
            continue
        filled = False
        for grp in ("X", "Y"):
            if r in chosen[grp]:
                continue
            midpa = int(s[o]) + want_a[grp][r]
            midpb = int(s[o]) + want_b[grp][r]
            if (int(lo[o]) < midpa < int(hi[o])
                    and int(lo[o]) < midpb < int(hi[o])):
                chosen[grp][r] = int(o)
                filled = True
                break
        if not filled and (r not in chosen["X"] or r not in chosen["Y"]):
            skips += 1
    nx, ny = len(chosen["X"]), len(chosen["Y"])
    print(f"control C-P1: chose {nx + ny}/{N_WANT} "
          f"(X={nx} Y={ny}; skips={skips})")
    if nx + ny != N_WANT or nx != 5 or ny != 5:
        print("control C-P1: SHORTFALL (feasibility): tabled, stop.")
        return

    # Build both control mids at the shared offsets.
    midpa = bytearray(mid)
    midpb = bytearray(mid)
    for grp in ("X", "Y"):
        for r, o in chosen[grp].items():
            midpa[o] = int(s[o]) + want_a[grp][r]
            midpb[o] = int(s[o]) + want_b[grp][r]
    midpa = bytes(midpa)
    midpb = bytes(midpb)
    spc_a = m51.interior_sites(v0, midpa, full, synth)
    spc_b = m51.interior_sites(v0, midpb, full, synth)
    tailc_a, _ = m51.tail_bulk_masks(spc_a["mask"], spc_a["delta"])
    tailc_b, _ = m51.tail_bulk_masks(spc_b["mask"], spc_b["delta"])
    inj_a, inj_b = {}, {}
    for grp in ("X", "Y"):
        for r, o in chosen[grp].items():
            inj_a[o] = want_a[grp][r]
            inj_b[o] = want_b[grp][r]
    injset = set(inj_a)
    t0set = set(np.flatnonzero(tail0).tolist())
    tcaset = set(np.flatnonzero(tailc_a).tolist())
    tcbset = set(np.flatnonzero(tailc_b).tolist())
    print(f"control C-P1: control-A tail n={len(tcaset)} "
          f"(want {len(t0set) + N_WANT})")
    print(f"control C-P1: control-B tail n={len(tcbset)} "
          f"(want {len(t0set) + N_WANT})")
    print(f"control C-P1: set-A exact={tcaset == (t0set | injset)} "
          f"set-B exact={tcbset == (t0set | injset)} "
          f"disjoint_orig={len(t0set & injset) == 0}")
    vals_a = all(int(spc_a["delta"][o]) == w for o, w in inj_a.items())
    vals_b = all(int(spc_b["delta"][o]) == w for o, w in inj_b.items())
    orig_a = all(int(spc_a["delta"][o]) == int(delta[o]) for o in t0set)
    orig_b = all(int(spc_b["delta"][o]) == int(delta[o]) for o in t0set)
    print(f"control C-P1: injected-A values exact={vals_a} "
          f"injected-B values exact={vals_b} "
          f"originals-A unchanged={orig_a} "
          f"originals-B unchanged={orig_b}")
    jv_a = m51.jaccard(tailc_a, tail0 | np.isin(np.arange(m51.N),
                                                np.array(sorted(injset))))
    jv_b = m51.jaccard(tailc_b, tail0 | np.isin(np.arange(m51.N),
                                                np.array(sorted(injset))))
    print(f"control C-P1: map jaccard A={jv_a:.4f} B={jv_b:.4f} "
          f"(want 1.0/1.0)")

    # Profile recovery on pseudo-columns (row->delta lists).
    prof_ok = True
    for grp in ("X", "Y"):
        for tag, spc, want in (("A", spc_a, want_a), ("B", spc_b, want_b)):
            rows = np.array(sorted(chosen[grp]), np.int64)
            dd = np.array([int(spc["delta"][chosen[grp][r]]) for r in rows],
                          np.int64)
            listed = np.array([want[grp][r] for r in rows], np.int64)
            ok = bool((dd == listed).all())
            prof_ok = prof_ok and ok
            print(f"control C-P1: pseudo-col {grp}-{tag}: n={len(rows)} "
                  f"profile_exact={ok} "
                  f"rowdelta={' '.join(f'{r}:{x}' for r, x in zip(rows, dd))}")

    # Fits per pseudo-col per frame + drift per pseudo-col.
    fit_ok, drift_ok = True, True
    for grp in ("X", "Y"):
        fits = {}
        for tag, spc in (("A", spc_a), ("B", spc_b)):
            rows = np.array(sorted(chosen[grp]), np.int64)
            dd = np.array([int(spc["delta"][chosen[grp][r]]) for r in rows],
                          np.int64)
            tf = m51.trifit(rows, dd)
            pt = m51.tri_apply(rows, tf)
            ht = int((pt == dd).sum())
            fits[tag] = (tf["p"], tf["h"], tf["e"], tf["w"])
            want = WANT_FIT_A[grp] if tag == "A" else WANT_FIT_B[grp]
            ok = fits[tag] == want and ht == 5
            fit_ok = fit_ok and ok
            print(f"control C-P1: fit {grp}-{tag}: TRI {ht}/{len(dd)} "
                  f"(p={tf['p']},h={tf['h']},e={tf['e']},w={tf['w']}) "
                  f"want p/h/e/w {want[0]}/{want[1]}/{want[2]}/{want[3]} "
                  f"exact={ok}")
        dp = fits["B"][0] - fits["A"][0]
        dh = fits["B"][1] - fits["A"][1]
        de = fits["B"][2] - fits["A"][2]
        dw = fits["B"][3] - fits["A"][3]
        ok = (dp, dh, de, dw) == WANT_DRIFT[grp]
        drift_ok = drift_ok and ok
        print(f"control C-P1: drift {grp}: got "
              f"{dp:+d}/{dh:+d}/{de:+d}/{dw:+d} want "
              f"{WANT_DRIFT[grp][0]:+d}/{WANT_DRIFT[grp][1]:+d}/"
              f"{WANT_DRIFT[grp][2]:+d}/{WANT_DRIFT[grp][3]:+d} "
              f"exact={ok}")

    # Full-control-frame TRI fits on named columns (tabled, no expect).
    for tag, spc, tailc in (("A", spc_a, tailc_a), ("B", spc_b, tailc_b)):
        offc = np.flatnonzero(tailc)
        dtc = spc["delta"][tailc].astype(np.int64)
        isy = pl[offc] == 0
        cprof = {}
        for ccol in m51.NAMED_COLS:
            sel = isy & (cc[offc] == ccol)
            ord_ = np.argsort(rr[offc[sel]])
            cprof[ccol] = {"rows": rr[offc[sel]][ord_].astype(np.int64),
                           "d": dtc[sel][ord_].astype(np.int64)}
        nn = sum(len(cprof[c]["rows"]) for c in m51.NAMED_COLS)
        tl = " ".join(
            f"c{c}=" + (f"p={m51.trifit(cprof[c]['rows'], cprof[c]['d'])['p']},"
                        f"h={m51.trifit(cprof[c]['rows'], cprof[c]['d'])['h']},"
                        f"e={m51.trifit(cprof[c]['rows'], cprof[c]['d'])['e']},"
                        f"w={m51.trifit(cprof[c]['rows'], cprof[c]['d'])['w']}"
                        if len(cprof[c]["d"]) else "empty")
            for c in m51.NAMED_COLS)
        print(f"control C-P1: full-frame-{tag} named n={nn} TRI: {tl}")

    passed = (vals_a and vals_b and orig_a and orig_b
              and tcaset == (t0set | injset)
              and tcbset == (t0set | injset)
              and prof_ok and fit_ok and drift_ok)
    print(f"control C-P1: wall={time.time() - t0:.1f}s pass={passed}")


if __name__ == "__main__":
    main()
