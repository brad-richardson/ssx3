#!/usr/bin/env python3
# G11: cross-k diff matrix PPM#i (paraLLEl iterate-true #i) vs PNG#j
# (PCSX2 post-vsync#(j-1), file _frame{j:05d}). G10 g10-diff.py shape:
# pixel-diff ONLY on exact geometry (all 512x448). Decides systematic
# one-vsync lag (shifted diagonal wins at every row) vs first-only
# artifact (same-boundary diagonal wins for i>=1).
import math, os, sys

def read_ppm(path):
    with open(path, 'rb') as f:
        assert f.readline().strip() == b'P6'
        line = f.readline()
        while line.startswith(b'#'):
            line = f.readline()
        w, h = map(int, line.split())
        assert int(f.readline().strip()) == 255
        data = f.read(w * h * 3)
        assert len(data) == w * h * 3
    return w, h, data

def read_png(path):
    from PIL import Image
    im = Image.open(path).convert('RGB')
    return im.size[0], im.size[1], im.tobytes()

def nonblack(w, h, data):
    n = w * h
    return sum(1 for i in range(n) if data[i*3:i*3+3] != b'\x00\x00\x00')

def diff(a, b):
    n = len(a) // 3
    exact = 0
    sq = [0, 0, 0]
    for i in range(n):
        o = i * 3
        if a[o:o+3] == b[o:o+3]:
            exact += 1
        for c in range(3):
            d = a[o+c] - b[o+c]
            sq[c] += d * d
    psnr = []
    for c in range(3):
        psnr.append(float('inf') if sq[c] == 0 else 10.0 * math.log10(255.0*255.0*n / sq[c]))
    return exact / n, psnr

def main(d):
    base = "SSX 3_SLUS-20772_20260920212606"
    ppm, png = [], []
    for i in range(8):
        w, h, px = read_ppm(os.path.join(d, base + ".gs.g10-vsync%d.ppm" % i))
        assert (w, h) == (512, 448), (i, w, h)
        ppm.append(px)
    for j in range(1, 8):
        w, h, px = read_png(os.path.join(d, base + "_frame%05d.png" % j))
        assert (w, h) == (512, 448), (j, w, h)
        png.append(px)
    print("nonblack PPM#0..7:", [nonblack(512, 448, p) for p in ppm])
    print("nonblack PNG#1..7 (post-vsync#0..6):", [nonblack(512, 448, p) for p in png])
    print()
    print("PSNR_R (dB) rows=PPM#i cols=PNG#j(post-vsync#(j-1)):")
    hdr = "       " + "".join("  PNG#%d " % j for j in range(1, 8))
    print(hdr)
    for i in range(8):
        row = "PPM#%d " % i
        for j in range(7):
            _, ps = diff(ppm[i], png[j])
            row += " %7.2f" % ps[0]
        print(row)
    print()
    print("exact_frac rows=PPM#i cols=PNG#j:")
    print(hdr)
    for i in range(8):
        row = "PPM#%d " % i
        for j in range(7):
            ef, _ = diff(ppm[i], png[j])
            row += " %7.4f" % ef
        print(row)

if __name__ == '__main__':
    main(sys.argv[1])
