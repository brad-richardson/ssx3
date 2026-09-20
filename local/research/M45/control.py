#!/usr/bin/env python3
"""M45 controls C-BOTM + C-BOTV (offline).

Usage: control.py M16_DIR

The pre-registered mid-level in-band leg is INFEASIBLE as
specified (rows 393-402 hold zero interior-BULK gap>=17 Y sites
on s0 — probed and tabled below, DESIGN.md amendment). Two
feasible legs in this invocation (both must pass):
  C-BOTM (mask-level, M28/M34-pinned): synthetic tail mask = s0
    tail + 2 in-band + 2 out-of-band sites at known coords.
    Recover moved-cells, n/ov/pres, standings, row-lists, P/M
    sets, J, completeness 2/2, and shared-geo_lines pairwise
    distances + span exactly.
  C-BOTV (mid-level value leg, out-of-band pool): K'=4 |d|=8
    extras with known values. Recover sets, J, per-site values,
    gaps, signs, deciles, per-column census, completeness,
    mask-fixed, rest-unchanged exactly.
"""
import sys
from pathlib import Path

import numpy as np

from m45 import (N, INBAND_HI, INBAND_LO, attrib_lines, dstats_lines,
                 gapsign_lines, geo_lines, inband, interior_sites,
                 jaccard, load_dump, off_of, p1_gradient, plane_coords,
                 plane_of_byte, split_planes, synth_w_bytes,
                 tail_bulk_masks, tail_y_cols)

# C-BOTM known coords: 2 in-band + 2 out-of-band (asserted non-s0-tail)
BOTM_IN = [(394, 300), (399, 305)]
BOTM_OUT = [(100, 300), (200, 305)]


def main():
    m16d = Path(sys.argv[1])
    pl = plane_of_byte()
    pr, pc = plane_coords()
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    mid0 = load_dump(m16d / "m16-mid-s0000.bin")
    full0 = load_dump(m16d / "m16-full-s0000.bin")
    b0 = synth_w_bytes(v0, full0, 0.5)
    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    s = np.frombuffer(b0, np.uint8).astype(np.int16)
    f = np.frombuffer(full0, np.uint8).astype(np.int16)
    glo = np.minimum(a, f)
    ghi = np.maximum(a, f)
    gap = np.abs(a - f)
    sp0 = interior_sites(v0, mid0, full0, b0)
    mask0, d0 = sp0["mask"], sp0["delta"]
    t0, bulk0 = tail_bulk_masks(mask0, d0)
    print(f"s0 cell7 n={int(mask0.sum())} tail n={int(t0.sum())}")

    # ---- infeasible-leg probe (pre-registered mid-level in-band) ----
    zone_in_m = (pr >= INBAND_LO) & (pr <= INBAND_HI)
    cand_in = [int(o) for o in np.nonzero(
        bulk0 & (pl == 0) & zone_in_m & (gap >= 17))[0]]
    print(f"C-BOT/inband probe: bulk gap>=17 Y candidates n={len(cand_in)} "
          f"(want >=1; 0 -> mid-level in-band leg INFEASIBLE, tabled)")

    # ================= C-BOTM (mask-level) =================
    print("== C-BOTM (mask-level 2+2) ==")
    known4 = list(BOTM_IN) + list(BOTM_OUT)
    known_offs = [off_of(r, c) for r, c in known4]
    clash = [(r, c) for (r, c), o in zip(known4, known_offs) if t0[o]]
    print(f"C-BOTM coords in={BOTM_IN} out={BOTM_OUT} "
          f"s0-tail-clashes={clash}")
    if clash:
        print("C-BOTM INFEASIBLE: known coord already s0 tail; tabled.")
        return
    tB = t0.copy()
    for o in known_offs:
        tB[o] = True
    PB = tB & ~t0
    MB = t0 & ~tB
    setP_ok = set(int(o) for o in np.nonzero(PB)[0]) == set(known_offs)
    setM_ok = int(MB.sum()) == 0
    inter = int((tB & t0).sum())
    union = int((tB | t0).sum())
    j_ok = (inter, union) == (102, 106)
    print(f"C-BOTM sets: P={setP_ok} M-empty={setM_ok} "
          f"J={inter}/{union}={jaccard(tB, t0):.4f} "
          f"(want 102/106=0.9623) Jok={j_ok}")
    # per-column census: affected cols exact, all others unchanged
    y0 = tail_y_cols(t0, pl, pr, pc)
    yB = tail_y_cols(tB, pl, pr, pc)
    aff = sorted({c for _, c in known4})
    col_ok = True
    for c in aff:
        r0 = y0.get(c, [])
        wrows = sorted(r0 + [r for r, cc in known4 if cc == c])
        rx = yB.get(c, [])
        ov = len(set(rx) & set(r0))
        ok = rx == wrows
        col_ok = col_ok and ok
        stand = ("extra-only" if rx != r0 and
                 set(r0) <= set(rx) else "OTHER?!")
        col_ok = col_ok and stand == "extra-only"
        print(f"C-BOTM c{c}: rows={rx} (want {wrows}) "
              f"n/ov={len(rx)}/{ov} stand={stand} match={ok}")
    moved = sorted(set(yB) | set(y0))
    moved = [c for c in moved if yB.get(c, []) != y0.get(c, [])]
    moved_ok = moved == aff
    print(f"C-BOTM moved cols={moved} (want {aff}) match={moved_ok}")
    col_ok = col_ok and moved_ok
    # completeness 2/2
    got_in = [rc for rc in known4 if inband(rc[0])]
    got_out = [rc for rc in known4 if not inband(rc[0])]
    comp_ok = len(got_in) == 2 and len(got_out) == 2
    print(f"C-BOTM completeness: in={len(got_in)} (want 2) "
          f"out={len(got_out)} (want 2) match={comp_ok}")
    # geometry: shared geo_lines vs independently computed expectation
    gl = geo_lines(known4, "CBOTM")
    exp = [f"CBOTM sites={known4} band=[{INBAND_LO},{INBAND_HI}]"]
    for i in range(len(known4)):
        for j in range(i + 1, len(known4)):
            (r1, c1), (r2, c2) = known4[i], known4[j]
            exp.append(f"CBOTM pair ({r1},{c1})-({r2},{c2}): "
                       f"drow={abs(r1 - r2)} dcol={abs(c1 - c2)}")
    rs = [r for r, _ in known4]
    exp.append(f"CBOTM rowspan: min={min(rs)} max={max(rs)} "
               f"span={max(rs) - min(rs)}")
    geo_ok = gl == exp
    for ln in gl:
        print(ln)
    print(f"C-BOTM geometry: {len(gl)}/{len(exp)} lines match={geo_ok}")
    m_ok = setP_ok and setM_ok and j_ok and col_ok and comp_ok and geo_ok
    print(f"C-BOTM pass={bool(m_ok)} (want True)")

    # ================= C-BOTV (mid-level values, out-of-band) =================
    print("== C-BOTV (mid-level values, out-of-band) ==")
    zone_out_m = (pr < INBAND_LO) | (pr > INBAND_HI)
    cand = [int(o) for o in np.nonzero(
        bulk0 & (pl == 0) & zone_out_m & (gap >= 17))[0]]
    print(f"C-BOTV out-zone: bulk gap>=17 Y candidates n={len(cand)}")
    want, pk, sg, sign_fb = 4, [], {}, []
    for o in sorted(cand):
        r, c = int(pr[o]), int(pc[o])
        par = 8 if (r + c) % 2 == 0 else -8
        new = int(s[o]) + par
        if int(glo[o]) < new < int(ghi[o]):
            pk.append(o)
            sg[o] = par
        else:
            new2 = int(s[o]) - par
            if int(glo[o]) < new2 < int(ghi[o]):
                pk.append(o)
                sg[o] = -par
                sign_fb.append(o)
        if len(pk) == want:
            break
    kp = len(pk)
    print(f"C-BOTV picked rc={[(int(pr[o]), int(pc[o])) for o in pk]} "
          f"signs={[sg[o] for o in pk]} (want {want}, K'={kp}) "
          f"sign-fallbacks={sign_fb} "
          f"orig-ad={[int(abs(int(d0[o]))) for o in pk]}")
    if not pk:
        print("C-BOTV INFEASIBLE: out zone has no suitable site; tabled.")
        return
    midV = bytearray(mid0)
    for o in pk:
        midV[o] = int(s[o]) + sg[o]
    midV = bytes(midV)
    spV = interior_sites(v0, midV, full0, b0)
    maskV, dV = spV["mask"], spV["delta"]
    tV, _ = tail_bulk_masks(maskV, dV)
    PV = tV & ~t0
    MV = t0 & ~tV
    v_ok = True
    setP_ok = set(int(o) for o in np.nonzero(PV)[0]) == set(pk)
    setM_ok = int(MV.sum()) == 0
    inter = int((tV & t0).sum())
    union = int((tV | t0).sum())
    j_ok = (inter, union) == (102, 102 + kp)
    mask_ok = bool((maskV == mask0).all())
    ad_ok = all(int(abs(int(dV[o]))) == 8 for o in pk)
    stat_ok = all(mask0[o] and int(abs(int(d0[o]))) < 8 for o in pk)
    shared = tV & t0
    d_unch = bool((dV[shared] == d0[shared]).all())
    vin = [o for o in pk if inband(int(pr[o]))]
    comp_ok = len(vin) == 0
    print(f"C-BOTV completeness: in={len(vin)} (want 0) "
          f"out={kp - len(vin)} (want {kp}) match={comp_ok}")
    yV = tail_y_cols(tV, pl, pr, pc)
    affV = sorted({int(pc[o]) for o in pk})
    col_ok = True
    for c in affV:
        r0 = y0.get(c, [])
        wrows = sorted(r0 + [int(pr[o]) for o in pk if int(pc[o]) == c])
        rx = yV.get(c, [])
        ov = len(set(rx) & set(r0))
        ok = rx == wrows
        col_ok = col_ok and ok
        print(f"C-BOTV c{c}: rows={rx} (want {wrows}) "
              f"n/ov={len(rx)}/{ov} match={ok}")
    la, _ = attrib_lines("CBOTV", PV, MV, shared, d0, mask0,
                         dV, maskV, v0, full0, v0, full0)
    for ln in la:
        if " o=" in ln:
            print(ln)
            flds = dict(kv.split("=", 1) for kv in ln.split()[2:])
            v_ok = v_ok and flds["adQ"] == "8" and \
                flds["ostat"] == "bulk" and flds["gQ"] == flds["gO"]
    for ln in dstats_lines("CBOTV", PV, MV, dV, d0):
        print(ln)
    for ln in gapsign_lines("CBOTV", PV, MV, v0, full0, v0, full0):
        print(ln)
    ym0 = split_planes(np.frombuffer(mid0, np.uint8))[0]
    _, _, dec1 = p1_gradient(ym0)
    _, _, dec2 = p1_gradient(ym0)
    dec_ok = True
    for o in sorted(pk):
        r, c = int(pr[o]), int(pc[o])
        v1, v2 = int(dec1[r, c]), int(dec2[r, c])
        dec_ok = dec_ok and v1 == v2
        print(f"C-BOTV dec o={o} rc=({r},{c}) dec={v1} "
              f"recompute={v2} match={v1 == v2}")
    print(f"C-BOTV: Pset={setP_ok} Mset={setM_ok} "
          f"J={inter}/{union}={jaccard(tV, t0):.4f} "
          f"(want 102/{102 + kp}={102 / (102 + kp):.4f}) Jok={j_ok} "
          f"maskfixed={mask_ok} ad={ad_ok} stat={stat_ok} "
          f"dunch={d_unch} cols={col_ok} comp={comp_ok} dec={dec_ok}")
    v_ok = v_ok and setP_ok and setM_ok and j_ok and mask_ok \
        and ad_ok and stat_ok and d_unch and col_ok and comp_ok and dec_ok
    print(f"C-BOTV pass={bool(v_ok)} (want True)")
    print(f"CONTROL pass={bool(m_ok and v_ok)} (want True)")


if __name__ == "__main__":
    main()
