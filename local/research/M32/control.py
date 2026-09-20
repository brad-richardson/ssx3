#!/usr/bin/env python3
"""M32 positive controls: synthetic truths with KNOWN far extras.

Usage: control.py M16_DIR

Mask-level synthetics (DESIGN.md pinned: mid-level injection is
infeasible at dest columns — M27/M28: privates non-cell/static on
s0; the windowed census operates on tail masks, so the control
builds synthetic tail masks directly from the s0 tail mask with
KNOWN extras at known row distances; windowed standings +
off-span sets must recover exactly per computed K):

- C0 missing-only (d=0 probe): drop c340 r24.
  Known: moved at every computed K, missK=1, no-cand, off-span empty.
- C232 (c321 + r264, d=232): present + off {(321,264)} at K=1;
  extra-only (11/10), off empty, at K>=233.
- C233 (c321 + r265, d=233): present + off {(321,265)} at K=1;
  extra-only (11/10), off empty, at K>=233.
- C234 (c321 + r266, d=234, the s9 site): present + off {(321,266)}
  at K=1,233; extra-only (11/10), off empty, at K>=234.
- C235 (c321 + r267, d=235): present + off {(321,267)} at K=1,233,234;
  extra-only (11/10), off empty, at K>=366.
- C365 (c296 + r399, d=365): present + off {(296,399)} at K=1,233,234;
  extra-only (10/9), off empty, at K>=366.
- C366 (c296 + r400, d=366, the s22 site): present + off {(296,400)}
  at K=1,233,234; extra-only (10/9), off empty, at K>=366.
- C367 (c296 + r401, d=367, the s22 site): present + off {(296,401)}
  at K=1,233,234,366; extra-only (10/9), off empty, at K=367.
- C368 (c296 + r402, d=368): present + off {(296,402)} at EVERY K.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m32 import (KS_RUN, NAMED8, S0_ROWS, census_of_shape,  # noqa: E402
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
    # C232: c321 + r264 (d=232): off+present K=1; extra-only K>=233
    t232 = build(t0, [], [off_of(264, 321)])
    oks.append(check("C232", t232, t0, pl, pr, pc, [321],
                     {1: ([], {(321, 264)}, {}),
                      **{K: ([321], set(), {321: (11, 10, "none(extra-only)")})
                         for K in (233, 234, 366, 367)}}))
    # C233: c321 + r265 (d=233): off+present K=1; extra-only K>=233
    t233 = build(t0, [], [off_of(265, 321)])
    oks.append(check("C233", t233, t0, pl, pr, pc, [321],
                     {1: ([], {(321, 265)}, {}),
                      **{K: ([321], set(), {321: (11, 10, "none(extra-only)")})
                         for K in (233, 234, 366, 367)}}))
    # C234: c321 + r266 (d=234): off+present K=1,233; extra-only K>=234
    t234 = build(t0, [], [off_of(266, 321)])
    oks.append(check("C234", t234, t0, pl, pr, pc, [321],
                     {1: ([], {(321, 266)}, {}),
                      233: ([], {(321, 266)}, {}),
                      **{K: ([321], set(), {321: (11, 10, "none(extra-only)")})
                         for K in (234, 366, 367)}}))
    # C235: c321 + r267 (d=235): off+present K=1,233,234; extra-only K>=366
    t235 = build(t0, [], [off_of(267, 321)])
    oks.append(check("C235", t235, t0, pl, pr, pc, [321],
                     {1: ([], {(321, 267)}, {}),
                      233: ([], {(321, 267)}, {}),
                      234: ([], {(321, 267)}, {}),
                      **{K: ([321], set(), {321: (11, 10, "none(extra-only)")})
                         for K in (366, 367)}}))
    # C365: c296 + r399 (d=365): off+present K=1,233,234; extra-only K>=366
    t365 = build(t0, [], [off_of(399, 296)])
    oks.append(check("C365", t365, t0, pl, pr, pc, [296],
                     {1: ([], {(296, 399)}, {}),
                      233: ([], {(296, 399)}, {}),
                      234: ([], {(296, 399)}, {}),
                      **{K: ([296], set(), {296: (10, 9, "none(extra-only)")})
                         for K in (366, 367)}}))
    # C366: c296 + r400 (d=366): off+present K=1,233,234; extra-only K>=366
    t366 = build(t0, [], [off_of(400, 296)])
    oks.append(check("C366", t366, t0, pl, pr, pc, [296],
                     {1: ([], {(296, 400)}, {}),
                      233: ([], {(296, 400)}, {}),
                      234: ([], {(296, 400)}, {}),
                      **{K: ([296], set(), {296: (10, 9, "none(extra-only)")})
                         for K in (366, 367)}}))
    # C367: c296 + r401 (d=367): off+present K=1,233,234,366; extra-only K=367
    t367 = build(t0, [], [off_of(401, 296)])
    oks.append(check("C367", t367, t0, pl, pr, pc, [296],
                     {1: ([], {(296, 401)}, {}),
                      233: ([], {(296, 401)}, {}),
                      234: ([], {(296, 401)}, {}),
                      366: ([], {(296, 401)}, {}),
                      367: ([296], set(), {296: (10, 9, "none(extra-only)")})}))
    # C368: c296 + r402 (d=368): off+present every K
    t368 = build(t0, [], [off_of(402, 296)])
    oks.append(check("C368", t368, t0, pl, pr, pc, [296],
                     {K: ([], {(296, 402)}, {}) for K in KS_RUN}))
    print(f"controls pass={all(oks)}")


if __name__ == "__main__":
    main()
