#!/usr/bin/env python3
"""M46 positive control: synthetic truth with KNOWN far/near blocks.

Usage: control.py M16_DIR

Imports cell/tail/core from m46.py (same dir); expectations are
analytic. Shape A = s0 orig, shape B = s0 with injected mid':

- C-SPLIT (known far/near blocks, mimics the 16+6 split at small
  N): N_far=6 far-dmin + N_near=6 near-dmin
  currently-interior-BULK sites with gap>=17 (offset order),
  injected mid'=blend+8 on even (r+c) / blend-8 on odd (|d|=8,
  the tail boundary; per-site strict-interior check; far =
  dmin>=18 vs the post-miss shared set, near = dmin<=7) AND
  N_miss=4 currently-TAIL sites (first 4 in offset order),
  injected mid'=blend+1 (fall back to blend-1 per site if +1 is
  not strictly inside — tabled). The recomputed private set P_B
  = T_B - T_A must equal the injected 12 exactly, M_B = T_A -
  T_B must equal the injected 4 exactly, J(T_B,T_A) must equal
  98/114 = 0.8596 exactly (inter 102-4, union 102+12 per the
  M33 union rule), injected values exact, dmin ranges exact
  (far >=18, near <=7), per-block seat counts sum-exact,
  cell-7 mask fixed.

The estimator must recover the injected counts + sets + Jaccard
+ dmins + per-site values + seat sums exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m46 import (ROW_BAND, interior_sites, jaccard, load_dump,  # noqa: E402
                 p1_gradient, plane_coords, split_planes,
                 synth_w_bytes, tail_bulk_masks)


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
    pl = (np.arange(len(a)) % 4)
    isY = (pl == 0) | (pl == 2)
    r, c = plane_coords()

    # ---- miss injections: first-4 offset-order tail ----
    cand_m = [int(o) for o in np.nonzero(tail0)[0][:4]]
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
    print(f"C-SPLIT: miss inject n={len(idx_m)} (want 4) +1fb={nfb} "
          f"rc={[(int(r[o]), int(c[o])) for o in idx_m]}")
    assert len(idx_m) == 4
    inj_m = np.zeros(len(a), bool)
    inj_m[idx_m] = True
    shared_post = tail0 & ~inj_m

    # ---- priv candidates: offset-order bulk gap>=17 Y ----
    cand_p = [int(o) for o in np.nonzero(
        bulk0 & (gap >= 17) & isY)[0]]
    print(f"C-SPLIT: pool bulk gap>=17 Y n={len(cand_p)}")
    shr_y = np.nonzero(shared_post & isY)[0]
    shr_r = r[shr_y].astype(np.int32)
    shr_c = c[shr_y].astype(np.int32)

    def dmin_vs_shared(o):
        return int((np.abs(shr_r - int(r[o]))
                    + np.abs(shr_c - int(c[o]))).min())

    idx_far, want_far, d_far = [], {}, {}
    idx_near, want_near, d_near = [], {}, {}
    for o in cand_p:
        dv = 8 if (int(r[o]) + int(c[o])) % 2 == 0 else -8
        mid2 = int(s[o]) + dv
        if not (int(lo[o]) < mid2 < int(hi[o])):
            continue
        d = dmin_vs_shared(o)
        if d >= 18 and len(idx_far) < 6:
            idx_far.append(int(o))
            want_far[int(o)] = dv
            d_far[int(o)] = d
        elif d <= 7 and len(idx_near) < 6:
            idx_near.append(int(o))
            want_near[int(o)] = dv
            d_near[int(o)] = d
        if len(idx_far) == 6 and len(idx_near) == 6:
            break
    print(f"C-SPLIT: far inject n={len(idx_far)} (want 6) "
          f"dmins={sorted(d_far.values())} "
          f"rc={[(int(r[o]), int(c[o])) for o in idx_far]}")
    print(f"C-SPLIT: near inject n={len(idx_near)} (want 6) "
          f"dmins={sorted(d_near.values())} "
          f"rc={[(int(r[o]), int(c[o])) for o in idx_near]}")
    assert len(idx_far) == 6 and len(idx_near) == 6
    assert not (set(idx_far) & set(idx_near) | set(idx_far) & set(idx_m)
                | set(idx_near) & set(idx_m)), "inject sets overlap?!"
    inj_far = np.zeros(len(a), bool)
    inj_far[idx_far] = True
    inj_near = np.zeros(len(a), bool)
    inj_near[idx_near] = True
    inj_p = inj_far | inj_near
    want_p = dict(want_far)
    want_p.update(want_near)

    mid2 = m.copy()
    for o in idx_far + idx_near:
        mid2[o] = s[o] + want_p[int(o)]
    for o in idx_m:
        mid2[o] = s[o] + want_m[int(o)]
    sp = interior_sites(v0, mid2.astype(np.uint8).tobytes(), full, synth)
    tk2, _ = tail_bulk_masks(sp["mask"], sp["delta"])
    priv = tk2 & ~tail0
    miss = tail0 & ~tk2
    jj = jaccard(tk2, tail0)
    set_p_ok = bool((priv == inj_p).all())
    set_m_ok = bool((miss == inj_m).all())
    set_f_ok = bool(((priv & inj_far) == inj_far).all()
                    and int((priv & inj_far).sum()) == 6)
    set_q_ok = bool(((priv & inj_near) == inj_near).all()
                    and int((priv & inj_near).sum()) == 6)
    j_ok = f"{jj:.4f}" == "0.8596"
    cell_ok = bool((sp["mask"] == mask0).all())
    val_p_ok = all(bool(sp["delta"][o] == want_p[int(o)])
                   for o in idx_far + idx_near)
    val_m_ok = all(bool(sp["delta"][o] == want_m[int(o)]) for o in idx_m)
    keep = tail0 & ~inj_m
    keep_ok = bool((sp["delta"][keep] == delta0[keep]).all())
    # dmin ranges recomputed vs the recomputed shared set
    shared2 = tk2 & tail0
    shr2 = np.nonzero(shared2)[0]
    sr2 = r[shr2].astype(np.int32)
    sc2 = c[shr2].astype(np.int32)

    def dmin2(o):
        return int((np.abs(sr2 - int(r[o]))
                    + np.abs(sc2 - int(c[o]))).min())

    df2 = sorted(dmin2(o) for o in idx_far)
    dq2 = sorted(dmin2(o) for o in idx_near)
    dm2 = sorted(dmin2(o) for o in idx_m)
    dmin_ok = (all(d >= 18 for d in df2) and all(d <= 7 for d in dq2))
    print(f"C-SPLIT: recomputed far dmins={df2} (want all>=18) "
          f"near dmins={dq2} (want all<=7) miss dmins={dm2}")
    # seat sums per block (s0-anchored band + P1 decile)
    ym0 = split_planes(np.frombuffer(mid, np.uint8))[0]
    _, _, dec = p1_gradient(ym0)
    fb = [sum(1 for o in idx_far if int(ROW_BAND[int(r[o])]) == bi)
          for bi in range(3)]
    qb = [sum(1 for o in idx_near if int(ROW_BAND[int(r[o])]) == bi)
          for bi in range(3)]
    fd = [sum(1 for o in idx_far if int(dec[int(r[o]), int(c[o])]) == dci)
          for dci in range(10)]
    qd = [sum(1 for o in idx_near if int(dec[int(r[o]), int(c[o])]) == dci)
          for dci in range(10)]
    seat_ok = (sum(fb) == 6 and sum(qb) == 6 and sum(fd) == 6
               and sum(qd) == 6)
    print(f"C-SPLIT: far seats band={fb} dec={fd} (sums 6/6)")
    print(f"C-SPLIT: near seats band={qb} dec={qd} (sums 6/6)")
    npos = sum(1 for o in idx_far + idx_near if want_p[int(o)] > 0)
    ok = (set_p_ok and set_m_ok and set_f_ok and set_q_ok and j_ok
          and cell_ok and val_p_ok and val_m_ok and keep_ok and dmin_ok
          and seat_ok)
    print(f"C-SPLIT: injected priv=12 (far6+near6, +8x{npos}/-8x{12 - npos}) "
          f"miss=4 tailB={int(tk2.sum())} (want 110)")
    print(f"C-SPLIT: priv_n={int(priv.sum())} (want 12) "
          f"miss_n={int(miss.sum())} (want 4) J={jj:.4f} (want 0.8596) "
          f"priv_exact={set_p_ok} far_exact={set_f_ok} "
          f"near_exact={set_q_ok} miss_exact={set_m_ok} j_exact={j_ok} "
          f"cell_fixed={cell_ok} pvalues_exact={val_p_ok} "
          f"mvalues_exact={val_m_ok} orig_kept={keep_ok} "
          f"dminrange_exact={dmin_ok} seats_sum={seat_ok} pass={ok}")
    print(f"controls pass={bool(ok)}")


if __name__ == "__main__":
    main()
