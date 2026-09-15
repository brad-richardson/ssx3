#!/usr/bin/env python3
"""Give every texture in a pack the mip chain the guest texture had.

This is not an optimisation. Dolphin sets a custom texture's mip count from the
levels the *pack* supplies (`TextureCacheBase::CreateTextureEntry`:
`texLevels = custom_texture_data->m_slices[0].m_levels.size()`), so replacing a
mipmapped guest texture with a single PNG leaves it with one level while the
stock texture had a full chain. The base level is then sampled at every
distance, and an upscaled base has four times the detail to alias with: distant
snow and road surfaces shimmer and show moire banding that the stock game does
not have.

The fix is to ship the levels. Dolphin looks for `<name>_mip1`, `_mip2` and so
on next to the base, loading until one is missing, and requires each to be
exactly half the previous (`TextureAssetUtils.cpp`), which is what a box filter
of the level above gives. Levels are generated from the pack's own base, not
from the guest's mips, so the chain stays consistent with the art that is
actually shipped.

Cost is about a third more bytes and an order of magnitude more files, so
`--min-size` stops the chain early when the file count matters more than the
last two levels (a 4x4 mip covers a texture drawn a few pixels wide).
"""
import argparse
import json
from pathlib import Path

NAME_PREFIX = 'tex1_'


def chain_sizes(width, height, min_size=1):
    """Every level below the base, halving until one side reaches min_size."""
    sizes = []
    while width > min_size or height > min_size:
        width = max(width // 2, 1)
        height = max(height // 2, 1)
        sizes.append((width, height))
        if width == 1 and height == 1:
            break
    return sizes


def build_levels(image, min_size=1):
    """Box-filter the chain. Each level is exactly half of the one above it."""
    from PIL import Image
    levels = []
    current = image
    for width, height in chain_sizes(image.width, image.height, min_size):
        current = current.resize((width, height), Image.BOX)
        levels.append(current)
    return levels


def write_pack(pack, min_size=1, dry_run=False):
    from PIL import Image
    bases = sorted(p for p in pack.iterdir()
                   if p.suffix.lower() == '.png' and p.name.startswith(NAME_PREFIX)
                   and '_mip' not in p.name)
    written, bytes_added, skipped = 0, 0, []
    for path in bases:
        with Image.open(path) as image:
            image = image.convert('RGBA') if image.mode in ('RGBA', 'LA', 'P') else image.convert('RGB')
            levels = build_levels(image, min_size)
        for index, level in enumerate(levels, start=1):
            target = path.with_name(f'{path.stem}_mip{index}{path.suffix}')
            if target.exists():
                skipped.append(target.name)
                continue
            if not dry_run:
                level.save(target)
                bytes_added += target.stat().st_size
            written += 1
    return {'pack': str(pack), 'bases': len(bases), 'levels_written': written,
            'bytes_added': bytes_added, 'already_present': len(skipped),
            'min_size': min_size, 'dry_run': dry_run}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('pack', type=Path, help='pack directory to add mip levels to, in place')
    parser.add_argument('--min-size', type=int, default=1,
                        help='stop the chain when a side reaches this (default 1)')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--output', type=Path, help='JSON receipt')
    args = parser.parse_args()
    report = write_pack(args.pack, args.min_size, args.dry_run)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
