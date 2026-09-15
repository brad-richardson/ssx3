#!/usr/bin/env python3
"""Build a side-by-side sheet comparing upscaler passes on the same textures.

Rows are textures, columns are the source followed by each pass directory. The
source is enlarged with nearest-neighbour so it shows the texels it actually
has, and every cell is the same crop of the same region, so the comparison is
of detail rather than of framing. Pass directories are matched to the source by
file name, which the upscaler preserves.
"""
import argparse
import json
from pathlib import Path


def label_strip(width, height, text):
    from PIL import Image, ImageDraw
    strip = Image.new('RGBA', (width, height), (18, 18, 22, 255))
    draw = ImageDraw.Draw(strip)
    draw.text((6, max(0, height // 2 - 6)), text, fill=(235, 235, 240, 255))
    return strip


def crop_cell(image, cell, zoom, anchor):
    """The same region of every image, at a fixed output size."""
    from PIL import Image
    side = max(1, int(round(min(image.width, image.height) / zoom)))
    left = int((image.width - side) * anchor)
    top = int((image.height - side) * anchor)
    patch = image.crop((left, top, left + side, top + side))
    resample = Image.NEAREST if patch.width <= cell // 2 else Image.LANCZOS
    return patch.resize((cell, cell), resample)


def build(source, passes, names, output, cell=256, zoom=2.0, anchor=0.5, limit=None):
    from PIL import Image
    files = sorted(p for p in source.iterdir() if p.name.startswith('tex1_') and p.suffix == '.png')
    if limit:
        files = files[:limit]
    columns = ['source', *names]
    header = 22
    sheet = Image.new('RGBA', (len(columns) * cell, header + len(files) * (cell + header)),
                      (18, 18, 22, 255))
    for column, name in enumerate(columns):
        sheet.alpha_composite(label_strip(cell, header, name), (column * cell, 0))
    for row, path in enumerate(files):
        top = header + row * (cell + header)
        sheet.alpha_composite(label_strip(len(columns) * cell, header, path.name),
                              (0, top + cell))
        images = [Image.open(path).convert('RGBA')]
        for directory in passes:
            candidate = directory / path.name
            images.append(Image.open(candidate).convert('RGBA') if candidate.is_file() else None)
        for column, image in enumerate(images):
            if image is None:
                continue
            sheet.alpha_composite(crop_cell(image, cell, zoom, anchor), (column * cell, top))
    sheet.save(output)
    return {'output': str(output), 'textures': len(files), 'columns': columns,
            'cell': cell, 'zoom': zoom, 'anchor': anchor}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source', type=Path, help='Directory of the original dumped textures')
    ap.add_argument('passes', type=Path, nargs='+', help='One directory per upscaler pass')
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--names', nargs='+', help='Column labels (default: directory names)')
    ap.add_argument('--cell', type=int, default=256, help='Pixel size of each cell (default 256)')
    ap.add_argument('--zoom', type=float, default=2.0,
                    help='How far into each texture to crop; 1 shows the whole thing (default 2)')
    ap.add_argument('--anchor', type=float, default=0.5, help='Crop position, 0 top-left to 1 bottom-right')
    ap.add_argument('--limit', type=int, help='Only the first N textures')
    ap.add_argument('--receipt', type=Path)
    args = ap.parse_args()
    names = args.names or [d.name for d in args.passes]
    if len(names) != len(args.passes):
        ap.error('--names must match the number of pass directories')
    report = build(args.source, args.passes, names, args.output,
                   args.cell, args.zoom, args.anchor, args.limit)
    if args.receipt:
        args.receipt.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
