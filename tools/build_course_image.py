#!/usr/bin/env python3
"""Build one verified image with a rebuilt world, event name and locale description.

The archive is appended and the two same-size text edits share the image copy.
Original discs are read-only. Description indices are explicit, so the tool does
not infer locale keys from names. This is an experiment assembler, not M6's patcher.
"""
import argparse
import json
from pathlib import Path

from inspect_disc import Region
from relocate_archive import build, directory_records
from patch_executable import find_table, rename_bytes
from patch_locale import replace_strings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('iso', type=Path)
    ap.add_argument('archive', type=Path)
    ap.add_argument('--code', default='ARA1')
    ap.add_argument('--name', default='Garibaldi')
    ap.add_argument('--short', default='Gari')
    ap.add_argument('--locale', default='DATA/LOCALE/CMNAMER.LOC')
    ap.add_argument('--description-index', type=int, help='Defaults to 549 for ARA1; required for other codes')
    ap.add_argument('--description', default='Garibaldi from SSX Tricky. Experimental terrain port; race setup in progress.')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        ap.error('Output directory already exists')
    if args.description_index is None:
        if args.code != 'ARA1':
            ap.error('Provide --description-index for a destination other than ARA1')
        args.description_index = 549
    with args.iso.open('rb') as f:
        region = Region(f, 0, args.iso.stat().st_size)
        records = directory_records(region)
        def read(path):
            rec = records[path][1]
            return region.read(int.from_bytes(rec[2:6], 'little') * 2048,
                               int.from_bytes(rec[10:14], 'little'))
        elf_path = 'SLUS_207.72'
        elf = read(elf_path)
        elf, names = rename_bytes(elf, find_table(elf), {args.code: (args.name, args.short)})
        locale, strings = replace_strings(read(args.locale), {args.description_index: args.description})
    build(args.iso, args.archive, args.output, 'DATA/WORLDS/BAM.BIG', 'PAD0.000', append=True,
          file_replacements={elf_path: elf, args.locale: locale})
    (args.output / 'text-edits.json').write_text(json.dumps(dict(names=names, locale=args.locale,
                                                               strings=strings), indent=2) + '\n')


if __name__ == '__main__':
    main()
