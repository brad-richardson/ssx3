#!/usr/bin/env python3
"""M19 positive controls: synthetic truths with KNOWN direction splits.

Usage: control.py M16_DIR

Imports direction_split + synth from m19.py (same dir); expectations
are analytic (D-min/D-max/D-v0) or independently counted (D-out).
The estimator must recover each exactly.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m19 import (BAND_ROWS, N, cell_band_shares, direction_split,  # noqa: E402
                 load_dump, synth_w_bytes, y_cell_map)


def independent_cells(v0b: bytes, midb: bytes, fullb: bytes, synth: bytes):
    """Independently written 8-cell count (boolean algebra, own order)."""
    a = np.frombuffer(v0b, np.uint8).astype(np.int16)
    m = np.frombuffer(midb, np.uint8).astype(np.int16)
    b = np.frombuffer(fullb, np.uint8).astype(np.int16)
    s = np.frombuffer(synth, np.uint8).astype(np.int16)
    res = np.not_equal(s, m)
    same = np.equal(a, b)
    mx = np.maximum(a, b)
    mn = np.minimum(a, b)
    ismax = np.equal(m, mx)
    ismin = np.equal(m, mn)
    isv0 = np.equal(m, a)
    isfull = np.equal(m, b)
    out = [0] * 8
    out[6] = int(np.sum(res & same))
    mv = res & ~same
    out[0] = int(np.sum(mv & isv0 & ismax))
    out[1] = int(np.sum(mv & isv0 & ismin))
    out[2] = int(np.sum(mv & isfull & ismax))
    out[3] = int(np.sum(mv & isfull & ismin))
    out[4] = int(np.sum(mv & (m > mx)))
    out[5] = int(np.sum(mv & (m < mn)))
    out[7] = int(np.sum(mv & (m > mn) & (m < mx)))
    return out, int(np.sum(res))


def main():
    m16d = Path(sys.argv[1])
    v0 = load_dump(m16d / "m16-v0-s0000.bin")
    full = load_dump(m16d / "m16-full-s0000.bin")
    blend = synth_w_bytes(v0, full, 0.5)
    a = np.frombuffer(v0, np.uint8).astype(np.int16)
    b = np.frombuffer(full, np.uint8).astype(np.int16)
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)

    allpass = True

    # D-min: mid = darker endpoint everywhere
    mid_min = lo.astype(np.uint8).tobytes()
    sp = direction_split(v0, mid_min, full, blend)
    c = [int(x) for x in sp["counts"]]
    want_zero = c[0] == 0 and c[2] == 0 and c[4] == 0 and c[5] == 0 \
        and c[6] == 0 and c[7] == 0
    want_tot = (c[1] + c[3]) == sp["n"]
    ok = want_zero and want_tot
    allpass &= ok
    print(f"D-min (mid=lo): n={sp['n']} cells={c} pass={ok}")

    # D-max: mid = brighter endpoint everywhere
    mid_max = hi.astype(np.uint8).tobytes()
    sp = direction_split(v0, mid_max, full, blend)
    c = [int(x) for x in sp["counts"]]
    want_zero = c[1] == 0 and c[3] == 0 and c[4] == 0 and c[5] == 0 \
        and c[6] == 0 and c[7] == 0
    want_tot = (c[0] + c[2]) == sp["n"]
    ok = want_zero and want_tot
    allpass &= ok
    print(f"D-max (mid=hi): n={sp['n']} cells={c} pass={ok}")

    # D-v0: mid = v0 everywhere
    sp = direction_split(v0, v0, full, blend)
    c = [int(x) for x in sp["counts"]]
    want_zero = c[2] == 0 and c[3] == 0 and c[4] == 0 and c[5] == 0 \
        and c[6] == 0 and c[7] == 0
    want_tot = (c[0] + c[1]) == sp["n"]
    ok = want_zero and want_tot
    allpass &= ok
    print(f"D-v0 (mid=v0): n={sp['n']} cells={c} pass={ok}")

    # D-out: mid = lo-1 (lo>0) else lo; independent-count comparison
    mid_out = np.where(lo > 0, lo - 1, lo).astype(np.uint8).tobytes()
    sp = direction_split(v0, mid_out, full, blend)
    c = [int(x) for x in sp["counts"]]
    exp, nexp = independent_cells(v0, mid_out, full, blend)
    ok = (c == exp and sp["n"] == nexp and c[4] == 0 and c[7] == 0)
    allpass &= ok
    print(f"D-out (mid=lo-1): n={sp['n']} cells={c} expected={exp} pass={ok}")

    # B-share: band shares are fractional, unit-sum, match band counts.
    # Regression: an int() cast once truncated every share to 0.0000.
    sp = direction_split(v0, mid_min, full, blend)
    ym = y_cell_map(sp["labels"])
    shares = cell_band_shares(ym)
    ok = True
    frac_seen = False
    for c in range(8):
        tot = int((ym == c).sum())
        ss = shares[c]
        if tot == 0:
            ok &= all(s == 0.0 for s in ss)
            continue
        ok &= all(0.0 <= s <= 1.0 for s in ss)
        ok &= abs(sum(ss) - 1.0) < 1e-9
        for s, rows in zip(ss, BAND_ROWS):
            ok &= abs(s * tot - int((ym[rows] == c).sum())) < 1e-6
        frac_seen |= any(0.0 < s < 1.0 for s in ss)
    ok &= frac_seen
    allpass &= ok
    print(f"B-share (band fractions on D-min): frac_seen={frac_seen} pass={ok}")

    print(f"controls: {'ALL PASS' if allpass else 'FAIL'}")


if __name__ == "__main__":
    main()
