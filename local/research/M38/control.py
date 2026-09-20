#!/usr/bin/env python3
"""M38 positive control: synthetic truth with KNOWN shared missing sites.

Usage: control.py M16_DIR

Imports interior_sites + tail core from m38.py (same dir);
expectations are analytic. Shape A = s0 orig, shapes B/C = s0
with injected mid':

- C-SHARED (known shared sites, mimics the shared-missing
  triple): N_both=3 currently-TAIL Y sites (offset order,
  first 3 passing the per-site strict-interior landing check)
  injected on BOTH B and C (shared-missing, all-shapes style)
  + N_B=2 further tail sites injected on B only + N_C=2
  further tail sites injected on C only, each mid'=blend+1
  (fall back to blend-1 per site if +1 is not strictly
  inside -- tabled). Recompute cell 7 + tail on B and C:
  M_B = T_A - T_B must equal the injected 5 exactly,
  M_C = T_A - T_C must equal the injected 5 exactly,
  M_B ∩ M_C must equal the injected shared 3 exactly,
  per-site |d| exact (1), gaps equal on all three frames at
  every injected site (v0/full unchanged -- the known gaps
  recovered), the per-site per-shape table (status on B x
  status on C + gaps) recovered exactly, cell-7 masks fixed
  on both, all other tail members' d unchanged.

The estimator must recover the injected sets + shared table
exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m38 import (interior_sites, jaccard, load_dump,  # noqa: E402
                 plane_coords, plane_of_byte, synth_w_bytes,
                 tail_bulk_masks)


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
    lo = np.minimum(a, f)
    hi = np.maximum(a, f)
    pl = plane_of_byte()
    pr, pc = plane_coords()

    # ---- candidate pool: currently-TAIL Y sites (offset order) ----
    cand = [int(o) for o in np.nonzero(tail0 & (pl == 0))[0]]
    print(f"C-SHARED: pool tail-Y n={len(cand)}")

    def pick(cands, skip, n):
        idx, want = [], {}
        for o in cands:
            if o in skip:
                continue
            if int(lo[o]) < int(s[o]) + 1 < int(hi[o]):
                dv = 1
            elif int(lo[o]) < int(s[o]) - 1 < int(hi[o]):
                dv = -1
            else:
                continue
            idx.append(int(o))
            want[int(o)] = dv
            if len(idx) == n:
                break
        return idx, want

    used = set()
    idx_both, w_both = pick(cand, used, 3)
    used |= set(idx_both)
    idx_b, w_b = pick(cand, used, 2)
    used |= set(idx_b)
    idx_c, w_c = pick(cand, used, 2)
    used |= set(idx_c)
    print(f"C-SHARED: inject shared n={len(idx_both)} (want 3) "
          f"rc={[(int(pr[o]), int(pc[o])) for o in idx_both]} "
          f"dv={[w_both[o] for o in idx_both]}")
    print(f"C-SHARED: inject B-only n={len(idx_b)} (want 2) "
          f"rc={[(int(pr[o]), int(pc[o])) for o in idx_b]} "
          f"dv={[w_b[o] for o in idx_b]}")
    print(f"C-SHARED: inject C-only n={len(idx_c)} (want 2) "
          f"rc={[(int(pr[o]), int(pc[o])) for o in idx_c]} "
          f"dv={[w_c[o] for o in idx_c]}")
    if len(idx_both) != 3 or len(idx_b) != 2 or len(idx_c) != 2:
        print("C-SHARED: pool shortfall: tabled RED (cannot inject 3+2+2).")
        print("controls pass=False")
        return
    assert len(used) == 7, "inject sets overlap?!"
    injB = set(idx_both) | set(idx_b)
    injC = set(idx_both) | set(idx_c)
    wantB = {**w_both, **w_b}
    wantC = {**w_both, **w_c}
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    midB = m.copy()
    for o in injB:
        midB[o] = s[o] + wantB[int(o)]
    midC = m.copy()
    for o in injC:
        midC[o] = s[o] + wantC[int(o)]
    spB = interior_sites(v0, midB.astype(np.uint8).tobytes(), full, synth)
    spC = interior_sites(v0, midC.astype(np.uint8).tobytes(), full, synth)
    tB, _ = tail_bulk_masks(spB["mask"], spB["delta"])
    tC, _ = tail_bulk_masks(spC["mask"], spC["delta"])
    mB = tail0 & ~tB
    mC = tail0 & ~tC
    pB = tB & ~tail0
    pC = tC & ~tail0
    jjB = jaccard(tB, tail0)
    jjC = jaccard(tC, tail0)
    expB = np.zeros(len(a), bool)
    expB[list(injB)] = True
    expC = np.zeros(len(a), bool)
    expC[list(injC)] = True
    setB_ok = bool((mB == expB).all())
    setC_ok = bool((mC == expC).all())
    priv_empty_ok = int(pB.sum()) == 0 and int(pC.sum()) == 0
    inter = mB & mC
    expI = np.zeros(len(a), bool)
    expI[idx_both] = True
    inter_ok = bool((inter == expI).all())
    jwant = 97 / 102
    j_ok = abs(jjB - jwant) < 1e-12 and abs(jjC - jwant) < 1e-12
    valB_ok = all(bool(spB["delta"][o] == wantB[int(o)]) for o in injB)
    valC_ok = all(bool(spC["delta"][o] == wantC[int(o)]) for o in injC)
    # known gaps: B/C share v0/full bytes with A; recompute gB/gC
    # from the B/C frame bytes and check against the known gA values
    vB, fB = bytes(v0), bytes(full)
    vC, fC = bytes(v0), bytes(full)
    gB = (np.frombuffer(vB, np.uint8).astype(np.int16)
          - np.frombuffer(fB, np.uint8).astype(np.int16))
    gC = (np.frombuffer(vC, np.uint8).astype(np.int16)
          - np.frombuffer(fC, np.uint8).astype(np.int16))
    want_gaps = {int(o): int(gA[o]) for o in used}
    gap_ok = all(int(gB[o]) == want_gaps[int(o)]
                 and int(gC[o]) == want_gaps[int(o)] for o in used)
    tab_ok = True
    for o in sorted(used):
        stB = "missing" if int(o) in injB else "tail"
        stC = "missing" if int(o) in injC else "tail"
        gotB = "missing" if (bool(tail0[o]) and not bool(tB[o])) else (
            "tail" if bool(tB[o]) else "OTHER")
        gotC = "missing" if (bool(tail0[o]) and not bool(tC[o])) else (
            "tail" if bool(tC[o]) else "OTHER")
        good = (gotB == stB and gotC == stC)
        tab_ok = tab_ok and good
        print(f"C-SHARED site rc=({int(pr[o])},{int(pc[o])}) "
              f"B={gotB} (want {stB}) C={gotC} (want {stC}) "
              f"gA={int(gA[o])} gB={int(gB[o])} gC={int(gC[o])} "
              f"match={good}")
    cell_ok = bool((spB["mask"] == mask0).all()) and bool(
        (spC["mask"] == mask0).all())
    keep = tail0.copy()
    keep[list(used)] = False
    keep_ok = bool((spB["delta"][keep] == delta0[keep]).all()) and bool(
        (spC["delta"][keep] == delta0[keep]).all())
    print(f"C-SHARED: missB_n={int(mB.sum())} (want 5) "
          f"missC_n={int(mC.sum())} (want 5) "
          f"inter_n={int(inter.sum())} (want 3) "
          f"privB={int(pB.sum())} privC={int(pC.sum())} (want 0/0) "
          f"JB={jjB:.4f} JC={jjC:.4f} (want {jwant:.4f})")
    print(f"C-SHARED: setB_exact={setB_ok} setC_exact={setC_ok} "
          f"priv_empty={priv_empty_ok} inter_exact={inter_ok} "
          f"j_exact={j_ok} values_exact={valB_ok and valC_ok} "
          f"gaps_exact={gap_ok} table_exact={tab_ok} "
          f"cell_fixed={cell_ok} orig_kept={keep_ok}")
    ok = (setB_ok and setC_ok and priv_empty_ok and inter_ok and j_ok
          and valB_ok and valC_ok and gap_ok and tab_ok and cell_ok
          and keep_ok)
    print(f"controls pass={bool(ok)}")


if __name__ == "__main__":
    main()
