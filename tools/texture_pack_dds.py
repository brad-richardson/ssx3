#!/usr/bin/env python3
"""Convert a PNG texture pack to block-compressed DDS, chain and all.

A PNG pack pays for itself three times on the phone. It is 8,806 files for 927
textures (a base plus a `_mipN` sidecar per level), every one of which is a
separate open; each is PNG-compressed, so it has to be *decoded* before upload,
which is the mid-ride stall when new art appears; and it decodes to RGBA8, which
is 894 MB for `pack-v8` even after `texture_pack_cap.py`.

DDS answers all three at once, and the device can take it. `MTLUtil.mm` gates
`bSupportsST3CTextures` on `[device supportsBCTextureCompression]`, a runtime
question, and the app records the answer: on the A18 Pro it is true. So:

* one file carries its whole chain (`CustomTextureData.cpp`, the `mip_count`
  loop), turning 8,806 files into 927;
* block data is uploaded as-is with no decode, which removes the stall rather
  than moving it to load time;
* DXT1 is 0.5 bytes a pixel against RGBA8's 4, so the pack's resident cost
  drops by about 8x and preloading it becomes cheap.

Format per texture, not per pack. DXT1 wherever alpha is absent or already
binary - which is every alpha-tested cutout, and `PIL`'s DXT1 round-trips a hard
cutout edge as exactly {0, 255}, so the mask the guest alpha-*tests* survives
intact (docs/texture-remaster.md §10.5). DXT5 only where alpha is a genuine
gradient, at twice the size.

  python3 tools/texture_pack_dds.py PACK --output OUT [--report R] [--dry-run]

Levels come from the pack's own `_mipN` sidecars where they exist, so the
alpha-weighted colour averaging `pack_mipmaps.py` did is preserved rather than
recomputed; anything missing is rebuilt with the same helper.
"""

import argparse
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pack_mipmaps import build_levels, chain_sizes  # noqa: E402

MIP = re.compile(r'_mip(\d+)$')

DDS_MAGIC = 0x20534444                  # "DDS "
# DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT, which is exactly what
# ParseDDSHeader requires; PITCH and LINEARSIZE are deliberately NOT set, because
# Dolphin reinterprets dwPitchOrLinearSize only when both are present and we
# would rather it derive the layout from the dimensions.
DDSD_REQUIRED = 0x00001007
DDSD_MIPMAPCOUNT = 0x00020000
DDPF_FOURCC = 0x00000004
DDSCAPS_COMPLEX = 0x00000008
DDSCAPS_TEXTURE = 0x00001000
DDSCAPS_MIPMAP = 0x00400000
PIL_DDS_HEADER = 128                    # magic + DDS_HEADER, which PIL also writes

BLOCK = 4
BYTES_PER_BLOCK = {'DXT1': 8, 'DXT5': 16}


def blocks(extent):
    """Block count along one axis; a 2x2 level still occupies one whole block."""
    return max((extent + BLOCK - 1) // BLOCK, 1)


def level_size(width, height, fmt):
    return blocks(width) * blocks(height) * BYTES_PER_BLOCK[fmt]


def alpha_class(image):
    """'opaque', 'binary' or 'gradient' - which decides the format.

    Binary counts as opaque-grade for DXT1: its one alpha bit reproduces a hard
    mask exactly, and everything in this pack with alpha is an alpha-tested
    cutout rather than a blended sprite.
    """
    import numpy as np
    alpha = np.asarray(image.convert('RGBA'), dtype=np.uint8)[..., 3]
    if (alpha == 255).all():
        return 'opaque'
    edge = ((alpha == 0) | (alpha == 255)).mean()
    return 'binary' if edge >= 0.95 else 'gradient'


def pick_format(image):
    return 'DXT5' if alpha_class(image) == 'gradient' else 'DXT1'


def encode_level(image, fmt):
    """One level's block bytes, via PIL, with its own 128-byte header removed."""
    import io
    from PIL import Image
    buffer = io.BytesIO()
    image.convert('RGBA').save(buffer, format='DDS', pixel_format=fmt)
    data = buffer.getvalue()[PIL_DDS_HEADER:]
    expected = level_size(image.width, image.height, fmt)
    if len(data) != expected:
        raise ValueError(f'{fmt} {image.width}x{image.height}: '
                         f'{len(data)} block bytes, expected {expected}')
    return data


def dds_header(width, height, levels, fmt):
    """The 128 bytes Dolphin's ParseDDSHeader accepts for a mipmapped DXTn."""
    flags = DDSD_REQUIRED | (DDSD_MIPMAPCOUNT if levels > 1 else 0)
    caps = DDSCAPS_TEXTURE | ((DDSCAPS_COMPLEX | DDSCAPS_MIPMAP) if levels > 1 else 0)
    header = struct.pack(
        '<I'          # magic
        'I'           # dwSize
        'I'           # dwFlags
        'II'          # dwHeight, dwWidth
        'I'           # dwPitchOrLinearSize (informational; no flag claims it)
        'I'           # dwDepth
        'I'           # dwMipMapCount
        '44x'         # dwReserved1[11]
        'I'           # ddspf.dwSize
        'I'           # ddspf.dwFlags
        '4s'          # ddspf.dwFourCC
        '20x'         # bit counts and masks, unused for a fourCC format
        'I'           # dwCaps
        'I'           # dwCaps2
        '12x',        # dwCaps3, dwCaps4, dwReserved2
        DDS_MAGIC, 124, flags, height, width,
        level_size(width, height, fmt), 0, levels,
        32, DDPF_FOURCC, fmt.encode('ascii'),
        caps, 0)
    if len(header) != PIL_DDS_HEADER:
        raise ValueError(f'DDS header is {len(header)} bytes, must be {PIL_DDS_HEADER}')
    return header


def sidecar_levels(pack, stem):
    """The pack's own `_mipN` images for one base, in order, stopping at a gap."""
    from PIL import Image
    found = []
    index = 1
    while True:
        path = pack / f'{stem}_mip{index}.png'
        if not path.exists():
            break
        with Image.open(path) as image:
            found.append(image.convert('RGBA'))
        index += 1
    return found


def texture_levels(pack, path):
    """Base plus chain, preferring the sidecars the pack already carries."""
    from PIL import Image
    with Image.open(path) as opened:
        base = opened.convert('RGBA')
    wanted = chain_sizes(base.width, base.height)
    levels = [base] + sidecar_levels(pack, path.stem)
    sizes = [(level.width, level.height) for level in levels[1:]]
    if sizes == wanted:
        return levels, 'sidecars'
    # A partial or absent chain is rebuilt whole rather than mixed: Dolphin
    # stops at the first level that is not exactly half of the one above it.
    return [base] + build_levels(base), 'rebuilt'


def convert_texture(pack, path, destination, dry_run=False):
    levels, source = texture_levels(pack, path)
    fmt = pick_format(levels[0])
    payload = b''.join(encode_level(level, fmt) for level in levels)
    data = dds_header(levels[0].width, levels[0].height, len(levels), fmt) + payload
    if not dry_run:
        destination.write_bytes(data)
    return dict(name=path.name, format=fmt, levels=len(levels), chain=source,
                width=levels[0].width, height=levels[0].height,
                bytes=len(data), decoded=levels[0].width * levels[0].height * 4)


def convert_pack(pack, output, dry_run=False):
    pack = Path(pack)
    output = Path(output)
    if not dry_run:
        output.mkdir(parents=True, exist_ok=True)
    report = {'pack': str(pack), 'output': str(output), 'textures': 0,
              'dxt1': 0, 'dxt5': 0, 'rebuilt_chains': 0,
              'dds_bytes': 0, 'png_bytes': 0, 'entries': []}
    bases = sorted(p for p in pack.glob('tex1_*.png') if not MIP.search(p.stem))
    for path in bases:
        entry = convert_texture(pack, path, output / f'{path.stem}.dds', dry_run)
        report['textures'] += 1
        report['dxt1'] += entry['format'] == 'DXT1'
        report['dxt5'] += entry['format'] == 'DXT5'
        report['rebuilt_chains'] += entry['chain'] == 'rebuilt'
        report['dds_bytes'] += entry['bytes']
        report['entries'].append(entry)
    report['png_files'] = len(list(pack.glob('tex1_*.png')))
    report['png_bytes'] = sum(p.stat().st_size for p in pack.glob('tex1_*.png'))
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pack', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--report', type=Path)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    report = convert_pack(args.pack, args.output, args.dry_run)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(f"{report['textures']} textures: {report['dxt1']} DXT1, {report['dxt5']} DXT5, "
          f"{report['rebuilt_chains']} chains rebuilt")
    print(f"files {report['png_files']} -> {report['textures']}")
    print(f"on disk {report['png_bytes'] / 1e6:.0f} MB -> {report['dds_bytes'] / 1e6:.0f} MB")


if __name__ == '__main__':
    main()
