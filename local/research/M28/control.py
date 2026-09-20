#!/usr/bin/env python3
"""M28 positive controls: synthetic truths with KNOWN moved columns.

Usage: control.py M16_DIR

Mask-level synthetics (DESIGN.md pinned: mid-level injection is
infeasible at the true dest columns — M27 reads 733/731 privates
non-cell on s0, mostly static with gap 0, so no mid edit can make
them cell-7). Each synthetic is a tail mask derived from the s0
tail mask with a KNOWN moved-column set; census + displacement
must recover it exactly:

- S1 single move: drop s0 c301 rows, add c303 rows 25-33.
  Known: moved {301}, dest 303, off +2.
- S2 pair move: drop s0 c257+c277 rows 23-32, add c259+c279 rows
  25-33. Known: moved {257,277}, dests 259/279, off +2/+2.
- S3 odd offset: drop s0 c342 rows, add same rows in c345.
  Known: moved {342}, dest 345, off +3, row-shift 0.0.
- S4 missing-only: drop s0 c296 rows 24,25, add nothing.
  Known: moved {296}, dest none (no candidates).
- S5 extra-only: add row 28 to s0 c343. Known: moved {343},
  dest none (extra-only).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m28 import (NAMED8, S0_ROWS, assign_one, census_of_shape,  # noqa: E402
                 interior_sites, load_dump, off_of, plane_coords,
                 plane_of_byte, priv_y_cols, synth_w_bytes,
                 tail_bulk_masks)


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


def check(tag, t, t0, pl, pr, pc, want_moved, want_dis):
    """want_dis: {col: (dest, off, rshift) or None}."""
    colrows = {}
    for c in NAMED8:
        idx = np.nonzero(t & (pl == 0) & (pc == c))[0]
        colrows[c] = sorted(int(pr[o]) for o in idx)
    cen = census_of_shape(colrows)
    moved = sorted(c for c in NAMED8 if cen[c]["pres"] == 0)
    priv = t & ~t0
    pcols = priv_y_cols(priv, pl, pr, pc)
    ok = moved == sorted(want_moved)
    print(f"{tag}: moved={moved} (want {sorted(want_moved)}) "
          f"match={moved == sorted(want_moved)}")
    for c in NAMED8:
        e = "moved" if c in want_moved else "present"
        print(f"{tag} col {c}: n={cen[c]['n']} ov={cen[c]['ov']} "
              f"pres={cen[c]['pres']} ({e})")
    for c in moved:
        if cen[c]["miss"] == 0:
            is_extra = want_dis.get(c) == "extra-only"
            ok = ok and is_extra
            print(f"{tag} move c{c}->none(extra-only) want-extra={is_extra}")
            continue
        a = assign_one(c, pcols)
        w = want_dis.get(c)
        if w is None:
            good = a["status"] == "no-cand" and a["dest"] is None
            print(f"{tag} move c{c}->none(no-cand) match={good}")
            ok = ok and good
        else:
            wd, wo, wr = w
            good = (a["dest"] == wd and a["off"] == wo
                    and a["rshift"] == wr and a["status"] == "ok")
            print(f"{tag} move c{c}->{a['dest']}: off={a['off']} "
                  f"rshift={a['rshift']} (want {wd}/{wo}/{wr}) match={good}")
            ok = ok and good
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
    # S1: c301 -> c303 (+2), rows 25-33
    t1 = build(t0, [off_of(r, 301) for r in S0_ROWS[301]],
               [off_of(r, 303) for r in range(25, 34)])
    oks.append(check("S1", t1, t0, pl, pr, pc, [301],
                     {301: (303, 2, 1.0)}))
    # S2: c257+c277 -> c259+c279 (+2/+2), rows 25-33
    t2 = build(t0, [off_of(r, 257) for r in S0_ROWS[257]]
               + [off_of(r, 277) for r in S0_ROWS[277]],
               [off_of(r, 259) for r in range(25, 34)]
               + [off_of(r, 279) for r in range(25, 34)])
    oks.append(check("S2", t2, t0, pl, pr, pc, [257, 277],
                     {257: (259, 2, 1.5), 277: (279, 2, 1.5)}))
    # S3: c342 -> c345 (+3), same rows
    t3 = build(t0, [off_of(r, 342) for r in S0_ROWS[342]],
               [off_of(r, 345) for r in S0_ROWS[342]])
    oks.append(check("S3", t3, t0, pl, pr, pc, [342],
                     {342: (345, 3, 0.0)}))
    # S4: c296 drop rows 24,25, no dest
    t4 = build(t0, [off_of(24, 296), off_of(25, 296)], [])
    oks.append(check("S4", t4, t0, pl, pr, pc, [296], {296: None}))
    # S5: c343 add row 28 (extra-only)
    t5 = build(t0, [], [off_of(28, 343)])
    oks.append(check("S5", t5, t0, pl, pr, pc, [343],
                     {343: "extra-only"}))
    print(f"controls pass={all(oks)}")


if __name__ == "__main__":
    main()
