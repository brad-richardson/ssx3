#!/usr/bin/env python3
"""M41 positive control: synthetic truth with KNOWN boundary census.

Usage: control.py M16_DIR

Imports interior_sites + tail core from m41.py (same dir);
expectations are analytic. Shape A = s0 orig, shape B = s0
with injected mid':

- C-NEAR (known boundary census, mimics the near/far/noncell
  split): N_NEAR=2 known near-missing cells (|d_B| 6 and 7,
  one injected site each) + N_B5=1 known boundary-5-missing
  cell (|d_B| 5) + N_FAR=1 known far-missing cell (|d_B| 2) +
  N_NONCELL=1 known noncell-missing cell (endpoint landing),
  each at a currently-TAIL Y site in a distinct Y column
  (columns assigned greedily in numeric offset order,
  tabled). Injected dv = sign(d[o])*k (k=6,7,5,2) --
  strictly inside by construction (|d|>=8 strictly inside
  implies blend+k*sign(d) strictly inside; verified per site
  after recompute). Noncell landing mid'=v0 endpoint, falling
  back to full per site (endpoint reads noncell by
  construction since strict interior fails; verified per
  site after recompute). Recompute cell 7 + tail on B:
  per-cell standings must equal the injected 5xmissing-only
  delta-1 exactly, per-site values exact (near/b5/far
  landings |d|=6/7/5/2 bulk on B; noncell landing status
  noncell on B), boundary census exact (near=2, b5=1, far=1,
  noncell=1), gaps equal on both frames at every injected
  site (v0/full unchanged -- tabled), J(T_B,T_A) must equal
  97/102 exactly, row-lists exact per cell, cell-7 mask =
  maskA minus exactly the injected noncell site, all other
  tail members' d unchanged.

The estimator must recover the injected standings + row-lists +
values + boundary census + gaps exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m41 import (interior_sites, jaccard, load_dump,  # noqa: E402
                 off_of, plane_coords, plane_of_byte, synth_w_bytes,
                 tail_bulk_masks, tail_y_cols)


def main():
    m16d = Path(sys.argv[1])
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid = load_dump(m16d / "m16-mid-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    synth = synth_w_bytes(v0, full, 0.5)
    sp0 = interior_sites(v0, mid, full, synth)
    mask0, delta0 = sp0["mask"], sp0["delta"]
    tail0, _ = tail_bulk_masks(mask0, delta0)
    print(f"baseline s0 cell7 n={sp0['n']} (want 2475) "
          f"tail n={int(tail0.sum())} (want 102)")

    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    f = np.frombuffer(full, np.uint8).astype(np.int16)
    gA = a - f
    pl = plane_of_byte()
    pr, pc = plane_coords()

    # ---- candidate pool (offset order): currently-TAIL Y sites ----
    tail_cand = [int(o) for o in np.nonzero(tail0 & (pl == 0))[0]]
    print(f"C-NEAR: pool tail-Y n={len(tail_cand)}")

    # ---- greedy column assignment: 2 near + 1 b5 + 1 far + 1 noncell ----
    used_cols = set()
    used_sites = set()

    def pick_bulk(k, skip_cols):
        for o in tail_cand:
            if o in used_sites or int(pc[o]) in skip_cols:
                continue
            dv = int(np.sign(int(delta0[o]))) * k
            return o, dv
        return None, None

    def pick_noncell(skip_cols):
        for o in tail_cand:
            if o in used_sites or int(pc[o]) in skip_cols:
                continue
            return o, (int(a[o]), int(f[o]))
        return None, None

    plan = [("A", "near6", 6), ("B", "near7", 7), ("C", "b5", 5),
            ("D", "far2", 2)]
    picks = {}
    for tag, kind, k in plan:
        o, dv = pick_bulk(k, used_cols)
        picks[tag] = (kind, o, dv)
        if o is not None:
            used_cols.add(int(pc[o]))
            used_sites.add(o)
        print(f"C-NEAR: cell {tag} {kind} col="
              f"{int(pc[o]) if o is not None else None} "
              f"rc={(int(pr[o]), int(pc[o])) if o is not None else None} "
              f"dv={dv}")
    oE, midE = pick_noncell(used_cols)
    picks["E"] = ("noncell", oE, midE)
    if oE is not None:
        used_cols.add(int(pc[oE]))
        used_sites.add(oE)
    print(f"C-NEAR: cell E noncell col="
          f"{int(pc[oE]) if oE is not None else None} "
          f"rc={(int(pr[oE]), int(pc[oE])) if oE is not None else None} "
          f"mid'={midE}")
    if any(v[1] is None for v in picks.values()):
        print("C-NEAR: pool shortfall: tabled RED "
              "(cannot inject 2xnear + 1xb5 + 1xfar + 1xnoncell).")
        print("controls pass=False")
        return
    assert len(used_sites) == 5, "inject sets overlap?!"
    inj_bulk = {v[1]: v[2] for v in picks.values() if v[0] != "noncell"}
    inj_non = {oE: midE}
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
            print(f"C-NEAR: fallback site o={o}: v0-endpoint stayed "
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
    jwant = 97 / 102
    j_ok = abs(jj - jwant) < 1e-12
    valB_ok = all(bool(spB["delta"][o] == dv)
                  for o, dv in inj_bulk.items())
    qstatB_ok = all(bool(spB["mask"][o]) for o in inj_bulk)
    qstatN_ok = all(not bool(spB["mask"][o]) for o in inj_non)
    # boundary census on B over the 5 injected missings
    cen = {"near": 0, "b5": 0, "far": 0, "non": 0}
    for o in used_sites:
        if not bool(spB["mask"][o]):
            cen["non"] += 1
        else:
            ad = int(abs(int(spB["delta"][o])))
            if ad in (6, 7):
                cen["near"] += 1
            elif ad == 5:
                cen["b5"] += 1
            else:
                cen["far"] += 1
    cen_ok = cen == {"near": 2, "b5": 1, "far": 1, "non": 1}
    print(f"C-NEAR census: near/b5/far/non="
          f"{cen['near']}/{cen['b5']}/{cen['far']}/{cen['non']} "
          f"(want 2/1/1/1)")
    gB = (np.frombuffer(bytes(v0), np.uint8).astype(np.int16)
          - np.frombuffer(bytes(full), np.uint8).astype(np.int16))
    gap_ok = all(int(gB[o]) == int(gA[o]) for o in used_sites)
    # per-cell standings + row-lists
    tAcols = tail_y_cols(tail0, pl, pr, pc)
    tBcols = tail_y_cols(tB, pl, pr, pc)
    tab_ok = True
    for tag in ("A", "B", "C", "D", "E"):
        kind, o, _ = picks[tag]
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
        print(f"C-NEAR cell {tag} col={col} kind={kind}: s0rows={rA} "
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
            print(f"C-NEAR other-col drift col={col}: "
                  f"{tAcols.get(col, [])} vs {tBcols.get(col, [])}")
    for tag in ("A", "B", "C", "D"):
        kind, o, dv = picks[tag]
        print(f"C-NEAR {kind} rc=({int(pr[o])},{int(pc[o])}) "
              f"adB={int(abs(int(spB['delta'][o])))} (want {abs(dv)}) "
              f"qstatB={'bulk' if bool(spB['mask'][o]) else 'noncell'} "
              f"gA={int(gA[o])} gB={int(gB[o])} "
              f"match={bool(spB['delta'][o] == dv) and int(gB[o]) == int(gA[o])}")
    for o in sorted(inj_non):
        print(f"C-NEAR noncell rc=({int(pr[o])},{int(pc[o])}) "
              f"qstatB={'bulk' if bool(spB['mask'][o]) else 'noncell'} "
              f"(want noncell) gA={int(gA[o])} gB={int(gB[o])} "
              f"match={bool(not spB['mask'][o]) and int(gB[o]) == int(gA[o])}")
    wantmask = mask0.copy()
    wantmask[list(inj_non)] = False
    cell_ok = bool((spB["mask"] == wantmask).all())
    keep = tail0.copy()
    keep[list(used_sites)] = False
    keep_ok = bool((spB["delta"][keep] == delta0[keep]).all())
    print(f"C-NEAR: priv_n={int(priv.sum())} (want 0) "
          f"miss_n={int(miss.sum())} (want 5) "
          f"J={jj:.4f} (want {jwant:.4f})")
    print(f"C-NEAR: sets_exact={setP_ok and setM_ok} "
          f"j_exact={j_ok} values_exact={valB_ok} "
          f"census_exact={cen_ok} gaps_exact={gap_ok} "
          f"qstatB_exact={qstatB_ok} qstatN_exact={qstatN_ok} "
          f"table_exact={tab_ok} other_cols_fixed={other_ok} "
          f"cell_shrinks_exact={cell_ok} orig_kept={keep_ok}")
    ok = (setP_ok and setM_ok and j_ok and valB_ok and cen_ok
          and gap_ok and qstatB_ok and qstatN_ok and tab_ok and other_ok
          and cell_ok and keep_ok)
    print(f"controls pass={bool(ok)}")


if __name__ == "__main__":
    main()
