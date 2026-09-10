#!/usr/bin/env python3
"""Write a test ISO whose world archive lives inside a padding file's extent.

The source image is streamed once into a fresh output of identical size. Only two
ranges change: the archive's ISO9660 directory record (new extent and length, both
byte orders) and the padding region that receives the archive bytes. The old archive
bytes and the padding file's own directory record are left untouched, so the padding
entry now overlaps the relocated archive. Every output byte is read back and hashed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import time

from inspect_disc import Region, iso_files
from build_test_images import replace_ranges, stream_sha


def directory_records(region):
    """Map each file path to (record offset in image, record bytes)."""
    pvd = region.read(16 * 2048, 2048)
    records = {}

    def walk(record, prefix):
        extent = int.from_bytes(record[2:6], 'little')
        size = int.from_bytes(record[10:14], 'little')
        directory = region.read(extent * 2048, size)
        pos = 0
        while pos < size:
            length = directory[pos]
            if not length:
                pos = (pos // 2048 + 1) * 2048
                continue
            rec = directory[pos:pos + length]
            raw_name = rec[33:33 + rec[32]]
            if raw_name not in (b'\0', b'\1'):
                name = raw_name.decode('ascii').split(';')[0]
                if rec[25] & 2:
                    walk(rec, prefix + name + '/')
                else:
                    records[prefix + name] = (extent * 2048 + pos, rec)
            pos += length

    walk(pvd[156:156 + pvd[156]], '')
    return records


def rewritten_record(rec, extent_lba, length):
    out = bytearray(rec)
    struct.pack_into('<I', out, 2, extent_lba)
    struct.pack_into('>I', out, 6, extent_lba)
    struct.pack_into('<I', out, 10, length)
    struct.pack_into('>I', out, 14, length)
    return bytes(out)


def build(iso_path, archive_path, output_dir, archive_name, pad_name):
    size = iso_path.stat().st_size
    archive = archive_path.read_bytes()
    output_dir.mkdir(parents=True, exist_ok=False)
    destination, manifest = output_dir / 'SSX3-relocated.iso', output_dir / 'image.json'
    with iso_path.open('rb') as source:
        disc = Region(source, 0, size)
        _, files = iso_files(disc)
        records = directory_records(disc)
        by_path = {f['path']: f for f in files}
        pad, old = by_path[pad_name], by_path[archive_name]
        if pad['offset'] % 2048 or len(archive) > pad['size']:
            raise ValueError('Padding extent is unaligned or too small for the archive')
        rec_offset, rec = records[archive_name]
        if int.from_bytes(rec[2:6], 'little') * 2048 != old['offset'] or int.from_bytes(rec[10:14], 'little') != old['size']:
            raise ValueError('Directory record does not match the file inventory')
        new_rec = rewritten_record(rec, pad['offset'] // 2048, len(archive))
        replacements = [(rec_offset, new_rec), (pad['offset'], archive)]
        digest, source_digest = hashlib.sha256(), hashlib.sha256()
        offset, last = 0, time.monotonic()
        source.seek(0)
        try:
            with destination.open('xb') as out:
                while chunk := source.read(4 * 1024 * 1024):
                    source_digest.update(chunk)
                    new = replace_ranges(chunk, offset, replacements)
                    out.write(new); digest.update(new); offset += len(chunk)
                    if time.monotonic() - last > 15:
                        print(f'Copied {offset / size:.0%}', flush=True); last = time.monotonic()
        except BaseException:
            destination.unlink(missing_ok=True); raise
    expected = digest.hexdigest()
    if destination.stat().st_size != size or stream_sha(destination) != expected:
        raise ValueError('Output readback failed')
    with destination.open('rb') as f:
        _, out_files = iso_files(Region(f, 0, size))
    expected_files = [dict(f, offset=pad['offset'], size=len(archive)) if f['path'] == archive_name else f for f in files]
    if sorted(out_files, key=lambda f: f['path']) != sorted(expected_files, key=lambda f: f['path']):
        raise ValueError('Output directory differs from the planned relocation')
    report = dict(source_iso=str(iso_path), source_iso_sha256=source_digest.hexdigest(),
                  archive=str(archive_path), archive_sha256=hashlib.sha256(archive).hexdigest(),
                  archive_bytes=len(archive), output_iso=str(destination), output_iso_sha256=expected,
                  size=size, relocated_file=archive_name, new_offset=pad['offset'], new_extent_lba=pad['offset'] // 2048,
                  old_offset=old['offset'], old_size=old['size'], overlapping_padding_file=pad_name,
                  directory_record_offset=rec_offset, full_readback_verified=True, emulator_tested=False)
    manifest.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('iso', type=Path)
    ap.add_argument('archive', type=Path, help='World archive to place (original or rebuilt)')
    ap.add_argument('--output', type=Path, required=True, help='New directory; never overwrites')
    ap.add_argument('--file', default='DATA/WORLDS/BAM.BIG')
    ap.add_argument('--pad', default='PAD0.000')
    args = ap.parse_args()
    build(args.iso, args.archive, args.output, args.file, args.pad)
