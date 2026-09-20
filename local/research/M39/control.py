#!/usr/bin/env python3
"""M39 positive control: synthetic truth with KNOWN uniform + mixed cells.

Usage: control.py M16_DIR

Imports interior_sites + tail core from m39.py (same dir);
expectations are analytic. Shape A = s0 orig, shape B = s0
with injected mid':

- C-UNIFORM (known uniform + mixed cells, mimics the s3-vs-mixed
  split): N_UNI=3 known delta-1 cells (2 extra-only: 1 injected
  tail landing each at currently-interior-BULK Y sites with gap>=17,
  first in offset order, mid'=blend+8 on even (r+c) / blend-8 on
  odd, per-site strict-interior check with other-sign fallback;
  1 missing-only: 1 injected bulk landing at a currently-TAIL Y
  site, mid'=blend+1 falling back to blend-1 per site if +1 is not
  strictly inside) + N_MIX=1 known mixed cell (1 extra landing + 1
  missing landing in the SAME Y column, same injection rules), all
  4 cells in distinct Y columns except the mixed cell's shared
  column (columns assigned greedily in numeric order, tabled).
  Recompute cell 7 + tail on B: per-cell standings must equal the
  injected 3xdelta-1 (2 extra-only + 1 missing-only) + 1xmixed
  (1/1 d2) exactly, per-site |d| exact (extras 8, missings 1),
  gaps equal on both frames at every injected site (v0/full
  unchanged -- tabled), other-frame statuses exact (extras bulk on
  A with original |d| tabled; missings bulk on B), row-lists exact
  per cell, cell-7 mask fixed, all other tail members' d unchanged.

The estimator must recover the injected standings + row-lists +
values + gaps exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m39 import (interior_sites, jaccard, load_dump,  # noqa: E402
                 off_of, plane_coords, plane_of_byte, synth_w_bytes,
                 tail_bulk_masks, tail_y_cols, y_col_rows)


def main():
    m16d = Path(sys.argv[1])
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid = load_dump(m16d / "m16-mid-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    synth = synth_w_bytes(v0, full, 0.5)
    sp0 = interior_sites(v0, mid, full, synth)
    mask0, delta0 = sp0["mask"], sp0["delta"]
    tail0, bulk0 = tail_bulk_masks(mask0, delta0)
    print(f"baseline s0 cell7 n={sp0['n']} (want 2475) "
          f"tail n={int(tail0.sum())} (want 102)")

    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    f = np.frombuffer(full, np.uint8).astype(np.int16)
    gA = a - f
    lo = np.minimum(a, f)
    hi = np.maximum(a, f)
    pl = plane_of_byte()
    pr, pc = plane_coords()

    # ---- candidate pools (offset order) ----
    bulk_cand = [int(o) for o in np.nonzero(
        bulk0 & (pl == 0) & (np.abs(gA) >= 17))[0]]
    tail_cand = [int(o) for o in np.nonzero(tail0 & (pl == 0))[0]]
    print(f"C-UNIFORM: pool bulk-Y-gap>=17 n={len(bulk_cand)} "
          f"tail-Y n={len(tail_cand)}")

    def extra_dv(o):
        r, c = int(pr[o]), int(pc[o])
        first = 8 if (r + c) % 2 == 0 else -8
        for dv in (first, -first):
            if int(lo[o]) < int(s[o]) + dv < int(hi[o]):
                return dv
        return None

    def miss_dv(o):
        for dv in (1, -1):
            if int(lo[o]) < int(s[o]) + dv < int(hi[o]):
                return dv
        return None

    # ---- greedy column assignment: A, B extra-only; C missing-only;
    #      D mixed (extra + missing in the same column) ----
    used_cols = set()
    used_sites = set()

    def pick_extra(skip_cols):
        for o in bulk_cand:
            if o in used_sites or int(pc[o]) in skip_cols:
                continue
            dv = extra_dv(o)
            if dv is not None:
                return o, dv
        return None, None

    def pick_miss(skip_cols):
        for o in tail_cand:
            if o in used_sites or int(pc[o]) in skip_cols:
                continue
            dv = miss_dv(o)
            if dv is not None:
                return o, dv
        return None, None

    oA, dvA = pick_extra(used_cols)
    if oA is not None:
        used_cols.add(int(pc[oA]))
        used_sites.add(oA)
    oB, dvB = pick_extra(used_cols)
    if oB is not None:
        used_cols.add(int(pc[oB]))
        used_sites.add(oB)
    oC, dvC = pick_miss(used_cols)
    if oC is not None:
        used_cols.add(int(pc[oC]))
        used_sites.add(oC)
    # D: first column (numeric) outside used_cols holding both an
    # injectable bulk site and an injectable tail site.
    oD_e = oD_m = dvD_e = dvD_m = None
    if oA is not None and oB is not None and oC is not None:
        cols = sorted({int(pc[o]) for o in bulk_cand + tail_cand}
                      - used_cols)
        for c in cols:
            be = [o for o in bulk_cand
                  if int(pc[o]) == c and o not in used_sites
                  and extra_dv(o) is not None]
            bm = [o for o in tail_cand
                  if int(pc[o]) == c and o not in used_sites
                  and miss_dv(o) is not None]
            if be and bm:
                oD_e, dvD_e = be[0], extra_dv(be[0])
                oD_m, dvD_m = bm[0], miss_dv(bm[0])
                used_cols.add(c)
                used_sites |= {oD_e, oD_m}
                break
    cells = {"A": (oA, None), "B": (oB, None), "C": (None, oC),
             "D": (oD_e, oD_m)}
    print(f"C-UNIFORM: cell A extra-only col="
          f"{int(pc[oA]) if oA is not None else None} "
          f"rc={(int(pr[oA]), int(pc[oA])) if oA is not None else None} "
          f"dv={dvA}")
    print(f"C-UNIFORM: cell B extra-only col="
          f"{int(pc[oB]) if oB is not None else None} "
          f"rc={(int(pr[oB]), int(pc[oB])) if oB is not None else None} "
          f"dv={dvB}")
    print(f"C-UNIFORM: cell C missing-only col="
          f"{int(pc[oC]) if oC is not None else None} "
          f"rc={(int(pr[oC]), int(pc[oC])) if oC is not None else None} "
          f"dv={dvC}")
    print(f"C-UNIFORM: cell D mixed col="
          f"{int(pc[oD_e]) if oD_e is not None else None} "
          f"extra_rc={(int(pr[oD_e]), int(pc[oD_e])) if oD_e is not None else None} "
          f"dv={dvD_e} "
          f"miss_rc={(int(pr[oD_m]), int(pc[oD_m])) if oD_m is not None else None} "
          f"dv={dvD_m}")
    if oA is None or oB is None or oC is None or oD_e is None:
        print("C-UNIFORM: pool shortfall: tabled RED "
              "(cannot inject 3xdelta-1 + 1xmixed).")
        print("controls pass=False")
        return
    assert len(used_sites) == 5, "inject sets overlap?!"
    inj_extra = {oA: dvA, oB: dvB, oD_e: dvD_e}
    inj_miss = {oC: dvC, oD_m: dvD_m}
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    midB = m.copy()
    for o, dv in {**inj_extra, **inj_miss}.items():
        midB[o] = s[o] + dv
    spB = interior_sites(v0, midB.astype(np.uint8).tobytes(), full, synth)
    tB, _ = tail_bulk_masks(spB["mask"], spB["delta"])
    priv = tB & ~tail0
    miss = tail0 & ~tB
    expP = np.zeros(len(a), bool)
    expP[list(inj_extra)] = True
    expM = np.zeros(len(a), bool)
    expM[list(inj_miss)] = True
    setP_ok = bool((priv == expP).all())
    setM_ok = bool((miss == expM).all())
    jj = jaccard(tB, tail0)
    jwant = 100 / 105
    j_ok = abs(jj - jwant) < 1e-12
    valP_ok = all(bool(spB["delta"][o] == dv)
                  for o, dv in inj_extra.items())
    valM_ok = all(bool(spB["delta"][o] == dv)
                  for o, dv in inj_miss.items())
    gB = gA  # v0/full unchanged by construction; verify below
    vB, fB = bytes(v0), bytes(full)
    gB = (np.frombuffer(vB, np.uint8).astype(np.int16)
          - np.frombuffer(fB, np.uint8).astype(np.int16))
    gap_ok = all(int(gB[o]) == int(gA[o]) for o in used_sites)
    ostat_ok = all(bool(mask0[o]) for o in inj_extra)
    qstat_ok = all(bool(spB["mask"][o]) for o in inj_miss)
    # per-cell standings + row-lists
    tAcols = tail_y_cols(tail0, pl, pr, pc)
    tBcols = tail_y_cols(tB, pl, pr, pc)
    want = {"A": ("extra", 0, 1), "B": ("extra", 0, 1),
            "C": ("missing", 1, 0), "D": ("mixed", 1, 1)}
    tab_ok = True
    for tag, col in (("A", int(pc[oA])), ("B", int(pc[oB])),
                     ("C", int(pc[oC])), ("D", int(pc[oD_e]))):
        rA = tAcols.get(col, [])
        rB = tBcols.get(col, [])
        ov = len(set(rA) & set(rB))
        mi, ex = len(rA) - ov, len(rB) - ov
        stand = ("missing" if mi > 0 and ex == 0
                 else ("extra" if mi == 0 and ex > 0 else "mixed"))
        wst, wmi, wex = want[tag]
        oe, om = cells[tag]
        exrows = sorted(set(rB) - set(rA))
        mirows = sorted(set(rA) - set(rB))
        wexrows = sorted(int(pr[o]) for o in ([oe] if oe is not None
                                             else []))
        wmirows = sorted(int(pr[o]) for o in ([om] if om is not None
                                             else []))
        good = (stand == wst and mi == wmi and ex == wex
                and exrows == wexrows and mirows == wmirows)
        tab_ok = tab_ok and good
        print(f"C-UNIFORM cell {tag} col={col}: s0rows={rA} Brow={rB} "
              f"stand={stand} (want {wst}) miss/extra={mi}/{ex} "
              f"(want {wmi}/{wex}) exrows={exrows} mirows={mirows} "
              f"match={good}")
    # no other column changed
    other_ok = True
    for col in set(tAcols) | set(tBcols):
        if col in {int(pc[o]) for o in used_sites}:
            continue
        if tAcols.get(col, []) != tBcols.get(col, []):
            other_ok = False
            print(f"C-UNIFORM other-col drift col={col}: "
                  f"{tAcols.get(col, [])} vs {tBcols.get(col, [])}")
    for o, dv in sorted(inj_extra.items()):
        print(f"C-UNIFORM extra rc=({int(pr[o])},{int(pc[o])}) "
              f"adB={int(abs(int(spB['delta'][o])))} (want 8) "
              f"ostatA=bulk adA={int(abs(int(delta0[o])))} "
              f"gA={int(gA[o])} gB={int(gB[o])} "
              f"match={bool(spB['delta'][o] == dv) and int(gB[o]) == int(gA[o])}")
    for o, dv in sorted(inj_miss.items()):
        print(f"C-UNIFORM miss rc=({int(pr[o])},{int(pc[o])}) "
              f"adB={int(abs(int(spB['delta'][o])))} (want 1) "
              f"qstatB=bulk gA={int(gA[o])} gB={int(gB[o])} "
              f"match={bool(spB['delta'][o] == dv) and int(gB[o]) == int(gA[o])}")
    cell_ok = bool((spB["mask"] == mask0).all())
    keep = tail0.copy()
    keep[list(used_sites)] = False
    keep_ok = bool((spB["delta"][keep] == delta0[keep]).all())
    print(f"C-UNIFORM: priv_n={int(priv.sum())} (want 3) "
          f"miss_n={int(miss.sum())} (want 2) "
          f"J={jj:.4f} (want {jwant:.4f})")
    print(f"C-UNIFORM: sets_exact={setP_ok and setM_ok} "
          f"j_exact={j_ok} values_exact={valP_ok and valM_ok} "
          f"gaps_exact={gap_ok} ostat_exact={ostat_ok} "
          f"qstat_exact={qstat_ok} table_exact={tab_ok} "
          f"other_cols_fixed={other_ok} cell_fixed={cell_ok} "
          f"orig_kept={keep_ok}")
    ok = (setP_ok and setM_ok and j_ok and valP_ok and valM_ok
          and gap_ok and ostat_ok and qstat_ok and tab_ok and other_ok
          and cell_ok and keep_ok)
    print(f"controls pass={bool(ok)}")


if __name__ == "__main__":
    main()
