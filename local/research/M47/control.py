#!/usr/bin/env python3
"""M47 control: synthetic truth with KNOWN wipe + singleton/far pools.

Usage: control.py M16_DIR

Mid-level control (M36 C-VAL-style): s0 mid' with a known 7-site
wipe (c342+c343 rows, mimics 711) flipped tail->bulk, plus a
known singleton pool (3 cols x 1 site) and far pool (1 col x 4
sites) flipped bulk->tail. Checks exact recovery of the wipe +
listing tables. Read-only inputs; receipt text to stdout.
Tables, no verdicts.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m47 import (N, interior_sites, jaccard, load_dump, off_of,
                 plane_coords, plane_of_byte, priv_y_cols,
                 synth_w_bytes, tail_bulk_masks, tail_y_cols)

WIPE = [(27, 342), (28, 342), (29, 342), (34, 342), (35, 342),
        (26, 343), (27, 343)]  # (row, col): 711's 7 wiped rows


def main():
    m16d = Path(sys.argv[1])
    print("== C-WIPE setup (s0 mid' with known wipe + pools) ==")
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
    s0y = tail_y_cols(t0, pl, pr, pc)

    # wipe sites must be currently-TAIL Y
    woffs = [off_of(r, c) for r, c in WIPE]
    assert all(t0[o] and pl[o] == 0 for o in woffs), "wipe pool not all tail-Y"
    print(f"wipe pool: n={len(woffs)} all-tail-Y=True")

    # pool candidates: currently-interior-BULK gap>=17 Y, fresh col
    fresh = lambda o: int(pc[o]) not in s0y  # noqa: E731
    cands = [int(o) for o in np.nonzero(b0m & (pl == 0) & (gap >= 17))[0]
             if fresh(o)]
    print(f"bulk gap>=17 fresh-col Y pool: n={len(cands)}")

    def land8(o, idx):
        tgt = int(bl[o]) + (8 if idx % 2 == 0 else -8)
        if 0 <= tgt <= 255 and int(lo[o]) < tgt < int(hi[o]):
            return tgt
        return None

    # far col: first col (offset order) with >=4 landable sites
    bycol = {}
    for o in cands:
        bycol.setdefault(int(pc[o]), []).append(o)
    farcol, faroffs, fardir = None, [], {}
    # deterministic pass: try each col in first-offset order
    colorder = sorted(bycol, key=lambda c: bycol[c][0])
    for c in colorder:
        picks, dirs = [], {}
        for o in bycol[c]:
            idx = len(picks)
            tgt = land8(o, idx)
            if tgt is not None:
                picks.append(o)
                dirs[o] = tgt
            if len(picks) == 4:
                break
        if len(picks) == 4:
            farcol, faroffs, fardir = c, picks, dirs
            break
    assert farcol is not None, "no far col with 4 landable sites"
    print(f"far col: c={farcol} rows={[int(pr[o]) for o in faroffs]}")

    # singleton cols: first 3 landable sites in 3 distinct fresh cols
    used = {farcol}
    sing, singdir = [], {}
    idx = 0
    for o in cands:
        c = int(pc[o])
        if c in used or o in faroffs:
            continue
        tgt = land8(o, idx)
        if tgt is not None:
            sing.append(o)
            singdir[o] = tgt
            used.add(c)
            idx += 1
        if len(sing) == 3:
            break
    assert len(sing) == 3, "fewer than 3 singleton sites"
    print(f"sing cols: {[(int(pc[o]), int(pr[o])) for o in sing]}")

    # build mid': wipe -> bulk (+1, fallback -1), pools -> tail (+-8)
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
    for o, tgt in list(fardir.items()) + list(singdir.items()):
        midp[o] = tgt
    midp = bytes(midp)
    n_plus1 = sum(1 for v in wland.values() if v == 1)
    print(f"wipe landings: +1 x{n_plus1}, -1 x{len(wland) - n_plus1}")
    fard = ["+8" if fardir[o] > bl[o] else "-8" for o in faroffs]
    singd = ["+8" if singdir[o] > bl[o] else "-8" for o in sing]
    print(f"far landings: {fard}; sing landings: {singd}")

    # recompute sets on mid'
    spq = interior_sites(v0, midp, full0, b0)
    tq, _ = tail_bulk_masks(spq["mask"], spq["delta"])
    mask_fixed = bool((spq["mask"] == mask0).all())
    pq, mq = tq & ~t0, t0 & ~tq
    jj = jaccard(tq, t0)
    want_j = "0.8716"  # 95/109
    print(f"tail'={int(tq.sum())} (want 102) J={jj:.4f} (want {want_j}) "
          f"cell-fixed={mask_fixed}")
    ok_sets = (mask_fixed and int(tq.sum()) == 102
               and f"{jj:.4f}" == want_j
               and set(int(o) for o in np.nonzero(pq)[0]) == set(faroffs + sing)
               and set(int(o) for o in np.nonzero(mq)[0]) == set(woffs))
    print(f"sets-exact (priv=7 pool, miss=7 wipe): {ok_sets}")

    # listing recovery: singleton == 3 cols x 1, far == 1 col x 4
    pcols = priv_y_cols(pq, pl, pr, pc)
    sing_rec = sorted((c, v) for c, v in pcols.items() if len(v) == 1)
    far_rec = sorted((c, v) for c, v in pcols.items() if len(v) >= 2)
    want_sing = sorted((int(pc[o]), [int(pr[o])]) for o in sing)
    want_far = [(farcol, sorted(int(pr[o]) for o in faroffs))]
    print(f"singleton listing: {sing_rec} want={want_sing} "
          f"exact={sing_rec == want_sing}")
    print(f"far listing: {far_rec} want={want_far} exact={far_rec == want_far}")

    # value recovery: pool |d|==8 all; wipe sites bulk |d|==1 on mid'
    pool_ads = sorted(int(abs(int(spq["delta"][o]))) for o in faroffs + sing)
    wipe_ads = sorted(int(abs(int(spq["delta"][o]))) for o in woffs)
    print(f"pool |d'|: {pool_ads} (want [8]*7) exact={pool_ads == [8] * 7}")
    print(f"wipe |d'|: {wipe_ads} (want [1]*7) exact={wipe_ads == [1] * 7}")

    # gap recovery: signed gaps equal (v0/full unchanged)
    aA = np.frombuffer(v0, np.uint8).astype(np.int16)
    bA = np.frombuffer(full0, np.uint8).astype(np.int16)
    g = aA - bA
    geq = sum(1 for o in faroffs + sing + woffs
              if int(g[o]) == int(g[o]))
    print(f"gaps: {geq}/{len(faroffs + sing + woffs)} signed-eq "
          f"(v0/full fixed -> all equal)")

    ok = (ok_sets and sing_rec == want_sing and far_rec == want_far
          and pool_ads == [8] * 7 and wipe_ads == [1] * 7)
    print(f"C-WIPE pass: {ok}")
    print("tests: R=C-WIPE")


if __name__ == "__main__":
    main()
