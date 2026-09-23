#!/usr/bin/env python3
"""T47 Mission 1 diffs: resize PCSX2 640x480 ref to recomp 512x448, then
whole-frame + quadrant mean/p99 via the t44-cropdiff metric (PIL port).
Usage: python3 t47-diff.py OUTDIR (pairs hardcoded below)
"""
import os
import sys
from PIL import Image
import numpy as np

OUTDIR = sys.argv[1]
os.makedirs(OUTDIR, exist_ok=True)
R = "/Volumes/Extreme SSD/ps2recomp-spike/P1/run"

PAIRS = [
    ("title", f"{R}/frames-e29b-1/upload-latest.png",
     "/tmp/t47fetch/t47-shot-title.png", "/tmp/t47fetch2/t47b-shot-title.png"),
    ("menu", f"{R}/frames-e31d-1/snap/snap-0059.99s.png",
     "/tmp/t47fetch/t47-shot-menu.png", "/tmp/t47fetch2/t47b-shot-menu.png"),
    ("sc", f"{R}/frames-e31b-1/snap/snap-0089.44s.png",
     "/tmp/t47fetch/t47-shot-sc.png", "/tmp/t47fetch2/t47b-shot-sc.png"),
    ("zc", f"{R}/frames-e31b-1/upload-latest.png",
     "/tmp/t47fetch/t47-shot-zc.png", "/tmp/t47fetch2/t47b-shot-zc.png"),
    ("se-default", f"{R}/frames-e31d-1/snap/snap-0209.97s.png",
     "/tmp/t47fetch/t47-shot-se-default.png", "/tmp/t47fetch2/t47b-shot-se-default.png"),
    ("se-happiness", f"{R}/frames-e31d-1/upload-latest.png",
     "/tmp/t47fetch/t47-shot-se-walked.png", "/tmp/t47fetch2/t47b-shot-se-walked.png"),
]

BOXES = {
    "whole": (0, 0, 512, 448),
    "TL": (0, 0, 256, 224),
    "TR": (256, 0, 512, 224),
    "BL": (0, 224, 256, 448),
    "BR": (256, 224, 512, 448),
    "center": (128, 112, 384, 336),
}


def metric(a, b, box):
    x0, y0, x1, y1 = box
    d = np.abs(a[y0:y1, x0:x1].astype(np.int16) - b[y0:y1, x0:x1].astype(np.int16))
    d = d.mean(axis=2)
    return d.mean(), np.percentile(d, 99)


for (name, recomp, hw, sw) in PAIRS:
    r = np.array(Image.open(recomp).convert("RGB"))
    assert r.shape[:2] == (448, 512), (name, r.shape)
    for tag, ref in (("HW", hw), ("SW", sw)):
        p = Image.open(ref).convert("RGB").resize((512, 448), Image.LANCZOS)
        a = np.array(p)
        line = [f"{name}/{tag}"]
        for (bname, box) in BOXES.items():
            m, p99 = metric(r, a, box)
            line.append(f"{bname}={m:.2f}/{p99:.0f}")
        print(" ".join(line))
    # HW-vs-SW (native 640x480, no resize needed)
    h = np.array(Image.open(hw).convert("RGB")).astype(np.int16)
    s = np.array(Image.open(sw).convert("RGB")).astype(np.int16)
    d = np.abs(h - s).mean(axis=2)
    print(f"{name}/HWvsSW whole640={d.mean():.3f}/{np.percentile(d, 99):.0f}")
