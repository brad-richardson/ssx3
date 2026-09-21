#!/usr/bin/env python3
"""T37 rider-pixel tracker (frozen pre-run).

Two fixed metrics per snap / snap-pair, computed on 1280x1024 snaps whose
game area is x[0,647] y[24,511] (T36 npre measured bbox):

  RDCX/RDCY: centroid (px, 0.1) of dark pixels (luminance < 80) inside the
      rider ROI x[150,540] y[100,460] (game-area central band; excludes the
      position/clock/score HUD top strip, progress bar + speed left column,
      trick meter right column). Also reports npix + dark fraction.
      Rationale: rider outfit is near-black against bright snow; a Left
      carve displaces the rider sprite laterally before the chase cam
      re-centers.
  SCPS: snow column-profile shift (px, integer lag in [-40,40]) between two
      consecutive snaps: column-mean luminance profile over x[150,540] of
      rows y[380,460] (foreground snow band), normalized cross-correlation,
      best lag (+ = scene content moved right on screen). Also reports the
      peak correlation. Rationale: under a chase cam the world rotates
      around the rider, so a heading change reads as background lateral
      shift even when the rider stays centered.

Noise floor: |M(pre2) - M(pre1)| over the no-input pre-nudge pair gap.
Deterministic: identical bytes in -> identical numbers out (no RNG).

Usage: t37-track.py snap1.jpg [snap2.jpg ...]
  Prints per-snap RDC + per-consecutive-pair SCPS, one line each.
"""
import sys

import numpy as np
from PIL import Image

RIDER_ROI = (150, 100, 540, 460)  # x0, y0, x1, y1 (x1/y1 exclusive)
SNOW_ROWS = (380, 460)
SNOW_COLS = (150, 540)
DARK_MAX = 80
LAG_MAX = 40


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


def snow_shift(prev, cur):
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
    for lag in range(-LAG_MAX, LAG_MAX + 1):
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
        print(f"RDC {p} cx={cx:.1f} cy={cy:.1f} npix={npix} frac={frac:.4f}")
    for p0, p1, a, b in zip(paths, paths[1:], lumas, lumas[1:]):
        lag, corr = snow_shift(a, b)
        print(f"SCPS {p0} -> {p1} lag={lag:+d} corr={corr:.4f}")


if __name__ == "__main__":
    main(sys.argv[1:])
