#!/usr/bin/env python3
"""Repaint the GameCube button glyphs in SSX 3's UI sheets as Xbox-style icons.

The `art_` image of data/ui/fe_1.gsh, ov_1.gsh and gl_1.gsh (identical in
all three) holds the prompt icons. The game keeps drawing the GameCube
input's icon, so the icon in each slot is repainted for the Xbox button at
the same physical position: GameCube B (left) -> blue X, GameCube X (right)
-> red B, GameCube Y (top) -> yellow Y; A stays. Xbox blue is not in the
shared 256-colour palette, so the least-used palette entry is repurposed.
"""
import argparse
from collections import Counter
from pathlib import Path
import struct

from PIL import Image, ImageDraw, ImageFont

from gamecube_shape import entries, image, rgb5a3, untile, retile

# Slots measured from the stock sheet (x0, y0, x1, y1 inclusive) and their new look.
SLOTS = {
    'B': dict(rect=(2, 165, 25, 196), letter='X', colour=(0, 105, 200, 255)),
    'X': dict(rect=(62, 170, 82, 200), letter='B', colour=(196, 16, 16, 255)),
    'Y': dict(rect=(85, 174, 121, 205), letter='Y', colour=(225, 185, 30, 255)),
}
FONT_CANDIDATES = ['/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/System/Library/Fonts/Helvetica.ttc',
                   '/Library/Fonts/Arial Bold.ttf']


def to_rgb5a3(c):
    r, g, b, a = c
    if a >= 224:
        return 0x8000 | (r >> 3) << 10 | (g >> 3) << 5 | (b >> 3)
    return (a >> 5) << 12 | (r >> 4) << 8 | (g >> 4) << 4 | (b >> 4)


def font(size):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def repaint(pixels, palette, width, height):
    idx = bytearray(untile(pixels, width, height))
    cols = [rgb5a3(v) for v in palette]
    used = Counter(idx)
    # Repurpose the least-used entry for Xbox blue (never the transparent index 0).
    blue_index = min((i for i in range(len(cols)) if i != 0), key=lambda i: used[i])
    palette = list(palette)
    palette[blue_index] = to_rgb5a3(SLOTS['B']['colour'])
    cols[blue_index] = rgb5a3(palette[blue_index])
    opaque = [i for i in range(len(cols)) if cols[i][3] == 255]

    def nearest(c):
        if c[3] < 96:
            return 0
        return min(opaque, key=lambda i: sum(abs(a - b) for a, b in zip(cols[i][:3], c[:3])))

    changes = {}
    for slot, spec in SLOTS.items():
        x0, y0, x1, y1 = spec['rect']
        w, h = x1 - x0 + 1, y1 - y0 + 1
        canvas = Image.new('RGBA', (w * 4, h * 4), (0, 0, 0, 0))   # paint at 4x, then downsample
        d = ImageDraw.Draw(canvas)
        diameter = min(w, h) - 2
        cx, cy = w * 2, h * 2
        r = diameter * 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(0, 0, 0, 255))
        d.ellipse((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), fill=spec['colour'])
        f = font(int(diameter * 4 * 0.8))
        bbox = d.textbbox((0, 0), spec['letter'], font=f)
        tx, ty = cx - (bbox[0] + bbox[2]) / 2, cy - (bbox[1] + bbox[3]) / 2
        d.text((tx, ty), spec['letter'], font=f, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
        small = canvas.resize((w, h), Image.LANCZOS)
        px = list(small.getdata())
        for j in range(h):
            for i in range(w):
                idx[(y0 + j) * width + x0 + i] = nearest(px[j * w + i])
        changes[slot] = dict(rect=spec['rect'], letter=spec['letter'])
    return retile(bytes(idx), width, height), palette, dict(blue_index=blue_index, slots=changes)


def patch_sheet(path, output):
    data = bytearray(path.read_bytes())
    report = []
    for e in entries(data):
        if e['name'] != 'art_':
            continue
        img = image(data, e['offset'])
        pixels, palette, info = repaint(img['pixels'], img['palette'], img['width'], img['height'])
        data[img['pixel_offset']:img['pixel_offset'] + len(pixels)] = pixels
        for i, v in enumerate(palette):
            struct.pack_into('>H', data, img['palette_offset'] + i * 2, v)
        report.append(dict(entry=e['index'], **info))
    if not report:
        raise ValueError(f'{path} has no art_ image')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('ui_dir', type=Path, help='data/ui directory of an extracted disc')
    ap.add_argument('output', type=Path, help='Directory for the patched .gsh files')
    ap.add_argument('--preview', type=Path, help='Write a PNG of the patched art_ image')
    args = ap.parse_args()
    for name in ('fe_1', 'ov_1', 'gl_1'):
        report = patch_sheet(args.ui_dir / f'{name}.gsh', args.output / f'{name}.gsh')
        print(name, report)
    if args.preview:
        from gamecube_shape import to_png
        data = (args.output / 'fe_1.gsh').read_bytes()
        e = [x for x in entries(data) if x['name'] == 'art_'][0]
        to_png(data, e['offset'], args.preview)


if __name__ == '__main__':
    main()
