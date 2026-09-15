#!/usr/bin/env python3
"""Cap a pack's texture size, because upscale factor is not free on a phone.

A 4x pack costs 16x the texture memory of the art it replaces, and none of that
is optional at runtime: Dolphin decodes a custom texture to RGBA8 and uploads
it, so the pack's cost is its *decoded* size, not its size on disk. Measured
over SSX 3's 17-course pack (927 textures, base plus mip chain):

    source side   textures   decoded RGBA8
        <= 32        138          11 MB
        <= 64        165          54 MB
        <= 128       519         693 MB
        <= 256        85         445 MB
                             ------------
                             1,203 MB

The phone's app footprint went from about 457 MB without the pack to 1,137 MB
with it, and the frame-interval spikes that came with it are PNG decode on the
texture-load path. Both costs sit almost entirely in the two largest buckets,
and 4x on a 256-px source is 1024 px of texture for a 1280x1056 internal
render - past the point where any of it reaches a pixel.

Capping the *upscaled side* rather than the factor is what keeps the small art
intact: a 32-px tile still gets its full 4x, while a 256-px source drops to 2x.
The reduction is a plain Lanczos downsample of the pack's own output, so no
model has to run again, and the guest-to-pack ratio stays an integer - which
`TextureAssetUtils` requires, and which is why the cap must be a power-of-two
multiple of the guest size rather than an arbitrary pixel budget.

  python3 tools/texture_pack_cap.py PACK --max-side 512 [--output DIR] [--dry-run]

Existing `_mipN` sidecars for a capped texture are removed, so
`tools/pack_mipmaps.py` rebuilds the chain at the new size afterwards.
"""

import argparse
import json
import re
import shutil
from pathlib import Path

# The guest size is in the file name, which is also Dolphin's lookup key, so the
# name never changes - only the pixels behind it.
NAME = re.compile(r'^tex1_(\d+)x(\d+)(_m)?_')
MIP = re.compile(r'_mip\d+$')


def guest_size(name):
    """The guest texture's own width and height, from the Dolphin key."""
    match = NAME.match(name)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def capped_scale(guest, packed, max_side, min_scale=2):
    """The largest integer scale within max_side, or None to leave it alone.

    Integer because a custom texture has to stay a whole multiple of the guest
    size; a power of two so the mip chain halves cleanly all the way down.

    `min_scale` is a floor the cap may not cross, and it matters: a 216x368
    source cannot reach 512 at 2x, and without a floor the search walks down to
    1x and hands back the guest's own art - throwing the remaster away entirely
    to save memory on one texture. A texture that cannot honour the cap keeps
    the floor instead.
    """
    guest_side = max(guest)
    packed_side = max(packed)
    if guest_side == 0 or packed_side <= max_side:
        return None
    scale = packed_side // guest_side
    if scale <= min_scale:
        return None                      # already at or below the floor
    while scale > min_scale and guest_side * scale > max_side:
        scale //= 2
    return scale if scale * guest_side < packed_side else None


def cap_pack(pack_dir, max_side, output_dir=None, dry_run=False, min_scale=2):
    """Reduce every base texture above max_side; drop its stale mip sidecars."""
    from PIL import Image
    pack_dir = Path(pack_dir)
    destination = Path(output_dir) if output_dir else pack_dir
    in_place = destination == pack_dir
    if not in_place:
        destination.mkdir(parents=True, exist_ok=True)
    report = {'pack': str(pack_dir), 'output': str(destination),
              'max_side': max_side, 'capped': 0, 'kept': 0,
              'mips_removed': 0, 'bytes_before': 0, 'bytes_after': 0,
              'entries': []}
    bases = sorted(p for p in pack_dir.glob('tex1_*.png')
                   if not MIP.search(p.stem))
    capped_stems = set()
    for path in bases:
        guest = guest_size(path.name)
        if guest is None:
            continue
        with Image.open(path) as image:
            packed = (image.width, image.height)
            scale = capped_scale(guest, packed, max_side, min_scale)
            report['bytes_before'] += packed[0] * packed[1] * 4
            if scale is None:
                report['kept'] += 1
                report['bytes_after'] += packed[0] * packed[1] * 4
                if not in_place:
                    shutil.copy2(path, destination / path.name)
                continue
            size = (guest[0] * scale, guest[1] * scale)
            report['capped'] += 1
            report['bytes_after'] += size[0] * size[1] * 4
            report['entries'].append({'name': path.name, 'from': list(packed),
                                      'to': list(size), 'scale': scale})
            if not dry_run:
                image.convert('RGBA').resize(size, Image.LANCZOS).save(
                    destination / path.name)
        capped_stems.add(path.stem)
    # A stale chain is worse than none: the levels no longer halve from the base,
    # and Dolphin takes the mip count from whatever the pack supplies.
    for path in sorted(pack_dir.glob('tex1_*_mip*.png')):
        base = MIP.sub('', path.stem)
        if base in capped_stems:
            report['mips_removed'] += 1
            if not dry_run and in_place:
                path.unlink()          # out of place, it is simply not copied
        elif not in_place:
            shutil.copy2(path, destination / path.name)
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pack', type=Path)
    ap.add_argument('--max-side', type=int, default=512,
                    help='Largest upscaled side to keep (default 512)')
    ap.add_argument('--output', type=Path, help='Write a new pack here instead of in place')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    report = cap_pack(args.pack, args.max_side, args.output, args.dry_run)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(f"capped {report['capped']}, kept {report['kept']}, "
          f"stale mip levels removed {report['mips_removed']}")
    print(f"decoded base bytes {report['bytes_before'] / 1e6:.0f} MB "
          f"-> {report['bytes_after'] / 1e6:.0f} MB")
    for entry in report['entries'][:8]:
        print(f"  {entry['from'][0]}x{entry['from'][1]} -> "
              f"{entry['to'][0]}x{entry['to'][1]} ({entry['scale']}x)  {entry['name']}")


if __name__ == '__main__':
    main()
