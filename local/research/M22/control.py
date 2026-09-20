#!/usr/bin/env python3
"""M22 positive controls: synthetic truths with KNOWN tail injections.

Usage: control.py M16_DIR

Imports interior_sites + tail core from m22.py (same dir); expectations
are analytic. Rev 2 (control-feasibility fix; see REPORT.md defect
note): rev 1 assumed bulk sites with gap>=50/32 were plentiful enough
for N=60 +-20/cycled injections, but large gaps live almost entirely
on the tail itself (bulk gap>=50: 2 sites; gap>=32: 7). Rev 2 uses
pools the dumps actually have:

- C-T1: checker +-8 (|d|=8, the tail boundary) on N=60 bulk sites
  with gap>=17 (248 candidates; per-site strict-interior check).
- C-T2: cycled [+8,-12,+15] on N=60 ENDPOINT sites (moved, mid at an
  endpoint, currently not cell 7) with gap>=32 (90 candidates;
  per-site strict-interior check) — endpoint-to-interior transition
  into the tail.

The estimator must recover each injected count + values + map exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m22 import (interior_sites, load_dump, plane_coords,  # noqa: E402
                 synth_w_bytes, tail_bulk_masks)


def run_checker_bulk(v0, mid, full, synth, mask0, tail0, delta0, tag):
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
    idx, wantv = [], {}
    for o in cand:
        dv = 8 if (int(r[o]) + int(c[o])) % 2 == 0 else -8
        mid2 = int(s[o]) + dv
        if int(lo[o]) < mid2 < int(hi[o]):
            idx.append(int(o))
            wantv[int(o)] = dv
        if len(idx) == 60:
            break
    idx = np.array(idx, dtype=np.int64)
    inj = np.zeros(len(a), bool)
    inj[idx] = True
    mid2 = m.copy()
    for o in idx:
        mid2[o] = s[o] + wantv[int(o)]
    sp = interior_sites(v0, mid2.astype(np.uint8).tobytes(), full, synth)
    tk2, _ = tail_bulk_masks(sp["mask"], sp["delta"])
    want = tail0 | inj
    set_ok = bool((tk2 == want).all())
    cell_ok = bool((sp["mask"] == mask0).all())  # bulk->tail: cell set fixed
    val_ok = all(bool(sp["delta"][o] == wantv[int(o)]) for o in idx)
    keep_ok = bool((sp["delta"][tail0] == delta0[tail0]).all())
    npos = sum(1 for o in idx if wantv[int(o)] > 0)
    ok = (set_ok and cell_ok and val_ok and keep_ok and len(idx) == 60
          and not bool((tail0 & inj).any()))
    print(f"{tag}: injected={len(idx)} (+8x{npos}/-8x{len(idx) - npos}) "
          f"disjoint={not bool((tail0 & inj).any())} "
          f"recovered_n={int(tk2.sum())} (want {int(want.sum())}) "
          f"set_exact={set_ok} cell_fixed={cell_ok} values_exact={val_ok} "
          f"orig_kept={keep_ok} pass={ok}")
    return ok


def run_cycled_endpoint(v0, mid, full, synth, mask0, tail0, delta0, tag):
    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    b = np.frombuffer(full, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)
    gap = np.abs(a - b)
    endpoint = (a != b) & ((m == lo) | (m == hi)) & (~mask0)
    cyc = [8, -12, 15]
    cand = np.nonzero(endpoint & (gap >= 32))[0]
    idx, wantv = [], {}
    k = 0
    for o in cand:
        dv = cyc[k % 3]
        mid2 = int(s[o]) + dv
        if int(lo[o]) < mid2 < int(hi[o]):
            idx.append(int(o))
            wantv[int(o)] = dv
            k += 1
        if len(idx) == 60:
            break
    idx = np.array(idx, dtype=np.int64)
    inj = np.zeros(len(a), bool)
    inj[idx] = True
    mid2 = m.copy()
    for o in idx:
        mid2[o] = s[o] + wantv[int(o)]
    sp = interior_sites(v0, mid2.astype(np.uint8).tobytes(), full, synth)
    tk2, _ = tail_bulk_masks(sp["mask"], sp["delta"])
    want = tail0 | inj
    want_cell = mask0 | inj
    set_ok = bool((tk2 == want).all())
    cell_ok = bool((sp["mask"] == want_cell).all())
    val_ok = all(bool(sp["delta"][o] == wantv[int(o)]) for o in idx)
    keep_ok = bool((sp["delta"][tail0] == delta0[tail0]).all())
    got = [int((sp["delta"][inj] == v).sum()) for v in cyc]
    ok = (set_ok and cell_ok and val_ok and keep_ok and len(idx) == 60
          and not bool((mask0 & inj).any()))
    print(f"{tag}: injected={len(idx)} (+8x{got[0]}/-12x{got[1]}/+15x{got[2]}) "
          f"disjoint_from_cell={not bool((mask0 & inj).any())} "
          f"recovered_n={int(tk2.sum())} (want {int(want.sum())}) "
          f"set_exact={set_ok} cell_exact={cell_ok} values_exact={val_ok} "
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

    ok1 = run_checker_bulk(v0, mid, full, synth, mask0, tail0, delta0, "C-T1")
    ok2 = run_cycled_endpoint(v0, mid, full, synth, mask0, tail0, delta0, "C-T2")
    print(f"controls pass={bool(ok1 and ok2)}")


if __name__ == "__main__":
    main()
