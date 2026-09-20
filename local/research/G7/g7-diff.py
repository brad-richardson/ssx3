#!/usr/bin/env python3
# G7: scanout-vs-reference diff stats. Reads P6 PPM (parallel-gs) + PNG (PCSX2).
# Reports sizes, overlap geometry, exact-match %, |d| histogram, per-channel PSNR.
# No verdicts; method + numbers only.
import sys, math, struct

def read_ppm(path):
    with open(path, 'rb') as f:
        magic = f.readline().strip()
        assert magic == b'P6', magic
        line = f.readline()
        while line.startswith(b'#'):
            line = f.readline()
        w, h = map(int, line.split())
        maxval = int(f.readline().strip())
        assert maxval == 255, maxval
        data = f.read(w * h * 3)
        assert len(data) == w * h * 3, (len(data), w, h)
    return w, h, data

def read_png(path):
    from PIL import Image
    im = Image.open(path).convert('RGB')
    return im.size[0], im.size[1], im.tobytes()

def main(a_path, b_path):
    wa, ha, a = read_ppm(a_path)
    wb, hb, b = read_png(b_path)
    print(f"A(parallel-gs)={wa}x{ha} B(pcsx2-ref)={wb}x{hb}")
    # Center-crop overlap.
    w, h = min(wa, wb), min(ha, hb)
    oxa, oya = (wa - w) // 2, (ha - h) // 2
    oxb, oyb = (wb - w) // 2, (hb - h) // 2
    print(f"overlap={w}x{h} offsetA=({oxa},{oya}) offsetB=({oxb},{oyb})")
    n = w * h
    exact = 0
    hist = {}
    sq = [0, 0, 0]
    for y in range(h):
        ra = ((oya + y) * wa + oxa) * 3
        rb = ((oyb + y) * wb + oxb) * 3
        for x in range(w):
            ia, ib = ra + x * 3, rb + x * 3
            pa = a[ia:ia+3]
            pb = b[ib:ib+3]
            if pa == pb:
                exact += 1
            for c in range(3):
                d = abs(pa[c] - pb[c])
                hist[d] = hist.get(d, 0) + 1
                sq[c] += d * d
    print(f"pixels={n} exact={exact} exact_frac={exact/n:.4f}")
    tot = n * 3
    for thr in (0, 1, 2, 4, 8, 16, 32):
        cum = sum(v for k, v in hist.items() if k <= thr)
        print(f"|d|<={thr}: {cum} ({cum/tot:.4f})")
    peak = 255.0 * 255.0 * n
    for c, name in enumerate("RGB"):
        psnr = float('inf') if sq[c] == 0 else 10.0 * math.log10(peak / sq[c])
        print(f"PSNR_{name}={psnr:.2f} dB")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
