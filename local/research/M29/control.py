#!/usr/bin/env python3
"""M29 positive controls: synthetic truths with KNOWN partial moves.

Usage: control.py M16_DIR

Mid-level synthetics (M27-style — feasible because partial flips
keep cell-7 membership; only the injected mid bytes change, so no
other site's membership can move):

- C-PART-MISS (known missing-only partial, mimics 710): s0 mid''
  with the FIRST 2 offset-order s0-tail Y sites in column c340
  flipped to bulk (mid''=blend+1, fallback blend-1 per site if +1
  is not strictly inside — tabled).
- C-PART-EXTRA (known extra-only partial, mimics 22): s0 mid'
  with the FIRST 2 offset-order interior-BULK gap>=17 Y sites in
  column c296 flipped to tail (mid'=blend+8 even / blend-8 odd;
  if c296 holds <2 such sites, remainder from c343, then
  anywhere in offset order — tabled).

Pass = delta-row sets + n/ov/pres + standing + per-site values
exact on both (N=2 shapes).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m29 import (NAMED8, S0_ROWS, census_of_shape,  # noqa: E402
                 interior_sites, jaccard, load_dump, off_of,
                 plane_coords, plane_of_byte, priv_y_cols,
                 standing_of, synth_w_bytes, tail_bulk_masks, y_col_rows)


def main():
    m16d = Path(sys.argv[1])
    pl = plane_of_byte()
    pr, pc = plane_coords()
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid0 = load_dump(m16d / "m16-mid-s0000.bin")
    full0 = load_dump(m16d / "m16-full-s0000.bin")
    b0 = synth_w_bytes(v0, full0, 0.5)
    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    m = np.frombuffer(mid0, np.uint8).astype(np.int16)
    f = np.frombuffer(full0, np.uint8).astype(np.int16)
    s = np.frombuffer(b0, np.uint8).astype(np.int16)
    lo, hi = np.minimum(a, f), np.maximum(a, f)
    gap = np.abs(a - f)
    sp0 = interior_sites(v0, mid0, full0, b0)
    mask0, d0 = sp0["mask"], sp0["delta"]
    t0, bulk0 = tail_bulk_masks(mask0, d0)
    print(f"s0: cell7={sp0['n']} tail={int(t0.sum())} "
          f"bulk={int(bulk0.sum())}")

    all_ok = True

    # ---- C-PART-MISS: 2 tail->bulk flips in c340 ----
    print("== C-PART-MISS (known missing-only partial in c340) ==")
    cand = [int(o) for o in np.nonzero(
        t0 & (pl == 0) & (pc == 340))[0][:2]]
    print(f"inject sites: {[(o, int(pr[o]), int(pc[o])) for o in cand]} "
          f"(want first-2 offset-order s0-tail Y in c340)")
    mid2 = bytearray(mid0)
    used = {}
    for o in cand:
        if lo[o] < s[o] + 1 < hi[o]:
            mid2[o] = int(s[o] + 1)
            used[o] = "+1"
        else:
            assert lo[o] < s[o] - 1 < hi[o], f"o={o}: no bulk landing?!"
            mid2[o] = int(s[o] - 1)
            used[o] = "-1(fallback)"
    print(f"landing: {used}")
    sp = interior_sites(v0, bytes(mid2), full0, b0)
    t, _ = tail_bulk_masks(sp["mask"], sp["delta"])
    priv = t & ~t0
    miss = t0 & ~t
    jj = jaccard(t, t0)
    colrows = {c: y_col_rows(t, c, pl, pr, pc) for c in NAMED8}
    cen = census_of_shape(colrows)
    pcols = priv_y_cols(priv, pl, pr, pc)
    st = standing_of(340, cen[340], pcols)
    miss_rows = sorted(set(S0_ROWS[340]) - set(colrows[340]))
    ok = (sorted(int(o) for o in np.nonzero(miss)[0]) == sorted(cand)
          and int(priv.sum()) == 0
          and f"{jj:.4f}" == "0.9804"
          and cen[340]["n"] == 6 and cen[340]["ov"] == 6
          and cen[340]["pres"] == 0
          and all(cen[c]["pres"] == 1 for c in NAMED8 if c != 340)
          and st == "none(no-cand)")
    print(f"miss set exact={sorted(int(o) for o in np.nonzero(miss)[0]) == sorted(cand)} "
          f"priv empty={int(priv.sum()) == 0} J={jj:.4f} (want 0.9804)")
    print(f"c340 n/ov/p={cen[340]['n']}/{cen[340]['ov']}/{cen[340]['pres']} "
          f"(want 6/6/0) miss_rows={miss_rows} standing={st} "
          f"(want none(no-cand))")
    print(f"other 7 cols all present="
          f"{all(cen[c]['pres'] == 1 for c in NAMED8 if c != 340)}")
    vals_ok = True
    for o in cand:
        ad_orig = int(abs(int(d0[o])))
        bulk_now = bool(sp["mask"][o]) and int(abs(int(sp["delta"][o]))) == 1
        others_same = True  # membership change is per-byte by construction
        print(f"o={o} rc=({int(pr[o])},{int(pc[o])}): ad_orig={ad_orig} "
              f"(want>=8) synth_bulk_ad1={bulk_now}")
        vals_ok = vals_ok and ad_orig >= 8 and bulk_now and others_same
    # all other tail members' delta unchanged
    rest = t0.copy()
    rest[cand] = False
    same = bool((sp["delta"][rest] == d0[rest]).all())
    print(f"other tail members' delta unchanged={same}")
    print(f"C-PART-MISS pass={ok and vals_ok and same}")
    all_ok = all_ok and ok and vals_ok and same

    # ---- C-PART-EXTRA: 2 bulk->tail flips (c296 first) ----
    print("== C-PART-EXTRA (known extra-only partial, c296 first) ==")
    pool296 = [int(o) for o in np.nonzero(
        bulk0 & (gap >= 17) & (pl == 0) & (pc == 296))[0]]
    pool343 = [int(o) for o in np.nonzero(
        bulk0 & (gap >= 17) & (pl == 0) & (pc == 343))[0]]
    poolany = [int(o) for o in np.nonzero(
        bulk0 & (gap >= 17) & (pl == 0))[0]]
    print(f"pools: c296={len(pool296)} c343={len(pool343)} "
          f"anyY={len(poolany)} (bulk gap>=17 Y)")
    cand2 = (pool296[:2]
             + [o for o in pool343 if o not in pool296][:max(0, 2 - len(pool296[:2]))])
    cand2 += [o for o in poolany if o not in cand2][:max(0, 2 - len(cand2))]
    assert len(cand2) == 2, "pool exhausted?!"
    print(f"inject sites: {[(o, int(pr[o]), int(pc[o])) for o in cand2]}")
    mid3 = bytearray(mid0)
    used2 = {}
    for i, o in enumerate(cand2):
        delta_inject = 8 if i % 2 == 0 else -8
        if lo[o] < s[o] + delta_inject < hi[o]:
            mid3[o] = int(s[o] + delta_inject)
            used2[o] = f"{delta_inject:+d}"
        else:
            assert lo[o] < s[o] - delta_inject < hi[o], \
                f"o={o}: no tail landing?!"
            mid3[o] = int(s[o] - delta_inject)
            used2[o] = f"{-delta_inject:+d}(fallback)"
    print(f"landing: {used2}")
    sp2 = interior_sites(v0, bytes(mid3), full0, b0)
    t2, _ = tail_bulk_masks(sp2["mask"], sp2["delta"])
    priv2 = t2 & ~t0
    miss2 = t0 & ~t2
    jj2 = jaccard(t2, t0)
    colrows2 = {c: y_col_rows(t2, c, pl, pr, pc) for c in NAMED8}
    cen2 = census_of_shape(colrows2)
    pcols2 = priv_y_cols(priv2, pl, pr, pc)
    affcols = sorted({int(pc[o]) for o in cand2})
    ok2 = (sorted(int(o) for o in np.nonzero(priv2)[0]) == sorted(cand2)
           and int(miss2.sum()) == 0
           and f"{jj2:.4f}" == "0.9808")
    print(f"priv set exact={sorted(int(o) for o in np.nonzero(priv2)[0]) == sorted(cand2)} "
          f"miss empty={int(miss2.sum()) == 0} J={jj2:.4f} (want 0.9808)")
    for c in affcols:
        if c in NAMED8:
            ec = cen2[c]
            st2 = standing_of(c, ec, pcols2)
            print(f"c{c} n/ov/p={ec['n']}/{ec['ov']}/{ec['pres']} "
                  f"standing={st2} (want none(extra-only))")
            ok2 = ok2 and ec["pres"] == 0 and ec["miss"] == 0 \
                and st2 == "none(extra-only)"
        else:
            rs2 = y_col_rows(t2, c, pl, pr, pc)
            rs0 = y_col_rows(t0, c, pl, pr, pc)
            inj = sorted(int(pr[o]) for o in cand2 if int(pc[o]) == c)
            extra = sorted(set(rs2) - set(rs0))
            missc = sorted(set(rs0) - set(rs2))
            print(f"c{c} (non-named fallback col): rows0={rs0} rows2={rs2} "
                  f"extra={extra} (want {inj}) miss={missc} (want []) "
                  f"standing=none(extra-only) by rule (miss==0)")
            ok2 = ok2 and extra == inj and missc == []
    others_pres = all(cen2[c]["pres"] == 1 for c in NAMED8 if c not in affcols)
    print(f"unaffected named cols all present={others_pres}")
    ok2 = ok2 and others_pres
    vals_ok2 = True
    for o in cand2:
        ad_new = int(abs(int(sp2["delta"][o])))
        ad_s0 = int(abs(int(d0[o])))
        print(f"o={o} rc=({int(pr[o])},{int(pc[o])}): ad_new={ad_new} "
              f"(want 8) s0_bulk_ad={ad_s0} (want<8)")
        vals_ok2 = vals_ok2 and ad_new == 8 and ad_s0 < 8
    same2 = bool((sp2["delta"][t0] == d0[t0]).all())
    print(f"original tail members' delta unchanged={same2}")
    print(f"C-PART-EXTRA pass={ok2 and vals_ok2 and same2}")
    all_ok = all_ok and ok2 and vals_ok2 and same2

    print(f"ALL CONTROLS pass={all_ok}")


if __name__ == "__main__":
    main()
