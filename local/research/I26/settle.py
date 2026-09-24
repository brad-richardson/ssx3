#!/usr/bin/env python3
"""I26: for each scripted press, when did the screen it lands on appear?

For press k (guest tick Tk), the reference is the last snap before Tk. Walk
back from Tk to the previous press T(k-1); the screen 'appeared' at the
earliest snap after which every snap up to Tk stays within --thresh (mean
abs grey diff, 64x56 thumbnail) of the reference. Prints the appear tick,
the press tick and the wait (ticks, guest s).
Usage: settle.py <snap_dir> <boot_log> [--thresh 6]
"""
import argparse, glob, os, re, subprocess, tempfile

ap = argparse.ArgumentParser()
ap.add_argument("snap_dir"); ap.add_argument("boot_log")
ap.add_argument("--thresh", type=float, default=6.0)
a = ap.parse_args()

meta, pngs = [], []
for p in sorted(glob.glob(os.path.join(a.snap_dir, "snap-*.png"))):
    try:
        t = open(p[:-4] + ".txt").read()
        tick = int(re.search(r"tick=(\d+)", t).group(1))
        with open(p, "rb") as fh:
            fh.seek(-12, 2)
            if b"IEND" not in fh.read():
                continue  # PNG copied mid-write by the snapshotter
    except (OSError, AttributeError):
        continue
    pngs.append(p); meta.append((os.path.basename(p), tick))
W, H = 64, 56
with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
    for p in pngs:
        f.write(f"file '{os.path.abspath(p)}'\nduration 0.04\n")
    lst = f.name
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                      "-vf", f"scale={W}:{H},format=gray", "-fps_mode", "passthrough", "-f", "rawvideo", "-"],
                     capture_output=True).stdout
os.unlink(lst)
n = W * H
assert len(raw) == n * len(pngs)
fr = [raw[i * n:(i + 1) * n] for i in range(len(pngs))]
diff = lambda x, y: sum(abs(p - q) for p, q in zip(x, y)) / n

presses = []
for line in open(a.boot_log, errors="replace"):
    m = re.search(r"\[padscript\] press i=(\d+) now=(\d+)ms .*buttons=0x([0-9a-f]+)", line)
    if m:
        presses.append((int(m.group(1)), int(m.group(2)) * 5994 // 100000, m.group(3)))
presses.sort(key=lambda p: (p[1], p[0]))
prev_t = 0
print("press  btn     press_tick  ref_snap                appear_tick  appear_snap          wait_ticks  wait_s")
for i, t, b in presses:
    idx = [k for k, (_, tk) in enumerate(meta) if prev_t < tk < t]
    if not idx:
        print(f"i={i:2d} 0x{b} {t:6d}  (no snaps in window)"); prev_t = t; continue
    ref = fr[idx[-1]]
    appear = idx[-1]
    for k in reversed(idx):
        if diff(fr[k], ref) <= a.thresh:
            appear = k
        else:
            break
    at = meta[appear][1]
    print(f"i={i:2d} 0x{b}  {t:6d}  {meta[idx[-1]][0]:22s} {at:6d}      {meta[appear][0]:20s} {t - at:6d}  {(t - at) / 59.94:6.1f}")
    prev_t = t
