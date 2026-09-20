#!/usr/bin/env python3
"""M48 control: synthetic truth with KNOWN collision (2 wipes + 1 dest).

Usage: control.py M16_DIR

Mid-level control (M36 C-VAL-style): s0 mid' with a known 10-site
wipe (c340's 8 + c343's 2 rows, mimics 734) flipped tail->bulk,
plus a known 2-site dest in ONE shared column flipped bulk->tail
(|d|=8). Checks exact recovery of the wipe + dest + value tables
+ the displacement collision. Read-only inputs; receipt text to
stdout. Tables, no verdicts.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m48 import (assign_one, interior_sites, jaccard, load_dump,  # noqa: E402
                 off_of, plane_coords, plane_of_byte, priv_y_cols,
                 synth_w_bytes, tail_bulk_masks, y_col_rows)

WIPE = [(r, 340) for r in (24, 25, 26, 27, 31, 32, 33, 34)] + [
    (26, 343), (27, 343)]  # (row, col): 734's 10 wiped rows


def main():
    m16d = Path(sys.argv[1])
    print("== C-COLLISION setup (s0 mid' with known wipe + dest) ==")
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid0 = load_dump(m16d / "m16-mid-s0000.bin")
    full0 = load_dump(m16d / "m16-full-s0000.bin")
    b0 = synth_w_bytes(v0, full0, 0.5)
    sp0 = interior_sites(v0, mid0, full0, b0)
    mask0, d0 = sp0["mask"], sp0["delta"]
    t0, b0m = tail_bulk_masks(mask0, d0)
    pl = plane_of_byte()
    pr, pc = plane_coords()
    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    bb = np.frombuffer(full0, np.uint8).astype(np.int16)
    bl = np.frombuffer(b0, np.uint8).astype(np.int16)
    lo, hi = np.minimum(a, bb), np.maximum(a, bb)
    gap = np.abs(a - bb)

    # wipe sites must be currently-TAIL Y
    woffs = [off_of(r, c) for r, c in WIPE]
    assert all(t0[o] and pl[o] == 0 for o in woffs), "wipe pool not all tail-Y"
    print(f"wipe pool: n={len(woffs)} all-tail-Y=True")

    # dest candidates: currently-interior-BULK gap>=17 Y
    cands = [int(o) for o in np.nonzero(b0m & (pl == 0) & (gap >= 17))[0]]
    print(f"bulk gap>=17 Y pool: n={len(cands)}")

    def land8(o, idx):
        tgt = int(bl[o]) + (8 if idx % 2 == 0 else -8)
        if 0 <= tgt <= 255 and int(lo[o]) < tgt < int(hi[o]):
            return tgt
        return None

    # dest col: c342 if it holds >=2 landable sites, else first
    # offset-order col with >=2 (M29 C-PART-EXTRA precedent)
    bycol = {}
    for o in cands:
        bycol.setdefault(int(pc[o]), []).append(o)
    destcol, destoffs, destdir = None, [], {}
    colorder = ([342] if 342 in bycol else []) + sorted(
        c for c in bycol if c != 342)
    for c in colorder:
        picks, dirs = [], {}
        for o in bycol[c]:
            tgt = land8(o, len(picks))
            if tgt is not None:
                picks.append(o)
                dirs[o] = tgt
            if len(picks) == 2:
                break
        if len(picks) == 2:
            destcol, destoffs, destdir = c, picks, dirs
            break
    assert destcol is not None, "no dest col with 2 landable sites"
    print(f"dest col: c={destcol} (c342 preferred; fallback tabled) "
          f"rows={[int(pr[o]) for o in destoffs]}")

    # build mid': wipe -> bulk (+1, fallback -1), dest -> tail (+-8)
    midp = bytearray(mid0)
    wland = {}
    for o in woffs:
        placed = None
        for tgt in (int(bl[o]) + 1, int(bl[o]) - 1):
            if 0 <= tgt <= 255 and int(lo[o]) < tgt < int(hi[o]):
                placed = tgt
                break
        assert placed is not None, f"wipe o={o}: no bulk landing"
        midp[o] = placed
        wland[o] = placed - int(bl[o])
    for o, tgt in destdir.items():
        midp[o] = tgt
    midp = bytes(midp)
    n_plus1 = sum(1 for v in wland.values() if v == 1)
    print(f"wipe landings: +1 x{n_plus1}, -1 x{len(wland) - n_plus1}")
    destd = ["+8" if destdir[o] > bl[o] else "-8" for o in destoffs]
    print(f"dest landings: {destd}")

    # recompute sets on mid'
    spq = interior_sites(v0, midp, full0, b0)
    tq, _ = tail_bulk_masks(spq["mask"], spq["delta"])
    mask_fixed = bool((spq["mask"] == mask0).all())
    pq, mq = tq & ~t0, t0 & ~tq
    jj = jaccard(tq, t0)
    want_j = "0.8846"  # 92/104 (734's counts exactly)
    print(f"tail'={int(tq.sum())} (want 94) J={jj:.4f} (want {want_j}) "
          f"cell-fixed={mask_fixed}")
    ok_sets = (mask_fixed and int(tq.sum()) == 94
               and f"{jj:.4f}" == want_j
               and set(int(o) for o in np.nonzero(pq)[0]) == set(destoffs)
               and set(int(o) for o in np.nonzero(mq)[0]) == set(woffs))
    print(f"sets-exact (priv=2 dest, miss=10 wipe): {ok_sets}")

    # wipe + dest row recovery
    ok_rows = True
    for c in (340, 343):
        rq = y_col_rows(tq, c, pl, pr, pc)
        ok = rq == []
        ok_rows = ok_rows and ok
        print(f"wipe c{c}: rows={rq} (want []) exact={ok}")
    rqd = y_col_rows(tq, destcol, pl, pr, pc)
    r0d = y_col_rows(t0, destcol, pl, pr, pc)
    want_extra = sorted(int(pr[o]) for o in destoffs)
    got_extra = sorted(set(rqd) - set(r0d))
    ok = got_extra == want_extra
    ok_rows = ok_rows and ok
    print(f"dest c{destcol}: s0-rows={r0d} q-rows={rqd} extra={got_extra} "
          f"(want {want_extra}) exact={ok}")

    # displacement collision recovery: both wipes -> dest col
    pcols = priv_y_cols(pq, pl, pr, pc)
    a340 = assign_one(340, pcols)
    a343 = assign_one(343, pcols)
    ok_disp = (a340["dest"] == destcol and a343["dest"] == destcol)
    print(f"disp c340->{a340['dest']} off={a340['off']} "
          f"rs={a340['rshift']} ms={a340['minshift']}")
    print(f"disp c343->{a343['dest']} off={a343['off']} "
          f"rs={a343['rshift']} ms={a343['minshift']}")
    print(f"collision-exact (both -> c{destcol}): {ok_disp}")

    # value recovery: dest |d|==8 x2; wipe sites bulk |d|==1 on mid'
    dest_ads = sorted(int(abs(int(spq["delta"][o]))) for o in destoffs)
    wipe_ads = sorted(int(abs(int(spq["delta"][o]))) for o in woffs)
    print(f"dest |d'|: {dest_ads} (want [8, 8]) exact={dest_ads == [8, 8]}")
    print(f"wipe |d'|: {wipe_ads} (want [1]*10) exact={wipe_ads == [1] * 10}")

    # status recovery: dest bulk on s0, wipes bulk on mid'
    dest_bulk0 = sum(1 for o in destoffs if mask0[o])
    wipe_bulkq = sum(1 for o in woffs if spq["mask"][o])
    print(f"dest s0-bulk: {dest_bulk0}/2; wipe mid'-bulk: {wipe_bulkq}/10")

    # gap recovery: signed gaps equal (v0/full unchanged)
    g = a - bb
    geq = sum(1 for o in destoffs + woffs
              if int(g[o]) == int(g[o]))
    print(f"gaps: {geq}/{len(destoffs + woffs)} signed-eq "
          f"(v0/full fixed -> all equal)")

    ok = (ok_sets and ok_rows and ok_disp and dest_ads == [8, 8]
          and wipe_ads == [1] * 10 and dest_bulk0 == 2 and wipe_bulkq == 10)
    print(f"C-COLLISION pass: {ok}")
    print("tests: R=C-COLLISION")


if __name__ == "__main__":
    main()
