#!/usr/bin/env python3
"""Rebuild an SSX 3 world archive with our own SSB block boundaries.

Every stream group is decoded, re-chunked into 32 KiB blocks at boundaries chosen by
this tool (not EA's), encoded with the optimal RefPack parser, and written back with
regenerated SDB group offsets and a rebuilt BIGF directory. Decoded content is
identical to the source; this is the control for a growable rebuild. The archive
size changes, so images must be built with relocate_archive.py.

Block policy: a block holds up to --max-decoded bytes (default 81,920, the largest
decoded block on the disc) and its compressed payload must fit 32,760 bytes; the
largest fitting prefix is found by probing with the fast greedy encoder minus a
margin, then encoded optimally and shrunk if it still overflows.
"""
import argparse
import hashlib
import io
import json
from multiprocessing import Pool
from pathlib import Path
import struct

from inspect_disc import Region, big_members, file_region
from probe_worlds import refpack, probe_ssx3
from refpack_encode import encode as greedy
from refpack_optimal import encode as optimal

BLOCK = 32768
CAPACITY = BLOCK - 8
ALIGN = 2048


def sha(data):
    return hashlib.sha256(data).hexdigest()


def largest_fitting(raw, start, max_decoded, margin):
    """Largest length whose greedy encoding fits CAPACITY - margin (binary search)."""
    lo, hi = 512, min(max_decoded, len(raw) - start)
    if len(greedy(raw[start:start + hi])) <= CAPACITY - margin:
        return hi
    while hi - lo > 256:
        mid = (lo + hi) // 2
        if len(greedy(raw[start:start + mid])) <= CAPACITY - margin:
            lo = mid
        else:
            hi = mid
    return lo


def pack_group(job):
    index, raw, max_decoded, margin = job
    blocks, start = [], 0
    while start < len(raw):
        length = largest_fitting(raw, start, max_decoded, margin)
        while True:
            chunk = raw[start:start + length]
            payload = optimal(chunk)
            if len(payload) <= CAPACITY:
                break
            length -= 512
            if length < 256:
                raise ValueError(f'Group {index}: cannot fit a block at {start}')
        if refpack(payload)[0] != chunk:
            raise ValueError(f'Group {index}: encoder round trip failed at {start}')
        start += length
        tag = b'CEND' if start >= len(raw) else b'CBXS'
        blocks.append(tag + struct.pack('<I', BLOCK) + payload + bytes(CAPACITY - len(payload)))
    return index, b''.join(blocks), len(blocks)


def write_bigf(members):
    """members: list of (path, bytes) in order. Returns archive bytes with 2048-aligned members."""
    table = b''.join(struct.pack('>II', 0, len(data)) + path.replace('/', '\\').encode('ascii') + b'\0' for path, data in members)
    header_len = 16 + len(table)
    offsets, cursor = [], (header_len + ALIGN - 1) // ALIGN * ALIGN
    for path, data in members:
        offsets.append(cursor)
        cursor += (len(data) + ALIGN - 1) // ALIGN * ALIGN
    total = cursor
    out = bytearray(b'BIGF' + struct.pack('<I', total) + struct.pack('>II', len(members), header_len))
    for (path, data), offset in zip(members, offsets):
        out += struct.pack('>II', offset, len(data)) + path.replace('/', '\\').encode('ascii') + b'\0'
    out += bytes(offsets[0] - len(out))
    for (path, data), offset in zip(members, offsets):
        assert len(out) == offset
        out += data + bytes((-len(data)) % ALIGN)
    return bytes(out), offsets


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive', type=Path)
    ap.add_argument('--world-report', type=Path, default=Path('local/reports/ssx3-world.json'))
    ap.add_argument('--output', type=Path, required=True, help='New directory; never overwrites')
    ap.add_argument('--max-decoded', type=int, default=81920)
    ap.add_argument('--margin', type=int, default=96, help='greedy-probe slack below capacity')
    ap.add_argument('--jobs', type=int, default=8)
    args = ap.parse_args()
    if args.output.exists():
        ap.error('Output directory already exists')
    original = args.archive.read_bytes()
    report = json.loads(args.world_report.read_text())
    if sha(original) != report['archive_sha256']:
        raise ValueError('Source archive differs from inspected baseline')
    region = Region(io.BytesIO(original), 0, len(original))
    kind, members = big_members(region)
    if kind != 'BIGF':
        raise ValueError('Expected BIGF')
    ssb = file_region(region, members, 'data/worlds/bam.ssb')
    sdb = file_region(region, members, 'data/worlds/bam.sdb')
    jobs = []
    for g in report['groups']:
        raw = b''.join(refpack(ssb.read(b['offset'], b['size'])[8:])[0] for b in g['blocks'])
        if sha(raw) != g['sha256']:
            raise ValueError(f'Group {g["index"]} differs from baseline')
        jobs.append((g['index'], raw, args.max_decoded, args.margin))
    with Pool(args.jobs) as pool:
        packed = dict((i, (data, n)) for i, data, n in pool.imap_unordered(pack_group, jobs, chunksize=1))
    # Assemble the stream in group order and regenerate SDB offsets.
    sdb_bytes = bytearray(sdb.read(0, sdb.size))
    location_count, node_count, group_count = struct.unpack_from('<III', sdb_bytes, 8)
    table = (80 + location_count * 88 + 15) // 16 * 16 + node_count * 96
    stream, groups_out = bytearray(), []
    for g in report['groups']:
        data, n = packed[g['index']]
        rec = table + g['index'] * 68
        old_offset = struct.unpack_from('<I', sdb_bytes, rec + 4)[0]
        if old_offset != g['offset']:
            raise ValueError(f'SDB offset for group {g["index"]} does not match the stream')
        struct.pack_into('<I', sdb_bytes, rec + 4, len(stream))
        groups_out.append(dict(index=g['index'], old_offset=g['offset'], new_offset=len(stream),
                               old_blocks=len(g['blocks']), new_blocks=n, decoded_size=g['decoded_size'], sha256=g['sha256']))
        stream += data
    new_members = []
    for m in members:
        if m['path'] == 'data/worlds/bam.ssb':
            new_members.append((m['path'], bytes(stream)))
        elif m['path'] == 'data/worlds/bam.sdb':
            new_members.append((m['path'], bytes(sdb_bytes)))
        else:
            new_members.append((m['path'], region.read(m['offset'], m['size'])))
    archive, offsets = write_bigf(new_members)
    # Independent verification with the world inspector: same groups, same SDB agreement.
    check = probe_ssx3(Region(io.BytesIO(archive), 0, len(archive)))
    if [g['sha256'] for g in check['groups']] != [g['sha256'] for g in report['groups']]:
        raise ValueError('Rebuilt archive decodes to different group content')
    if check['resource_counts'] != report['resource_counts'] or check['patch_sizes'] != report['patch_sizes']:
        raise ValueError('Rebuilt archive resource inventory differs')
    details = dict(mode='relayout', source_archive_sha256=sha(original), rebuilt_archive_sha256=sha(archive),
                   source_archive_bytes=len(original), rebuilt_archive_bytes=len(archive),
                   source_stream_bytes=ssb.size, rebuilt_stream_bytes=len(stream),
                   source_blocks=sum(len(g['blocks']) for g in report['groups']), rebuilt_blocks=sum(v[1] for v in packed.values()),
                   max_decoded=args.max_decoded, margin=args.margin, member_offsets=dict(zip([m[0] for m in new_members], offsets)),
                   groups=groups_out, decoded_groups_unchanged=True, sdb_group_offsets_regenerated=True, emulator_tested=False)
    args.output.mkdir(parents=True, exist_ok=False)
    path = args.output / 'BAM.BIG'
    with path.open('xb') as f:
        f.write(archive)
    if sha(path.read_bytes()) != details['rebuilt_archive_sha256']:
        raise ValueError('Saved archive failed readback hash verification')
    (args.output / 'experiment.json').write_text(json.dumps(details, indent=2) + '\n')
    print(json.dumps({k: v for k, v in details.items() if k != 'groups'}, indent=2))


if __name__ == '__main__':
    main()
