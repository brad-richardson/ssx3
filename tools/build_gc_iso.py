#!/usr/bin/env python3
"""Rebuild a GameCube disc image from an extracted directory (sys/ + files/).

Keeps the original boot.bin, bi2.bin, apploader, DOL, and FST tree/order, and
re-lays out every file from the original first-file offset, keeping each
file's original alignment (4 bytes for most, 32 KiB for the .dat files),
recomputing FST offsets and sizes. Files that changed size (for
example a rebuilt world archive) therefore fit. Verified by rebuilding the
stock GXBE69 extraction and comparing against dtk's ISO conversion.
"""
import argparse
import hashlib
from pathlib import Path
import struct

ALIGN = 4
MAX_ALIGN = 0x8000
DISC_SIZE = 1459978240


def read_fst(fst):
    root_flags, _, count = struct.unpack_from('>III', fst, 0)
    strings = count * 12
    entries = []
    for i in range(count):
        flags_name, offset, size = struct.unpack_from('>III', fst, i * 12)
        name = fst[strings + (flags_name & 0xffffff):].split(b'\0')[0].decode('ascii')
        entries.append(dict(index=i, is_dir=bool(flags_name >> 24), name=name, name_offset=flags_name & 0xffffff,
                            offset=offset, size=size))
    return entries, fst[strings:]


def paths_for(entries):
    """Resolve each file entry to its path under files/ using directory parent/next fields."""
    result = {}
    stack = [(0, entries[0]['size'], '')]  # (dir index, next index, path)
    i = 1
    while i < len(entries):
        while stack and i >= stack[-1][1]:
            stack.pop()
        e = entries[i]
        parent_path = stack[-1][2] if stack else ''
        if e['is_dir']:
            stack.append((i, e['size'], f'{parent_path}{e["name"]}/'))
        else:
            result[i] = parent_path + e['name']
        i += 1
    return result


def build(root, output, disc_size=DISC_SIZE):
    root = Path(root)
    sys_dir, files_dir = root / 'sys', root / 'files'
    boot = bytearray((sys_dir / 'boot.bin').read_bytes())
    bi2 = (sys_dir / 'bi2.bin').read_bytes()
    apploader = (sys_dir / 'apploader.img').read_bytes()
    dol = (sys_dir / 'main.dol').read_bytes()
    fst = bytearray((sys_dir / 'fst.bin').read_bytes())
    dol_off, fst_off, fst_size, fst_max = struct.unpack_from('>4I', boot, 0x420)
    if len(boot) != 0x440 or len(bi2) != 0x2000:
        raise ValueError('Unexpected boot.bin/bi2.bin sizes')
    if 0x2440 + len(apploader) > dol_off or dol_off + len(dol) > fst_off or fst_size != len(fst):
        raise ValueError('System area layout does not match boot.bin')
    entries, _ = read_fst(fst)
    paths = paths_for(entries)
    files = sorted(paths.items(), key=lambda kv: entries[kv[0]]['offset'])
    first = min(entries[i]['offset'] for i, _ in files)
    if first < fst_off + fst_max:
        raise ValueError('First file overlaps the FST')
    position = first
    layout = []
    for index, rel in files:
        data_path = files_dir / rel
        size = data_path.stat().st_size
        original = entries[index]['offset']
        align = min(MAX_ALIGN, original & -original) if original else ALIGN
        align = max(align, ALIGN)
        position = (position + align - 1) // align * align
        struct.pack_into('>II', fst, index * 12 + 4, position, size)
        layout.append((position, size, data_path, rel))
        position += size
    total = (position + 0x8000 - 1) // 0x8000 * 0x8000
    if disc_size and total > disc_size:
        raise ValueError(f'Content ({total} bytes) exceeds the disc size')
    output = Path(output)
    with output.open('wb') as out:
        out.write(boot)
        out.write(bi2)
        out.write(apploader)
        out.seek(dol_off)
        out.write(dol)
        out.seek(fst_off)
        out.write(fst)
        for position, size, data_path, _ in layout:
            out.seek(position)
            with data_path.open('rb') as f:
                while True:
                    chunk = f.read(8 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
        out.truncate(disc_size or total)
    return dict(files=len(layout), first_file_offset=first, content_end=position, image_size=disc_size or total,
                changed=[rel for (_, size, _, rel), e in zip(layout, (entries[i] for i, _ in files)) if size != e['size']])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('root', type=Path, help='Extracted disc directory containing sys/ and files/')
    ap.add_argument('output', type=Path)
    ap.add_argument('--trim', action='store_true', help='Do not pad to the standard 1,459,978,240-byte disc size')
    ap.add_argument('--sha256', action='store_true')
    args = ap.parse_args()
    report = build(args.root, args.output, 0 if args.trim else DISC_SIZE)
    if args.sha256:
        with args.output.open('rb') as f:
            report['sha256'] = hashlib.file_digest(f, 'sha256').hexdigest()
    print(report)


if __name__ == '__main__':
    main()
