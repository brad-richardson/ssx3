#!/usr/bin/env python3
"""M25 positive control C-P1: known column profiles (offline).

Usage: control.py M16_DIR  (run from the work dir; importable m25 nearby)

Synthetic truth mid' on s0: N=60 sites from the M24 union pool
(interior-BULK gap>=17 + ENDPOINT gap>=32, offset order; skips
counted), first 30 passing -> pseudo-column A listed delta=+10
(constant, listed gradient 0), next 30 passing -> pseudo-column B
listed delta=+14 (constant, listed gradient 0). Recompute cell 7 +
tail from (v0,mid',full): tail set must equal T_s0 union injected
exactly (count 162 + values + map), originals unchanged. Profile
recovery: pseudo-column row->delta lists + medians must read the
listed constants exactly. Restricted fits on injected-only must
read CONST 60/60 and LINEAR 60/60 (slope exactly 0.0, tie) with
argmax CONST by list-order tie-break; SIGNC tabled. Tables only.
"""
import sys
import time
from pathlib import Path

import numpy as np

import m25

N_WANT = 60
PER_COL = 30
LISTED = {"A": 10, "B": 14}  # listed constants; listed gradients 0/0


def main():
    m16d = Path(sys.argv[1])
    t0 = time.time()
    rr, cc = m25.plane_coords()
    pl = m25.plane_of_byte()

    v0 = m25.load_dump(m16d / "m16-v0-s0000.bin")
    mid = m25.load_dump(m16d / "m16-mid-s0000.bin")
    full = m25.load_dump(m16d / "m16-full-s0000.bin")
    synth = m25.synth_w_bytes(v0, full, 0.5)
    sp = m25.interior_sites(v0, mid, full, synth)
    mask, delta = sp["mask"], sp["delta"]
    print(f"control C-P1: s0 cell7 n={sp['n']} (want 2475)")
    tail0, bulk0 = m25.tail_bulk_masks(mask, delta)
    print(f"control C-P1: s0 tail n={int(tail0.sum())} (want 102)")

    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    m = np.frombuffer(mid, np.uint8).astype(np.int16)
    b = np.frombuffer(full, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    g = (a - b).astype(np.int16)
    ag = np.abs(g)
    moved = a != b
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)
    endpoint = moved & ((m == lo) | (m == hi))

    pool_bulk = np.flatnonzero(bulk0 & (ag >= 17))
    pool_endp = np.flatnonzero(endpoint & ~mask & (ag >= 32))
    pool = np.array(sorted(set(pool_bulk.tolist())
                           | set(pool_endp.tolist())), np.int64)
    print(f"control C-P1: pool bulk-gap>=17 n={len(pool_bulk)} + "
          f"endpoint-gap>=32 n={len(pool_endp)} union n={len(pool)}")

    # Choose N sites in offset order; first 30 -> A (+10), next 30 -> B.
    chosen, skips = [], 0
    for o in pool.tolist():
        if len(chosen) >= N_WANT:
            break
        want = LISTED["A"] if len(chosen) < PER_COL else LISTED["B"]
        midp = int(s[o]) + want
        if not (int(lo[o]) < midp < int(hi[o])):
            skips += 1
            continue
        chosen.append((int(o), want))
    na = sum(1 for _, w in chosen if w == LISTED["A"])
    nb = sum(1 for _, w in chosen if w == LISTED["B"])
    print(f"control C-P1: chose {len(chosen)}/{N_WANT} "
          f"(A={na} B={nb}; skips={skips})")
    if len(chosen) != N_WANT or na != PER_COL or nb != PER_COL:
        print("control C-P1: SHORTFALL (feasibility): tabled, stop.")
        return

    midp = bytearray(mid)
    for o, want in chosen:
        midp[o] = int(s[o]) + want
    midp = bytes(midp)
    spc = m25.interior_sites(v0, midp, full, synth)
    tailc, _ = m25.tail_bulk_masks(spc["mask"], spc["delta"])
    injset = {o for o, _ in chosen}
    t0set = set(np.flatnonzero(tail0).tolist())
    tcset = set(np.flatnonzero(tailc).tolist())
    print(f"control C-P1: control tail n={len(tcset)} "
          f"(want {len(t0set) + N_WANT})")
    print(f"control C-P1: set exact={tcset == (t0set | injset)} "
          f"disjoint_orig={len(t0set & injset) == 0}")
    vals_ok = all(int(spc["delta"][o]) == w for o, w in chosen)
    orig_ok = all(int(spc["delta"][o]) == int(delta[o]) for o in t0set)
    print(f"control C-P1: injected values exact={vals_ok} "
          f"originals unchanged={orig_ok}")
    jv = m25.jaccard(tailc, tail0 | np.isin(np.arange(m25.N),
                                            np.array(sorted(injset))))
    print(f"control C-P1: map jaccard vs T+inj = {jv:.4f} (want 1.0)")

    # Profile recovery on pseudo-columns (row->delta lists + medians).
    for grp, want in (("A", LISTED["A"]), ("B", LISTED["B"])):
        offs = sorted(o for o, w in chosen if w == want)
        dd = [int(spc["delta"][o]) for o in offs]
        med = m25.int_median(dd)
        print(f"control C-P1: pseudo-col {grp}: n={len(offs)} "
              f"median={med} (want {want}) all_exact={all(x == want for x in dd)} "
              f"rows: {' '.join(str(int(rr[o])) for o in offs)}")

    # Restricted fits on injected-only (known truth).
    for grp, want in (("A", LISTED["A"]), ("B", LISTED["B"])):
        offs = np.array(sorted(o for o, w in chosen if w == want))
        rows = rr[offs]
        dd = np.array([int(spc["delta"][o]) for o in offs], np.int64)
        med = m25.int_median(dd)
        lf = m25.linfit(rows, dd)
        pc = np.full(len(dd), med, np.int64)
        if lf is None:
            plin = pc.copy()
            lfstr = "CONST-fb"
        else:
            ae, be = lf
            plin = np.array([m25.rhalf(ae + be * float(r)) for r in rows],
                            np.int64)
            lfstr = f"a={ae:.4f},b={be:.4f}"
        gg = g[offs].astype(np.int64)
        ps = np.sign(med).astype(np.int64) * ((9 * np.abs(gg) + 10) // 20)
        hc = int((pc == dd).sum())
        hl = int((plin == dd).sum())
        hs = int((ps == dd).sum())
        print(f"control C-P1: restricted {grp}: CONST {hc}/{len(dd)} "
              f"LINEAR {hl}/{len(dd)} ({lfstr}) SIGNC {hs}/{len(dd)}")
    # Pooled identity.
    print(f"control C-P1: pooled CONST 60/60 expect + LINEAR 60/60 expect "
          f"(slope exactly 0.0, tie) -> argmax CONST by list order")
    ok = True
    for grp, want in (("A", LISTED["A"]), ("B", LISTED["B"])):
        offs = np.array(sorted(o for o, w in chosen if w == want))
        dd = np.array([int(spc["delta"][o]) for o in offs], np.int64)
        lf = m25.linfit(rr[offs], dd)
        ok = ok and (lf is not None and lf[1] == 0.0
                     and m25.int_median(dd) == want)
    print(f"control C-P1: identity CONST (tie-break) recovered exactly={ok}")

    # Full-control-frame scores (fit on control frame, M23/M24 precedent).
    print("control C-P1: full-control-frame scores (fit on control frame):")
    offc = np.flatnonzero(tailc)
    dtc = spc["delta"][tailc].astype(np.int64)
    gtc = g[tailc].astype(np.int64)
    isy = pl[offc] == 0
    cfit, lfit, sfit = {}, {}, {}
    for ccol in m25.NAMED_COLS:
        sel = isy & (cc[offc] == ccol)
        dd = dtc[sel]
        cfit[ccol] = m25.int_median(dd) if len(dd) else 0
        lfit[ccol] = m25.linfit(rr[offc[sel]], dd) if len(dd) else None
        mu = float(dd.mean()) if len(dd) else 0.0
        sfit[ccol] = 1 if mu >= 0 else -1
    for fid in m25.FIT_IDS:
        tall, pall = [], []
        for ccol in m25.NAMED_COLS:
            sel = isy & (cc[offc] == ccol)
            t = dtc[sel]
            if fid == "CONST":
                p = np.full(len(t), cfit[ccol], np.int64)
            elif fid == "LINEAR":
                if lfit[ccol] is None:
                    p = np.full(len(t), cfit[ccol], np.int64)
                else:
                    ae, be = lfit[ccol]
                    p = np.array([m25.rhalf(ae + be * float(r))
                                  for r in rr[offc[sel]]], np.int64)
            else:
                p = (sfit[ccol]
                     * ((9 * np.abs(gtc[sel]) + 10) // 20)).astype(np.int64)
            tall.append(t)
            pall.append(p)
        t = np.concatenate(tall)
        p = np.concatenate(pall)
        ae = np.abs(p - t)
        print(f"control C-P1: full-frame {fid}: n={len(t)} "
              f"hits={int((ae == 0).sum())} near={int((ae == 1).sum())} "
              f"errvalues: {m25.exact_counts(ae)}")

    print(f"control C-P1: wall={time.time() - t0:.1f}s "
          f"pass={vals_ok and orig_ok and tcset == (t0set | injset) and ok}")


if __name__ == "__main__":
    main()
