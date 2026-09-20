#!/usr/bin/env python3
"""M44 control O-OPP: known opposite standings (offline).

Usage: control.py M16_DIR

Value-level synthetic truths on s0 mid' (M35 C-VAL machinery;
v0/full unchanged so gaps equal both frames at every injected
site). Three synthetic shapes from s0:
  B  (wipe + lone):   drop all 4 s0 c298 tail rows + drop (296,311)
  C1 (growth + crowd-A): +2 extras in c298 + 1 extra in c311
  C2 (crowd-B): +1 extra in c311 (c298 untouched/present)
Then c298 reads 1 wipe (B) + 1 growth (C1) with C2 present;
c311 reads 1 miss-only (B) + 2 extra-only (C1, C2).
Pass = moved-sets + per-column n/ov/pres + row-lists + per-site
values + standings exact on all 3 shapes.
"""
import sys
from pathlib import Path

import numpy as np

from m44 import (N, attrib_lines, dstats_lines, gapsign_lines,
                 interior_sites, jaccard, load_dump, off_of,
                 plane_coords, plane_of_byte, synth_w_bytes,
                 tail_bulk_masks, tail_y_cols, y_col_rows,
                 C298_S0, C311_S0)


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
    glo = np.minimum(a, f)
    ghi = np.maximum(a, f)
    gap = np.abs(a - f)
    sp0 = interior_sites(v0, mid0, full0, b0)
    mask0, d0 = sp0["mask"], sp0["delta"]
    t0, bulk0 = tail_bulk_masks(mask0, d0)
    print(f"s0 cell7 n={int(mask0.sum())} tail n={int(t0.sum())}")

    # ---- miss targets: c298 4 rows + (296,311) ----
    miss_offs = [off_of(r, 298) for r in C298_S0] + [off_of(296, 311)]
    print(f"miss targets: {[(int(pr[o]), int(pc[o])) for o in miss_offs]}")
    if not all(t0[o] for o in miss_offs):
        print("O-OPP INFEASIBLE: a miss target is not s0 tail; tabled.")
        return
    # ---- extra candidates: interior-BULK Y, gap>=17, per column ----
    want = {298: 2, 311: 2}
    extra_offs = {}
    extra_signs = {}
    for c, k in want.items():
        cand = [int(o) for o in np.nonzero(
            bulk0 & (pl == 0) & (pc == c) & (gap >= 17))[0]]
        print(f"col {c}: bulk gap>=17 Y candidates n={len(cand)}")
        picked = []
        signs = {}
        sign_fb = []
        for o in sorted(cand):
            r = int(pr[o])
            par = 8 if (r + c) % 2 == 0 else -8
            new = int(s[o]) + par
            if int(glo[o]) < new < int(ghi[o]):
                picked.append(o)
                signs[o] = par
            else:
                new2 = int(s[o]) - par
                if int(glo[o]) < new2 < int(ghi[o]):
                    picked.append(o)
                    signs[o] = -par
                    sign_fb.append(o)
            if len(picked) == k:
                break
        extra_offs[c] = picked
        extra_signs[c] = signs
        print(f"col {c}: picked rows={[int(pr[o]) for o in picked]} "
              f"signs={[signs[o] for o in picked]} (want {k}, "
              f"K'={len(picked)}) sign-fallbacks={sign_fb}")
        if not picked:
            print(f"O-OPP INFEASIBLE: col {c} has no suitable site; tabled.")
            return
    e298 = extra_offs[298]
    e311 = extra_offs[311]
    # C1 takes all e298 + first e311; C2 takes second e311 (or reuses
    # C1's row pick order: C2 needs a DISTINCT site; if K'311==1 the
    # crowd-B leg is infeasible -> table, do not substitute columns)
    c1_extra = e298 + e311[:1]
    c2_extra = e311[1:2]
    print(f"C1 extra rc={[(int(pr[o]), int(pc[o])) for o in c1_extra]}")
    print(f"C2 extra rc={[(int(pr[o]), int(pc[o])) for o in c2_extra]}")
    if not c2_extra:
        print("O-OPP INFEASIBLE: col 311 holds only 1 suitable site, "
              "crowd needs 2 distinct; tabled.")
        return

    # ---- build synthetic mids ----
    midB = bytearray(mid0)
    fallbacks = []
    for o in miss_offs:
        new = int(s[o]) + 1
        if not (int(glo[o]) < new < int(ghi[o])):
            new = int(s[o]) - 1
            fallbacks.append(o)
        assert int(glo[o]) < new < int(ghi[o]), f"B o={o}: not interior"
        midB[o] = new
    print(f"B miss fallbacks (-1 used): n={len(fallbacks)} "
          f"offs={fallbacks}")
    midC1 = bytearray(mid0)
    for o in c1_extra:
        c = int(pc[o])
        midC1[o] = int(s[o]) + extra_signs[c][o]
    midC2 = bytearray(mid0)
    for o in c2_extra:
        c = int(pc[o])
        midC2[o] = int(s[o]) + extra_signs[c][o]

    # ---- recompute + verify ----
    shapes = {"B": (bytes(midB), [], miss_offs, (97, 102)),
              "C1": (bytes(midC1), c1_extra, [], (102, 102 + len(c1_extra))),
              "C2": (bytes(midC2), c2_extra, [], (102, 102 + len(c2_extra)))}
    all_ok = True
    g0 = a - f
    for nm, (midX, wantP, wantM, (wi, wu)) in shapes.items():
        spX = interior_sites(v0, midX, full0, b0)
        maskX, dX = spX["mask"], spX["delta"]
        tX, _ = tail_bulk_masks(maskX, dX)
        PX = tX & ~t0
        MX = t0 & ~tX
        setP_ok = set(int(o) for o in np.nonzero(PX)[0]) == set(wantP)
        setM_ok = set(int(o) for o in np.nonzero(MX)[0]) == set(wantM)
        inter = int((tX & t0).sum())
        union = int((tX | t0).sum())
        j_ok = (inter, union) == (wi, wu)
        mask_ok = bool((maskX == mask0).all())
        # per-site |d| exact
        ad_ok = all(int(abs(int(dX[o]))) == 8 for o in wantP) and \
            all(int(abs(int(dX[o]))) == 1 for o in wantM)
        # gaps equal both frames (v0/full unchanged) + statuses
        gap_ok = True  # structural: same v0/full; verified per site below
        stat_ok = all(maskX[o] for o in wantM) and \
            all(mask0[o] and int(abs(int(d0[o]))) < 8 for o in wantP)
        # other tail members' d unchanged
        shared = tX & t0
        d_unch = bool((dX[shared] == d0[shared]).all())
        # per-column census rows (c298/c311)
        yX = tail_y_cols(tX, pl, pr, pc)
        col_ok = True
        for c, r0 in ((298, C298_S0), (311, C311_S0)):
            rx = yX.get(c, [])
            if nm == "B":
                wrows = [] if c == 298 else [r for r in r0 if r != 296]
            elif nm == "C1":
                wrows = sorted(r0 + [int(pr[o]) for o in wantP
                                       if int(pc[o]) == c])
            else:
                wrows = sorted(r0 + [int(pr[o]) for o in wantP
                                       if int(pc[o]) == c]) if c == 311 \
                    else list(r0)
            ok = rx == wrows
            col_ok = col_ok and ok
            ov = len(set(rx) & set(r0))
            print(f"O-OPP {nm} c{c}: rows={rx} (want {wrows}) "
                  f"n/ov={len(rx)}/{ov} match={ok}")
        # per-site value rows (exactness asserted field by field)
        z = np.zeros(N, bool)
        la, _ = attrib_lines(f"O{nm}", PX, MX, tX & t0, d0, mask0,
                             dX, maskX, v0, full0, v0, full0)
        for ln in la:
            if " o=" in ln:
                print(ln)
                f = dict(kv.split("=", 1) for kv in ln.split()[2:])
                o = int(f["o"])
                if o in wantP:
                    all_ok = all_ok and f["adQ"] == "8" and \
                        f["ostat"] == "bulk" and f["gQ"] == f["gO"]
                if o in wantM:
                    all_ok = all_ok and f["adO"] == "1" and \
                        f["ostat"] == "bulk" and f["gQ"] == f["gO"]
        print(f"O-OPP {nm}: Pset={setP_ok} Mset={setM_ok} "
              f"J={inter}/{union}={jaccard(tX, t0):.4f} "
              f"(want {wi}/{wu}={wi / wu:.4f}) Jok={j_ok} "
              f"maskfixed={mask_ok} ad={ad_ok} stat={stat_ok} "
              f"dunch={d_unch} cols={col_ok}")
        all_ok = all_ok and setP_ok and setM_ok and j_ok and mask_ok \
            and ad_ok and stat_ok and d_unch and col_ok
    # opposite-standings structure summary
    print(f"O-OPP structure: c298 B-wipe + C1-growth(+{len(e298)}) + "
          f"C2-present; c311 B-miss1 + C1-extra1 + C2-extra1")
    print(f"O-OPP pass={bool(all_ok)} (want True)")


if __name__ == "__main__":
    main()
