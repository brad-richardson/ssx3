#!/usr/bin/env python3
"""M58 control C-OFF51: known off-mode seats on a synthetic plane (offline).

Pure-synthetic (no dumps): seats/selection/histograms operate on
(plane, sites), so a synthetic plane exercises the identical m58 code
path (seat_of, off51_select, col_counts, band_hist, decile_hist,
ROW_BAND) with zero dump coupling. Carrier N/A synthetic (no masks,
disclosed, no expectation); peak N/A synthetic (cols=None, disclosed,
no expectation).

Synthetic plane 8x12 (DESIGN.md pinned): cols 0-5 dec 9 (mode block),
cols 6-7 dec 3 (off-mode block), col 8 dec 0, col 9 dec 1, col 10
dec 4, col 11 dec 5. Sites: M1-M6 mode (dec 9 x6), F1-F6 off-mode
(dec 3 x2, 0, 1, 4, 5).
Tables, no verdicts.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m58 import (ROW_BAND, band_hist, col_counts, decile_hist,  # noqa: E402
                 off51_select, seat_of)

PLANE = np.zeros((8, 12), np.int32)
PLANE[:, 0:6] = 9
PLANE[:, 6:8] = 3
PLANE[:, 8] = 0
PLANE[:, 9] = 1
PLANE[:, 10] = 4
PLANE[:, 11] = 5

SITES = {
    "M1": ((0, 0), 9), "M2": ((1, 1), 9), "M3": ((2, 2), 9),
    "M4": ((3, 3), 9), "M5": ((4, 4), 9), "M6": ((5, 5), 9),
    "F1": ((0, 6), 3), "F2": ((1, 7), 3), "F3": ((2, 8), 0),
    "F4": ((3, 9), 1), "F5": ((4, 10), 4), "F6": ((5, 11), 5),
}

WANT_OFF = [(0, 8, 2), (1, 9, 3), (3, 6, 0), (3, 7, 1),
            (4, 10, 4), (5, 11, 5)]  # (dec, col, row) sorted
WANT_COLS = {6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1}
WANT_BAND = {0: 12}
WANT_HIST = {0: 1, 1: 1, 2: 0, 3: 2, 4: 1, 5: 1, 6: 0, 7: 0,
             8: 0, 9: 6}


def main():
    ok = True
    for name in ("M1", "M2", "M3", "M4", "M5", "M6",
                 "F1", "F2", "F3", "F4", "F5", "F6"):
        (r, c), want_dec = SITES[name]
        st = seat_of(r, c, None, PLANE, None)
        m_dec = st["dec"] == want_dec
        m_band = st["band"] == int(ROW_BAND[r]) == 0
        m_streak = st["streak"] == "other"
        print(f"C-OFF51 {name} rc=({r},{c}): dec={st['dec']} "
              f"(want {want_dec}) match={m_dec}")
        print(f"C-OFF51 {name} band={st['band']} (want 0) "
              f"match={m_band} streak={st['streak']} match={m_streak} "
              f"carrier={st['carrier_in']} split701={st['split701']} "
              f"peak={st['peak']} atpeak={st['atpeak']}")
        if not (m_dec and m_band and m_streak):
            ok = False
        if not (st["carrier_in"] is None and st["split701"] is None
                and st["peak"] is None and st["atpeak"] is None):
            print(f"C-OFF51 {name} N/A-SEAT MISMATCH")
            ok = False
    sites = [rc for rc, _ in SITES.values()]
    off = off51_select(sites, PLANE)
    m_off = [tuple(t) for t in off] == WANT_OFF
    print(f"C-OFF51 select: {off} (want {WANT_OFF}) match={m_off}")
    if not m_off:
        ok = False
    offrc = [(r, c) for (dec, c, r) in off]
    cc = col_counts(offrc)
    m_cc = cc == WANT_COLS
    print(f"C-OFF51 coltable: {cc} (want {WANT_COLS}) match={m_cc}")
    if not m_cc:
        ok = False
    bh = band_hist(sites)
    m_bh = bh == WANT_BAND
    print(f"C-OFF51 bandhist: {bh} (want {WANT_BAND}) match={m_bh}")
    if not m_bh:
        ok = False
    hh = decile_hist(sites, PLANE)
    m_hist = hh["counts"] == WANT_HIST
    m_n = hh["n"] == 12
    m_d9 = abs(hh["dec9share"] - 0.5) < 1e-12
    m_mode = hh["mode"] == 9 and abs(hh["modeshare"] - 0.5) < 1e-12
    m_r3 = hh["rank_of"](3) == 2
    print(f"C-OFF51 hist: counts={hh['counts']} (want {WANT_HIST}) "
          f"match={m_hist}")
    print(f"C-OFF51 hist: n={hh['n']} (want 12) match={m_n} "
          f"dec9share={hh['dec9share']:.4f} (want 0.5000) match={m_d9}")
    print(f"C-OFF51 hist: mode={hh['mode']} "
          f"modeshare={hh['modeshare']:.4f} (want 9/0.5000) "
          f"match={m_mode} rank3={hh['rank_of'](3)} (want 2) "
          f"match={m_r3}")
    if not (m_hist and m_n and m_d9 and m_mode and m_r3):
        ok = False
    print("C-OFF51 carrier/peak: N/A synthetic (no masks/cols, disclosed)")
    print(f"C-OFF51 pass={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
