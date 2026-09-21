#!/usr/bin/env python3
# G10: same-boundary pair comparison (G8 g8-diff.py shape).
# Rule (unchanged): pixel-diff ONLY on exact geometry match; on mismatch
# report per-image stats + geometry delta, NO resampling, NO crop proxy.
# Pairing: paraLLEl g10-vsync{k}.ppm <-> PCSX2 _frame{k+1:05d}.png for
# k=0..6 (file N names post-dump-vsync#(N-1) state; _frame00008 absent).
import sys, math, glob, os

def read_ppm(path):
    with open(path, 'rb') as f:
        magic = f.readline().strip()
        assert magic == b'P6', magic
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

def stats(tag, w, h, data):
    n = w * h
    px = [data[i:i+3] for i in range(0, len(data), 3)]
    d = len(set(px))
    nb = sum(1 for p in px if p != b'\x00\x00\x00')
    sr = sum(p[0] for p in px); sg = sum(p[1] for p in px); sb = sum(p[2] for p in px)
    print(f"{tag}: {w}x{h} distinct={d} nonblack={nb} ({nb/n:.4f}) "
          f"mean=({sr/n:.2f},{sg/n:.2f},{sb/n:.2f})")
    return d, nb

def exact_diff(a_path, b_path, ao, bo):
    (wa, ha, a), (wb, hb, b) = ao, bo
    assert (wa, ha) == (wb, hb)
    n = wa * ha
    exact = sum(1 for i in range(n) if a[i*3:i*3+3] == b[i*3:i*3+3])
    hist = {}
    sq = [0, 0, 0]
    for i in range(n):
        for c in range(3):
            d = abs(a[i*3+c] - b[i*3+c])
            hist[d] = hist.get(d, 0) + 1
            sq[c] += d * d
    print(f"pixels={n} exact={exact} exact_frac={exact/n:.4f}")
    tot = n * 3
    for thr in (0, 1, 2, 4, 8, 16, 32):
        cum = sum(v for k, v in hist.items() if k <= thr)
        print(f"|d|<={thr}: {cum} ({cum/tot:.4f})")
    for c, name in enumerate("RGB"):
        psnr = float('inf') if sq[c] == 0 else 10.0 * math.log10(255.0*255.0*n / sq[c])
        print(f"PSNR_{name}={psnr:.2f} dB")

def main(d):
    base = "SSX 3_SLUS-20772_20260920212606"
    for k in range(7):
        ppm = os.path.join(d, base + ".gs.g10-vsync%d.ppm" % k)
        png = os.path.join(d, base + "_frame%05d.png" % (k + 1))
        print(f"=== boundary k={k}: vsync{k}.ppm vs _frame{k+1:05d}.png ===")
        pa = read_ppm(ppm); ra = read_png(png)
        print(f"G10-PPM={pa[0]}x{pa[1]} PCSX2-PNG={ra[0]}x{ra[1]}")
        stats("PPM", *pa); stats("PNG", *ra)
        if (pa[0], pa[1]) == (ra[0], ra[1]):
            exact_diff(ppm, png, pa, ra)
        else:
            print(f"GEOMETRY_MISMATCH: {pa[0]}x{pa[1]} vs {ra[0]}x{ra[1]}; "
                  f"no pixel diff per G8 alignment rule (no crop proxy).")

if __name__ == '__main__':
    main(sys.argv[1])
