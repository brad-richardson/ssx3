#!/usr/bin/env python3
"""E4 miner (final): reproduce the branch-(c) join from canonical artifacts.

Reads $W/P1/run/{boot-e4-1.log, e4-1/*, frames-e4-1/*, park-e4-1/*} plus the
K1 prim baseline /tmp/k1-prim.txt (regenerable: grep gs:prim boot-k1-1.log).
Part 1: determinism + coverage. Part 2: history tables. Part 3: VRAM surface
decode with correct block=fbp<<5 addressing (repairs report erratum E1).
Part 4: Present join. Writes thumbnails e4-disp1.png / e4-fbp0.png.
"""
import collections
import re
import struct
import sys
import zlib

W = "/Volumes/Extreme SSD/ps2recomp-spike"
RUN = W + "/P1/run"
E4 = RUN + "/e4-1"
HIST = E4 + "/e4-history.txt"
PRES = E4 + "/e4-present.txt"
VRAM = E4 + "/e4-vram-freeze.bin"
LOG = RUN + "/boot-e4-1.log"

BLOCK_TBL = [
    [0, 1, 4, 5, 16, 17, 20, 21], [2, 3, 6, 7, 18, 19, 22, 23],
    [8, 9, 12, 13, 24, 25, 28, 29], [10, 11, 14, 15, 26, 27, 30, 31],
]
COL_TBL = [
    [0, 1, 4, 5, 8, 9, 12, 13], [2, 3, 6, 7, 10, 11, 14, 15],
    [16, 17, 20, 21, 24, 25, 28, 29], [18, 19, 22, 23, 26, 27, 30, 31],
    [32, 33, 36, 37, 40, 41, 44, 45], [34, 35, 38, 39, 42, 43, 46, 47],
    [48, 49, 52, 53, 56, 57, 60, 61], [50, 51, 54, 55, 58, 59, 62, 63],
]

def addr_ct32(block, bw, x, y):
    ppr = bw if bw else 1
    page = (block >> 5) + (y >> 5) * ppr + (x >> 6)
    bid = (block & 0x1F) + BLOCK_TBL[(y >> 3) & 3][(x >> 3) & 7]
    return (page << 13) + ((bid >> 5) << 13) + (bid & 0x1F) * 256 + COL_TBL[y & 7][x & 7] * 4

def write_png(path, w, h, rgba):
    raw = b"".join(b"\x00" + bytes(rgba[y * w * 4:(y + 1) * w * 4]) for y in range(h))
    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))

print("== P1 determinism ==")
e4prim = [l for l in open(LOG, errors="replace") if "[gs:prim]" in l]
k1prim = [l for l in open("/tmp/k1-prim.txt") if "[gs:prim]" in l]
print(f"R4-prefix identical: {e4prim == k1prim} ({len(e4prim)} lines)")
up1 = [l for l in open(LOG, errors="replace") if "[frame:upload]" in l][0]
print(f"first-upload: {up1.strip()}")

print("== P1 coverage ==")
hdr = [l for l in open(HIST) if l.startswith("#")]
print("".join(hdr).strip())
evs = [l for l in open(HIST) if l.startswith("[e4:ev]")]
print(f"event lines: {len(evs)} (cap 512, overflow: none)" if len(evs) < 512 else "OVERFLOW")

print("== P2 history tables ==")
print("kinds:", dict(collections.Counter(re.search(r"kind=([a-z]+)", l).group(1) for l in evs)))
draws = [l for l in evs if "kind=draw" in l]
print("draw prims:", dict(collections.Counter(re.search(r"prim=(\d)", l).group(1) for l in draws)))
print("draw fbp:", dict(collections.Counter(re.search(r"fbp=(\d+)", l).group(1) for l in draws)))
print("draw tex0:", dict(collections.Counter(re.search(r"tex0=([^ ]+)", l).group(1) for l in draws)))
regs = [l for l in evs if "kind=reg" in l]
print("regs:", sorted(collections.Counter(re.search(r"reg=0x([0-9a-f]+)", l).group(1) for l in regs).items()))
xs, ys = [], []
for l in draws:
    m = re.search(r"x=([0-9.]+)\.\.([0-9.]+) y=([0-9.]+)\.\.([0-9.]+)", l)
    xs += [float(m.group(1)) - 1792, float(m.group(2)) - 1792]
    ys += [float(m.group(3)) - 1824, float(m.group(4)) - 1824]
print(f"draw onscreen x: {min(xs):.1f}..{max(xs):.1f} y: {min(ys):.1f}..{max(ys):.1f} (ofx/ofy=1792/1824)")

print("== P3 surface decode (block=fbp<<5) ==")
vram = open(VRAM, "rb").read()
def census(name, fbp, fbw, w, h, thumb, tw=128, th=112):
    block = fbp << 5
    raw = rgb = 0
    minx, miny, maxx, maxy = w, h, -1, -1
    first = None
    for y in range(h):
        for x in range(w):
            v = struct.unpack_from("<I", vram, addr_ct32(block, fbw, x, y))[0]
            if v: raw += 1
            if v & 0x00FFFFFF:
                rgb += 1
                minx = min(minx, x); miny = min(miny, y); maxx = max(maxx, x); maxy = max(maxy, y)
                if first is None: first = (x, y, f"0x{v:08x}")
    print(f"{name}: fbp={fbp} fbw={fbw} {w}x{h} rawNz={raw} rgbNz={rgb} "
          f"bbox={None if first is None else (minx, miny, maxx, maxy)} first={first}")
    px = bytearray(tw * th * 4)
    for ty in range(th):
        for tx in range(tw):
            v = struct.unpack_from("<I", vram, addr_ct32(block, fbw, (tx * w) // tw, (ty * h) // th))[0]
            i = (ty * tw + tx) * 4
            px[i] = v & 0xFF; px[i+1] = (v >> 8) & 0xFF; px[i+2] = (v >> 16) & 0xFF; px[i+3] = 255
    write_png(thumb, tw, th, px)
    print(f"  thumb={thumb}")
census("disp1-fbp112", 112, 8, 512, 448, "/tmp/e4-disp1.png")
census("fbp0", 0, 8, 512, 512, "/tmp/e4-fbp0.png", 128, 128)

print("== P4 present join ==")
for l in open(LOG, errors="replace"):
    if re.search(r"frame:dump.*tick=60[01] ", l):
        print(l.strip())
print(open(PRES).read().strip().splitlines()[1])
