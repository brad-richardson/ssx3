#!/usr/bin/env python3
"""I26: contact sheet of the snaps nearest the given guest ticks.
Usage: sheet.py <snap_dir> <out.png> <cols> tick1 tick2 ...  (labels = ticks)"""
import glob, os, re, subprocess, sys
d, out, cols = sys.argv[1], sys.argv[2], int(sys.argv[3])
want = [int(x) for x in sys.argv[4:]]
snaps = []
for p in sorted(glob.glob(os.path.join(d, "snap-*.png"))):
    try:
        t = int(re.search(r"tick=(\d+)", open(p[:-4] + ".txt").read()).group(1))
        with open(p, "rb") as fh:
            fh.seek(-12, 2)
            if b"IEND" not in fh.read():
                continue
    except (OSError, AttributeError):
        continue
    snaps.append((t, os.path.abspath(p)))
pick = [min(snaps, key=lambda s: abs(s[0] - w)) for w in want]
lst = out + ".txt"
with open(lst, "w") as f:
    for t, p in pick:
        f.write(f"file '{p}'\nduration 0.04\n")
rows = (len(pick) + cols - 1) // cols
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                "-vf", f"scale=256:224,tile={cols}x{rows}", "-frames:v", "1", out], check=True)
os.remove(lst)
print(" ".join(str(t) for t, _ in pick))
