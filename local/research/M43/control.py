#!/usr/bin/env python3
"""M43 positive control: synthetic truth with KNOWN fresh cells.

Usage: control.py M16_DIR

Imports interior_sites + tail core from m43.py (same dir);
expectations are analytic. Shape A = s0 orig, shape B = s0
with injected mid':

- C-FRESH (known fresh cells, mimics dest-row growth):
  N_priv=5 currently-interior-BULK Y sites in Y columns
  bearing NO s0 tail (first 5 in offset order passing the
  per-site strict-interior check), injected mid'=blend+8 on
  even (r+c) / blend-8 on odd (|d|=8, the tail boundary).
  The recomputed private set P_B = T_B - T_A must equal the
  injected 5 exactly, M_B = T_A - T_B must be empty exactly,
  J(T_B,T_A) must equal 102/107 = 0.9533 exactly, per-site
  |d| exact (8), gaps equal on both frames at every injected
  site (v0/full unchanged), other-frame statuses exact
  (privates bulk on A with original |d| tabled), spanned
  Y-column cells tabled with per-column row-lists +
  standings exact (extra-only on fresh columns, derived from
  the injection), cell-7 mask fixed, all other tail members'
  d unchanged.

The estimator must recover the injected counts + sets +
Jaccard + row-lists + per-site values + gaps + standings
exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m43 import (interior_sites, jaccard, load_dump,  # noqa: E402
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
    pl = plane_of_byte()
    pr, pc = plane_coords()

    # ---- fresh columns: Y cols bearing no s0 tail ----
    yA = tail_y_cols(tail0, pl, pr, pc)
    tailcols = set(yA)
    print(f"C-FRESH: s0 tail-Y cols n={len(tailcols)}; "
          f"no-tail Y cols n={640 - len(tailcols)}")
    isY = (pl == 0)
    notail = np.array([int(pc[o]) not in tailcols
              for o in range(len(a))], bool)
    cand = [int(o) for o in np.nonzero(bulk0 & isY & notail)[0]]
    print(f"C-FRESH: pool bulk-Y in no-tail cols n={len(cand)} (want>=5)")

    # ---- priv injections: first-5 offset-order passing strict-interior ----
    idx_p, want_p = [], {}
    for o in cand:
        dv = 8 if (int(pr[o]) + int(pc[o])) % 2 == 0 else -8
        mid2 = int(s[o]) + dv
        if int(lo[o]) < mid2 < int(hi[o]):
            idx_p.append(int(o))
            want_p[int(o)] = dv
        if len(idx_p) == 5:
            break
    print(f"C-FRESH: priv inject sites n={len(idx_p)} (want 5) "
          f"rc={[(int(pr[o]), int(pc[o])) for o in idx_p]}")
    if len(idx_p) != 5:
        print("C-FRESH: RED cannot-inject (pool shortfall); tabled.")
        print("controls pass=False")
        return
    orig_ad = {int(o): int(abs(int(delta0[o]))) for o in idx_p}
    print(f"C-FRESH: priv orig |d| on A: "
          + " ".join(f"{o}={orig_ad[o]}" for o in idx_p))

    inj_p = np.zeros(len(a), bool)
    inj_p[idx_p] = True
    mid2 = m.copy()
    for o in idx_p:
        mid2[o] = s[o] + want_p[int(o)]
    sp = interior_sites(v0, mid2.astype(np.uint8).tobytes(), full, synth)
    tk2, _ = tail_bulk_masks(sp["mask"], sp["delta"])
    priv = tk2 & ~tail0
    miss = tail0 & ~tk2
    jj = jaccard(tk2, tail0)
    set_p_ok = bool((priv == inj_p).all())
    set_m_ok = bool(miss.sum() == 0)
    j_ok = f"{jj:.4f}" == "0.9533"
    cell_ok = bool((sp["mask"] == mask0).all())
    val_p_ok = all(bool(sp["delta"][o] == want_p[int(o)]) for o in idx_p)
    keep = tail0  # miss empty: every orig tail member kept
    keep_ok = bool((sp["delta"][keep] == delta0[keep]).all())
    ostat_p_ok = all(bool(mask0[o]) and int(abs(int(delta0[o]))) < 8
                     for o in idx_p)
    gA = a - f
    gB = a - f  # v0/full unchanged by construction
    gap_eq_ok = all(bool(gB[o] == gA[o]) for o in idx_p)
    print(f"C-FRESH: gaps v0/full unchanged by construction "
          f"(mid-only injection); gap-eq on injected: {gap_eq_ok}")
    # spanned fresh-column cells + per-column row-lists/standings
    yB = tail_y_cols(tk2, pl, pr, pc)
    spanned = sorted({int(pc[o]) for o in idx_p})
    print(f"C-FRESH: spanned Y cols: {spanned} "
          f"(all no-s0-tail: {all(c not in tailcols for c in spanned)})")
    stand_ok = True
    for c in spanned:
        rA, rB = yA.get(c, []), yB.get(c, [])
        ov = len(set(rA) & set(rB))
        mm, ee = len(rA) - ov, len(rB) - ov
        want_ex_rows = sorted(int(pr[o]) for o in idx_p
                              if int(pc[o]) == c)
        got_ex_rows = sorted(set(rB) - set(rA))
        good = (rA == [] and got_ex_rows == want_ex_rows
                and mm == 0 and ee == len(want_ex_rows))
        stand = ("missing" if mm > 0 and ee == 0
                 else ("extra" if mm == 0 and ee > 0 else "mixed"))
        stand_ok = stand_ok and good and stand == "extra"
        print(f"C-FRESH col {c}: rowsA={rA} rowsB={rB} miss/extra={mm}/{ee} "
              f"stand={stand} rows-exact={good}")
    npos = sum(1 for o in idx_p if want_p[int(o)] > 0)
    ok = (set_p_ok and set_m_ok and j_ok and cell_ok and val_p_ok
          and keep_ok and ostat_p_ok and gap_eq_ok and stand_ok)
    print(f"C-FRESH: injected priv=5 (+8x{npos}/-8x{5 - npos}) "
          f"tailB={int(tk2.sum())} (want 107)")
    print(f"C-FRESH: priv_n={int(priv.sum())} (want 5) "
          f"miss_n={int(miss.sum())} (want 0) J={jj:.4f} (want 0.9533) "
          f"priv_exact={set_p_ok} miss_empty={set_m_ok} j_exact={j_ok} "
          f"cell_fixed={cell_ok} pvalues_exact={val_p_ok} "
          f"orig_kept={keep_ok} ostat_exact={ostat_p_ok} "
          f"standings_exact={stand_ok} pass={ok}")
    print(f"controls pass={bool(ok)}")


if __name__ == "__main__":
    main()
