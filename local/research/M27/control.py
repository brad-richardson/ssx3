#!/usr/bin/env python3
"""M27 positive controls: synthetic truths with KNOWN private/missing sites.

Usage: control.py M16_DIR

Imports interior_sites + tail core from m27.py (same dir); expectations
are analytic. Shape A = s0 orig, shape B = s0 with injected mid':

- C-P1 (known privates): N=20 interior-BULK sites with gap>=17 (first
  20 in offset order), injected mid'=blend+8 on even / blend-8 on odd
  (|d|=8, the tail boundary; per-site strict-interior check). The
  recomputed private set P_B = T_B - T_A must equal the injected set
  exactly, M_B empty, J(T_B,T_A) = 102/122 = 0.8361 exactly, original
  tail members' d unchanged, injected values exact.
- C-P2 (known missings): N=20 TAIL sites (first 20 in offset order),
  injected mid''=blend+1 (fall back to blend-1 per site if +1 is not
  strictly inside — tabled). The recomputed missing set M_B = T_A - T_B
  must equal the injected set exactly, P_B empty, J(T_B,T_A) = 82/102
  = 0.8039 exactly, all other tail members' d unchanged.

The estimator must recover each injected count + sets + Jaccard exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m27 import (interior_sites, jaccard, load_dump,  # noqa: E402
                 plane_coords, synth_w_bytes, tail_bulk_masks)


def run_known_privates(v0, mid, full, synth, mask0, tail0, delta0, tag):
    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    b = np.frombuffer(full, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)
    gap = np.abs(a - b)
    _, bulk0 = tail_bulk_masks(mask0, delta0)
    r, c = plane_coords()
    cand = np.nonzero(bulk0 & (gap >= 17))[0]
    print(f"{tag}: pool bulk gap>=17 n={len(cand)} (want>=20)")
    idx, wantv = [], {}
    for o in cand:
        dv = 8 if (int(r[o]) + int(c[o])) % 2 == 0 else -8
        mid2 = int(s[o]) + dv
        if int(lo[o]) < mid2 < int(hi[o]):
            idx.append(int(o))
            wantv[int(o)] = dv
        if len(idx) == 20:
            break
    idx = np.array(idx, dtype=np.int64)
    inj = np.zeros(len(a), bool)
    inj[idx] = True
    mid2 = m.copy()
    for o in idx:
        mid2[o] = s[o] + wantv[int(o)]
    sp = interior_sites(v0, mid2.astype(np.uint8).tobytes(), full, synth)
    tk2, _ = tail_bulk_masks(sp["mask"], sp["delta"])
    priv = tk2 & ~tail0
    miss = tail0 & ~tk2
    jj = jaccard(tk2, tail0)
    set_ok = bool((priv == inj).all()) and int(miss.sum()) == 0
    j_ok = f"{jj:.4f}" == "0.8361"
    cell_ok = bool((sp["mask"] == mask0).all())  # bulk->tail: cell fixed
    val_ok = all(bool(sp["delta"][o] == wantv[int(o)]) for o in idx)
    keep_ok = bool((sp["delta"][tail0] == delta0[tail0]).all())
    npos = sum(1 for o in idx if wantv[int(o)] > 0)
    ok = (set_ok and j_ok and cell_ok and val_ok and keep_ok
          and len(idx) == 20 and not bool((tail0 & inj).any()))
    print(f"{tag}: injected={len(idx)} (+8x{npos}/-8x{len(idx) - npos}) "
          f"disjoint={not bool((tail0 & inj).any())} "
          f"priv_n={int(priv.sum())} (want 20) miss_n={int(miss.sum())} "
          f"(want 0) J={jj:.4f} (want 0.8361) set_exact={set_ok} "
          f"j_exact={j_ok} cell_fixed={cell_ok} values_exact={val_ok} "
          f"orig_kept={keep_ok} pass={ok}")
    return ok


def run_known_missings(v0, mid, full, synth, mask0, tail0, delta0, tag):
    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    b = np.frombuffer(full, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)
    cand = np.nonzero(tail0)[0]
    print(f"{tag}: pool tail n={len(cand)} (want 102)")
    idx, wantv = [], {}
    nfb = 0
    for o in cand:
        for dv in (1, -1):
            mid2 = int(s[o]) + dv
            if int(lo[o]) < mid2 < int(hi[o]):
                idx.append(int(o))
                wantv[int(o)] = dv
                nfb += int(dv == -1)
                break
        if len(idx) == 20:
            break
    idx = np.array(idx, dtype=np.int64)
    inj = np.zeros(len(a), bool)
    inj[idx] = True
    mid2 = m.copy()
    for o in idx:
        mid2[o] = s[o] + wantv[int(o)]
    sp = interior_sites(v0, mid2.astype(np.uint8).tobytes(), full, synth)
    tk2, _ = tail_bulk_masks(sp["mask"], sp["delta"])
    priv = tk2 & ~tail0
    miss = tail0 & ~tk2
    jj = jaccard(tk2, tail0)
    set_ok = bool((miss == inj).all()) and int(priv.sum()) == 0
    j_ok = f"{jj:.4f}" == "0.8039"
    cell_ok = bool((sp["mask"] == mask0).all())  # tail->bulk: cell fixed
    val_ok = all(bool(sp["delta"][o] == wantv[int(o)]) for o in idx)
    keep = tail0 & ~inj
    keep_ok = bool((sp["delta"][keep] == delta0[keep]).all())
    ok = (set_ok and j_ok and cell_ok and val_ok and keep_ok
          and len(idx) == 20)
    print(f"{tag}: injected={len(idx)} (+1fb={nfb}) "
          f"miss_n={int(miss.sum())} (want 20) priv_n={int(priv.sum())} "
          f"(want 0) J={jj:.4f} (want 0.8039) set_exact={set_ok} "
          f"j_exact={j_ok} cell_fixed={cell_ok} values_exact={val_ok} "
          f"orig_kept={keep_ok} pass={ok}")
    return ok


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

    ok1 = run_known_privates(v0, mid, full, synth, mask0, tail0, delta0,
                             "C-P1")
    ok2 = run_known_missings(v0, mid, full, synth, mask0, tail0, delta0,
                             "C-P2")
    print(f"controls pass={bool(ok1 and ok2)}")


if __name__ == "__main__":
    main()
