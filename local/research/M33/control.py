#!/usr/bin/env python3
"""M33 positive control: synthetic truth with KNOWN cluster sets.

Usage: control.py M16_DIR

Imports interior_sites + tail core from m33.py (same dir);
expectations are analytic. Shape A = s0 orig, shape B = s0
with injected mid':

- C-CLUS (known cluster sets, mimics shape 9's 22+8): N1=22
  currently-interior-BULK sites with gap>=17 (first 22 in
  offset order), injected mid'=blend+8 on even / blend-8 on
  odd (|d|=8, the tail boundary; per-site strict-interior
  check) AND N2=8 currently-TAIL sites (first 8 in offset
  order), injected mid'=blend+1 (fall back to blend-1 per
  site if +1 is not strictly inside — tabled). The recomputed
  private set P_B = T_B - T_A must equal the injected 22
  exactly, M_B = T_A - T_B must equal the injected 8 exactly,
  J(T_B,T_A) must equal 94/124 = 0.7581 exactly, injected
  values exact, all other tail members' d unchanged, cell-7
  mask fixed.

The estimator must recover the injected counts + sets +
Jaccard + per-site values exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m33 import (interior_sites, jaccard, load_dump,  # noqa: E402
                 plane_coords, synth_w_bytes, tail_bulk_masks)


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
    r, c = plane_coords()

    # ---- priv injections: first-22 offset-order bulk gap>=17 Y ----
    cand_p = [int(o) for o in np.nonzero(
        bulk0 & (gap >= 17) & ((np.arange(len(a)) % 4 == 0)
                               | (np.arange(len(a)) % 4 == 2)))[0]]
    print(f"C-CLUS: pool bulk gap>=17 Y n={len(cand_p)} (want>=22)")
    idx_p, want_p = [], {}
    for o in cand_p:
        dv = 8 if (int(r[o]) + int(c[o])) % 2 == 0 else -8
        mid2 = int(s[o]) + dv
        if int(lo[o]) < mid2 < int(hi[o]):
            idx_p.append(int(o))
            want_p[int(o)] = dv
        if len(idx_p) == 22:
            break
    print(f"C-CLUS: priv inject sites n={len(idx_p)} (want 22) "
          f"rc={[(int(r[o]), int(c[o])) for o in idx_p]}")

    # ---- miss injections: first-8 offset-order tail Y ----
    cand_m = [int(o) for o in np.nonzero(tail0)[0][:8]]
    print(f"C-CLUS: pool tail n={int(tail0.sum())} (want 102); "
          f"miss inject n={len(cand_m)} (want 8)")
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
    print(f"C-CLUS: miss landing +1fb={nfb} "
          f"rc={[(int(r[o]), int(c[o])) for o in idx_m]}")

    assert len(idx_p) == 22 and len(idx_m) == 8
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
    tk2, _ = tail_bulk_masks(sp["mask"], sp["delta"])
    priv = tk2 & ~tail0
    miss = tail0 & ~tk2
    jj = jaccard(tk2, tail0)
    set_p_ok = bool((priv == inj_p).all())
    set_m_ok = bool((miss == inj_m).all())
    j_ok = f"{jj:.4f}" == "0.7581"
    cell_ok = bool((sp["mask"] == mask0).all())
    val_p_ok = all(bool(sp["delta"][o] == want_p[int(o)]) for o in idx_p)
    val_m_ok = all(bool(sp["delta"][o] == want_m[int(o)]) for o in idx_m)
    keep = tail0 & ~inj_m
    keep_ok = bool((sp["delta"][keep] == delta0[keep]).all())
    npos = sum(1 for o in idx_p if want_p[int(o)] > 0)
    ok = (set_p_ok and set_m_ok and j_ok and cell_ok and val_p_ok
          and val_m_ok and keep_ok)
    print(f"C-CLUS: injected priv=22 (+8x{npos}/-8x{22 - npos}) miss=8 "
          f"disjoint={not bool((inj_p & inj_m).any())} "
          f"tailB={int(tk2.sum())} (want 116)")
    print(f"C-CLUS: priv_n={int(priv.sum())} (want 22) "
          f"miss_n={int(miss.sum())} (want 8) J={jj:.4f} (want 0.7581) "
          f"priv_exact={set_p_ok} miss_exact={set_m_ok} j_exact={j_ok} "
          f"cell_fixed={cell_ok} pvalues_exact={val_p_ok} "
          f"mvalues_exact={val_m_ok} orig_kept={keep_ok} pass={ok}")
    print(f"controls pass={bool(ok)}")


if __name__ == "__main__":
    main()
