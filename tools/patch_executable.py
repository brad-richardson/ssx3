#!/usr/bin/env python3
"""Rename SSX 3 events in the executable inside an image (level-selector names).

SLUS_207.72 (NTSC-U) carries a 24-record event table: five u32 words, then the
display name (32 bytes), short name (16), SDB location code (16) and archive
name (16), 100 bytes per record; the transport menu shows the display name.
This tool streams the source image to a new file, overwriting only the two name
fields of the requested records. The executable is found through the ISO9660
directory and the table by verifying its known content, so a different build
of the executable is refused rather than patched blindly.

    patch_executable.py IN.iso --output OUT.iso --rename ARA1="Garibaldi" --rename DRA4="Mesablanca:Mesa"
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from inspect_disc import Region
from relocate_archive import directory_records

RECORD, COUNT = 100, 24
NAMES = (20, 32), (52, 16), (68, 16), (84, 16)  # display, short, code, archive


def find_table(elf):
    """Offset of the event table: the record whose code is ARA1 and archive BAM, with 24 consistent records."""
    pos = elf.find(b'ARA1\0' + bytes(11) + b'BAM\0')
    if pos < 0:
        raise ValueError('Event table not found in executable')
    base = pos - NAMES[2][0]
    table = parse_table(elf, base)
    if [r['code'] for r in table[:3]] != ['ARA1', 'BRA2', 'CRA3'] or table[17]['code'] != 'A':
        raise ValueError('Event table content differs from the known NTSC-U layout')
    return base


def parse_table(elf, base):
    out = []
    for i in range(COUNT):
        r = elf[base + RECORD * i: base + RECORD * (i + 1)]
        f = lambda a, n: r[a:a + n].split(b'\0')[0].decode('ascii', 'replace')
        out.append(dict(index=i, words=list(struct.unpack_from('<5I', r, 0)), display=f(*NAMES[0]), short=f(*NAMES[1]), code=f(*NAMES[2]), archive=f(*NAMES[3])))
    return out


def rename_bytes(elf, base, renames):
    """Return (patched executable, list of edits). renames: {code: (display, short or None)}."""
    elf = bytearray(elf); edits = []
    table = parse_table(elf, base)
    for code, (display, short) in renames.items():
        recs = [r for r in table if r['code'] == code]
        if not recs:
            raise ValueError(f'No event with code {code}')
        rec = recs[0]
        for value, (off, size), field in ((display, NAMES[0], 'display'), (short, NAMES[1], 'short')):
            if value is None:
                continue
            data = value.encode('ascii')
            if len(data) >= size:
                raise ValueError(f'{field} name {value!r} longer than {size - 1} characters')
            at = base + RECORD * rec['index'] + off
            elf[at:at + size] = data + bytes(size - len(data))
            edits.append(dict(code=code, field=field, old=rec[field], new=value, offset=at))
    return bytes(elf), edits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso', type=Path)
    ap.add_argument('--output', type=Path, required=True, help='new image; never overwrites')
    ap.add_argument('--rename', action='append', default=[], help='CODE=Display[:Short]')
    ap.add_argument('--list', action='store_true', help='print the event table and exit')
    args = ap.parse_args()
    with args.iso.open('rb') as f:
        region = Region(f, 0, args.iso.stat().st_size)
        records = directory_records(region)
        path = next(p for p in records if p.upper().startswith('SLUS_'))
        rec = records[path][1]
        extent, size = int.from_bytes(rec[2:6], 'little'), int.from_bytes(rec[10:14], 'little')
        elf = region.read(extent * 2048, size)
        base = find_table(elf)
        if args.list:
            print(json.dumps(parse_table(elf, base), indent=1)); return
        renames = {}
        for item in args.rename:
            code, _, names = item.partition('=')
            display, _, short = names.partition(':')
            renames[code] = (display or None, short or None)
        patched, edits = rename_bytes(elf, base, renames)
        if args.output.exists():
            ap.error('Output already exists')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        elf_start = extent * 2048
        h = hashlib.sha256()
        f.seek(0)
        with args.output.open('xb') as out:
            pos = 0
            while chunk := f.read(1 << 22):
                lo, hi = max(pos, elf_start), min(pos + len(chunk), elf_start + size)
                if lo < hi:
                    chunk = chunk[:lo - pos] + patched[lo - elf_start:hi - elf_start] + chunk[hi - pos:]
                out.write(chunk); h.update(chunk); pos += len(chunk)
    details = dict(mode='rename', source_iso=str(args.iso), output_iso=str(args.output), executable=path, executable_offset=elf_start,
                   table_offset=base, edits=edits, output_sha256=h.hexdigest(), emulator_tested=False)
    (args.output.with_suffix('.json')).write_text(json.dumps(details, indent=2) + '\n')
    print(json.dumps(details, indent=2))


if __name__ == '__main__':
    main()
