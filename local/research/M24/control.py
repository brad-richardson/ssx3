#!/usr/bin/env python3
"""M24 positive control: synthetic truth with KNOWN residuals (offline).

Usage: control.py M16_DIR   (run from the work dir; imports m24)

C-R1: inject d = K45+(g) + r on N=60 s0 sites from the union
pool (currently-interior-BULK sites with gap>=17 PLUS endpoint
sites with gap>=32, M22 C-T2 precedent; first 60 in offset order
passing the per-site |d|>=8 + strict-inside checks; skips
counted), with r = +1 where frac(0.45*g) >= 0.5 else -1 (the FRAC
rule). Rev 2: rev-1 pooled bulk-gap>=17 only (248 candidates) and
chose 40/60 (DESIGN.md pool as specified; the +/-1 pushes most
small-gap injections outside the strict-inside bound or below
|d|>=8) — superseded feasibility defect, tabled in REPORT.md.
Recompute cell 7 +
tail from (v0,mid',full): tail set must equal T_s0 U injected
exactly (count 162 + values + map), original tail members' d
unchanged. Residual-pattern recovery: r-sign vs frac-half joint
on injected sites must read the injected rule exactly. Correction
fits on the injected-only (known-truth) set; restricted scoring
on the 60 injected sites must read argmax = FRAC unique with
60/60 exact hits.
Tables, no verdicts.
"""
import sys
from pathlib import Path

import numpy as np

import m24

N_INJ = 60


def main():
    m16d = Path(sys.argv[1])
    v0 = m24.load_dump(m16d / "m16-v0-s0000.bin")
    mid = m24.load_dump(m16d / "m16-mid-s0000.bin")
    full = m24.load_dump(m16d / "m16-full-s0000.bin")
    bl = m24.synth_w_bytes(v0, full, 0.5)
    sp = m24.interior_sites(v0, mid, full, bl)
    tail, bulk = m24.tail_bulk_masks(sp["mask"], sp["delta"])
    print(f"C-R1 baseline: cell={sp['n']} (want 2475) "
          f"tail={int(tail.sum())} (want 102)")
    if sp["n"] != 2475 or int(tail.sum()) != 102:
        print("C-R1 BASELINE MISMATCH: tabled, no injection.")
        return

    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    b = np.frombuffer(full, np.uint8).astype(np.int16)
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    s = np.frombuffer(bl, np.uint8).astype(np.int16)
    g = (a - b).astype(np.int16)
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)

    moved = a != b
    at_end = (m == lo) | (m == hi)
    endpoint = moved & at_end & ~sp["mask"]
    pool_bulk = np.flatnonzero(bulk & (np.abs(g) >= 17))
    pool_end = np.flatnonzero(endpoint & (np.abs(g) >= 32))
    pool = np.union1d(pool_bulk, pool_end)  # offset order
    print(f"C-R1 pool: bulk gap>=17 n={len(pool_bulk)} + endpoint "
          f"gap>=32 n={len(pool_end)} union={len(pool)}")
    chosen = []
    skipped = 0
    for o in pool:
        gg = int(g[o])
        r_inj = 1 if int(m24.frac_hi(np.array([gg]))[0]) == 1 else -1
        inj = int(m24.k45pred(np.array([gg]))[0]) + r_inj
        if abs(inj) < 8:
            skipped += 1
            continue
        mp = int(s[o]) + inj
        if not (int(lo[o]) < mp < int(hi[o])):
            skipped += 1
            continue
        chosen.append((int(o), inj, r_inj))
        if len(chosen) == N_INJ:
            break
    print(f"C-R1 chosen={len(chosen)} skipped={skipped} "
          f"(want {N_INJ}/counted)")
    if len(chosen) != N_INJ:
        print("C-R1 POOL SHORTFALL: tabled, no injection.")
        return
    offs = np.array([o for o, _, _ in chosen])
    injs = np.array([v for _, v, _ in chosen])
    rinj = np.array([r for _, _, r in chosen])
    print(f"C-R1 inj values: {m24.exact_counts(injs)}")
    print(f"C-R1 inj r: plus1={int((rinj == 1).sum())} "
          f"minus1={int((rinj == -1).sum())}")
    nondeg = bool(((rinj == 1).any() and (rinj == -1).any()))
    print(f"C-R1 non-degenerate r (both signs present): {nondeg}")

    midp = m.copy()
    midp[offs] = s[offs] + injs
    sp2 = m24.interior_sites(v0, midp.astype(np.uint8).tobytes(), full,
                             bl)
    tail2, _ = m24.tail_bulk_masks(sp2["mask"], sp2["delta"])
    want = tail.copy()
    want[offs] = True
    set_eq = bool(np.array_equal(tail2, want))
    n2 = int(tail2.sum())
    vals_inj = sp2["delta"][offs].astype(np.int64)
    vals_eq = bool(np.array_equal(vals_inj, injs.astype(np.int64)))
    orig = np.flatnonzero(tail)
    orig_eq = bool(np.array_equal(sp2["delta"][orig].astype(np.int64),
                                  sp["delta"][orig].astype(np.int64)))
    print(f"C-R1 recompute: tailn={n2} (want 162) set_exact={set_eq} "
          f"inj_values_exact={vals_eq} orig_unchanged={orig_eq} "
          f"pass={n2 == 162 and set_eq and vals_eq and orig_eq}")

    # residual-pattern recovery on injected sites (frac rule exact?)
    gt_inj = g[offs].astype(np.int64)
    hi_inj = m24.frac_hi(gt_inj)
    r_rec = (vals_inj - m24.k45pred(gt_inj).astype(np.int64)).astype(
        np.int64)
    pat = bool(np.array_equal(r_rec, rinj.astype(np.int64)))
    hi_ok = bool(((hi_inj == 1) == (r_rec == 1)).all())
    print(f"C-R1 pattern: r_recovered_exact={pat} "
          f"HI<->+1_exact={hi_ok} "
          f"HI_n={int((hi_inj == 1).sum())} "
          f"LO_n={int((hi_inj == 0).sum())}")

    # correction fits on the injected-only (known-truth) set
    ym = m24.split_planes(midp.astype(np.uint8))[0]
    _, _, dec = m24.p1_gradient(ym)
    rr, cc = m24.plane_coords()
    pl = m24.plane_of_byte()
    fits_inj = {}
    for cid in m24.CORR_IDS:
        lv = m24.corr_levels(cid, gt_inj, offs, dec, rr, cc, pl)
        fits_inj[cid] = m24.fit_corr(cid, lv, r_rec)
        print(f"C-R1 fit-injected {cid}: "
              + " ".join(
                  f"{m24.LEVEL_NAMES[cid][lev]}="
                  f"{fits_inj[cid]['c'][lev]}"
                  for lev in sorted(fits_inj[cid]["c"])
                  if lev < len(m24.LEVEL_NAMES[cid]))
              + f" fallback={fits_inj[cid]['fallback']} "
              f"empties={fits_inj[cid]['empties']}")
    preds_inj = {}
    for cid in m24.CORR_IDS:
        preds_inj[cid] = m24.apply_corr(cid, gt_inj, offs, dec, rr, cc,
                                        pl, fits_inj[cid])
    LC2, HC2 = m24.score_corr_lines("control injected-only",
                                    vals_inj, preds_inj)
    for ln in LC2:
        print(ln)
    mx = max(HC2.values())
    arg = [p for p in m24.CORR_IDS if HC2[p] == mx]
    ident = nondeg and len(arg) == 1 and arg[0] == "FRAC" \
        and HC2["FRAC"] == 60
    print(f"C-R1 identity: argmax={arg} FRAC={HC2['FRAC']}/60 "
          f"unique_exact={ident}")

    # full-control-frame scores (fit on control frame), tabled
    im_yt = m24.flat_to_planes(tail2)[0]
    ey = m24.flat_to_planes(sp2["delta"])[0].astype(np.int64)
    off2 = np.flatnonzero(tail2)
    dt2 = sp2["delta"][tail2].astype(np.int64)
    gt2 = g[tail2].astype(np.int64)
    art2 = {"off": off2, "dt": dt2, "gt": gt2, "im_yt": im_yt, "ey": ey,
            "dec": dec, "delta": sp2["delta"]}
    fits_full = {}
    for cid in m24.CORR_IDS:
        lv = m24.corr_levels(cid, gt2, off2, dec, rr, cc, pl)
        fits_full[cid] = m24.fit_corr(cid, lv, dt2 - m24.k45pred(
            gt2).astype(np.int64))
    preds = m24.build_preds(art2, fits_full, rr, cc, pl)
    LC, HC = m24.score_corr_lines("control fullframe", dt2, preds)
    for ln in LC:
        print(ln)
    cpass = n2 == 162 and set_eq and vals_eq and orig_eq and pat \
        and hi_ok and ident
    print(f"C-R1 PASS={cpass}")


if __name__ == "__main__":
    main()
