#!/usr/bin/env python3
"""Inspect or replace SSX 3 LOCH/LOCT/LOCL strings in a new ISO.

Edits fit within the existing UTF-16 string slots. Hashes, indices, offsets,
directory records and image size stay intact. Outputs never overwrite files;
the complete image is hashed again after writing. Layout reference: the pinned
SSX-Library LOC.cs; all bounds and terminators are checked against input bytes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from inspect_disc import Region
from relocate_archive import directory_records


def parse_locale(raw):
    if len(raw) < 36 or raw[:4] != b'LOCH':
        raise ValueError('Missing LOCH header')
    header_size, _, version, base = struct.unpack_from('<4I', raw, 4)
    if header_size != 20 or version != 1 or base < 20 or base + 16 > len(raw):
        raise ValueError('Unsupported LOCH layout')
    hashes = {}
    if base != 20:
        if raw[20:24] != b'LOCT' or base < 36 or (base - 36) % 8:
            raise ValueError('Invalid LOCT layout')
        if struct.unpack_from('<I', raw, 24)[0] != 16:
            raise ValueError('Unsupported LOCT header size')
        for at in range(36, base, 8):
            key, index = struct.unpack_from('<II', raw, at)
            hashes.setdefault(index, []).append(key)
    if raw[base:base + 4] != b'LOCL':
        raise ValueError('Missing LOCL section')
    size, _, count = struct.unpack_from('<3I', raw, base + 4)
    if size < 16 or base + size != len(raw) or 16 + count * 4 > size:
        raise ValueError('Invalid LOCL size or count')
    if any(i >= count for i in hashes):
        raise ValueError('LOCT string index out of range')
    offsets = struct.unpack_from(f'<{count}I', raw, base + 16)
    if any(o < 16 + count * 4 or o % 2 or o + 2 > size for o in offsets):
        raise ValueError('String offset out of bounds or unaligned')
    unique = sorted(set(offsets))
    ends = dict(zip(unique, unique[1:] + [size]))
    entries = []
    for index, offset in enumerate(offsets):
        start, limit = base + offset, base + ends[offset]
        end = start
        while end + 2 <= limit and raw[end:end + 2] != b'\0\0':
            end += 2
        terminator_size = 2 if end == start else 4
        if end + terminator_size > limit or raw[end:end + terminator_size] != bytes(terminator_size):
            raise ValueError(f'String {index} lacks a double UTF-16 terminator')
        entries.append(dict(index=index, hashes=hashes.get(index, []), offset=start,
                            end=limit, text=raw[start:end].decode('utf-16le')))
    return entries


def replace_strings(raw, replacements):
    entries = parse_locale(raw)
    patched, edits, slots = bytearray(raw), [], {}
    for index, text in replacements.items():
        if not 0 <= index < len(entries):
            raise ValueError(f'String index {index} out of range')
        if '\0' in text:
            raise ValueError('Replacement contains NUL')
        e = entries[index]
        aliases = [r['index'] for r in entries if r['offset'] == e['offset']]
        if any(replacements.get(i) != text for i in aliases):
            raise ValueError(f'Shared string slot: explicitly replace all indices {aliases}')
        data = text.encode('utf-16le') + bytes(4 if text else 2)
        capacity = e['end'] - e['offset']
        if len(data) > capacity:
            raise ValueError(f'String {index} needs {len(data)} bytes; slot holds {capacity}')
        slots[e['offset']] = data.ljust(capacity, b'\0')
        edits.append(dict(index=index, hashes=e['hashes'], old=e['text'], new=text,
                          offset=e['offset'], size=capacity))
    for offset, data in slots.items():
        patched[offset:offset + len(data)] = data
    after = parse_locale(patched)
    if any(e['text'] != replacements.get(e['index'], entries[e['index']]['text']) for e in after):
        raise ValueError('Locale verification failed')
    return bytes(patched), edits


def write_patched_image(source, output, patches):
    """Stream nonoverlapping (absolute offset, replacement bytes) edits; verify readback."""
    patches = sorted(patches)
    size, last = source.stat().st_size, 0
    for offset, data in patches:
        if offset < last or offset < 0 or offset + len(data) > size:
            raise ValueError('Overlapping or out-of-bounds image edits')
        last = offset + len(data)
    output.parent.mkdir(parents=True, exist_ok=True)
    source_hash, expected = hashlib.sha256(), hashlib.sha256()
    with source.open('rb') as src, output.open('xb') as dst:
        pos = 0
        while chunk := src.read(4 << 20):
            source_hash.update(chunk)
            for offset, data in patches:
                lo, hi = max(pos, offset), min(pos + len(chunk), offset + len(data))
                if lo < hi:
                    chunk = chunk[:lo - pos] + data[lo - offset:hi - offset] + chunk[hi - pos:]
            dst.write(chunk)
            expected.update(chunk)
            pos += len(chunk)
    actual = hashlib.sha256()
    with output.open('rb') as f:
        while chunk := f.read(4 << 20):
            actual.update(chunk)
    if output.stat().st_size != size or actual.digest() != expected.digest():
        raise ValueError('Image readback verification failed')
    return dict(source_sha256=source_hash.hexdigest(), output_sha256=actual.hexdigest(),
                full_readback_verified=True, image_bytes=size)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('iso', type=Path)
    ap.add_argument('--locale', default='DATA/LOCALE/CMNAMER.LOC')
    ap.add_argument('--find', help='list entries containing this text (case insensitive)')
    ap.add_argument('--set', action='append', default=[], metavar='INDEX=TEXT')
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    path = args.locale.upper()
    with args.iso.open('rb') as f:
        region = Region(f, 0, args.iso.stat().st_size)
        records = {p.upper(): r for p, r in directory_records(region).items()}
        if path not in records:
            ap.error('Locale file not found in ISO')
        rec = records[path][1]
        offset = int.from_bytes(rec[2:6], 'little') * 2048
        raw = region.read(offset, int.from_bytes(rec[10:14], 'little'))
    entries = parse_locale(raw)
    if args.find is not None:
        print(json.dumps([e for e in entries if args.find.casefold() in e['text'].casefold()], indent=2))
        return
    if not args.set or args.output is None:
        ap.error('Provide --find, or --set INDEX=TEXT and --output')
    replacements = {}
    for item in args.set:
        key, sep, value = item.partition('=')
        if not sep or not key.isdecimal() or int(key) in replacements:
            ap.error('Each --set must contain a distinct numeric INDEX=TEXT')
        replacements[int(key)] = value
    if args.output.exists() or args.output.with_suffix('.json').exists():
        ap.error('Output image or report already exists')
    patched, edits = replace_strings(raw, replacements)
    result = write_patched_image(args.iso, args.output, [(offset, patched)])
    result.update(mode='locale', source_iso=str(args.iso), output_iso=str(args.output),
                  locale=path, locale_offset=offset, edits=edits, emulator_tested=False)
    args.output.with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
