#!/usr/bin/env python3
"""G14: score on-device scanouts vs G13 dual-agreed oracles (corrected labels).

Oracle:  /Volumes/Extreme SSD/ps2x-g13  (8 PPMs g13-dump.gs.g10-vsync{i}.ppm
         + 7 PNGs SSX 3_..._frame0000{i}.png, i=1..7; corrected mapping
         file N <-> post-vsync#N per G12/G13).
Device:  /Volumes/Extreme SSD/ps2x-g14  (device PPMs, if the run produced any).

Steps: (1) re-verify oracle pixel-shas vs G13 §3c; (2) list device scanouts;
(3) if present, same-boundary diff table (exact/le2/le32/PSNR) device-vs-PPM
and device-vs-PNG; if absent, report N/A with reason (this G14 run: crash
before first iterate -> 0 device scanouts).
"""
import glob
import hashlib
import math
import os
import sys
from PIL import Image

ORACLE = sys.argv[1] if len(sys.argv) > 1 else "/Volumes/Extreme SSD/ps2x-g13"
DEVICE = sys.argv[2] if len(sys.argv) > 2 else "/Volumes/Extreme SSD/ps2x-g14"

# G13 §3c pixel-data sha256 (first 8 hex) for PPM#0..7.
G13_PIXSHA = ["9c70d3e9", "667e7cf3", "37151cf4", "8ac47660",
              "1ccda8b6", "1ccda8b6", "def2f366", "def2f366"]


def pixsha256(path):
    d = open(path, "rb").read()
    hdr_end = d.index(b"255\n") + 4
    return hashlib.sha256(d[hdr_end:]).hexdigest()[:8]


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


print("== oracle re-verify (G13 §3c pixel-shas) ==")
oracles_ok = True
for i in range(8):
    p = os.path.join(ORACLE, f"g13-dump.gs.g10-vsync{i}.ppm")
    got = pixsha256(p)
    ok = got == G13_PIXSHA[i]
    oracles_ok &= ok
    print(f"PPM#{i} {got} expect {G13_PIXSHA[i]} {'OK' if ok else 'MISMATCH'}")
print("oracles:", "ALL OK" if oracles_ok else "MISMATCH - STOP")

print("== device scanouts ==")
dev = sorted(glob.glob(os.path.join(DEVICE, "*.ppm")))
print(f"device PPMs in {DEVICE}: {len(dev)}")
for p in dev:
    print(f"  {os.path.basename(p)} {os.path.getsize(p)} B")

if not oracles_ok:
    sys.exit(2)
if not dev:
    print("SCORE: N/A - 0 device scanouts (G14 run crashed before first iterate)")
    sys.exit(0)

ppms = [Image.open(os.path.join(ORACLE, f"g13-dump.gs.g10-vsync{i}.ppm")).convert("RGB")
        for i in range(8)]
print("== device-vs-PPM-oracle (corrected labels, k=1..7) ==")
print("k exact le2 le32 psnrR psnrG psnrB")
for i in range(1, 8):
    cand = [p for p in dev if f"vsync{i}.ppm" in p]
    if not cand:
        print(f"{i} NO DEVICE FILE")
        continue
    d = Image.open(cand[0]).convert("RGB")
    if d.size != ppms[i].size:
        print(f"{i} SIZE MISMATCH {d.size} vs {ppms[i].size}")
        continue
    e, l2, l32, ps = diff(d, ppms[i])
    print(f"{i} {e:.4f} {l2:.4f} {l32:.4f} {ps[0]:.1f} {ps[1]:.1f} {ps[2]:.1f}")
