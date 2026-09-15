#!/usr/bin/env python3
"""GameCube ports of replace_terrain.py's dependency cleanup steps.

Same record layouts as PS2 with big-endian words; instance ids are encoded
as ``track << 24 | rid`` (PS2: ``rid << 8 | track``). Kind-13 object tables
start with byte 1 on GameCube (0 on PS2). LUN programs are big-endian with
the magic 0x4E554C and the same 20/36/36 empty-return shape.
"""
import struct


def instance_id(entry):
    return (entry['track'] << 24) | entry['rid']


def clear_removed_instance_references(records, removed):
    """Blank kind-13 object rows and kind-18 NIS slots that name removed kind-3 instances."""
    ids = {instance_id(e) for e, _ in removed if e['kind'] == 3}
    out, changes = [], []
    for e, payload in records:
        if not ids or e['kind'] not in (13, 18):
            out.append((e, payload))
            continue
        if e['kind'] == 13:
            if len(payload) < 16 or payload[0] != 1:
                raise ValueError('Unsupported kind-13 object table')
            count = struct.unpack_from('>I', payload, 12)[0]
            table_end = 16 + count * 24
            if table_end > len(payload):
                raise ValueError('Truncated kind-13 object table')
            for i in range(count):
                offset = struct.unpack_from('>I', payload, 16 + i * 24 + 16)[0]
                if offset < table_end or offset + 8 > len(payload):
                    raise ValueError('Invalid kind-13 object data offset')
            offsets = range(28, table_end, 24)
        else:
            if len(payload) != 72:
                raise ValueError('Unsupported kind-18 object table size')
            offsets = range(0, len(payload), 4)
        data = bytearray(payload)
        for offset in offsets:
            oid = struct.unpack_from('>I', data, offset)[0]
            if oid in ids:
                struct.pack_into('>I', data, offset, 0xffffffff)
                changes.append(dict(kind=e['kind'], track=e['track'], rid=e['rid'], offset=offset, instance_id=oid))
        out.append((e, bytes(data)))
    return out, changes


def _check_script_header(payload):
    if len(payload) < 92 or payload[:4] != b'\x00\x10\x00\x00':
        raise ValueError('Unsupported kind-16 script header')


def clear_script_bindings(records, removed):
    """Disable kind-16 binding tables for whole removed instance/spline tables and collision definitions."""
    out, edits = [], []
    for e, payload in records:
        if e['kind'] != 16:
            out.append((e, payload))
            continue
        _check_script_header(payload)
        data = bytearray(payload)
        for kind, count_offset, index_size in ((3, 68, 2), (8, 84, 4)):
            removed_ids = {r['rid'] for r, _ in removed if r['kind'] == kind and r['track'] == e['track']}
            if not removed_ids:
                continue
            count, offset = struct.unpack_from('>II', data, count_offset)
            if removed_ids != set(range(count)) or offset + count * index_size > len(data):
                raise ValueError('Script binding count does not match complete removed resource table')
            struct.pack_into('>I', data, count_offset, 0)
            edits.append(dict(kind=16, track=e['track'], rid=e['rid'], offset=count_offset,
                              action='disable_binding_table', resource_kind=kind, count=count))
        collision_ids = {instance_id(r) for r, _ in removed if r['kind'] == 12}
        base = struct.unpack_from('>I', data, 64)[0]
        count, offset = struct.unpack_from('>II', data, 76)
        if offset + count * 4 > len(data):
            raise ValueError('Truncated script definition table')
        seen = set()
        for i in range(count):
            start = base + struct.unpack_from('>I', data, offset + 4 * i)[0]
            if start + 16 > len(data):
                raise ValueError('Script definition is outside its resource')
            if start in seen:
                continue
            seen.add(start)
            kind, _, _, oid = struct.unpack_from('>4I', data, start)
            if kind in (1, 3) and oid in collision_ids:
                struct.pack_into('>I', data, start, 0)
                struct.pack_into('>I', data, start + 12, 0xffffffff)
                edits.append(dict(kind=16, track=e['track'], rid=e['rid'], offset=start,
                                  action='disable_collision_definition', definition_type=kind, collision_id=oid))
        out.append((e, bytes(data)))
    return out, edits


def disable_course_scripts(records):
    """Replace every LUN program with the original empty-return program."""
    out, changes = [], []
    for e, payload in records:
        if e['kind'] != 16:
            out.append((e, payload))
            continue
        _check_script_header(payload)
        count, table, end = struct.unpack_from('>3I', payload, 56)
        if count < 2 or table + 4 * count > len(payload) or end > len(payload):
            raise ValueError('Invalid course-script index table')
        starts = struct.unpack_from(f'>{count}I', payload, table)
        if list(starts) != sorted(set(starts)) or starts[0] < table + 4 * count:
            raise ValueError('Invalid course-script program offsets')
        spans = list(zip(starts, (*starts[1:], end)))
        for start, stop in spans:
            if stop - start < 36:
                raise ValueError('Truncated LUN program')
            magic, code_end, data_end, length = struct.unpack_from('>4I', payload, start)
            # The span after the last program is padded to the section end. 29 of
            # the world's 49 locations pad it (4, 8 or 12 zero bytes); ARA1 does
            # not, which is why an exact length was enough for Snow Jam. Only
            # zero padding, and only up to one 16-byte boundary, is accepted.
            padding = stop - start - length
            if (magic != 0x4e554c or not 20 <= code_end <= data_end <= length
                    or not 0 <= padding < 16 or payload[start + length:stop] != bytes(padding)):
                raise ValueError('Unsupported LUN program bounds')
        template = payload[spans[0][0]:spans[0][1]]
        if (len(template) != 36 or template != payload[spans[1][0]:spans[1][1]] or
                struct.unpack_from('>3I', template, 4) != (20, 36, 36) or template[16:20] != b'\x2a\xff\x00\x00'):
            raise ValueError('Expected matching original empty-return LUN programs')
        data = bytearray(payload)
        for index, (start, stop) in enumerate(spans):
            replacement = template + bytes(stop - start - len(template))
            if data[start:stop] != replacement:
                data[start:stop] = replacement
                changes.append(dict(kind=16, track=e['track'], rid=e['rid'], program=index, offset=start, bytes=stop - start))
        out.append((e, bytes(data)))
    return out, changes


def pin_texture_group(gdb, location, texture_group, bounds):
    """Replace one location's texture-streaming tree with a single leaf (GameCube big-endian port)."""
    from gamecube_world import parse_gdb, LOCATION_RECORD, SPATIAL_RECORD
    parsed = parse_gdb(gdb, 'big')
    owner = next(l for l in parsed['locations'] if l['name'] == location)
    if not owner['group_start'] <= texture_group < owner['last_group']:
        raise ValueError('Texture group must belong to the target location')
    kinds = parsed['groups'][texture_group]['kind_counts']
    if not kinds or set(kinds) - {9, 10}:
        raise ValueError('Pinned group must contain only textures and lightmaps')
    start, count = owner['spatial_start'], owner['spatial_count']
    if count < 1:
        raise ValueError('Location has no spatial tree')
    end, delta = start + count, count - 1
    nloc, nodes, _ = struct.unpack_from('>III', gdb, 8)
    base = parsed['spatial_base']
    prefix = bytearray(gdb[:base])
    struct.pack_into('>I', prefix, 12, nodes - delta)
    for loc in parsed['locations']:
        offset = 80 + loc['index'] * LOCATION_RECORD
        if loc['name'] == location:
            struct.pack_into('>I', prefix, offset + 16, 1)
        elif loc['spatial_start'] >= end:
            struct.pack_into('>I', prefix, offset + 28, loc['spatial_start'] - delta)
        elif start <= loc['spatial_start'] < end:
            raise ValueError('Overlapping location spatial trees')
    old = struct.unpack_from('>8f', gdb, base + start * SPATIAL_RECORD)
    low = [min(old[k], bounds[0][k] - 1000) for k in range(3)]
    high = [max(old[k + 4], bounds[1][k] + 1000) for k in range(3)]
    leaf = struct.pack('>20f4i', *low, 1, *high, 1, *([0] * 12), -1, -1, texture_group, 0)
    chunks = []
    for i in range(nodes):
        if i == start:
            chunks.append(leaf)
        elif start < i < end:
            continue
        else:
            raw = bytearray(gdb[base + i * SPATIAL_RECORD:base + (i + 1) * SPATIAL_RECORD])
            for offset in (80, 84):
                child = struct.unpack_from('>i', raw, offset)[0]
                if start <= child < end:
                    raise ValueError('Another tree references the replaced location')
                if child >= end:
                    struct.pack_into('>i', raw, offset, child - delta)
            chunks.append(bytes(raw))
    result = bytes(prefix) + b''.join(chunks) + gdb[base + nodes * SPATIAL_RECORD:]
    parse_gdb(result, 'big')
    return result, dict(group=texture_group, old_nodes=count, new_nodes=1, bounds=[low, high])
