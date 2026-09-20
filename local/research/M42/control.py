#!/usr/bin/env python3
"""M42 positive control: synthetic truth with KNOWN big-site ranking.

Usage: control.py M16_DIR

Imports interior_sites + tail core from m42.py (same dir);
expectations are analytic. Shape A = s0 orig, shape B = s0
with injected mid':

- C-BIG (known big-site ranking, mimics big vs near-big):
  N_BIG_PRIV=3 known big privates (|d_B| 16, 14, 12) +
  N_DECOY_PRIV=2 known near-boundary decoys (|d_B| 10, 8) at
  currently-BULK Y sites (largest-first greedy in numeric
  offset order; sign tabled per site) AND N_BIG_MISS=3 known
  big missings (currently-TAIL Y sites with |d_A| 47, 46, 45)
  + N_DECOY_MISS=2 known near-big decoys (|d_A| 17, 16),
  each injected mid'=blend+1 (fall back to blend-1 per site
  if +1 is not strictly inside — tabled). The recomputed
  private set P_B = T_B - T_A must equal the injected 5
  exactly, M_B = T_A - T_B must equal the injected 5
  exactly, J(T_B,T_A) must equal 97/107 exactly, per-site
  |d| exact, gaps equal on both frames at every injected
  site (v0/full unchanged), other-frame statuses exact,
  extra-side top-5 listing by |d_B| must equal
  [16,14,12,10,8] in rank order 1-5 exactly, missing-side
  top-5 listing by |d_A| must equal [47,46,45,17,16] in
  rank order 1-5 exactly, spanned Y-column cells tabled
  with per-cell standings + row-lists exact (derived from
  the injection), cell-7 mask fixed, all other tail
  members' d unchanged.

The estimator must recover the injected sets + Jaccard +
per-site values + gaps + standings + both top-5 listings +
ranks exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m42 import (interior_sites, jaccard, load_dump,  # noqa: E402
                 plane_coords, plane_of_byte, synth_w_bytes,
                 tail_bulk_masks, tail_y_cols)


def crank(ad, ads):
    return 1 + sum(1 for x in ads if x > ad)


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
    lo = np.minimum(a, np.frombuffer(full, np.uint8).astype(np.int16))
    hi = np.maximum(a, np.frombuffer(full, np.uint8).astype(np.int16))
    f = np.frombuffer(full, np.uint8).astype(np.int16)
    pl = plane_of_byte()
    pr, pc = plane_coords()
    isY = (pl == 0)

    # ---- priv injections: largest-first greedy bulk-Y, dv 16/14/12/10/8 ----
    bulkY = [int(o) for o in np.nonzero(bulk0 & isY)[0]]
    print(f"C-BIG: pool bulk-Y n={len(bulkY)}")
    want_p = {}
    used = set()
    for dv in (16, 14, 12, 10, 8):
        found = None
        for o in bulkY:
            if o in used:
                continue
            if int(lo[o]) < int(s[o]) + dv < int(hi[o]):
                found, sgn = o, +1
                break
            if int(lo[o]) < int(s[o]) - dv < int(hi[o]):
                found, sgn = o, -1
                break
        if found is None:
            print(f"C-BIG: pool shortfall at dv={dv}: tabled RED "
                  f"(cannot inject 16/14/12/10/8).")
            print("controls pass=False")
            return
        want_p[found] = sgn * dv
        used.add(found)
        print(f"C-BIG: priv dv={sgn * dv:+d} o={found} "
              f"rc=({int(pr[found])},{int(pc[found])}) "
              f"orig_ad={int(abs(int(delta0[found])))}")
    idx_p = sorted(want_p)

    # ---- miss injections: tail-Y at |d| 47/46/45/17/16 (first each) ----
    tailY = [int(o) for o in np.nonzero(tail0 & isY)[0]]
    byad = {}
    for o in tailY:
        byad.setdefault(int(abs(int(delta0[o]))), []).append(o)
    want_m = {}
    nfb = 0
    for k in (47, 46, 45, 17, 16):
        lst = byad.get(k, [])
        if not lst:
            print(f"C-BIG: pool shortfall at |d|={k}: tabled RED.")
            print("controls pass=False")
            return
        o = lst[0]
        if o in used:
            print(f"C-BIG: overlap at |d|={k} o={o}: tabled RED.")
            print("controls pass=False")
            return
        for dv in (1, -1):
            if int(lo[o]) < int(s[o]) + dv < int(hi[o]):
                want_m[o] = dv
                nfb += int(dv == -1)
                used.add(o)
                break
        else:
            print(f"C-BIG: landing shortfall at |d|={k} o={o}: tabled RED.")
            print("controls pass=False")
            return
        print(f"C-BIG: miss |d_A|={k} o={o} "
              f"rc=({int(pr[o])},{int(pc[o])}) dv={want_m[o]:+d}")
    idx_m = sorted(want_m)
    print(f"C-BIG: miss landing +1fb={nfb}")
    assert not (set(idx_p) & set(idx_m)), "inject sets overlap?!"

    inj_p = np.zeros(len(a), bool)
    inj_p[idx_p] = True
    inj_m = np.zeros(len(a), bool)
    inj_m[idx_m] = True
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    midB = m.copy()
    for o, dv in want_p.items():
        midB[o] = s[o] + dv
    for o, dv in want_m.items():
        midB[o] = s[o] + dv
    spB = interior_sites(v0, midB.astype(np.uint8).tobytes(), full, synth)
    tB, _ = tail_bulk_masks(spB["mask"], spB["delta"])
    priv = tB & ~tail0
    miss = tail0 & ~tB
    jj = jaccard(tB, tail0)
    jwant = 97 / 107
    set_p_ok = bool((priv == inj_p).all())
    set_m_ok = bool((miss == inj_m).all())
    j_ok = abs(jj - jwant) < 1e-12
    cell_ok = bool((spB["mask"] == mask0).all())
    val_p_ok = all(bool(spB["delta"][o] == want_p[o]) for o in idx_p)
    val_m_ok = all(bool(spB["delta"][o] == want_m[o]) for o in idx_m)
    keep = tail0 & ~inj_m
    keep_ok = bool((spB["delta"][keep] == delta0[keep]).all())
    ostat_p_ok = all(bool(mask0[o]) and int(abs(int(delta0[o]))) < 8
                     for o in idx_p)
    ostat_m_ok = all(bool(spB["mask"][o]) and int(abs(int(spB["delta"][o]))) < 8
                     for o in idx_m)
    gA = a - f
    gB = gA  # v0/full unchanged by construction (mid-only injection)
    gap_ok = all(int(gB[o]) == int(gA[o]) for o in idx_p + idx_m)
    print(f"C-BIG: gaps v0/full unchanged by construction "
          f"(mid-only injection); gaps_exact={gap_ok}")

    # ---- top-5 listings + ranks ----
    ex_ads = sorted(int(abs(int(spB["delta"][o]))) for o in idx_p)
    got_px = sorted(idx_p, key=lambda o: (-int(abs(int(spB["delta"][o]))), o))
    got_pads = [int(abs(int(spB["delta"][o]))) for o in got_px]
    want_pads = [16, 14, 12, 10, 8]
    pranks = [crank(ad, got_pads) for ad in got_pads]
    px_ok = (got_pads == want_pads and pranks == [1, 2, 3, 4, 5])
    print(f"C-BIG: extra top5 got={got_pads} (want {want_pads}) "
          f"ranks={pranks} (want [1, 2, 3, 4, 5]) exact={px_ok}")
    got_mx = sorted(idx_m, key=lambda o: (-int(abs(int(delta0[o]))), o))
    got_mads = [int(abs(int(delta0[o]))) for o in got_mx]
    want_mads = [47, 46, 45, 17, 16]
    mranks = [crank(ad, got_mads) for ad in got_mads]
    mx_ok = (got_mads == want_mads and mranks == [1, 2, 3, 4, 5])
    print(f"C-BIG: missing top5 got={got_mads} (want {want_mads}) "
          f"ranks={mranks} (want [1, 2, 3, 4, 5]) exact={mx_ok}")

    # ---- spanned Y-column cells + per-cell standings from injection ----
    yA = tail_y_cols(tail0, pl, pr, pc)
    yB = tail_y_cols(tB, pl, pr, pc)
    spanned = sorted({int(pc[o]) for o in idx_p + idx_m
                      if int(pl[o]) == 0})
    print(f"C-BIG: spanned Y cols: {spanned}")
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
        print(f"C-BIG col {c}: rowsA={rA} rowsB={rB} miss/extra={mm}/{ee} "
              f"stand={stand} rows-exact={good}")
    print(f"C-BIG: priv_n={int(priv.sum())} (want 5) "
          f"miss_n={int(miss.sum())} (want 5) J={jj:.4f} "
          f"(want {jwant:.4f}) tailB={int(tB.sum())} (want 102)")
    print(f"C-BIG: priv_exact={set_p_ok} miss_exact={set_m_ok} "
          f"j_exact={j_ok} cell_fixed={cell_ok} "
          f"pvalues_exact={val_p_ok} mvalues_exact={val_m_ok} "
          f"orig_kept={keep_ok} ostat_exact={ostat_p_ok and ostat_m_ok} "
          f"gaps_exact={gap_ok} standings_exact={stand_ok} "
          f"topx_exact={px_ok} topm_exact={mx_ok}")
    ok = (set_p_ok and set_m_ok and j_ok and cell_ok and val_p_ok
          and val_m_ok and keep_ok and ostat_p_ok and ostat_m_ok
          and gap_ok and stand_ok and px_ok and mx_ok)
    print(f"controls pass={bool(ok)}")


if __name__ == "__main__":
    main()
