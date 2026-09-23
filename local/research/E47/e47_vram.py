#!/usr/bin/env python3
"""E47 VRAM decode: E4 arm/freeze snapshots -> PNGs + nonblack census.

Usage: python3 local/research/E47/e47_vram.py <label> [<label> ...]
Reads ~/dev/ssx3-work/E47-run/e4-<label>/e4-vram-{arm,freeze}.bin; writes
local/research/E47/frames/<label>-{arm,freeze}-fbp{0,112}.png.
fbp0 = draw target (PSMCT32, fbw 8), fbp112 = display (PSMCT24, fbw 8);
both use CT32 addressing (block = fbp << 5), copied from E4/e4-mine.py.
"""
import os
import struct
import sys
import zlib

RUN = os.path.expanduser("~/dev/ssx3-work/E47-run")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames")

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


def decode(vram, fbp, w=512, h=448, bw=8):
    rgba = bytearray(w * h * 4)
    nonblack = 0
    lum = 0
    for y in range(h):
        for x in range(w):
            a = addr_ct32(fbp << 5, bw, x, y) % len(vram)
            r, g, b = vram[a], vram[a + 1], vram[a + 2]
            i = (y * w + x) * 4
            rgba[i:i + 4] = bytes((r, g, b, 255))
            if r | g | b:
                nonblack += 1
            lum += r + g + b
    return rgba, nonblack / (w * h), lum / (w * h * 3)


def main(labels):
    os.makedirs(OUT, exist_ok=True)
    print("| label | snapshot | surface | nonblack px | mean level (0-255) | png |")
    print("|---|---|---|---|---|---|")
    for label in labels:
        for snap in ("arm", "freeze"):
            vram = open(f"{RUN}/e4-{label}/e4-vram-{snap}.bin", "rb").read()
            for fbp in (0, 112):
                rgba, nb, lum = decode(vram, fbp)
                name = f"{label}-{snap}-fbp{fbp}.png"
                write_png(os.path.join(OUT, name), 512, 448, rgba)
                print(f"| {label} | {snap} | fbp{fbp} | {nb:.1%} | {lum:.1f} | `frames/{name}` |")


if __name__ == "__main__":
    main(sys.argv[1:])
