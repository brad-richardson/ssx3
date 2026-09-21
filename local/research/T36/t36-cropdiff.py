#!/usr/bin/env python3
# T27 title detector comparator: text-band crop (380,200,1180,480) abs-diff
# stats (mean / p99 / max) between a candidate snap and a reference snap.
# Dual-mode: uses PIL when importable (laptop analysis, JPEG or PPM), else
# pure-python PPM-P6 parsing (bytesize WSL, no PIL). Grayscale = (R+G+B)/3
# in both paths so scores are comparable across modes.
# Usage: t27-cropdiff.py <candidate> <reference> [x0,y0,x1,y1]
# Exit 0 always on success; prints: mean=<m> p99=<p> max=<x> npix=<n>
import sys

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False


def load_pil(path):
    im = Image.open(path).convert("RGB")
    return im.size, list(im.tobytes())


def load_ppm(path):
    with open(path, "rb") as f:
        magic = f.readline().strip()
        if magic != b"P6":
            raise ValueError("not P6 PPM: %r" % magic)
        toks = []
        while len(toks) < 3:
            line = f.readline()
            if not line:
                raise ValueError("truncated PPM header")
            line = line.split(b"#")[0]
            toks += line.split()
        w, h, depth = int(toks[0]), int(toks[1]), int(toks[2])
        if depth == 255:
            raw = f.read(w * h * 3)
            if len(raw) != w * h * 3:
                raise ValueError("truncated PPM body %d != %d" % (len(raw), w * h * 3))
            return (w, h), raw
        if depth == 65535:
            # xwdtopnm emits 16-bit samples (big-endian) from the Xvfb root
            # visual; scale down to 8-bit (R1 fix: maxval-255-only parser
            # scored nothing remotely).
            n = w * h * 3
            raw16 = f.read(n * 2)
            if len(raw16) != n * 2:
                raise ValueError("truncated 16-bit PPM body")
            raw = bytes(int((int.from_bytes(raw16[i:i + 2], "big") * 255 + 32767) / 65535)
                        for i in range(0, n * 2, 2))
            return (w, h), raw
        raise ValueError("need maxval 255/65535, got %d" % depth)


def load(path):
    if HAVE_PIL:
        return load_pil(path)
    return load_ppm(path)


def gray(px, i):
    return (px[i] + px[i + 1] + px[i + 2]) / 3.0


def main():
    if len(sys.argv) < 3:
        print("usage: t27-cropdiff.py <candidate> <reference> [x0,y0,x1,y1]",
              file=sys.stderr)
        return 2
    cand, ref = sys.argv[1], sys.argv[2]
    box = tuple(int(v) for v in sys.argv[3].split(",")) if len(sys.argv) > 3 \
        else (380, 200, 1180, 480)
    x0, y0, x1, y1 = box
    (wc, hc), pc = load(cand)
    (wr, hr), pr = load(ref)
    if (wc, hc) != (wr, hr):
        print("size mismatch %dx%d vs %dx%d" % (wc, hc, wr, hr), file=sys.stderr)
        return 2
    hist = [0] * 256
    tot = 0.0
    n = 0
    mx = 0
    for y in range(y0, y1):
        base = (y * wc + x0) * 3
        span = (x1 - x0)
        for k in range(span):
            i = base + k * 3
            d = abs(gray(pc, i) - gray(pr, i))
            di = int(round(d))
            hist[di] += 1
            tot += d
            if di > mx:
                mx = di
            n += 1
    mean = tot / n
    acc = 0
    p99 = 255
    for v in range(256):
        acc += hist[v]
        if acc >= 0.99 * n:
            p99 = v
            break
    print("mean=%.4f p99=%d max=%d npix=%d mode=%s" %
          (mean, p99, mx, n, "PIL" if HAVE_PIL else "PPM"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
