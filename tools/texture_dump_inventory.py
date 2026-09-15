#!/usr/bin/env python3
"""Inventory a Dolphin texture dump, split by ride phase, with an optional contact sheet.

`gamecube_course_check.py --texture-dump` leaves PROFILE/Dump/Textures/GXBE69
full of `tex1_<w>x<h>_<hash>[_<tlut hash>]_<format>.png`. Most of a run's dumps
are the frontend and the video that plays before it, so the useful split is
*when* each file was written: a run's rider trace records the wall time of the
race start, and anything dumped after it belongs to the course being ridden.

Format numbers are GX texture formats: 0 I4, 1 I8, 2 IA4, 3 IA8, 4 RGB565,
5 RGB5A3, 6 RGBA8, 8 C4, 9 C8, 10 C14X2, 14 CMPR.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

# Dolphin's texture name (VideoCommon/TextureInfo.cpp CalculateTextureName):
#   tex1_<w>x<h>[_m]_<tex hash>[_<palette hash>]_<format>[_arb][_mipN]
# `_m` means the guest texture has mipmaps enabled, and a dump then also writes
# one `_mipN` sidecar per level. Both hashes are XXH64, 16 hex digits — the
# palette hash covers only the palette range the texels actually index.
NAME = re.compile(r'^tex1_(\d+)x(\d+)(_m)?_([0-9a-f]{16})(?:_([0-9a-f]{16}))?_(\d+)'
                  r'(_arb)?(?:_mip(\d+))?$')
FORMATS = {0: 'I4', 1: 'I8', 2: 'IA4', 3: 'IA8', 4: 'RGB565', 5: 'RGB5A3', 6: 'RGBA8',
           8: 'C4', 9: 'C8', 10: 'C14X2', 14: 'CMPR'}


def parse(path):
    match = NAME.match(path.stem)
    if not match:
        return None
    width, height, mipmapped, texture_hash, tlut_hash, fmt, arbitrary, mip = match.groups()
    return {'name': path.name, 'width': int(width), 'height': int(height),
            'texture_hash': texture_hash, 'tlut_hash': tlut_hash,
            'format': int(fmt), 'format_name': FORMATS.get(int(fmt), f'0x{int(fmt):x}'),
            'mipmapped': bool(mipmapped), 'mip_level': int(mip) if mip else 0,
            'arbitrary_mips': bool(arbitrary), 'bytes': path.stat().st_size,
            'mtime': path.stat().st_mtime, 'path': str(path)}


def run_boundaries(run):
    """Wall clocks of (the observer's first sample, the race start).

    The observer only writes once the rider pointer exists, which is the
    briefing — so its first sample is the earliest moment the course itself can
    be loading. A course's own textures are uploaded during the load screen,
    *before* the rider moves, so that first sample is the useful boundary and
    the race start only separates load-time art from art first seen while
    riding.
    """
    rows = [json.loads(line) for line in (Path(run) / 'rider.jsonl').read_text().splitlines() if line.strip()]
    if not rows:
        raise ValueError('The run has no rider samples')
    placed = [r for r in rows if any(r.get(k) for k in 'xyz')]
    if not placed:
        raise ValueError('The run has no positioned rider samples')
    spawn = placed[0]
    for row in placed:
        if sum((row[k] - spawn[k]) ** 2 for k in 'xyz') ** .5 > 1:
            return rows[0]['wall_time'], row['wall_time']
    raise ValueError('The rider never left its spawn')


# Asset families, by the only signal a dump carries: its GX format. The
# measured reason to split (docs/texture-remaster.md) is that CMPR is 4x4 block
# compression, so a sharpening model amplifies its block edges into quilting
# and a smoothing model does not; paletted art is flat and tolerant; direct
# colour takes the sharpest model well.
FAMILY_BY_FORMAT = {14: 'block-compressed',
                    0: 'paletted', 1: 'paletted', 8: 'paletted', 9: 'paletted', 10: 'paletted',
                    2: 'direct-colour', 3: 'direct-colour', 4: 'direct-colour',
                    5: 'direct-colour', 6: 'direct-colour'}


def family(entry):
    return FAMILY_BY_FORMAT.get(entry['format'], 'other')


def is_framebuffer(entry):
    """Dolphin also dumps EFB/XFB copies; they are paletted and screen-shaped."""
    return entry['format'] in (9, 10) and entry['width'] >= 320 and entry['height'] >= 224


def contact_sheet(entries, path, columns=8, cell=128):
    from PIL import Image
    rows = (len(entries) + columns - 1) // columns
    sheet = Image.new('RGBA', (columns * cell, rows * cell), (24, 24, 28, 255))
    for index, entry in enumerate(entries):
        image = Image.open(entry['path']).convert('RGBA')
        image.thumbnail((cell, cell), Image.LANCZOS)
        x = (index % columns) * cell + (cell - image.width) // 2
        y = (index // columns) * cell + (cell - image.height) // 2
        sheet.alpha_composite(image, (x, y))
    sheet.save(path)
    return {'path': str(path), 'images': len(entries), 'columns': columns, 'cell': cell}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('dump', type=Path, help='Dump directory (PROFILE/Dump/Textures/GXBE69)')
    ap.add_argument('--run', type=Path, help="A run directory, to split at its race start")
    ap.add_argument('--select', type=int,
                    help='Also pick this many course textures, largest first, one per content hash')
    ap.add_argument('--copy-selection', type=Path, help='Copy the selection into this directory')
    ap.add_argument('--copy-groups', type=Path,
                    help='Copy every course texture into DIR/<asset family>/, so each family '
                         'can go through the model that suits it')
    ap.add_argument('--copy-frontend', type=Path,
                    help='Copy every frontend texture into DIR/<asset family>/ instead of the '
                         "course's, for remastering the menus")
    ap.add_argument('--sheet', type=Path, help='Write a contact sheet of the selection here')
    ap.add_argument('--output', type=Path, help='Write the JSON inventory here')
    args = ap.parse_args()
    entries = [entry for entry in (parse(p) for p in sorted(args.dump.iterdir())
                                   if p.suffix.lower() == '.png') if entry]
    if not entries:
        raise SystemExit(f'No dumped textures in {args.dump}')
    briefing, start = run_boundaries(args.run) if args.run else (None, None)
    for entry in entries:
        entry['phase'] = ('unknown' if briefing is None else
                          'ride' if entry['mtime'] >= start else
                          'course load' if entry['mtime'] >= briefing else 'frontend')
        entry['framebuffer'] = is_framebuffer(entry)
    # A `_mipN` file is another level of its base texture, not a texture of its
    # own, so the sidecars are counted but never selected as art. A pack still
    # needs levels - the loader takes a custom texture's mip count from the
    # files the pack supplies - but they are generated from the pack's own base
    # by `pack_mipmaps.py`, not carried over from the guest's dump.
    course = [e for e in entries if e['phase'] in ('course load', 'ride')
              and not e['framebuffer'] and not e['mip_level']]
    frontend = [e for e in entries if e['phase'] == 'frontend'
                and not e['framebuffer'] and not e['mip_level']]
    report = {
        'dump': str(args.dump), 'run': str(args.run) if args.run else None,
        'briefing_wall': briefing, 'race_start_wall': start, 'textures': len(entries),
        'by_phase': dict(Counter(e['phase'] for e in entries)),
        'framebuffer_copies': sum(e['framebuffer'] for e in entries),
        'mip_sidecars': sum(1 for e in entries if e['mip_level']),
        'mipmapped_course_textures': sum(1 for e in entries if e['mipmapped'] and not e['mip_level']
                                         and e['phase'] in ('course load', 'ride')),
        'course_art': len(course), 'frontend_art': len(frontend),
        'course_by_format': dict(Counter(e['format_name'] for e in course).most_common()),
        'course_by_size': dict(Counter(f"{e['width']}x{e['height']}" for e in course).most_common()),
    }
    report['course_by_family'] = dict(Counter(family(e) for e in course).most_common())
    if args.copy_groups:
        import shutil
        for entry in course:
            directory = args.copy_groups / family(entry)
            directory.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(entry['path'], directory / entry['name'])
        report['groups'] = {name: sum(1 for e in course if family(e) == name)
                            for name in sorted({family(e) for e in course})}
        report['groups_directory'] = str(args.copy_groups)
    if args.copy_frontend:
        import shutil
        seen = set()
        for entry in frontend:
            if entry['texture_hash'] in seen:
                continue
            seen.add(entry['texture_hash'])
            directory = args.copy_frontend / family(entry)
            directory.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(entry['path'], directory / entry['name'])
        report['frontend_groups'] = {name: sum(1 for e in frontend if family(e) == name)
                                     for name in sorted({family(e) for e in frontend})}
        report['frontend_directory'] = str(args.copy_frontend)
    selection = []
    if args.select:
        # Largest first, one per content hash, spread across formats by keeping
        # the natural size order rather than filtering to a single kind.
        seen = set()
        for entry in sorted(course, key=lambda e: -e['width'] * e['height']):
            if entry['texture_hash'] in seen:
                continue
            seen.add(entry['texture_hash'])
            selection.append(entry)
            if len(selection) == args.select:
                break
        report['selection'] = [e['name'] for e in selection]
        report['selection_by_size'] = dict(Counter(f"{e['width']}x{e['height']}" for e in selection).most_common())
        if args.copy_selection:
            import shutil
            args.copy_selection.mkdir(parents=True, exist_ok=True)
            for entry in selection:
                shutil.copyfile(entry['path'], args.copy_selection / entry['name'])
            report['selection_directory'] = str(args.copy_selection)
        if args.sheet:
            report['contact_sheet'] = contact_sheet(selection, args.sheet)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'selection'}, indent=2))


if __name__ == '__main__':
    main()
