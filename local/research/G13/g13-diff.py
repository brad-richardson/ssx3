#!/usr/bin/env python3
"""G13: same-boundary diffs with CORRECTED labels (file N <-> post-vsync#N).

Pairs: PPM#i (g10-vsync{i}.ppm, post-vsync#i) vs PNG file{i} (post-vsync#i),
i=1..7 (file0 absent per G12). Pixel-diff on exact geometry only (all
512x448 here); RGB channels (PNG RGBA alpha ignored). Reports exact_frac,
|d|<=2/<=32 fracs, per-channel PSNR, nonblack counts. Also PPM self-table
(pairwise identity + nonblack) and PNG self-table.
"""
import glob
import hashlib
import math
import os
import sys
from PIL import Image

D = sys.argv[1] if len(sys.argv) > 1 else "/Volumes/Extreme SSD/ps2x-g13"


def load_rgb(p):
    return Image.open(p).convert("RGB")


def psnr(mse):
    return float("inf") if mse == 0 else 10 * math.log10(255 * 255 / mse)


def diff(a, b):
    la, lb = list(a.getdata()), list(b.getdata())
    n = len(la)
    se = [0, 0, 0]
    exact = le2 = le32 = 0
    for pa, pb in zip(la, lb):
        d = [abs(x - y) for x, y in zip(pa, pb)]
        m = max(d)
        if m == 0:
            exact += 1
        if m <= 2:
            le2 += 1
        if m <= 32:
            le32 += 1
        for c in range(3):
            se[c] += d[c] * d[c]
    return exact / n, le2 / n, le32 / n, [psnr(s / n) for s in se]


def nonblack(im):
    return sum(1 for p in im.getdata() if p != (0, 0, 0))

ppms = [load_rgb(os.path.join(D, f"g13-dump.gs.g10-vsync{i}.ppm")) for i in range(8)]
pngs = {}
for f in sorted(glob.glob(os.path.join(D, "*_frame*.png"))):
    i = int(f[-7:-4])
    pngs[i] = load_rgb(f)
print(f"ppm_geoms={[p.size for p in ppms]} png_keys={sorted(pngs)} "
      f"png_geoms={[pngs[i].size for i in sorted(pngs)]}")

print("== PPM self ==")
for i, p in enumerate(ppms):
    h = hashlib.sha256(p.tobytes()).hexdigest()[:12]
    print(f"PPM#{i} sha={h} nonblack={nonblack(p)}")
print("== PNG self ==")
for i in sorted(pngs):
    p = pngs[i]
    h = hashlib.sha256(p.tobytes()).hexdigest()[:12]
    print(f"PNG#{i} sha={h} nonblack={nonblack(p)}")

print("== same-boundary diffs (PPM#i vs PNG#i) ==")
for i in range(1, 8):
    e, l2, l32, ps = diff(ppms[i], pngs[i])
    print(f"k={i} exact={e:.4f} le2={l2:.4f} le32={l32:.4f} "
          f"psnr={ps[0]:.1f}/{ps[1]:.1f}/{ps[2]:.1f}")
