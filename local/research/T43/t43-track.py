#!/usr/bin/env python3
"""T43 gradient-gated rider tracker: T42's retuned tracker with a GRADIENT lock.

T43 Task 1 (T40-G1 third arm, static test on T42 R3's 12 committed dense
snaps): RIDER_ROI kept at x[220,420] y[180,360] and DARK_MAX kept at 80,
but the dark mask is AND-gated with a Sobel gradient-magnitude floor
(gradmag = |Gx|+|Gy| >= GRAD_MIN=60): smooth dark expanses (shade glow,
trunk interiors, wall faces) carry little gradient and drop out, while
the rider complex (limbs/board/helmet edges against snow) survives. The
validity gate is RECALIBRATED to gradient counts (500..3000): gradient
keeps ~30-50% of dark pixels on rider snaps, so the 200..6000 dark-count
band does not transfer. SCPS40/SCPS120 untouched (bit-identical output).

Calibration (T42 R3's 12 committed dense snaps, static): 11/12 VALID with
7 on-rider, 3 borderline-on, 1 off-rider (d-post3 trunk — the gate hole:
bark texture is dark AND edge-rich, npix 2046 inside the band; caught by
lock-QA, not the gate); d-post2 tree flood gates out (4448 > 3000).
d-post5 shade bias recentered off->on, d-post9 totem bias 50px->~15px
(borderline), d-post1 trunk-shoulder stays borderline. Floods do NOT
separate by gradient count (edge-rich bark/walls) — the ROI gate remains
the operative flood defense; the gradient's value is centroid quality on
in-band-biased snaps. See T43 REPORT for the full calibration table.
Deterministic: identical bytes in -> identical out.

Usage: t43-track.py snap1.jpg [snap2.jpg ...]
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
GRAD_MIN = 60  # Sobel |Gx|+|Gy| floor (luma units)
LAG_MAX = 40
LAG_MAX_WIDE = 120
RDC_NPIX_MIN = 500
RDC_NPIX_MAX = 3000

_SOBEL_X = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
_SOBEL_Y = _SOBEL_X.T


def load_luma(path):
    return np.asarray(Image.open(path).convert("L"), dtype=np.float64)


def grad_mag(roi):
    p = np.pad(roi, 1, mode="edge")
    gx = sum(
        _SOBEL_X[i, j] * p[i : i + roi.shape[0], j : j + roi.shape[1]]
        for i in range(3)
        for j in range(3)
    )
    gy = sum(
        _SOBEL_Y[i, j] * p[i : i + roi.shape[0], j : j + roi.shape[1]]
        for i in range(3)
        for j in range(3)
    )
    return np.abs(gx) + np.abs(gy)


def rider_centroid(luma):
    x0, y0, x1, y1 = RIDER_ROI
    roi = luma[y0:y1, x0:x1]
    mask = (roi < DARK_MAX) & (grad_mag(roi) >= GRAD_MIN)
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
