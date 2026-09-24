#!/usr/bin/env python3
"""I26: find screen changes in a snap dir (snap-<s>.png + .txt with tick=).

Downscales every snap to 16x14 grey with one ffmpeg pass, then flags a
'scene change' where the mean absolute difference to the previous snap
exceeds --thresh (0-255 scale). Prints: snap, tick, fnv1a, diff, marker.
Usage: snap_screens.py <snap_dir> [--thresh 12] [--all]
"""
import argparse, glob, os, re, subprocess, tempfile

ap = argparse.ArgumentParser()
ap.add_argument("snap_dir")
ap.add_argument("--thresh", type=float, default=12.0)
ap.add_argument("--all", action="store_true")
a = ap.parse_args()

meta, pngs = [], []
for p in sorted(glob.glob(os.path.join(a.snap_dir, "snap-*.png"))):
    try:
        t = open(p[:-4] + ".txt").read()
        tick = int(re.search(r"tick=(\d+)", t).group(1))
        h = re.search(r"fnv1a=([0-9a-f]+)", t).group(1)
        with open(p, "rb") as fh:
            fh.seek(-12, 2)
            if b"IEND" not in fh.read():
                continue  # PNG copied mid-write by the snapshotter
    except (OSError, AttributeError):
        continue  # sidecar caught mid-write by the snapshotter: skip the pair
    pngs.append(p)
    meta.append((os.path.basename(p), tick, h))
with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
    for p in pngs:
        f.write(f"file '{os.path.abspath(p)}'\nduration 0.04\n")
    lst = f.name
W, H = 16, 14
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                      "-vf", f"scale={W}:{H},format=gray", "-fps_mode", "passthrough", "-f", "rawvideo", "-"],
                     capture_output=True, check=True).stdout
os.unlink(lst)
assert len(raw) == W * H * len(pngs), (len(raw), len(pngs))
n = W * H
frames = [raw[i * n:(i + 1) * n] for i in range(len(raw) // n)]
prev = None
for (name, tick, h), fr in zip(meta, frames):
    d = 0.0 if prev is None else sum(abs(x - y) for x, y in zip(fr, prev)) / n
    mark = "  <== change" if d >= a.thresh else ""
    if a.all or mark or prev is None:
        print(f"{name} tick={tick:5d} fnv={h} diff={d:6.1f}{mark}")
    prev = fr
