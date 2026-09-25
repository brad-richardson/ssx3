#!/usr/bin/env python3
"""ST1: per-row mean luminance + period-2 (alternate-line) stripe test.

Usage: st1_rowluma.py [--rows|--tiles] A.png [B.png ...]
PNG decoder is GB8's validated stdlib reader (rgb/rgba8, non-interlaced).
--tiles prints an 8x8 grid of signed period-2 amplitude per tile:
mean((L[y][x]-tilemean) * (-1)^y). Coherent stripes give large |A| with a
consistent sign; random content edges cancel toward 0.

Metrics per frame (luma = 0.299R + 0.587G + 0.114B, per-row mean over x):
  mean      global mean luma
  A         signed period-2 amplitude = mean((row[y]-mean) * (-1)^y);
            A > 0 means even rows brighter; |A| is the stripe strength in LSB
  d1/d2     RMS of adjacent-row diffs / RMS of stride-2-row diffs;
            pure stripes give d1 >> d2 (ratio >> 1); smooth content ~ 1
  even/odd  mean luma of even / odd rows
--rows also prints the full per-row mean table (for committed text evidence).
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


def row_means(w, h, ch, px):
    rows = []
    for y in range(h):
        base = y * w * ch
        sr = sg = sb = 0
        for x in range(w):
            o = base + x * ch
            sr += px[o]
            sg += px[o + 1]
            sb += px[o + 2]
        rows.append((0.299 * sr + 0.587 * sg + 0.114 * sb) / w)
    return rows


def analyze(path):
    w, h, ch, px = read_png(path)
    rows = row_means(w, h, ch, px)
    mean = sum(rows) / h
    alt = sum((r - mean) * (1 if (y % 2 == 0) else -1) for y, r in enumerate(rows)) / h
    even = sum(rows[0::2]) / ((h + 1) // 2)
    odd = sum(rows[1::2]) / (h // 2)
    d1 = (sum((rows[y + 1] - rows[y]) ** 2 for y in range(h - 1)) / (h - 1)) ** 0.5
    d2 = (sum((rows[y + 2] - rows[y]) ** 2 for y in range(h - 2)) / (h - 2)) ** 0.5
    return {'file': path, 'size': '%dx%d' % (w, h), 'mean': mean, 'A': alt,
            'even': even, 'odd': odd, 'd1': d1, 'd2': d2,
            'd1/d2': d1 / d2 if d2 else float('inf'), 'rows': rows}


def tile_map(w, h, ch, px, nx=8, ny=8):
    # luma plane
    lum = [[0.0] * w for _ in range(h)]
    for y in range(h):
        base = y * w * ch
        row = lum[y]
        for x in range(w):
            o = base + x * ch
            row[x] = 0.299 * px[o] + 0.587 * px[o + 1] + 0.114 * px[o + 2]
    acc = [[0.0] * nx for _ in range(ny)]
    tot = [[0.0] * nx for _ in range(ny)]
    cnt = [[0] * nx for _ in range(ny)]
    for y in range(h):
        ty = min(y * ny // h, ny - 1)
        sgn = 1.0 if (y % 2 == 0) else -1.0
        row = lum[y]
        for x in range(w):
            tx = min(x * nx // w, nx - 1)
            acc[ty][tx] += sgn * row[x]
            tot[ty][tx] += row[x]
            cnt[ty][tx] += 1
    out = []
    for ty in range(ny):
        orow = []
        for tx in range(nx):
            # tiles hold equal even/odd row counts, so no mean bias
            orow.append(acc[ty][tx] / cnt[ty][tx])
        out.append(orow)
    return out


def main():
    args = sys.argv[1:]
    want_rows = want_tiles = False
    if args and args[0] == '--rows':
        want_rows = True
        args = args[1:]
    elif args and args[0] == '--tiles':
        want_tiles = True
        args = args[1:]
    if not args:
        raise SystemExit('usage: st1_rowluma.py [--rows|--tiles] A.png [B.png ...]')
    print('%-42s %-9s %7s %8s %7s %7s %6s %6s %6s' %
          ('file', 'size', 'mean', 'A(alt)', 'even', 'odd', 'd1', 'd2', 'd1/d2'))
    for path in args:
        a = analyze(path)
        print('%-42s %-9s %7.2f %+8.3f %7.2f %7.2f %6.2f %6.2f %6.2f' %
              (a['file'][-42:], a['size'], a['mean'], a['A'], a['even'],
               a['odd'], a['d1'], a['d2'], a['d1/d2']))
        if want_rows:
            print('y,rowmean')
            for y, r in enumerate(a['rows']):
                print('%d,%.3f' % (y, r))
        if want_tiles:
            w, h, ch, px = read_png(path)
            for trow in tile_map(w, h, ch, px):
                print(' '.join('%5.2f' % v for v in trow))


if __name__ == '__main__':
    main()
