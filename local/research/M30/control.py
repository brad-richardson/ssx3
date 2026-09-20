#!/usr/bin/env python3
"""M30 positive controls: synthetic truths with KNOWN far extras.

Usage: control.py M16_DIR

Mask-level synthetics (DESIGN.md pinned: mid-level injection is
infeasible at dest columns — M27/M28: privates non-cell/static on
s0; the windowed census operates on tail masks, so the control
builds synthetic tail masks directly from the s0 tail mask with
KNOWN extras at known row distances; windowed standings +
off-span sets must recover exactly per K):

- W1 far extra (mimics s9): add c321 r266 (d=+234).
  Known: exact 11/10 extra-only; windowed pres=1 + off-span
  {(321,266)} at EVERY K.
- W2 far pair (mimics s22): add c296 r400+r401 (d=+366/+367).
  Known: exact 11/9 extra-only; windowed pres=1 + off-span
  {(296,400),(296,401)} at EVERY K.
- W3 boundary extra: add c296 r41 (d=+7 from max 34).
  Known: off-span + windowed-present at K=2,5; in-window
  extra-only (nK/ovK 10/9), off-span empty, at K=10.
- W4 near extra (mimics s734): add c342 r26 (d=1).
  Known: extra-only (nK/ovK 6/5), off-span empty, at EVERY K.
- W5 missing-only (mimics s710): drop c340 r24.
  Known: moved at every K, missK=1, no-cand, off-span empty.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m30 import (KS, NAMED8, S0_ROWS, census_of_shape,  # noqa: E402
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
    for K in KS:
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
    # W1: c321 + r266 (d=+234): exact extra-only; off-span every K
    t1 = build(t0, [], [off_of(266, 321)])
    oks.append(check("W1", t1, t0, pl, pr, pc, [321],
                     {K: ([], {(321, 266)}, {}) for K in KS}))
    # W2: c296 + r400+r401 (d=+366/+367): exact extra-only; off every K
    t2 = build(t0, [], [off_of(400, 296), off_of(401, 296)])
    oks.append(check("W2", t2, t0, pl, pr, pc, [296],
                     {K: ([], {(296, 400), (296, 401)}, {}) for K in KS}))
    # W3: c296 + r41 (d=+7): off-span K=2,5; extra-only K=10
    t3 = build(t0, [], [off_of(41, 296)])
    oks.append(check("W3", t3, t0, pl, pr, pc, [296],
                     {2: ([], {(296, 41)}, {}),
                      5: ([], {(296, 41)}, {}),
                      10: ([296], set(), {296: (10, 9, "none(extra-only)" )})}))
    # W4: c342 + r26 (d=1): extra-only every K, off-span empty
    t4 = build(t0, [], [off_of(26, 342)])
    oks.append(check("W4", t4, t0, pl, pr, pc, [342],
                     {K: ([342], set(), {342: (6, 5, "none(extra-only)")})
                      for K in KS}))
    # W5: c340 - r24: moved every K, missK=1, no-cand, off-span empty
    t5 = build(t0, [off_of(24, 340)], [])
    oks.append(check("W5", t5, t0, pl, pr, pc, [340],
                     {K: ([340], set(), {340: (7, 7, "none(no-cand)")})
                      for K in KS}))
    print(f"controls pass={all(oks)}")


if __name__ == "__main__":
    main()
