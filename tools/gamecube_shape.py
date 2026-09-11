#!/usr/bin/env python3
"""GameCube SSX 3 shape containers (.gsh, magic SHPG): list, decode, and patch.

Layout (decoded 2026-09-11 from data/ui/fe_1.gsh):
  header  : 'SHPG', u32 LE total size, u32 BE entry count, 4-byte group tag
  entries : count x (4-byte name, u32 BE offset), from byte 16
  image   : u8 type (0x19 = 8-bit indexed), u24 BE size (header + pixels),
            u16 BE width, u16 BE height, 4 bytes zero, u32 LE header length
            (32), pixels; then a palette chunk: u8 type (0x32), u24 BE size,
            u16 BE entries, u16 BE 1, 4 zero, u32 LE 0, 256 x u16 BE RGB5A3.
The pixel swizzle is implemented in `untile`/`retile`; see PIXEL_LAYOUT.
"""
import argparse
from pathlib import Path
import struct

PIXEL_LAYOUT = 'tiles8x4'  # updated once verified against a runtime texture dump


def entries(data):
    if data[:4] != b'SHPG':
        raise ValueError('Not a SHPG shape container')
    count = struct.unpack_from('>I', data, 8)[0]
    out = []
    for i in range(count):
        name = data[16 + i * 8:20 + i * 8].decode('latin1')
        offset = struct.unpack_from('>I', data, 20 + i * 8)[0]
        out.append(dict(index=i, name=name, offset=offset))
    for e, nxt in zip(out, out[1:] + [dict(offset=len(data))]):
        e['end'] = nxt['offset']
    return out


def image(data, offset):
    kind = data[offset]
    size = int.from_bytes(data[offset + 1:offset + 4], 'big')
    width, height = struct.unpack_from('>HH', data, offset + 4)
    header = struct.unpack_from('<I', data, offset + 12)[0]
    if kind != 0x19 or header != 32 or size != header + width * height:
        raise ValueError(f'Unsupported image record at {offset:#x}: type {kind:#x}')
    pixels = data[offset + header:offset + size]
    pal_at = offset + size
    pal_kind = data[pal_at]
    pal_size = int.from_bytes(data[pal_at + 1:pal_at + 4], 'big')
    count = struct.unpack_from('>H', data, pal_at + 4)[0]
    palette = data[pal_at + 16:pal_at + 16 + count * 2]
    if pal_kind != 0x32 or len(palette) != count * 2:
        raise ValueError('Unsupported palette record')
    return dict(offset=offset, width=width, height=height, pixels=pixels, pixel_offset=offset + header,
                palette=[struct.unpack_from('>H', palette, i * 2)[0] for i in range(count)], palette_offset=pal_at + 16)


def rgb5a3(v):
    if v & 0x8000:
        return ((v >> 10 & 31) * 255 // 31, (v >> 5 & 31) * 255 // 31, (v & 31) * 255 // 31, 255)
    return ((v >> 8 & 15) * 17, (v >> 4 & 15) * 17, (v & 15) * 17, (v >> 12 & 7) * 255 // 7)


def untile(pixels, width, height):
    """Swizzled bytes -> row-major index image."""
    out = bytearray(width * height)
    i = 0
    for by in range(0, height, 4):
        for bx in range(0, width, 8):
            for y in range(4):
                out[(by + y) * width + bx:(by + y) * width + bx + 8] = pixels[i:i + 8]
                i += 8
    return bytes(out)


def retile(indices, width, height):
    """Row-major index image -> swizzled bytes (inverse of untile)."""
    out = bytearray(width * height)
    i = 0
    for by in range(0, height, 4):
        for bx in range(0, width, 8):
            for y in range(4):
                out[i:i + 8] = indices[(by + y) * width + bx:(by + y) * width + bx + 8]
                i += 8
    return bytes(out)


def to_png(data, offset, path):
    from PIL import Image
    img = image(data, offset)
    idx = untile(img['pixels'], img['width'], img['height'])
    cols = [rgb5a3(v) for v in img['palette']]
    im = Image.new('RGBA', (img['width'], img['height']))
    im.putdata([cols[i] for i in idx])
    im.save(path)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('shape', type=Path)
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--png', type=Path, help='Directory to write one PNG per image entry')
    args = ap.parse_args()
    data = args.shape.read_bytes()
    for e in entries(data):
        if args.list:
            print(f"{e['index']:3} {e['name']!r:8} {e['offset']:#8x} {e['end'] - e['offset']:8}")
        if args.png and data[e['offset']] == 0x19:
            args.png.mkdir(parents=True, exist_ok=True)
            img = to_png(data, e['offset'], args.png / f"{e['index']:02}_{e['name'].strip().replace(' ', '_')}.png")
            print(f"wrote {e['index']} {img['width']}x{img['height']}")


if __name__ == '__main__':
    main()
