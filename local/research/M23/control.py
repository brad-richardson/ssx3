#!/usr/bin/env python3
"""M23 positive control: synthetic truth with KNOWN tail values (offline).

Usage: control.py M16_DIR   (run from the work dir; imports m23)

C-V1: inject d = K45+ (round(0.45*g), a listed predictor) on N=60
currently-interior-BULK s0 sites with gap>=17 (first 60 in offset
order passing the per-site strict-inside check; skips counted).
Recompute cell 7 + tail from (v0,mid',full): tail set must equal
T_s0 U injected exactly (count 162 + values + map), original tail
members' d unchanged. Restricted scoring on the 60 injected sites
must read argmax = K45+ unique with 60/60 exact hits.
Tables, no verdicts.
"""
import sys
from pathlib import Path

import numpy as np

import m23

N_INJ = 60


def main():
    m16d = Path(sys.argv[1])
    v0 = m23.load_dump(m16d / "m16-v0-s0000.bin")
    mid = m23.load_dump(m16d / "m16-mid-s0000.bin")
    full = m23.load_dump(m16d / "m16-full-s0000.bin")
    bl = m23.synth_w_bytes(v0, full, 0.5)
    sp = m23.interior_sites(v0, mid, full, bl)
    tail, bulk = m23.tail_bulk_masks(sp["mask"], sp["delta"])
    print(f"C-V1 baseline: cell={sp['n']} (want 2475) "
          f"tail={int(tail.sum())} (want 102)")
    if sp["n"] != 2475 or int(tail.sum()) != 102:
        print("C-V1 BASELINE MISMATCH: tabled, no injection.")
        return

    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    b = np.frombuffer(full, np.uint8).astype(np.int16)
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    s = np.frombuffer(bl, np.uint8).astype(np.int16)
    g = (a - b).astype(np.int16)
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)

    pool = np.flatnonzero(bulk & (np.abs(g) >= 17))
    print(f"C-V1 pool: bulk gap>=17 candidates={len(pool)}")
    chosen = []
    skipped = 0
    for o in pool:
        inj = int(m23.formula_pred("K45+", np.array([g[o]]))[0])
        if abs(inj) < 8:
            skipped += 1
            continue
        mp = int(s[o]) + inj
        if not (int(lo[o]) < mp < int(hi[o])):
            skipped += 1
            continue
        chosen.append((int(o), inj))
        if len(chosen) == N_INJ:
            break
    print(f"C-V1 chosen={len(chosen)} skipped={skipped} "
          f"(want {N_INJ}/counted)")
    if len(chosen) != N_INJ:
        print("C-V1 POOL SHORTFALL: tabled, no injection.")
        return
    offs = np.array([o for o, _ in chosen])
    injs = np.array([v for _, v in chosen])
    print(f"C-V1 inj values: {m23.exact_counts(injs)}")

    midp = m.copy()
    midp[offs] = s[offs] + injs
    sp2 = m23.interior_sites(v0, midp.astype(np.uint8).tobytes(), full,
                             bl)
    tail2, _ = m23.tail_bulk_masks(sp2["mask"], sp2["delta"])
    want = tail.copy()
    want[offs] = True
    set_eq = bool(np.array_equal(tail2, want))
    n2 = int(tail2.sum())
    vals_inj = sp2["delta"][offs].astype(np.int64)
    vals_eq = bool(np.array_equal(vals_inj, injs.astype(np.int64)))
    orig = np.flatnonzero(tail)
    orig_eq = bool(np.array_equal(sp2["delta"][orig].astype(np.int64),
                                  sp["delta"][orig].astype(np.int64)))
    print(f"C-V1 recompute: tailn={n2} (want 162) set_exact={set_eq} "
          f"inj_values_exact={vals_eq} orig_unchanged={orig_eq} "
          f"pass={n2 == 162 and set_eq and vals_eq and orig_eq}")

    # score all 9 predictors on the control frame (fit = control frame)
    ym = m23.split_planes(midp.astype(np.uint8))[0]
    _, _, dec = m23.p1_gradient(ym)
    rr, cc = m23.plane_coords()
    pl = m23.plane_of_byte()
    im_yt = m23.flat_to_planes(tail2)[0]
    ey = m23.flat_to_planes(sp2["delta"])[0].astype(np.int64)
    off2 = np.flatnonzero(tail2)
    dt2 = sp2["delta"][tail2].astype(np.int64)
    gt2 = g[tail2].astype(np.int64)
    art2 = {"off": off2, "dt": dt2, "gt": gt2, "im_yt": im_yt, "ey": ey,
            "dec": dec, "delta": sp2["delta"]}
    fc = m23.fit_comp(im_yt, ey)
    fp = m23.fit_pos(off2, sp2["delta"], dec, rr, cc, pl)
    preds = m23.build_same_preds(art2, fc, fp, rr, cc, pl)
    LC, HC = m23.score_lines("control fullframe", dt2, preds)
    for ln in LC:
        print(ln)
    # restricted scoring on the 60 injected sites only
    pos = {int(o): i for i, o in enumerate(off2)}
    idx = np.array([pos[int(o)] for o in offs])
    LC2, HC2 = m23.score_lines("control injected-only", dt2[idx],
                               {k: v[idx] for k, v in preds.items()})
    for ln in LC2:
        print(ln)
    arg = [p for p in m23.PRED_IDS
           if HC2[p] == max(v for v in HC2.values() if v is not None)]
    ident = len(arg) == 1 and arg[0] == "K45+" and HC2["K45+"] == 60
    print(f"C-V1 identity: argmax={arg} K45+={HC2['K45+']}/60 "
          f"unique_exact={ident}")
    cpass = n2 == 162 and set_eq and vals_eq and orig_eq and ident
    print(f"C-V1 PASS={cpass}")


if __name__ == "__main__":
    main()
