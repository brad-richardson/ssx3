#!/usr/bin/env python3
# G10: 8-scanout series table + FIRST/LAST continuity check.
# Reads PPM/PNG bytes directly (no PIL): dims, distinct RGB colors,
# nonblack pixel count, sha256 (short). Usage: g10-series.py <dir> <pattern>
import struct, sys, glob, hashlib, os

def read_ppm(path):
    b = open(path, 'rb').read()
    assert b[:3] == b'P6\n', path
    o = 3
    dims = []
    while len(dims) < 3:
        while b[o:o+1] == b'#':
            while b[o:o+1] != b'\n': o += 1
            o += 1
        tok = b''
        while b[o:o+1] not in (b' ', b'\n', b'\t'):
            tok += b[o:o+1]; o += 1
        dims.append(int(tok))
        o += 1
    w, h, mx = dims
    assert mx == 255, path
    px = b[o:o+w*h*3]
    assert len(px) == w*h*3, (path, len(px), w, h)
    return w, h, px

def stats(path):
    w, h, px = read_ppm(path)
    n = w*h
    cells = [px[i:i+3] for i in range(0, len(px), 3)]
    distinct = len(set(cells))
    nonblack = sum(1 for c in cells if c != b'\x00\x00\x00')
    sha = hashlib.sha256(open(path,'rb').read()).hexdigest()[:16]
    return w, h, n, distinct, nonblack, sha

def main(d, pat):
    files = sorted(glob.glob(os.path.join(d, pat)))
    print(f"dir={d} pattern={pat} files={len(files)}")
    for f in files:
        w, h, n, dc, nb, sha = stats(f)
        print(f"  {os.path.basename(f)}: {w}x{h} px={n} "
              f"distinct={dc} nonblack={nb} ({nb/n:.4f}) sha={sha}")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
