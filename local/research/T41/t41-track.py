#!/usr/bin/env python3
"""T38 rider-pixel tracker (frozen pre-run).

T37's RDC + SCPS(+-40) unchanged (comparability), plus the two cheap T37
recipe refinements:

  RDC validity gate: VALID iff 200 <= npix <= 6000 (rider-scale band;
      T37 calibration: valid snaps npix 1299-3786, mixed 8595-12177,
      flooded >= 18624; T36 npre rider-clean 2462). Gated-out snaps print
      tag INVALID and their cx/cy must not be used for deltas.
  SCPS wide window: SCPS120 = same normalized-xcorr column-profile shift
      over lag in [-120,+120] (T37 railed +-40 nearly every step incl. the
      no-input pre-pair gap at ~3 s exposure gaps under turbo).

Game area x[0,647] y[24,511] of the 1280x1024 snap (T36 npre bbox).
RDC: centroid (px, 0.1) of dark pixels (luminance < 80) inside rider ROI
x[150,540] y[100,460]. SCPS band: rows y[380,460], cols x[150,540].

Noise floor: |M(pre2) - M(pre1)| over the no-input pre-hold pair gap.
Deterministic: identical bytes in -> identical numbers out (no RNG).

Usage: t38-track.py snap1.jpg [snap2.jpg ...]
  Prints per-snap RDC (+ validity tag) + per-consecutive-pair SCPS40 and
  SCPS120, one line each.
"""
import sys

import numpy as np
from PIL import Image

RIDER_ROI = (150, 100, 540, 460)  # x0, y0, x1, y1 (x1/y1 exclusive)
SNOW_ROWS = (380, 460)
SNOW_COLS = (150, 540)
DARK_MAX = 80
LAG_MAX = 40
LAG_MAX_WIDE = 120
RDC_NPIX_MIN = 200
RDC_NPIX_MAX = 6000


def load_luma(path):
    return np.asarray(Image.open(path).convert("L"), dtype=np.float64)


def rider_centroid(luma):
    x0, y0, x1, y1 = RIDER_ROI
    roi = luma[y0:y1, x0:x1]
    mask = roi < DARK_MAX
    npix = int(mask.sum())
    frac = npix / mask.size
    if npix == 0:
        return (float("nan"), float("nan"), 0, 0.0)
    ys, xs = np.nonzero(mask)
    return (x0 + xs.mean(), y0 + ys.mean(), npix, frac)


def rdc_valid(npix):
    return RDC_NPIX_MIN <= npix <= RDC_NPIX_MAX


def snow_shift(prev, cur, lag_max=LAG_MAX):
    r0, r1 = SNOW_ROWS
    c0, c1 = SNOW_COLS
    a = prev[r0:r1, c0:c1].mean(axis=0)
    b = cur[r0:r1, c0:c1].mean(axis=0)
    a = a - a.mean()
    b = b - b.mean()
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return (0, 0.0)
    best_lag, best_corr = 0, -2.0
    for lag in range(-lag_max, lag_max + 1):
        if lag >= 0:
            aa, bb = a[: len(a) - lag], b[lag:]
        else:
            aa, bb = a[-lag:], b[: len(b) + lag]
        corr = float(np.dot(aa, bb) / (np.linalg.norm(aa) * np.linalg.norm(bb)))
        if corr > best_corr:
            best_corr, best_lag = corr, lag
    return (best_lag, best_corr)


def main(paths):
    lumas = [load_luma(p) for p in paths]
    for p, lum in zip(paths, lumas):
        cx, cy, npix, frac = rider_centroid(lum)
        tag = "VALID" if rdc_valid(npix) else "INVALID"
        print(f"RDC {p} cx={cx:.1f} cy={cy:.1f} npix={npix} frac={frac:.4f} {tag}")
    for p0, p1, a, b in zip(paths, paths[1:], lumas, lumas[1:]):
        lag, corr = snow_shift(a, b, LAG_MAX)
        print(f"SCPS40 {p0} -> {p1} lag={lag:+d} corr={corr:.4f}")
    for p0, p1, a, b in zip(paths, paths[1:], lumas, lumas[1:]):
        lag, corr = snow_shift(a, b, LAG_MAX_WIDE)
        print(f"SCPS120 {p0} -> {p1} lag={lag:+d} corr={corr:.4f}")


if __name__ == "__main__":
    main(sys.argv[1:])
