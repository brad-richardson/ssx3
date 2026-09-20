#!/usr/bin/env python3
"""M50 positive control: synthetic truth with KNOWN wipe+dest sets.

Usage: control.py (no args; fully synthetic — no dump reads)

Imports interior_sites + tail core from m50.py (same dir);
expectations are analytic. Frames A/B are full 573440-B
synthetic triplets (all zeros = static non-cell background)
with hand-set Y sites via off_of:

- C-WIPEDEST (known wipe+dest sets incl. KNOWN g==0 sites):
  N_STATIC=3 wipe sites (tail on A |d|=10, g_A!=0; static
  non-cell on B g_B==0) + N_NONSTATIC=3 wipe sites (tail on A
  |d|=10; bulk on B |d|=2, g_B!=0) + N_STATIC=3 dest sites
  (static non-cell on A g_A==0; tail on B |d|=10) +
  N_NONSTATIC=3 dest sites (bulk on A |d|=2; tail on B |d|=10)
  + N_KEPT=2 kept sites (tail both frames |d|=10, g!=0 both).
  Tail values: v0=0/full=100/blend=50/mid=60 (|d|=10); bulk
  values: mid=52 (|d|=2); static values: v0=full=50/mid=50
  (g==0, non-cell). The recomputed wipe set (T_A-T_B) must
  equal the injected 6 exactly, dest set (T_B-T_A) the injected
  6 exactly, kept 2 exactly, J must equal 2/14 = 0.1429
  exactly, per-site |d| exact, statuses exact (3 bulk + 3
  noncell per side), gaps exact (g==0 on the 6 static legs,
  g=-100 elsewhere), static census exact (wiped g_B==0 3/6,
  dest g_A==0 3/6, kept g==0 0/2 either frame), per-column
  row-lists + standings exact, all background bytes non-tail.

The estimator must recover the injected counts + sets +
Jaccard + row-lists + per-site values + gaps + static census
exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m50 import (N, interior_sites, jaccard, off_of,  # noqa: E402
                 plane_coords, plane_of_byte, synth_w_bytes,
                 tail_bulk_masks, tail_y_cols)


def paint(arr, o, v):
    arr[o] = v


def main():
    pl = plane_of_byte()
    pr, pc = plane_coords()

    # ---- synthetic frames (all-zero background: v0==mid==full==0) ----
    v0A = np.zeros(N, np.uint8)
    midA = np.zeros(N, np.uint8)
    fullA = np.zeros(N, np.uint8)
    v0B = np.zeros(N, np.uint8)
    midB = np.zeros(N, np.uint8)
    fullB = np.zeros(N, np.uint8)

    # site plan: distinct Y sites; wipe col 100/101, dest col 102/103,
    # kept col 104. Rows 25..30.
    wipe_st = [off_of(r, 100) for r in (25, 26, 27)]  # static on B
    wipe_ns = [off_of(r, 101) for r in (25, 26, 27)]  # bulk on B
    dest_st = [off_of(r, 102) for r in (25, 26, 27)]  # static on A
    dest_ns = [off_of(r, 103) for r in (25, 26, 27)]  # bulk on A
    kept = [off_of(25, 104), off_of(26, 104)]

    def set_tail(v0a, mida, fulla, o):
        paint(v0a, o, 0)
        paint(fulla, o, 100)
        paint(mida, o, 60)  # blend 50 -> d=+10 tail

    def set_bulk(v0a, mida, fulla, o):
        paint(v0a, o, 0)
        paint(fulla, o, 100)
        paint(mida, o, 52)  # blend 50 -> d=+2 bulk

    def set_static(v0a, mida, fulla, o):
        paint(v0a, o, 50)
        paint(fulla, o, 50)
        paint(mida, o, 50)  # g==0, moved=False -> non-cell

    for o in wipe_st + wipe_ns:
        set_tail(v0A, midA, fullA, o)
    for o in wipe_st:
        set_static(v0B, midB, fullB, o)
    for o in wipe_ns:
        set_bulk(v0B, midB, fullB, o)
    for o in dest_st + dest_ns:
        set_tail(v0B, midB, fullB, o)
    for o in dest_st:
        set_static(v0A, midA, fullA, o)
    for o in dest_ns:
        set_bulk(v0A, midA, fullA, o)
    for o in kept:
        set_tail(v0A, midA, fullA, o)
        set_tail(v0B, midB, fullB, o)

    v0Ab, midAb, fullAb = v0A.tobytes(), midA.tobytes(), fullA.tobytes()
    v0Bb, midBb, fullBb = v0B.tobytes(), midB.tobytes(), fullB.tobytes()
    synA = synth_w_bytes(v0Ab, fullAb, 0.5)
    synB = synth_w_bytes(v0Bb, fullBb, 0.5)
    spA = interior_sites(v0Ab, midAb, fullAb, synA)
    spB = interior_sites(v0Bb, midBb, fullBb, synB)
    tA, _ = tail_bulk_masks(spA["mask"], spA["delta"])
    tB, _ = tail_bulk_masks(spB["mask"], spB["delta"])
    print(f"C-WIPEDEST: cellA={spA['n']} tailA={int(tA.sum())} "
          f"(want 11/8: 8 tail + 3 bulk) cellB={spB['n']} "
          f"tailB={int(tB.sum())} (want 11/8)")

    # ---- sets + J ----
    want_wipe = np.zeros(N, bool)
    want_wipe[wipe_st + wipe_ns] = True
    want_dest = np.zeros(N, bool)
    want_dest[dest_st + dest_ns] = True
    want_kept = np.zeros(N, bool)
    want_kept[kept] = True
    wipe = tA & ~tB
    dest = tB & ~tA
    shared = tA & tB
    jj = jaccard(tB, tA)
    set_w_ok = bool((wipe == want_wipe).all())
    set_d_ok = bool((dest == want_dest).all())
    set_k_ok = bool((shared == want_kept).all())
    j_ok = f"{jj:.4f}" == "0.1429"
    print(f"C-WIPEDEST: wipe_n={int(wipe.sum())} (want 6) "
          f"dest_n={int(dest.sum())} (want 6) "
          f"kept_n={int(shared.sum())} (want 2) J={jj:.4f} "
          f"(want 0.1429) sets_exact={set_w_ok and set_d_ok and set_k_ok} "
          f"j_exact={j_ok}")

    # ---- per-site values + statuses + gaps ----
    dA, dB = spA["delta"], spB["delta"]
    mA, mB = spA["mask"], spB["mask"]
    aA = v0A.astype(np.int16)
    fA = fullA.astype(np.int16)
    aB = v0B.astype(np.int16)
    fB = fullB.astype(np.int16)
    gA, gB = aA - fA, aB - fB
    val_ok = all(int(dA[o]) == 10 for o in wipe_st + wipe_ns)
    val_ok = val_ok and all(int(dB[o]) == 10 for o in dest_st + dest_ns)
    val_ok = val_ok and all(int(dB[o]) == 2 for o in wipe_ns)
    val_ok = val_ok and all(int(dA[o]) == 2 for o in dest_ns)
    val_ok = val_ok and all(int(dA[o]) == 10 and int(dB[o]) == 10
                           for o in kept)
    ostat_w_ok = (all((not mB[o]) for o in wipe_st)
                  and all(bool(mB[o]) and int(abs(int(dB[o]))) == 2
                          for o in wipe_ns))
    ostat_d_ok = (all((not mA[o]) for o in dest_st)
                  and all(bool(mA[o]) and int(abs(int(dA[o]))) == 2
                          for o in dest_ns))
    gap_w_ok = (all(int(gB[o]) == 0 for o in wipe_st)
                and all(int(gB[o]) == -100 for o in wipe_ns)
                and all(int(gA[o]) == -100 for o in wipe_st + wipe_ns))
    gap_d_ok = (all(int(gA[o]) == 0 for o in dest_st)
                and all(int(gA[o]) == -100 for o in dest_ns)
                and all(int(gB[o]) == -100 for o in dest_st + dest_ns))
    gap_k_ok = all(int(gA[o]) == -100 and int(gB[o]) == -100
                     for o in kept)
    print(f"C-WIPEDEST: values_exact={val_ok} ostat_w={ostat_w_ok} "
          f"ostat_d={ostat_d_ok} gaps_w={gap_w_ok} gaps_d={gap_d_ok} "
          f"gaps_k={gap_k_ok}")

    # ---- static census ----
    w_q0 = sum(1 for o in wipe_st + wipe_ns if int(gB[o]) == 0)
    d_a0 = sum(1 for o in dest_st + dest_ns if int(gA[o]) == 0)
    k_e0 = sum(1 for o in kept
               if int(gA[o]) == 0 or int(gB[o]) == 0)
    cen_ok = (w_q0 == 3 and d_a0 == 3 and k_e0 == 0)
    print(f"C-WIPEDEST: wiped gB==0 {w_q0}/6 (want 3) dest gA==0 "
          f"{d_a0}/6 (want 3) kept either0 {k_e0}/2 (want 0) "
          f"census_exact={cen_ok}")

    # ---- per-column row-lists + standings ----
    yA = tail_y_cols(tA, pl, pr, pc)
    yB = tail_y_cols(tB, pl, pr, pc)
    stand_ok = True
    for c, kind in ((100, "missing"), (101, "missing"),
                    (102, "extra"), (103, "extra")):
        rA, rB = yA.get(c, []), yB.get(c, [])
        ov = len(set(rA) & set(rB))
        mm, ee = len(rA) - ov, len(rB) - ov
        stand = ("missing" if mm > 0 and ee == 0
                 else ("extra" if mm == 0 and ee > 0 else "mixed"))
        good = stand == kind and ((mm == 3 and ee == 0)
                                  if kind == "missing"
                                  else (mm == 0 and ee == 3))
        stand_ok = stand_ok and good
        print(f"C-WIPEDEST col {c}: rowsA={rA} rowsB={rB} "
              f"miss/extra={mm}/{ee} stand={stand} rows-exact={good}")
    rAk, rBk = yA.get(104, []), yB.get(104, [])
    kept_col_ok = (rAk == [25, 26] and rBk == [25, 26])
    stand_ok = stand_ok and kept_col_ok
    print(f"C-WIPEDEST col 104 (kept): rowsA={rAk} rowsB={rBk} "
          f"kept-exact={kept_col_ok}")

    # ---- background: no other tail ----
    bg_ok = (int(tA.sum()) == 8 and int(tB.sum()) == 8)
    ok = (set_w_ok and set_d_ok and set_k_ok and j_ok and val_ok
          and ostat_w_ok and ostat_d_ok and gap_w_ok and gap_d_ok
          and gap_k_ok and cen_ok and stand_ok and bg_ok)
    print(f"C-WIPEDEST: pass={ok}")
    print(f"controls pass={bool(ok)}")


if __name__ == "__main__":
    main()
