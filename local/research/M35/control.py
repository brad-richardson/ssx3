#!/usr/bin/env python3
"""M35 positive control: synthetic truth with KNOWN unnamed-cell values.

Usage: control.py M16_DIR

Imports interior_sites + tail core from m35.py (same dir);
expectations are analytic. Shape A = s0 orig, shape B = s0
with injected mid':

- C-VAL (known values, mimics unnamed-cell extras+missings):
  N_priv=6 currently-interior-BULK Y sites with gap>=17 (first
  6 in offset order), injected mid'=blend+8 on even (r+c) /
  blend-8 on odd (|d|=8, the tail boundary; per-site
  strict-interior check) AND N_miss=4 currently-TAIL sites
  (first 4 in offset order), injected mid'=blend+1 (fall back
  to blend-1 per site if +1 is not strictly inside — tabled).
  The recomputed private set P_B = T_B - T_A must equal the
  injected 6 exactly, M_B = T_A - T_B must equal the injected
  4 exactly, J(T_B,T_A) must equal 98/108 = 0.9074 exactly,
  per-site |d| exact (privates 8, missings 1), gaps equal on
  both frames at every injected site (v0/full unchanged),
  other-frame statuses exact (privates bulk on A with
  original |d| tabled; missings bulk on B), spanned Y-column
  cells tabled with per-cell standings exact (derived from
  the injection), cell-7 mask fixed, all other tail members'
  d unchanged.

The estimator must recover the injected counts + sets +
Jaccard + per-site values + gaps + standings exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m35 import (interior_sites, jaccard, load_dump,  # noqa: E402
                 plane_coords, plane_of_byte, synth_w_bytes,
                 tail_bulk_masks, tail_y_cols)


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
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    f = np.frombuffer(full, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    lo = np.minimum(a, f)
    hi = np.maximum(a, f)
    gap = np.abs(a - f)
    pl = plane_of_byte()
    pr, pc = plane_coords()

    # ---- priv injections: first-6 offset-order bulk gap>=17 Y ----
    isY = (np.arange(len(a)) % 4 == 0) | (np.arange(len(a)) % 4 == 2)
    cand_p = [int(o) for o in np.nonzero(bulk0 & (gap >= 17) & isY)[0]]
    print(f"C-VAL: pool bulk gap>=17 Y n={len(cand_p)} (want>=6)")
    idx_p, want_p = [], {}
    for o in cand_p:
        dv = 8 if (int(pr[o]) + int(pc[o])) % 2 == 0 else -8
        mid2 = int(s[o]) + dv
        if int(lo[o]) < mid2 < int(hi[o]):
            idx_p.append(int(o))
            want_p[int(o)] = dv
        if len(idx_p) == 6:
            break
    print(f"C-VAL: priv inject sites n={len(idx_p)} (want 6) "
          f"rc={[(int(pr[o]), int(pc[o])) for o in idx_p]}")
    orig_ad = {int(o): int(abs(int(delta0[o]))) for o in idx_p}
    print(f"C-VAL: priv orig |d| on A: "
          + " ".join(f"{o}={orig_ad[o]}" for o in idx_p))

    # ---- miss injections: first-4 offset-order tail ----
    cand_m = [int(o) for o in np.nonzero(tail0)[0][:4]]
    print(f"C-VAL: pool tail n={int(tail0.sum())} (want 102); "
          f"miss inject n={len(cand_m)} (want 4) "
          f"rc={[(int(pr[o]), int(pc[o])) for o in cand_m]} "
          f"planes={[int(pl[o]) for o in cand_m]}")
    idx_m, want_m = [], {}
    nfb = 0
    for o in cand_m:
        for dv in (1, -1):
            mid2 = int(s[o]) + dv
            if int(lo[o]) < mid2 < int(hi[o]):
                idx_m.append(int(o))
                want_m[int(o)] = dv
                nfb += int(dv == -1)
                break
    print(f"C-VAL: miss landing +1fb={nfb} "
          f"rc={[(int(pr[o]), int(pc[o])) for o in idx_m]}")

    assert len(idx_p) == 6 and len(idx_m) == 4
    assert not (set(idx_p) & set(idx_m)), "inject sets overlap?!"
    inj_p = np.zeros(len(a), bool)
    inj_p[idx_p] = True
    inj_m = np.zeros(len(a), bool)
    inj_m[idx_m] = True
    mid2 = m.copy()
    for o in idx_p:
        mid2[o] = s[o] + want_p[int(o)]
    for o in idx_m:
        mid2[o] = s[o] + want_m[int(o)]
    sp = interior_sites(v0, mid2.astype(np.uint8).tobytes(), full, synth)
    tk2, bk2 = tail_bulk_masks(sp["mask"], sp["delta"])
    priv = tk2 & ~tail0
    miss = tail0 & ~tk2
    jj = jaccard(tk2, tail0)
    set_p_ok = bool((priv == inj_p).all())
    set_m_ok = bool((miss == inj_m).all())
    j_ok = f"{jj:.4f}" == "0.9074"
    cell_ok = bool((sp["mask"] == mask0).all())
    val_p_ok = all(bool(sp["delta"][o] == want_p[int(o)]) for o in idx_p)
    val_m_ok = all(bool(sp["delta"][o] == want_m[int(o)]) for o in idx_m)
    keep = tail0 & ~inj_m
    keep_ok = bool((sp["delta"][keep] == delta0[keep]).all())
    # other-frame statuses: privates bulk on A, missings bulk on B
    ostat_p_ok = all(bool(mask0[o]) and int(abs(int(delta0[o]))) < 8
                     for o in idx_p)
    ostat_m_ok = all(bool(sp["mask"][o]) and int(abs(int(sp["delta"][o]))) < 8
                     for o in idx_m)
    # gaps equal on both frames at every injected site (v0/full same)
    gA = a - f
    gap_eq_ok = all(bool(priv[o] or miss[o]) for o in idx_p + idx_m)
    print(f"C-VAL: gaps v0/full unchanged by construction "
          f"(mid-only injection); all injected in P_B/M_B: {gap_eq_ok}")
    # spanned Y-column cells + per-cell standings from the injection
    yA = tail_y_cols(tail0, pl, pr, pc)
    yB = tail_y_cols(tk2, pl, pr, pc)
    spanned = sorted({int(pc[o]) for o in idx_p + idx_m
                      if int(pl[o]) == 0})
    print(f"C-VAL: spanned Y cols: {spanned}")
    stand_ok = True
    for c in spanned:
        rA, rB = yA.get(c, []), yB.get(c, [])
        ov = len(set(rA) & set(rB))
        mm, ee = len(rA) - ov, len(rB) - ov
        want_miss_rows = sorted(int(pr[o]) for o in idx_m
                                if int(pc[o]) == c)
        want_ex_rows = sorted(int(pr[o]) for o in idx_p
                              if int(pc[o]) == c)
        got_miss_rows = sorted(set(rA) - set(rB))
        got_ex_rows = sorted(set(rB) - set(rA))
        good = (got_miss_rows == want_miss_rows
                and got_ex_rows == want_ex_rows)
        stand = ("missing" if mm > 0 and ee == 0
                 else ("extra" if mm == 0 and ee > 0 else "mixed"))
        stand_ok = stand_ok and good
        print(f"C-VAL col {c}: rowsA={rA} rowsB={rB} miss/extra={mm}/{ee} "
              f"stand={stand} rows-exact={good}")
    npos = sum(1 for o in idx_p if want_p[int(o)] > 0)
    ok = (set_p_ok and set_m_ok and j_ok and cell_ok and val_p_ok
          and val_m_ok and keep_ok and ostat_p_ok and ostat_m_ok
          and gap_eq_ok and stand_ok)
    print(f"C-VAL: injected priv=6 (+8x{npos}/-8x{6 - npos}) miss=4 "
          f"disjoint={not bool((inj_p & inj_m).any())} "
          f"tailB={int(tk2.sum())} (want 104)")
    print(f"C-VAL: priv_n={int(priv.sum())} (want 6) "
          f"miss_n={int(miss.sum())} (want 4) J={jj:.4f} (want 0.9074) "
          f"priv_exact={set_p_ok} miss_exact={set_m_ok} j_exact={j_ok} "
          f"cell_fixed={cell_ok} pvalues_exact={val_p_ok} "
          f"mvalues_exact={val_m_ok} orig_kept={keep_ok} "
          f"ostat_exact={ostat_p_ok and ostat_m_ok} "
          f"standings_exact={stand_ok} pass={ok}")
    print(f"controls pass={bool(ok)}")


if __name__ == "__main__":
    main()
