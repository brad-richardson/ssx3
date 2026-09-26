#!/usr/bin/env python3
"""VK1 screen-level pixel check: a device screencap (SurfaceFlinger's composited
display, after HWC/GPU scaling) against the readback frame the backend wrote
at a compare tick (vk-t<T>-readback.ppm, RGB). The game rect on the display
is given (default: full 1920x1080, SSX 3's anamorphic 16:9). The display rect
is box-averaged down to the frame size and compared per channel: mean absolute
error and PSNR. Scaling filters differ (HWC scaler vs box average), so this is
a geometry/colour check, not a byte compare (the byte compare is the in-app
gralloc-vs-readback line). Usage:
  scapcompare.py <screencap.png> <readback.ppm> [x0 y0 x1 y1]
"""
import math
import os
import struct
import subprocess
import sys
import tempfile


def read_bmp(path):
    d = open(path, 'rb').read()
    off = struct.unpack_from('<I', d, 10)[0]
    w, h = struct.unpack_from('<ii', d, 18)
    bpp = struct.unpack_from('<H', d, 28)[0]
    comp = struct.unpack_from('<I', d, 30)[0]
    step = bpp // 8
    stride = (w * step + 3) & ~3
    flip = h > 0
    h = abs(h)
    # sips writes 32-bit BI_BITFIELDS BGRA or 24-bit BGR
    px = []
    for y in range(h):
        row = (h - 1 - y) if flip else y
        base = off + row * stride
        r = []
        for x in range(w):
            p = base + x * step
            b, g, rr = d[p], d[p + 1], d[p + 2]
            r.append((rr, g, b))
        px.append(r)
    return w, h, px, (bpp, comp)


def read_ppm(path):
    d = open(path, 'rb').read()
    parts = d.split(b'\n', 3)
    w, h = map(int, parts[1].split())
    raw = parts[3]
    return w, h, raw


def main():
    png, ppm = sys.argv[1], sys.argv[2]
    tmp = tempfile.mktemp(suffix='.bmp')
    subprocess.run(['sips', '-s', 'format', 'bmp', png, '--out', tmp], check=True, capture_output=True)
    W, H, disp, fmt = read_bmp(tmp)
    os.unlink(tmp)
    x0, y0, x1, y1 = (int(v) for v in sys.argv[3:7]) if len(sys.argv) >= 7 else (0, 0, W, H)
    fw, fh, raw = read_ppm(ppm)
    sx = (x1 - x0) / fw
    sy = (y1 - y0) / fh
    se = [0.0, 0.0, 0.0]
    ae = [0.0, 0.0, 0.0]
    n = 0
    for fy in range(fh):
        ya, yb = y0 + int(fy * sy), y0 + max(int(fy * sy) + 1, int((fy + 1) * sy))
        for fx in range(fw):
            xa, xb = x0 + int(fx * sx), x0 + max(int(fx * sx) + 1, int((fx + 1) * sx))
            acc = [0, 0, 0]
            cnt = 0
            for yy in range(ya, min(yb, H)):
                row = disp[yy]
                for xx in range(xa, min(xb, W)):
                    p = row[xx]
                    acc[0] += p[0]
                    acc[1] += p[1]
                    acc[2] += p[2]
                    cnt += 1
            if not cnt:
                continue
            ref = raw[(fy * fw + fx) * 3:(fy * fw + fx) * 3 + 3]
            for c in range(3):
                e = acc[c] / cnt - ref[c]
                se[c] += e * e
                ae[c] += abs(e)
            n += 1
    mse = sum(se) / (3 * n)
    psnr = 10 * math.log10(255 * 255 / mse) if mse > 0 else float('inf')
    print(f'screencap {W}x{H} (bmp {fmt}) rect [{x0},{y0} {x1},{y1}] vs frame {fw}x{fh}: '
          f'MAE R/G/B {ae[0] / n:.2f}/{ae[1] / n:.2f}/{ae[2] / n:.2f}  PSNR {psnr:.2f} dB  (n={n})')


if __name__ == '__main__':
    main()
