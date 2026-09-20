#!/usr/bin/env python3
"""M57 control C-DEC1: known decile seats on a synthetic plane (offline).

Pure-synthetic (no dumps): seats/histograms operate on (plane, sites),
so a synthetic plane exercises the identical m57 code path (seat_of,
decile_hist, ROW_BAND) with zero dump coupling. Carrier N/A synthetic
(no masks, disclosed, no expectation); peak N/A synthetic (cols=None,
disclosed, no expectation).

Synthetic plane 6x12 (DESIGN.md pinned): cols 0-5 dec 9 (mode block),
cols 6-7 dec 3 (off-mode block), col 8 dec 6, col 9 dec 7, col 10
dec 8, col 11 dec 0. Sites: M1-M6 mode (dec 9 x6), F1-F3 off-mode
(dec 3 x3), E1-E3 edge (dec 6/7/8).
Tables, no verdicts.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m57 import ROW_BAND, decile_hist, seat_of

PLANE = np.zeros((6, 12), np.int32)
PLANE[:, 0:6] = 9
PLANE[:, 6:8] = 3
PLANE[:, 8] = 6
PLANE[:, 9] = 7
PLANE[:, 10] = 8
PLANE[:, 11] = 0

SITES = {
    "M1": ((0, 0), 9), "M2": ((1, 1), 9), "M3": ((2, 2), 9),
    "M4": ((3, 3), 9), "M5": ((4, 4), 9), "M6": ((5, 5), 9),
    "F1": ((0, 6), 3), "F2": ((1, 7), 3), "F3": ((2, 6), 3),
    "E1": ((0, 8), 6), "E2": ((0, 9), 7), "E3": ((0, 10), 8),
}

WANT_HIST = {0: 0, 1: 0, 2: 0, 3: 3, 4: 0, 5: 0, 6: 1, 7: 1,
             8: 1, 9: 6}


def main():
    ok = True
    for name in ("M1", "M2", "M3", "M4", "M5", "M6",
                 "F1", "F2", "F3", "E1", "E2", "E3"):
        (r, c), want_dec = SITES[name]
        st = seat_of(r, c, None, PLANE, None)
        m_dec = st["dec"] == want_dec
        m_band = st["band"] == int(ROW_BAND[r]) == 0
        m_streak = st["streak"] == "other"
        print(f"C-DEC1 {name} rc=({r},{c}): dec={st['dec']} "
              f"(want {want_dec}) match={m_dec}")
        print(f"C-DEC1 {name} band={st['band']} (want 0) "
              f"match={m_band} streak={st['streak']} match={m_streak} "
              f"carrier={st['carrier_in']} split701={st['split701']} "
              f"peak={st['peak']} atpeak={st['atpeak']}")
        if not (m_dec and m_band and m_streak):
            ok = False
        if not (st["carrier_in"] is None and st["split701"] is None
                and st["peak"] is None and st["atpeak"] is None):
            print(f"C-DEC1 {name} N/A-SEAT MISMATCH")
            ok = False
    sites = [rc for rc, _ in SITES.values()]
    hh = decile_hist(sites, PLANE)
    m_hist = hh["counts"] == WANT_HIST
    m_n = hh["n"] == 12
    m_d9 = abs(hh["dec9share"] - 0.5) < 1e-12
    m_mode = hh["mode"] == 9 and abs(hh["modeshare"] - 0.5) < 1e-12
    m_r3 = hh["rank_of"](3) == 2
    print(f"C-DEC1 hist: counts={hh['counts']} (want {WANT_HIST}) "
          f"match={m_hist}")
    print(f"C-DEC1 hist: n={hh['n']} (want 12) match={m_n} "
          f"dec9share={hh['dec9share']:.4f} (want 0.5000) match={m_d9}")
    print(f"C-DEC1 hist: mode={hh['mode']} "
          f"modeshare={hh['modeshare']:.4f} (want 9/0.5000) "
          f"match={m_mode} rank3={hh['rank_of'](3)} (want 2) "
          f"match={m_r3}")
    if not (m_hist and m_n and m_d9 and m_mode and m_r3):
        ok = False
    print("C-DEC1 carrier/peak: N/A synthetic (no masks/cols, disclosed)")
    print(f"C-DEC1 pass={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
