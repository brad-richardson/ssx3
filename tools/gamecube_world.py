#!/usr/bin/env python3
"""GameCube SSX 3 world archive reader/writer (BAM.BIG: bam.gdb + bam.gsb).

The GameCube world uses the PS2 layout with big-endian tables and resource
headers. CBXS/CEND block lengths stay little-endian and blocks are 32 KiB, so
the PS2 block packer and BIGF writer are reused. Verified 2026-09-11 against
GXBE69: 49 locations, 275 spatial records, 205 stream groups.
"""
import hashlib
import io
from pathlib import Path
import struct

from inspect_disc import Region, big_members, file_region
from probe_worlds import refpack
from relayout_stream import pack_group, write_bigf

LOCATION_RECORD, SPATIAL_RECORD, GROUP_RECORD = 88, 96, 68
GDB_PATH, GSB_PATH = 'data/worlds/bam.gdb', 'data/worlds/bam.gsb'


def parse_gdb(gdb, byteorder='big'):
    e = '>' if byteorder == 'big' else '<'
    n_loc, n_spatial, n_group = struct.unpack_from(e + 'III', gdb, 8)
    locations = []
    for i in range(n_loc):
        o = 80 + i * LOCATION_RECORD
        name = gdb[o:o + 16].split(b'\0')[0].decode('ascii')
        spatial_count, group_count, last_group, spatial_start = struct.unpack_from(e + 'IIII', gdb, o + 16)
        kinds = struct.unpack_from(e + '24H', gdb, o + 32)
        locations.append(dict(index=i, name=name, spatial_start=spatial_start, spatial_count=spatial_count,
                              group_start=last_group - group_count + 1, group_count=group_count,
                              last_group=last_group, kind_counts={k: c for k, c in enumerate(kinds) if c}))
    spatial_base = (80 + n_loc * LOCATION_RECORD + 15) // 16 * 16
    group_base = spatial_base + n_spatial * SPATIAL_RECORD
    if group_base + n_group * GROUP_RECORD != len(gdb):
        raise ValueError('Unexpected GDB layout')
    groups = []
    for i in range(n_group):
        o = group_base + i * GROUP_RECORD
        count, index, offset, memsize = struct.unpack_from(e + 'HHII', gdb, o)
        kinds = struct.unpack_from(e + '14H', gdb, o + 12)
        if index != i:
            raise ValueError('GDB group index mismatch')
        groups.append(dict(index=i, count=count, stream_offset=offset, memsize=memsize,
                           kind_counts={k: c for k, c in enumerate(kinds) if c}))
    for loc in locations:
        for g in range(loc['group_start'], loc['last_group'] + 1):
            groups[g]['location'] = loc['name']
    return dict(byteorder=byteorder, locations=locations, groups=groups, spatial_base=spatial_base,
                group_base=group_base, counts=(n_loc, n_spatial, n_group))


def resource_records(data, byteorder='big'):
    pos = 0
    while pos < len(data):
        if len(data) - pos < 8:
            raise ValueError('Truncated resource header')
        kind = data[pos]
        size = int.from_bytes(data[pos + 1:pos + 4], byteorder)
        track = data[pos + 4]
        rid = int.from_bytes(data[pos + 5:pos + 8], byteorder)
        if pos + 8 + size > len(data):
            raise ValueError('Resource outside group')
        yield dict(kind=kind, size=size, track=track, rid=rid, offset=pos), data[pos + 8:pos + 8 + size]
        pos += size + 8


def serialize_resources(records, byteorder='big'):
    out = bytearray()
    for entry, payload in records:
        out.extend(bytes([entry['kind']]) + len(payload).to_bytes(3, byteorder)
                   + bytes([entry['track']]) + entry['rid'].to_bytes(3, byteorder))
        out.extend(payload)
    return bytes(out)


def read_group(stream, offset):
    """Decode one group's blocks starting at a stream offset; returns (decoded bytes, end offset, block count)."""
    pos, decoded, blocks = offset, bytearray(), 0
    while pos < len(stream):
        tag, size = struct.unpack_from('<4sI', stream, pos)
        if tag not in (b'CBXS', b'CEND') or size < 13 or pos + size > len(stream):
            raise ValueError(f'Unsupported stream block at {pos}: {tag!r}, {size}')
        raw, _ = refpack(stream[pos + 8:pos + size])
        decoded.extend(raw)
        pos += size
        blocks += 1
        if tag == b'CEND':
            return bytes(decoded), pos, blocks
    raise ValueError('Stream ended without CEND')


class World:
    """An opened BAM.BIG with lazily decoded groups."""

    def __init__(self, archive_bytes, byteorder='big', gdb_path=GDB_PATH, gsb_path=GSB_PATH):
        self.archive = archive_bytes
        self.byteorder = byteorder
        region = Region(io.BytesIO(archive_bytes), 0, len(archive_bytes))
        _, self.members = big_members(region)
        gdb = file_region(region, self.members, gdb_path)
        self.gdb_bytes = gdb.read(0, gdb.size)
        self.index = parse_gdb(self.gdb_bytes, byteorder)
        gsb = file_region(region, self.members, gsb_path)
        self.stream = gsb.read(0, gsb.size)
        self.gdb_path, self.gsb_path = gdb_path, gsb_path
        self._cache = {}

    def location(self, name):
        for loc in self.index['locations']:
            if loc['name'] == name:
                return loc
        raise KeyError(name)

    def group_bytes(self, index):
        if index not in self._cache:
            g = self.index['groups'][index]
            decoded, _, blocks = read_group(self.stream, g['stream_offset'])
            if sum(1 for _ in resource_records(decoded, self.byteorder)) != g['count']:
                raise ValueError(f'Group {index}: resource count does not match the index')
            self._cache[index] = decoded
        return self._cache[index]

    def records(self, index):
        return list(resource_records(self.group_bytes(index), self.byteorder))

    def group_end(self, index):
        """Walk block headers (no decoding) to the end of a group's CEND block."""
        pos = self.index['groups'][index]['stream_offset']
        while pos < len(self.stream):
            tag, size = struct.unpack_from('<4sI', self.stream, pos)
            if tag not in (b'CBXS', b'CEND') or size < 13 or pos + size > len(self.stream):
                raise ValueError(f'Unsupported stream block at {pos}: {tag!r}, {size}')
            pos += size
            if tag == b'CEND':
                return pos
        raise ValueError('Stream ended without CEND')

    def original_group_blocks(self, index):
        return self.stream[self.index['groups'][index]['stream_offset']:self.group_end(index)]


def update_group_index(gdb_bytes, index, records, byteorder='big'):
    """Rewrite one group's count, memory size, and per-kind counts for new records."""
    e = '>' if byteorder == 'big' else '<'
    parsed = parse_gdb(gdb_bytes, byteorder)
    o = parsed['group_base'] + index * GROUP_RECORD
    kinds = [0] * 14
    memsize = 0
    for entry, payload in records:
        if entry['kind'] < 14:
            kinds[entry['kind']] += 1
        if entry['kind'] <= 12:
            memsize += 8 + len(payload)
    out = bytearray(gdb_bytes)
    struct.pack_into(e + 'H', out, o, len(records))
    struct.pack_into(e + 'I', out, o + 8, memsize)
    struct.pack_into(e + '14H', out, o + 12, *kinds)
    # Location per-kind totals (kinds 0-23) follow the four index words.
    loc = next(l for l in parsed['locations'] if l['group_start'] <= index <= l['last_group'])
    totals = [0] * 24
    for g in range(loc['group_start'], loc['last_group'] + 1):
        row = records if g == index else None
        if row is None:
            counts = struct.unpack_from(e + '14H', gdb_bytes, parsed['group_base'] + g * GROUP_RECORD + 12)
            for k, c in enumerate(counts):
                totals[k] += c
        else:
            for k, c in enumerate(kinds):
                totals[k] += c
    lo = 80 + loc['index'] * LOCATION_RECORD + 32
    old = list(struct.unpack_from(e + '24H', gdb_bytes, lo))
    # Kinds 14-23 are not tracked per group; keep the location's stored values.
    totals[14:] = old[14:]
    struct.pack_into(e + '24H', out, lo, *totals)
    return bytes(out)


def assemble(world, replaced, jobs=4, max_decoded=81920, margin=96):
    """Rebuild BAM.BIG with some groups replaced by new record lists.

    replaced: {group index: [(entry, payload), ...]}. Untouched groups keep their
    original blocks verbatim. Returns (archive bytes, layout report).
    """
    from multiprocessing import Pool
    gdb_bytes = world.gdb_bytes
    for index, records in replaced.items():
        gdb_bytes = update_group_index(gdb_bytes, index, records, world.byteorder)
    jobs_list = [(i, serialize_resources(r, world.byteorder), max_decoded, margin) for i, r in replaced.items()]
    packed = {}
    if jobs_list:
        with Pool(min(jobs, len(jobs_list))) as pool:
            for i, data, n in pool.imap_unordered(pack_group, jobs_list, chunksize=1):
                packed[i] = (data, n)
    e = '>' if world.byteorder == 'big' else '<'
    parsed = parse_gdb(gdb_bytes, world.byteorder)
    gdb_out = bytearray(gdb_bytes)
    stream, layout = bytearray(), []
    for g in parsed['groups']:
        if g['index'] in packed:
            data, n = packed[g['index']]
        else:
            data, n = world.original_group_blocks(g['index']), None
        struct.pack_into(e + 'I', gdb_out, parsed['group_base'] + g['index'] * GROUP_RECORD + 4, len(stream))
        layout.append(dict(index=g['index'], old_offset=g['stream_offset'], new_offset=len(stream),
                           blocks=n, bytes=len(data), replaced=g['index'] in packed))
        stream += data
    members = []
    region = Region(io.BytesIO(world.archive), 0, len(world.archive))
    for m in world.members:
        if m['path'] == world.gsb_path:
            members.append((m['path'], bytes(stream)))
        elif m['path'] == world.gdb_path:
            members.append((m['path'], bytes(gdb_out)))
        else:
            members.append((m['path'], region.read(m['offset'], m['size'])))
    archive, _ = write_bigf(members, world.archive)
    return archive, layout


def sha256(data):
    return hashlib.sha256(data).hexdigest()
