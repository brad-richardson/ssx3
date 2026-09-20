#!/usr/bin/env python3
"""M26 positive control C-P1: known hump profiles (offline).

Usage: control.py M16_DIR  (run from the work dir; importable m26 nearby)

Synthetic truth mid' on s0: M25 union pool (interior-BULK gap>=17 +
ENDPOINT gap>=32, offset order), distinct rows 26..30, N=10 total:
group A (5 sites, one per row) listed TRIANGLE delta = 8,10,12,10,8
(p=28,h=12,e=8,w=2); group B (5 sites, one per row) listed QUADRATIC
delta = 8,11,12,11,8 (exactly 8+(r-26)(30-r)). Recompute cell 7 +
tail from (v0,mid',full): tail set must equal T_s0 union injected
exactly (count 112 + values + map), originals unchanged. Profile
recovery: per-group row->delta lists must read the listed shapes
exactly. Restricted fits on injected-only per group: A -> TRI 5/5
(argmax TRI; QUAD 4/5 + TWO 2/5 expected), B -> QUAD 5/5 (argmax
QUAD; TRI 3/5 + TWO 2/5 expected). Tables only.
"""
import sys
import time
from pathlib import Path

import numpy as np

import m26

ROWS = [26, 27, 28, 29, 30]
LISTED = {"A": [8, 10, 12, 10, 8], "B": [8, 11, 12, 11, 8]}
N_WANT = 10


def main():
    m16d = Path(sys.argv[1])
    t0 = time.time()
    rr, cc = m26.plane_coords()
    pl = m26.plane_of_byte()

    v0 = m26.load_dump(m16d / "m16-v0-s0000.bin")
    mid = m26.load_dump(m16d / "m16-mid-s0000.bin")
    full = m26.load_dump(m16d / "m16-full-s0000.bin")
    synth = m26.synth_w_bytes(v0, full, 0.5)
    sp = m26.interior_sites(v0, mid, full, synth)
    mask, delta = sp["mask"], sp["delta"]
    print(f"control C-P1: s0 cell7 n={sp['n']} (want 2475)")
    tail0, bulk0 = m26.tail_bulk_masks(mask, delta)
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

    # Choose N sites in offset order; one per row per group.
    want = {grp: dict(zip(ROWS, vals)) for grp, vals in LISTED.items()}
    chosen = {"A": {}, "B": {}}  # grp -> {row: offset}
    skips = 0
    for o in pool.tolist():
        if all(len(chosen[grp]) == 5 for grp in ("A", "B")):
            break
        r = int(rr[o])
        if r not in ROWS:
            continue
        filled = False
        for grp in ("A", "B"):
            if r in chosen[grp]:
                continue
            midp = int(s[o]) + want[grp][r]
            if int(lo[o]) < midp < int(hi[o]):
                chosen[grp][r] = int(o)
                filled = True
                break
        if not filled and (r not in chosen["A"] or r not in chosen["B"]):
            skips += 1
    na, nb = len(chosen["A"]), len(chosen["B"])
    print(f"control C-P1: chose {na + nb}/{N_WANT} "
          f"(A={na} B={nb}; skips={skips})")
    if na + nb != N_WANT or na != 5 or nb != 5:
        print("control C-P1: SHORTFALL (feasibility): tabled, stop.")
        return

    midp = bytearray(mid)
    for grp in ("A", "B"):
        for r, o in chosen[grp].items():
            midp[o] = int(s[o]) + want[grp][r]
    midp = bytes(midp)
    spc = m26.interior_sites(v0, midp, full, synth)
    tailc, _ = m26.tail_bulk_masks(spc["mask"], spc["delta"])
    inj = {}
    for grp in ("A", "B"):
        for r, o in chosen[grp].items():
            inj[o] = want[grp][r]
    injset = set(inj)
    t0set = set(np.flatnonzero(tail0).tolist())
    tcset = set(np.flatnonzero(tailc).tolist())
    print(f"control C-P1: control tail n={len(tcset)} "
          f"(want {len(t0set) + N_WANT})")
    print(f"control C-P1: set exact={tcset == (t0set | injset)} "
          f"disjoint_orig={len(t0set & injset) == 0}")
    vals_ok = all(int(spc["delta"][o]) == w for o, w in inj.items())
    orig_ok = all(int(spc["delta"][o]) == int(delta[o]) for o in t0set)
    print(f"control C-P1: injected values exact={vals_ok} "
          f"originals unchanged={orig_ok}")
    jv = m26.jaccard(tailc, tail0 | np.isin(np.arange(m26.N),
                                            np.array(sorted(injset))))
    print(f"control C-P1: map jaccard vs T+inj = {jv:.4f} (want 1.0)")

    # Profile recovery on pseudo-columns (row->delta lists + hump).
    prof_ok = True
    for grp in ("A", "B"):
        rows = np.array(sorted(chosen[grp]), np.int64)
        dd = np.array([int(spc["delta"][chosen[grp][r]]) for r in rows],
                      np.int64)
        listed = np.array([want[grp][r] for r in rows], np.int64)
        ok = bool((dd == listed).all())
        prof_ok = prof_ok and ok
        hm = m26.hump_metrics(rows, dd)
        print(f"control C-P1: pseudo-col {grp}: n={len(rows)} "
              f"profile_exact={ok} "
              f"rowdelta={' '.join(f'{r}:{x}' for r, x in zip(rows, dd))} "
              f"hump peak={hm['peakrow']}/{hm['peakval']} "
              f"rise={hm['rise']} fall={hm['fall']} third={hm['third']}")

    # Restricted fits on injected-only (known truth).
    ident = {}
    for grp in ("A", "B"):
        rows = np.array(sorted(chosen[grp]), np.int64)
        dd = np.array([int(spc["delta"][chosen[grp][r]]) for r in rows],
                      np.int64)
        qf = m26.quadfit(rows, dd)
        pq = np.array([m26.rhalf(qf[0] * float(r) ** 2 + qf[1] * float(r) + qf[2])
                       for r in rows], np.int64)
        tf = m26.trifit(rows, dd)
        pt = m26.tri_apply(rows, tf)
        wf = m26.twolevel(rows, dd)
        pw = m26.two_apply(rows, wf)
        hq, ht, hw = (int((pq == dd).sum()), int((pt == dd).sum()),
                      int((pw == dd).sum()))
        ai = {"QUAD": hq, "TRI": ht, "TWO": hw}
        order = {"QUAD": 0, "TRI": 1, "TWO": 2}
        ident[grp] = sorted(ai, key=lambda f: (-ai[f], order[f]))[0]
        print(f"control C-P1: restricted {grp}: QUAD {hq}/{len(dd)} "
              f"(a={qf[0]:.6f},b={qf[1]:.6f},c={qf[2]:.6f}) "
              f"TRI {ht}/{len(dd)} "
              f"(p={tf['p']},h={tf['h']},e={tf['e']},w={tf['w']}) "
              f"TWO {hw}/{len(dd)} "
              f"(top={wf[0]},bot={wf[1]}) argmax={ident[grp]}")
    print(f"control C-P1: expect A TRI 5/5 (QUAD 4/5, TWO 2/5) + "
          f"B QUAD 5/5 (TRI 3/5, TWO 2/5); identities TRI/QUAD")
    id_ok = ident["A"] == "TRI" and ident["B"] == "QUAD"

    # Full-control-frame scores (fit on control frame, M25 precedent).
    print("control C-P1: full-control-frame scores (fit on control frame):")
    offc = np.flatnonzero(tailc)
    dtc = spc["delta"][tailc].astype(np.int64)
    isy = pl[offc] == 0
    cprof = {}
    for ccol in m26.NAMED_COLS:
        sel = isy & (cc[offc] == ccol)
        ord_ = np.argsort(rr[offc[sel]])
        cprof[ccol] = {"rows": rr[offc[sel]][ord_].astype(np.int64),
                       "d": dtc[sel][ord_].astype(np.int64)}
    cart = {"profs": cprof}
    alld = np.concatenate([cprof[c]["d"] for c in m26.NAMED_COLS])
    fb = m26.int_median(alld)
    cfit = {"quad": {c: (m26.quadfit(cprof[c]["rows"], cprof[c]["d"])
                          if len(cprof[c]["d"]) else None)
                      for c in m26.NAMED_COLS},
            "tri": {c: (m26.trifit(cprof[c]["rows"], cprof[c]["d"])
                         if len(cprof[c]["d"]) else None)
                     for c in m26.NAMED_COLS},
            "two": {c: (m26.twolevel(cprof[c]["rows"], cprof[c]["d"])
                         if len(cprof[c]["d"]) else None)
                     for c in m26.NAMED_COLS},
            "const": {c: (m26.int_median(cprof[c]["d"])
                           if len(cprof[c]["d"]) else fb)
                       for c in m26.NAMED_COLS}}
    for fid in m26.FIT_IDS:
        tall, pall = [], []
        pr = m26.apply_fit(fid, cfit, cart)
        for ccol in m26.NAMED_COLS:
            tall.append(cprof[ccol]["d"])
            pall.append(pr[ccol])
        t = np.concatenate(tall)
        p = np.concatenate(pall)
        ae = np.abs(p - t)
        print(f"control C-P1: full-frame {fid}: n={len(t)} "
              f"hits={int((ae == 0).sum())} near={int((ae == 1).sum())} "
              f"errvalues: {m26.exact_counts(ae)}")

    print(f"control C-P1: wall={time.time() - t0:.1f}s "
          f"pass={vals_ok and orig_ok and tcset == (t0set | injset) and prof_ok and id_ok}")


if __name__ == "__main__":
    main()
