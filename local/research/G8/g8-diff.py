#!/usr/bin/env python3
# G8: aligned scanout-vs-reference comparison.
# Rule (frontier alignment correction): pixel-diff ONLY on exact geometry
# match; on mismatch report per-image stats + geometry delta, NO center-crop.
import sys, math

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

def main(first_ppm, last_ppm, ref_png):
    fa = read_ppm(first_ppm); la = read_ppm(last_ppm); ra = read_png(ref_png)
    print(f"FIRST(parallel-gs)={fa[0]}x{fa[1]} LAST={la[0]}x{la[1]} "
          f"REF(pcsx2)={ra[0]}x{ra[1]}")
    stats("FIRST", *fa); stats("LAST", *la); stats("REF", *ra)
    print("--- FIRST vs REF ---")
    if (fa[0], fa[1]) == (ra[0], ra[1]):
        exact_diff(first_ppm, ref_png, fa, ra)
    else:
        print(f"GEOMETRY_MISMATCH: {fa[0]}x{fa[1]} vs {ra[0]}x{ra[1]}; "
              f"no pixel diff per G8 alignment rule (no crop proxy).")
    print("--- FIRST vs LAST (same-geometry animation delta) ---")
    if (fa[0], fa[1]) == (la[0], la[1]):
        exact_diff(first_ppm, last_ppm, fa, la)
    else:
        print("GEOMETRY_MISMATCH first/last (unexpected).")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
