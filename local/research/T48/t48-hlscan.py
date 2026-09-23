#!/usr/bin/env python3
"""T48 orange-bar row scanner (16-bit PPM aware). Prints highlight bar
center y (xwd pixels) + orange count. No calibration: caller navigates by
convergence (UP until y stops decreasing; a big y jump = wrap)."""
import sys
from collections import Counter


def load_ppm(path):
    with open(path, "rb") as f:
        assert f.readline().strip() == b"P6"
        w, h = map(int, f.readline().split())
        maxval = int(f.readline().strip())
        return w, h, maxval, f.read()


def main():
    w, h, maxval, px = load_ppm(sys.argv[1])
    x0, x1, y0, y1 = (int(a) for a in (sys.argv + ["0", "0", "0", "0"])[2:6])
    if x1 <= x0:
        x0, x1 = 0, w
    if y1 <= y0:
        y0, y1 = 0, h
    if maxval > 255:
        n = len(px) // 6
        def rgb(i):
            return px[6 * i], px[6 * i + 2], px[6 * i + 4]
    else:
        n = len(px) // 3
        def rgb(i):
            return px[3 * i], px[3 * i + 1], px[3 * i + 2]
    rows = Counter()
    for y in range(y0, y1):
        base = y * w
        for x in range(x0, x1, 2):
            r, g, b = rgb(base + x)
            if 195 <= r <= 230 and 70 <= g <= 100 and b <= 10:
                rows[y] += 2
    if not rows:
        print("y=-1 n=0")
        return
    ys = sorted(rows)
    best, cur = [], []
    for y in ys:
        if cur and y - cur[-1] > 4:
            if sum(rows[v] for v in cur) > sum(rows[v] for v in best):
                best = cur
            cur = []
        cur.append(y)
    if sum(rows[v] for v in cur) > sum(rows[v] for v in best):
        best = cur
    tot = sum(rows[v] for v in best)
    yc = sum(v * rows[v] for v in best) / tot
    print("y=%.1f n=%d" % (yc, tot))


main()
