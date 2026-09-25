#!/usr/bin/env python3
"""F2: stripe check on Odin 1080p screencaps (ST1 period-6 screen signature).

ST1 4d: Odin stripes are a ~+-4 LSB oscillation with ~6-row screen period
(guest period 2 x 2.125 vertical upscale + bilinear beat), global incl. static UI.
Method: decode PNG (stdlib, ST1 reader), crop window, per-row mean luma,
high-pass residual = rowmean - moving-avg(+-8), then:
  rms   RMS of residual (stripe strength in LSB)
  ac3   autocorrelation of residual at lag 3 (period-6 => strong negative)
Compares F1 (pre-fix) vs F2 (force-progressive) on identical geometry.
Usage: stripes.py --win x0,y0,x1,y1 [--rows] A.png [B.png ...]
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


def window_rows(w, h, ch, px, x0, y0, x1, y1):
    rows = []
    for y in range(y0, y1):
        base = y * w * ch
        sr = sg = sb = 0
        for x in range(x0, x1):
            o = base + x * ch
            sr += px[o]
            sg += px[o + 1]
            sb += px[o + 2]
        n = x1 - x0
        rows.append((0.299 * sr + 0.587 * sg + 0.114 * sb) / n)
    return rows


def main():
    args = sys.argv[1:]
    win = None
    want_rows = False
    while args and args[0].startswith('--'):
        a = args.pop(0)
        if a == '--win':
            win = tuple(int(v) for v in args.pop(0).split(','))
        elif a == '--rows':
            want_rows = True
    x0, y0, x1, y1 = win
    print('%-40s %7s %8s %12s' % ('file', 'rms', 'ac3', 'winmean'))
    for path in args:
        w, h, ch, px = read_png(path)
        rows = window_rows(w, h, ch, px, x0, y0, x1, y1)
        n = len(rows)
        sm = [sum(rows[max(0, i - 8):min(n, i + 9)]) / len(rows[max(0, i - 8):min(n, i + 9)])
              for i in range(n)]
        res = [rows[i] - sm[i] for i in range(n)]
        rms = (sum(r * r for r in res) / n) ** 0.5
        var = sum(r * r for r in res) / n or 1e-9
        ac3 = sum(res[i] * res[i + 3] for i in range(n - 3)) / (n - 3) / var
        print('%-40s %7.3f %+8.3f %12.2f' % (path[-40:], rms, ac3, sum(rows) / n))
        if want_rows:
            print('y,rowmean,resid')
            for i, (r, e) in enumerate(zip(rows, res)):
                print('%d,%.3f,%+.3f' % (y0 + i, r, e))


if __name__ == '__main__':
    main()
