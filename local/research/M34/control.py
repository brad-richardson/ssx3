#!/usr/bin/env python3
"""M34 positive controls: synthetic truths with KNOWN unnamed moves.

Usage: control.py M16_DIR

Mask-level synthetics (M28 pinned: the census logic under test
operates on tail masks, so the control builds synthetic tail masks
directly from the s0 tail mask with KNOWN moved unnamed columns and
checks exact recovery). Universe = s0-bearing unnamed columns +
the injected fresh columns; target columns derived from the s0
tail at control time (tabled); the KNOWN part is the injected
edit + expected census rows:

- U1 unnamed missing-only partial (mimics 709-c298): drop s0
  c298 rows 28,29, add nothing. Known: moved {298}, delta 2.
- U2 fresh-column extra-only (n0==0 move): add rows 100,101 in
  the first Y column with no s0 tail (tabled). Known: moved
  {that col}, n/ov = 2/0, delta 2, extra-only.
- U3 unnamed full wipe: drop ALL s0 rows of the smallest-n0>0
  unnamed column (tabled). Known: moved {that col}, n/ov =
  0/0, delta = n0, missing-only wipe.
- U4 unnamed mixed: drop 1 s0 row + add 1 fresh row in the
  largest-n0>0 unnamed column (tabled). Known: moved {that
  col}, delta 2, mixed.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m34 import (NAMED8, census_unnamed_of, interior_sites,  # noqa: E402
                 load_dump, off_of, plane_coords, plane_of_byte,
                 synth_w_bytes, tail_bulk_masks, tail_y_cols)


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


def check(tag, t, t0, pl, pr, pc, s0u, want_moved, want_cell):
    """want_cell: {col: (n, ov, pres, miss, extra, delta)}."""
    ycols = tail_y_cols(t, pl, pr, pc)
    cen = census_unnamed_of(ycols, s0u)
    moved = sorted(c for c in s0u if cen[c]["pres"] == 0)
    ok = moved == sorted(want_moved)
    print(f"{tag}: moved={moved} (want {sorted(want_moved)}) "
          f"match={moved == sorted(want_moved)}")
    for c, w in want_cell.items():
        e = cen[c]
        got = (e["n"], e["ov"], e["pres"], e["miss"], e["extra"],
               e["delta"])
        good = got == w
        ok = ok and good
        print(f"{tag} col {c}: n/ov/p/m/e/d={got} (want {w}) "
              f"match={good}")
    # all other universe cols must read present
    others_ok = all(cen[c]["pres"] == 1 for c in s0u
                    if c not in want_moved)
    ok = ok and others_ok
    print(f"{tag}: others-present={others_ok} pass={ok}")
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
    s0y = tail_y_cols(t0, pl, pr, pc)
    bearing = sorted(c for c in s0y if c not in NAMED8)
    print(f"s0-bearing unnamed cols: n={len(bearing)} cols={bearing}")
    assert 298 in bearing, "c298 must be s0-bearing (M29 guard)!"

    # U2 fresh column: first Y col with no s0 tail
    u2col = next(c for c in range(640) if c not in s0y)
    print(f"U2 fresh col: {u2col}")
    s0u = {c: s0y.get(c, []) for c in bearing + [u2col]}

    oks = []
    # U1: c298 drop rows 28,29 (missing-only partial)
    n0_298 = len(s0y[298])
    t1 = build(t0, [off_of(28, 298), off_of(29, 298)], [])
    oks.append(check("U1", t1, t0, pl, pr, pc, s0u, [298],
                     {298: (n0_298 - 2, n0_298 - 2, 0, 2, 0, 2)}))
    # U2: fresh col add rows 100,101 (extra-only, n0==0)
    t2 = build(t0, [], [off_of(100, u2col), off_of(101, u2col)])
    oks.append(check("U2", t2, t0, pl, pr, pc, s0u, [u2col],
                     {u2col: (2, 0, 0, 0, 2, 2)}))
    # U3: wipe smallest-n0>0 unnamed column
    u3col = min(bearing, key=lambda c: (len(s0y[c]), c))
    n0_u3 = len(s0y[u3col])
    print(f"U3 wipe col: {u3col} n0={n0_u3}")
    t3 = build(t0, [off_of(r, u3col) for r in s0y[u3col]], [])
    oks.append(check("U3", t3, t0, pl, pr, pc, s0u, [u3col],
                     {u3col: (0, 0, 0, n0_u3, 0, n0_u3)}))
    # U4: mixed on largest-n0>0 unnamed column (drop first row, add one)
    u4col = min(bearing, key=lambda c: (-len(s0y[c]), c))
    drop_r = s0y[u4col][0]
    add_r = next(r for r in range(448) if r not in s0y[u4col])
    print(f"U4 mixed col: {u4col} n0={len(s0y[u4col])} "
          f"drop={drop_r} add={add_r}")
    t4 = build(t0, [off_of(drop_r, u4col)], [off_of(add_r, u4col)])
    n0_u4 = len(s0y[u4col])
    oks.append(check("U4", t4, t0, pl, pr, pc, s0u, [u4col],
                     {u4col: (n0_u4, n0_u4 - 1, 0, 1, 1, 2)}))
    print(f"controls pass={all(oks)}")


if __name__ == "__main__":
    main()
