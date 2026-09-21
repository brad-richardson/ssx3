#!/usr/bin/env python3
"""T42 rider-pixel tracker: T41's frozen tracker with a SMALLER RIDER ROI.

T42 retune (T40-G1 second arm, T41 G1/G2 recipe): RIDER_ROI shrunk from
x[150,540] y[100,460] to x[220,180,420,360] (area 140400 -> 36000 px) to
exclude forest trunks / arch shade / barrier tops / wall edges that
flooded 11/12 of T41's dense snaps at ~0.57 s exposures. Everything else
is FROZEN: DARK_MAX 80, gate 200..6000, SCPS40/SCPS120 untouched.

Calibration (T41 R4's 12 committed dense snaps, static): retuned npix
1138-3926 VALID on 11/11 non-wall snaps (frozen gate untouched), d-post10
wall 12609 INVALID (correctly gated); centroids on/borderline-on the
rider complex on 7/11, off-rider but in-band on 4/11 with named causes
(d2/d3 adjacent tree, d6 barrier, d9 gate pole). Held-out T40 snaps
(no tuning): 8/12 VALID vs frozen 2/12. See T42 REPORT for the full
calibration table. Deterministic: identical bytes in -> identical out.

Usage: t42-track.py snap1.jpg [snap2.jpg ...]
  Prints per-snap RDC (+ validity tag) + per-consecutive-pair SCPS40 and
  SCPS120, one line each.
"""
import sys

import numpy as np
from PIL import Image

RIDER_ROI = (220, 180, 420, 360)  # x0, y0, x1, y1 (x1/y1 exclusive)
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
