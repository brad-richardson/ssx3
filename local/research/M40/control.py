#!/usr/bin/env python3
"""M40 positive control: synthetic truth with KNOWN split cells.

Usage: control.py M16_DIR

Imports interior_sites + tail core from m40.py (same dir);
expectations are analytic. Shape A = s0 orig, shape B = s0
with injected mid':

- C-SPLIT (known split cells, mimics the bulk-vs-noncell
  missing split): N_BULK=2 known all-bulk-missing cells (1
  injected bulk landing each at a currently-TAIL Y site,
  mid'=blend+1 falling back to blend-1 per site if +1 is not
  strictly inside) + N_NONCELL=2 known all-noncell-missing
  cells (1 injected noncell landing each at a currently-TAIL
  Y site, mid'=endpoint v0[o] falling back to full[o] per
  site -- endpoint reads noncell by construction since
  strict interior fails; verified per site after recompute),
  all 4 cells in distinct Y columns (columns assigned
  greedily in numeric order, tabled). Recompute cell 7 +
  tail on B: per-cell standings must equal the injected
  4xmissing-only delta-1 exactly, per-site values exact
  (bulk landings |d|=1 bulk on B; noncell landings status
  noncell on B), gaps equal on both frames at every injected
  site (v0/full unchanged -- tabled), J(T_B,T_A) must equal
  98/102 exactly, row-lists exact per cell, cell-7 mask =
  maskA minus exactly the 2 injected noncell sites, all
  other tail members' d unchanged.

The estimator must recover the injected standings + row-lists +
values + gaps exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m40 import (interior_sites, jaccard, load_dump,  # noqa: E402
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

    # ---- candidate pool (offset order): currently-TAIL Y sites ----
    tail_cand = [int(o) for o in np.nonzero(tail0 & (pl == 0))[0]]
    print(f"C-SPLIT: pool tail-Y n={len(tail_cand)}")

    def bulk_dv(o):
        for dv in (1, -1):
            if int(lo[o]) < int(s[o]) + dv < int(hi[o]):
                return dv
        return None

    def noncell_mid(o):
        # Endpoint reads noncell by construction (strict interior
        # fails at lo/hi); prefer v0, fall back to full.
        return int(a[o]), int(f[o])

    # ---- greedy column assignment: A, B bulk-missing; C, D noncell ----
    used_cols = set()
    used_sites = set()

    def pick_bulk(skip_cols):
        for o in tail_cand:
            if o in used_sites or int(pc[o]) in skip_cols:
                continue
            dv = bulk_dv(o)
            if dv is not None:
                return o, dv
        return None, None

    def pick_noncell(skip_cols):
        for o in tail_cand:
            if o in used_sites or int(pc[o]) in skip_cols:
                continue
            return o, noncell_mid(o)
        return None, None

    oA, dvA = pick_bulk(used_cols)
    if oA is not None:
        used_cols.add(int(pc[oA]))
        used_sites.add(oA)
    oB, dvB = pick_bulk(used_cols)
    if oB is not None:
        used_cols.add(int(pc[oB]))
        used_sites.add(oB)
    oC, midC = pick_noncell(used_cols)
    if oC is not None:
        used_cols.add(int(pc[oC]))
        used_sites.add(oC)
    oD, midD = pick_noncell(used_cols)
    if oD is not None:
        used_cols.add(int(pc[oD]))
        used_sites.add(oD)
    cells = {"A": ("bulk", oA), "B": ("bulk", oB),
             "C": ("noncell", oC), "D": ("noncell", oD)}
    print(f"C-SPLIT: cell A bulk-missing col="
          f"{int(pc[oA]) if oA is not None else None} "
          f"rc={(int(pr[oA]), int(pc[oA])) if oA is not None else None} "
          f"dv={dvA}")
    print(f"C-SPLIT: cell B bulk-missing col="
          f"{int(pc[oB]) if oB is not None else None} "
          f"rc={(int(pr[oB]), int(pc[oB])) if oB is not None else None} "
          f"dv={dvB}")
    print(f"C-SPLIT: cell C noncell-missing col="
          f"{int(pc[oC]) if oC is not None else None} "
          f"rc={(int(pr[oC]), int(pc[oC])) if oC is not None else None} "
          f"mid'={midC}")
    print(f"C-SPLIT: cell D noncell-missing col="
          f"{int(pc[oD]) if oD is not None else None} "
          f"rc={(int(pr[oD]), int(pc[oD])) if oD is not None else None} "
          f"mid'={midD}")
    if oA is None or oB is None or oC is None or oD is None:
        print("C-SPLIT: pool shortfall: tabled RED "
              "(cannot inject 2xbulk-missing + 2xnoncell-missing).")
        print("controls pass=False")
        return
    assert len(used_sites) == 4, "inject sets overlap?!"
    inj_bulk = {oA: dvA, oB: dvB}
    inj_non = {oC: midC, oD: midD}
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    midB = m.copy()
    for o, dv in inj_bulk.items():
        midB[o] = s[o] + dv
    for o, (mv0, mvf) in inj_non.items():
        # Prefer the v0 endpoint; use full if v0 equals current mid
        # (else no change lands); fall back to full below if the
        # v0 endpoint would stay cell-7 (tabled either way).
        midB[o] = mv0 if mv0 != int(m[o]) else mvf
    spB = interior_sites(v0, midB.astype(np.uint8).tobytes(), full, synth)
    tB, _ = tail_bulk_masks(spB["mask"], spB["delta"])
    # Fallback pass: any noncell injection that stayed cell-7 gets full[o].
    for o, (mv0, mvf) in inj_non.items():
        if bool(spB["mask"][o]):
            print(f"C-SPLIT: fallback site o={o}: v0-endpoint stayed "
                  f"cell-7, retrying full-endpoint")
            midB[o] = mvf
    spB = interior_sites(v0, midB.astype(np.uint8).tobytes(), full, synth)
    tB, _ = tail_bulk_masks(spB["mask"], spB["delta"])
    priv = tB & ~tail0
    miss = tail0 & ~tB
    expP = np.zeros(len(a), bool)
    expM = np.zeros(len(a), bool)
    expM[list(used_sites)] = True
    setP_ok = bool((priv == expP).all())
    setM_ok = bool((miss == expM).all())
    jj = jaccard(tB, tail0)
    jwant = 98 / 102
    j_ok = abs(jj - jwant) < 1e-12
    valB_ok = all(bool(spB["delta"][o] == dv)
                  for o, dv in inj_bulk.items())
    qstatB_ok = all(bool(spB["mask"][o]) for o in inj_bulk)
    qstatN_ok = all(not bool(spB["mask"][o]) for o in inj_non)
    gB = (np.frombuffer(bytes(v0), np.uint8).astype(np.int16)
          - np.frombuffer(bytes(full), np.uint8).astype(np.int16))
    gap_ok = all(int(gB[o]) == int(gA[o]) for o in used_sites)
    # per-cell standings + row-lists
    tAcols = tail_y_cols(tail0, pl, pr, pc)
    tBcols = tail_y_cols(tB, pl, pr, pc)
    tab_ok = True
    for tag, (kind, o) in (("A", ("bulk", oA)), ("B", ("bulk", oB)),
                           ("C", ("noncell", oC)), ("D", ("noncell", oD))):
        col = int(pc[o])
        rA = tAcols.get(col, [])
        rB = tBcols.get(col, [])
        ov = len(set(rA) & set(rB))
        mi, ex = len(rA) - ov, len(rB) - ov
        stand = ("missing" if mi > 0 and ex == 0
                 else ("extra" if mi == 0 and ex > 0 else "mixed"))
        exrows = sorted(set(rB) - set(rA))
        mirows = sorted(set(rA) - set(rB))
        good = (stand == "missing" and mi == 1 and ex == 0
                and exrows == [] and mirows == [int(pr[o])])
        tab_ok = tab_ok and good
        print(f"C-SPLIT cell {tag} col={col} kind={kind}: s0rows={rA} "
              f"Brow={rB} stand={stand} (want missing) "
              f"miss/extra={mi}/{ex} (want 1/0) exrows={exrows} "
              f"mirows={mirows} match={good}")
    # no other column changed
    other_ok = True
    for col in set(tAcols) | set(tBcols):
        if col in {int(pc[o]) for o in used_sites}:
            continue
        if tAcols.get(col, []) != tBcols.get(col, []):
            other_ok = False
            print(f"C-SPLIT other-col drift col={col}: "
                  f"{tAcols.get(col, [])} vs {tBcols.get(col, [])}")
    for o, dv in sorted(inj_bulk.items()):
        print(f"C-SPLIT bulk rc=({int(pr[o])},{int(pc[o])}) "
              f"adB={int(abs(int(spB['delta'][o])))} (want 1) "
              f"qstatB={'bulk' if bool(spB['mask'][o]) else 'noncell'} "
              f"gA={int(gA[o])} gB={int(gB[o])} "
              f"match={bool(spB['delta'][o] == dv) and int(gB[o]) == int(gA[o])}")
    for o in sorted(inj_non):
        print(f"C-SPLIT noncell rc=({int(pr[o])},{int(pc[o])}) "
              f"qstatB={'bulk' if bool(spB['mask'][o]) else 'noncell'} "
              f"(want noncell) gA={int(gA[o])} gB={int(gB[o])} "
              f"match={bool(not spB['mask'][o]) and int(gB[o]) == int(gA[o])}")
    wantmask = mask0.copy()
    wantmask[list(inj_non)] = False
    cell_ok = bool((spB["mask"] == wantmask).all())
    keep = tail0.copy()
    keep[list(used_sites)] = False
    keep_ok = bool((spB["delta"][keep] == delta0[keep]).all())
    print(f"C-SPLIT: priv_n={int(priv.sum())} (want 0) "
          f"miss_n={int(miss.sum())} (want 4) "
          f"J={jj:.4f} (want {jwant:.4f})")
    print(f"C-SPLIT: sets_exact={setP_ok and setM_ok} "
          f"j_exact={j_ok} values_exact={valB_ok} "
          f"gaps_exact={gap_ok} qstatB_exact={qstatB_ok} "
          f"qstatN_exact={qstatN_ok} table_exact={tab_ok} "
          f"other_cols_fixed={other_ok} cell_shrinks_exact={cell_ok} "
          f"orig_kept={keep_ok}")
    ok = (setP_ok and setM_ok and j_ok and valB_ok
          and gap_ok and qstatB_ok and qstatN_ok and tab_ok and other_ok
          and cell_ok and keep_ok)
    print(f"controls pass={bool(ok)}")


if __name__ == "__main__":
    main()
