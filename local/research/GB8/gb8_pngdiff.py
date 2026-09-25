#!/usr/bin/env python3
"""GB8: pixel-diff two non-interlaced RGB/RGBA PNGs with stdlib only.

Usage: gb8_pngdiff.py A.png B.png
Prints size, fraction of exactly-equal pixels, and fraction within +/-2 per
channel (TL1's bilinear-noise metric).
"""
import struct
import sys
import zlib


def read_png(path):
    data = open(path, 'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', path
    w = h = bitd = ctype = None
    raw = b''
    pos = 8
    while pos < len(data):
        (ln,) = struct.unpack('>I', data[pos:pos + 4])
        typ = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        if typ == b'IHDR':
            w, h, bitd, ctype, comp, filt, inter = struct.unpack('>IIBBBBB', chunk)
            assert bitd == 8 and ctype in (2, 6) and inter == 0, (path, bitd, ctype, inter)
        elif typ == b'IDAT':
            raw += chunk
        pos += 12 + ln
    ch = 3 if ctype == 2 else 4
    stride = w * ch
    px = zlib.decompress(raw)
    out = bytearray(w * h * ch)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = px[p]
        p += 1
        line = bytearray(px[p:p + stride])
        p += stride
        if f == 1:
            for i in range(ch, stride):
                line[i] = (line[i] + line[i - ch]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                b = prev[i]
                c = prev[i - ch] if i >= ch else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        elif f != 0:
            raise SystemExit('bad filter %d' % f)
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, ch, bytes(out)


def main():
    a, b = sys.argv[1], sys.argv[2]
    w1, h1, c1, d1 = read_png(a)
    w2, h2, c2, d2 = read_png(b)
    assert (w1, h1) == (w2, h2), ((w1, h1), (w2, h2))
    n = w1 * h1
    if c1 == 4:
        d1 = bytes(x for i, x in enumerate(d1) if i % 4 != 3)
    if c2 == 4:
        d2 = bytes(x for i, x in enumerate(d2) if i % 4 != 3)
    eq = sum(1 for i in range(0, 3 * n, 3)
             if d1[i:i + 3] == d2[i:i + 3])
    per = [max(abs(d1[3 * i + k] - d2[3 * i + k]) for k in range(3)) for i in range(n)]
    w2n = sum(1 for d in per if d <= 2)
    w8n = sum(1 for d in per if d <= 8)
    print('%dx%d equal_px=%.4f within2=%.4f within8=%.4f meanabs=%.2f maxdiff=%d'
          % (w1, h1, eq / n, w2n / n, w8n / n, sum(per) / n, max(per)))


if __name__ == '__main__':
    main()
