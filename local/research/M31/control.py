#!/usr/bin/env python3
"""M31 positive controls: synthetic truths with KNOWN boundary extras.

Usage: control.py M16_DIR

Mask-level synthetics (DESIGN.md pinned: mid-level injection is
infeasible at dest columns — M27/M28: privates non-cell/static on
s0; the windowed census operates on tail masks, so the control
builds synthetic tail masks directly from the s0 tail mask with
KNOWN extras at known row distances; windowed standings +
off-span sets must recover exactly per computed K):

- C0 missing-only (d=0 probe): drop c340 r24.
  Known: moved at every computed K, missK=1, no-cand, off-span empty.
- C1 near extra (d=1): add c342 r26.
  Known: exact extra-only 6/5; present + off {(342,26)} at K=0;
  extra-only (6/5), off empty, at K>=1.
- C2 second-ring extra (d=2): add c342 r31.
  Known: exact extra-only 6/5; present + off {(342,31)} at K=0,1;
  extra-only (6/5), off empty, at K>=2.
- C7 boundary extra (d=7): add c296 r41.
  Known: exact extra-only 10/9; present + off {(296,41)} at K=0,1,2;
  extra-only (10/9), off empty, at K>=15.
- C15 upper-grid extra (d=15): add c296 r49.
  Known: exact extra-only 10/9; present + off {(296,49)} at K=0,1,2;
  extra-only (10/9), off empty, at K>=15.
- C234 far extra (d=+234): add c321 r266.
  Known: exact extra-only 11/10; present + off {(321,266)} at EVERY K.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m31 import (KS_RUN, NAMED8, S0_ROWS, census_of_shape,  # noqa: E402
                 interior_sites, load_dump, off_of, offspan_sites,
                 plane_coords, plane_of_byte, priv_y_cols,
                 standing_of_K, synth_w_bytes, tail_bulk_masks,
                 wcensus_of_shape)


def build(t0, drops, adds):
    """Copy t0, clear drop offsets, set add offsets. Returns mask."""
    t = t0.copy()
    for o in drops:
        assert t[o], f"drop o={o} not tail on s0?!"
        t[o] = False
    for o in adds:
        assert not t[o], f"add o={o} already tail on s0 (collision)!"
        t[o] = True
    return t


def colrows_of(t, pl, pr, pc):
    out = {}
    for c in NAMED8:
        idx = np.nonzero(t & (pl == 0) & (pc == c))[0]
        out[c] = sorted(int(pr[o]) for o in idx)
    return out


def check(tag, t, t0, pl, pr, pc, want_exact_moved, want):
    """want: {K: (moved_list, offspan_set, {col: (nK, ovK, standing)})}."""
    colrows = colrows_of(t, pl, pr, pc)
    cen = census_of_shape(colrows)
    moved = sorted(c for c in NAMED8 if cen[c]["pres"] == 0)
    priv = t & ~t0
    pcols = priv_y_cols(priv, pl, pr, pc)
    ok = moved == sorted(want_exact_moved)
    print(f"{tag}: exact moved={moved} (want {sorted(want_exact_moved)}) "
          f"match={moved == sorted(want_exact_moved)}")
    for K in KS_RUN:
        wc = wcensus_of_shape(colrows, K)
        off = offspan_sites(colrows, K)
        wmoved = sorted(c for c in NAMED8 if wc[c]["presK"] == 0)
        wmv, woff, wcols = want[K]
        g = wmoved == sorted(wmv) and off == set(woff)
        for c in wmoved:
            st = standing_of_K(c, wc[c], pcols)
            wn, wo, ws = wcols[c]
            g = g and wc[c]["nK"] == wn and wc[c]["ovK"] == wo and st == ws
        ok = ok and g
        print(f"{tag} K={K}: wmoved={wmoved} (want {sorted(wmv)}) "
              f"offspan={sorted(off)} (want {sorted(woff)}) match={g}")
        for c in wmoved:
            st = standing_of_K(c, wc[c], pcols)
            print(f"{tag} K={K} col {c}: nK={wc[c]['nK']} "
                  f"ovK={wc[c]['ovK']} standing={st} "
                  f"(want {wcols[c]})")
    print(f"{tag}: pass={ok}")
    return ok


def main():
    m16d = Path(sys.argv[1])
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid = load_dump(m16d / "m16-mid-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    synth = synth_w_bytes(v0, full, 0.5)
    sp0 = interior_sites(v0, mid, full, synth)
    mask0, delta0 = sp0["mask"], sp0["delta"]
    t0, _ = tail_bulk_masks(mask0, delta0)
    print(f"baseline s0 cell7 n={sp0['n']} (want 2475) "
          f"tail n={int(t0.sum())} (want 102)")
    pl, (pr, pc) = plane_of_byte(), plane_coords()

    oks = []
    # C0: c340 - r24 (d=0 probe): moved every K, missK=1, no-cand
    t0m = build(t0, [off_of(24, 340)], [])
    oks.append(check("C0", t0m, t0, pl, pr, pc, [340],
                     {K: ([340], set(), {340: (7, 7, "none(no-cand)")})
                      for K in KS_RUN}))
    # C1: c342 + r26 (d=1): off+present K=0; extra-only K>=1
    t1 = build(t0, [], [off_of(26, 342)])
    oks.append(check("C1", t1, t0, pl, pr, pc, [342],
                     {0: ([], {(342, 26)}, {}),
                      **{K: ([342], set(), {342: (6, 5, "none(extra-only)")})
                         for K in (1, 2, 15, 20, 50, 100)}}))
    # C2: c342 + r31 (d=2): off+present K=0,1; extra-only K>=2
    t2 = build(t0, [], [off_of(31, 342)])
    oks.append(check("C2", t2, t0, pl, pr, pc, [342],
                     {0: ([], {(342, 31)}, {}),
                      1: ([], {(342, 31)}, {}),
                      **{K: ([342], set(), {342: (6, 5, "none(extra-only)")})
                         for K in (2, 15, 20, 50, 100)}}))
    # C7: c296 + r41 (d=7): off+present K=0,1,2; extra-only K>=15
    t7 = build(t0, [], [off_of(41, 296)])
    oks.append(check("C7", t7, t0, pl, pr, pc, [296],
                     {0: ([], {(296, 41)}, {}),
                      1: ([], {(296, 41)}, {}),
                      2: ([], {(296, 41)}, {}),
                      **{K: ([296], set(), {296: (10, 9, "none(extra-only)")})
                         for K in (15, 20, 50, 100)}}))
    # C15: c296 + r49 (d=15): off+present K=0,1,2; extra-only K>=15
    t15 = build(t0, [], [off_of(49, 296)])
    oks.append(check("C15", t15, t0, pl, pr, pc, [296],
                     {0: ([], {(296, 49)}, {}),
                      1: ([], {(296, 49)}, {}),
                      2: ([], {(296, 49)}, {}),
                      **{K: ([296], set(), {296: (10, 9, "none(extra-only)")})
                         for K in (15, 20, 50, 100)}}))
    # C234: c321 + r266 (d=+234): off+present every K
    t234 = build(t0, [], [off_of(266, 321)])
    oks.append(check("C234", t234, t0, pl, pr, pc, [321],
                     {K: ([], {(321, 266)}, {}) for K in KS_RUN}))
    print(f"controls pass={all(oks)}")


if __name__ == "__main__":
    main()
