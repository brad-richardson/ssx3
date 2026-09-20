#!/usr/bin/env python3
"""M37 positive control: synthetic truth with KNOWN 701-mask membership.

Usage: control.py M16_DIR

Imports interior_sites + tail/mask core from m37.py (same dir);
expectations are analytic. Shape A = s0 orig, shape B = s0
with injected mid':

- C-MASK (known mask membership, mimics mask-bound extras):
  N_in=6 currently-interior-BULK Y sites INSIDE the 701 mask
  (offset order, first 6 passing the per-site strict-interior
  check) + N_out=4 same-pool sites OUTSIDE the 701 mask
  (offset order, first 4 passing), injected mid'=blend+8 on
  even (r+c) / blend-8 on odd (|d|=8, the tail boundary).
  The recomputed private set P_B = T_B - T_A must equal the
  injected 10 exactly, M_B = T_A - T_B must be empty exactly,
  membership of P_B vs the 701 mask must read in=6/out=4 on
  the injected sets exactly (per-site in/out exact), per-site
  |d| exact (8), cell-7 mask fixed, all other tail members' d
  unchanged.

The estimator must recover the injected sets + membership
table exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m37 import (compute_dec_masks, interior_sites, jaccard,  # noqa: E402
                 load_dump, load_triplet, plane_coords,
                 plane_of_byte, synth_w_bytes, tail_bulk_masks)


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
    _, _, masks, _ = compute_dec_masks(m16d, mid, synth)
    rm701 = masks[701]
    print(f"baseline 701 mask nrem={int(rm701.sum())} (want 649)")

    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    f = np.frombuffer(full, np.uint8).astype(np.int16)
    lo = np.minimum(a, f)
    hi = np.maximum(a, f)
    pl = plane_of_byte()
    pr, pc = plane_coords()

    def in701(o):
        o = int(o)
        return bool(rm701[int(pr[o]), int(pc[o])])

    # ---- candidate pools: in-mask vs out-of-mask bulk Y (offset order) ----
    isY = (pl == 0)
    cand_in = [int(o) for o in np.nonzero(bulk0 & isY)[0] if in701(o)]
    cand_out = [int(o) for o in np.nonzero(bulk0 & isY)[0] if not in701(o)]
    print(f"C-MASK: pool bulk-Y in-mask n={len(cand_in)} "
          f"out-of-mask n={len(cand_out)}")

    def pick(cands, n):
        idx, want = [], {}
        for o in cands:
            dv = 8 if (int(pr[o]) + int(pc[o])) % 2 == 0 else -8
            mid2 = int(s[o]) + dv
            if int(lo[o]) < mid2 < int(hi[o]):
                idx.append(int(o))
                want[int(o)] = dv
            if len(idx) == n:
                break
        return idx, want

    idx_in, want_in = pick(cand_in, 6)
    idx_out, want_out = pick(cand_out, 4)
    print(f"C-MASK: inject in-sites n={len(idx_in)} (want 6) "
          f"rc={[(int(pr[o]), int(pc[o])) for o in idx_in]}")
    print(f"C-MASK: inject out-sites n={len(idx_out)} (want 4) "
          f"rc={[(int(pr[o]), int(pc[o])) for o in idx_out]}")
    if len(idx_in) != 6 or len(idx_out) != 4:
        print("C-MASK: pool shortfall: tabled RED (cannot inject 6+4).")
        print("controls pass=False")
        return
    assert not (set(idx_in) & set(idx_out)), "inject sets overlap?!"
    idx_all = idx_in + idx_out
    want = {**want_in, **want_out}
    inj = np.zeros(len(a), bool)
    inj[idx_all] = True
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    mid2 = m.copy()
    for o in idx_all:
        mid2[o] = s[o] + want[int(o)]
    sp = interior_sites(v0, mid2.astype(np.uint8).tobytes(), full, synth)
    tk2, _ = tail_bulk_masks(sp["mask"], sp["delta"])
    priv = tk2 & ~tail0
    miss = tail0 & ~tk2
    jj = jaccard(tk2, tail0)
    set_p_ok = bool((priv == inj).all())
    miss_empty_ok = int(miss.sum()) == 0
    in_exact = all(in701(o) for o in idx_in)
    out_exact = all(not in701(o) for o in idx_out)
    npos = sum(1 for o in np.nonzero(priv)[0] if in701(o))
    memb_ok = in_exact and out_exact and npos == 6
    val_ok = all(bool(sp["delta"][o] == want[int(o)]) for o in idx_all)
    cell_ok = bool((sp["mask"] == mask0).all())
    keep = tail0 & ~inj
    keep_ok = bool((sp["delta"][keep] == delta0[keep]).all())
    print(f"C-MASK: priv_n={int(priv.sum())} (want 10) "
          f"miss_n={int(miss.sum())} (want 0) J={jj:.4f} "
          f"membership_in={npos}/10 (want 6)")
    print(f"C-MASK: priv_exact={set_p_ok} miss_empty={miss_empty_ok} "
          f"in_exact={in_exact} out_exact={out_exact} "
          f"values_exact={val_ok} cell_fixed={cell_ok} "
          f"orig_kept={keep_ok}")
    ok = (set_p_ok and miss_empty_ok and memb_ok and val_ok and cell_ok
          and keep_ok)
    print(f"controls pass={bool(ok)}")


if __name__ == "__main__":
    main()
