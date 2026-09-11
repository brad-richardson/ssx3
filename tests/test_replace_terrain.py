import math
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from replace_terrain import (placement, replace_patches, update_sdb,
                             clear_removed_instance_references, clear_script_bindings, pin_texture_group,
                             disable_course_scripts)
from import_terrain import apply, transform_coefficients
from probe_worlds import patch_point, patch_corner_error
from location_inventory import parse_sdb


def patch(rid=7):
    return (dict(kind=1, track=8, rid=rid, size=432), bytes(432))


def synthetic_sdb(records):
    raw = bytearray(80 + 96 + 68)
    struct.pack_into('<III', raw, 8, 1, 0, 1)
    raw[80:84] = b'ARA1'
    struct.pack_into('<IIII', raw, 96, 0, 1, 0, 0)
    struct.pack_into('<HHII', raw, 176, len(records), 0, 0,
                     sum(len(p) + 8 for e, p in records if e['kind'] <= 12))
    for e, _ in records:
        for off in (80 + 32 + 2 * e['kind'], 176 + 12 + 2 * e['kind']):
            struct.pack_into('<H', raw, off, struct.unpack_from('<H', raw, off)[0] + 1)
    return bytes(raw)


class ReplacementTests(unittest.TestCase):
    def test_disabling_course_programs_keeps_indices_and_other_data(self):
        empty = struct.pack('<9I', 0x4e554c, 20, 36, 36, 0xff2a, 0xffffffec, 0, 2, 0)
        active = struct.pack('<4I', 0x4e554c, 36, 52, 52) + bytes(range(36))
        data = bytearray(104 + 36 * 2 + 52 + 8)
        struct.pack_into('<I', data, 0, 0x1000)
        struct.pack_into('<3I', data, 56, 3, 92, 228)
        struct.pack_into('<3I', data, 92, 104, 140, 176)
        data[104:228] = empty + empty + active
        data[228:] = b'keep me!'
        records = [(dict(kind=16, track=8, rid=0), bytes(data))]
        out, edits = disable_course_scripts(records)
        self.assertEqual(out[0][1][:176], data[:176])
        self.assertEqual(out[0][1][176:228], empty + bytes(16))
        self.assertEqual(out[0][1][228:], b'keep me!')
        self.assertEqual([e['program'] for e in edits], [2])
        for offset, value in ((92, 4), (140, 0), (188, 500), (108, 24)):
            broken = bytearray(data)
            struct.pack_into('<I', broken, offset, value)
            with self.assertRaises(ValueError):
                disable_course_scripts([(records[0][0], broken)])

    def test_script_cleanup_preserves_unrelated_definitions(self):
        data = bytearray(176)
        struct.pack_into('<I', data, 0, 0x1000)
        struct.pack_into('<7I', data, 64, 112, 2, 92, 2, 96, 1, 104)
        struct.pack_into('<2I', data, 96, 0, 32)
        struct.pack_into('<4I', data, 112, 1, 0x10000, 99, 8)
        struct.pack_into('<4I', data, 144, 3, 0x10000, 99, 9)
        records = [(dict(kind=16, track=8, rid=0), bytes(data))]
        removed = [(dict(kind=k, track=8, rid=i), b'') for k, n in ((3, 2), (8, 1), (12, 1)) for i in range(n)]
        after, edits = clear_script_bindings(records, removed)
        expected = bytearray(data)
        for offset, value in ((68, 0), (84, 0), (112, 0), (124, 0xffffffff)):
            struct.pack_into('<I', expected, offset, value)
        self.assertEqual(after[0][1], bytes(expected))
        self.assertEqual(len(edits), 3)
        with self.assertRaises(ValueError):
            clear_script_bindings(records, removed[1:])

    def test_pinned_streaming_tree_remaps_other_location_children(self):
        # A's leaf, B's three-node tree, C's three-node tree.
        nloc, nnodes, ngroups = 3, 7, 5
        base = (80 + nloc * 88 + 15) // 16 * 16
        raw = bytearray(base + nnodes * 96 + ngroups * 68)
        struct.pack_into('<III', raw, 8, nloc, nnodes, ngroups)
        for i, (name, start, count, last, groups) in enumerate((('A', 0, 1, 0, 1), ('B', 1, 3, 3, 3), ('C', 4, 3, 4, 1))):
            off = 80 + i * 88
            raw[off:off + 1] = name.encode()
            struct.pack_into('<4I', raw, off + 16, count, groups, last, start)
        for i in range(nnodes):
            off = base + i * 96
            struct.pack_into('<8f', raw, off, -10, -20, -30, 1, 10, 20, 30, 1)
            struct.pack_into('<4i', raw, off + 80, -1, -1, 1, 0)
        struct.pack_into('<3i', raw, base + 96 + 80, 2, 3, -1)
        struct.pack_into('<3i', raw, base + 4 * 96 + 80, 5, 6, -1)
        for i in range(ngroups):
            struct.pack_into('<H', raw, base + nnodes * 96 + i * 68 + 2, i)
        struct.pack_into('<H', raw, base + nnodes * 96 + 68 + 12 + 9 * 2, 1)
        out, report = pin_texture_group(bytes(raw), 'B', 1, [[-100, -200, -300], [100, 200, 300]])
        parsed = parse_sdb(out)
        self.assertEqual(len(parsed['spatial']), 5)
        self.assertEqual(parsed['locations'][1]['spatial_count'], 1)
        self.assertEqual(parsed['locations'][2]['spatial_start'], 2)
        self.assertEqual(parsed['spatial'][2]['ints'][20:23], [3, 4, -1])
        self.assertEqual(parsed['spatial'][1]['ints'][20:23], [-1, -1, 1])
        self.assertEqual(parsed['spatial'][1]['floats'][:3], [-1100, -1200, -1300])
        self.assertEqual(out[-ngroups * 68:], raw[-ngroups * 68:])
        self.assertEqual(report['old_nodes'], 3)

    def test_reference_cleanup_only_changes_known_removed_ids(self):
        removed = [(dict(kind=3, track=8, rid=7), b'')]
        oid = 7 << 8 | 8
        table = bytearray(96)
        struct.pack_into('<I', table, 12, 3)
        for i, ref in enumerate((oid, 7 << 8 | 9, 0xffffffff)):
            struct.pack_into('<III', table, 28 + i * 24, ref, 88, oid)
        nis = struct.pack('<18I', oid, *([0xffffffff] * 17))
        records = [(dict(kind=13, track=8, rid=0), bytes(table)),
                   (dict(kind=18, track=8, rid=0), nis),
                   (dict(kind=16, track=8, rid=0), struct.pack('<I', oid))]
        after, edits = clear_removed_instance_references(records, removed)
        expected = bytearray(table)
        struct.pack_into('<I', expected, 28, 0xffffffff)
        self.assertEqual(after[0][1], bytes(expected))
        self.assertEqual(after[1][1], bytes.fromhex('ff' * 72))
        self.assertEqual(after[2], records[2])
        self.assertEqual([(e['kind'], e['offset']) for e in edits], [(13, 28), (18, 0)])
        self.assertEqual(clear_removed_instance_references(after, removed), (after, []))

    def test_reference_cleanup_rejects_malformed_tables(self):
        removed = [(dict(kind=3, track=8, rid=7), b'')]
        for payload in (bytes(12), struct.pack('<4I', 0, 0, 0, 100),
                        struct.pack('<4I', 1, 0, 0, 0),
                        struct.pack('<4I', 0, 0, 0, 1) + bytes(24)):
            with self.assertRaises(ValueError):
                clear_removed_instance_references([(dict(kind=13, track=8, rid=0), payload)], removed)
        with self.assertRaises(ValueError):
            clear_removed_instance_references([(dict(kind=18, track=8, rid=0), bytes(4))], removed)

    def test_affine_transform_evaluates_same_surface(self):
        c = [[i * .125, -i * .25, i * .5] for i in range(16)]
        source, target = (11, 12, 13), (-4, 5, 6)
        matrix, t = placement(source, target, 73, .55)
        self.assertLess(math.dist(apply(matrix, t, source), target), 1e-10)
        transformed = transform_coefficients(c, matrix, t)
        for u, v in ((0, 0), (.3, .7), (1, 1)):
            self.assertLess(math.dist(patch_point(transformed, u, v), apply(matrix, t, patch_point(c, u, v))), 1e-9)

    def test_replacement_preserves_other_resources_and_ids(self):
        other = (dict(kind=3, track=8, rid=1, size=4), b'prop')
        records = [patch(7), other, patch(20)]
        coeffs = [[0, 0, 0] for _ in range(16)]
        coeffs[15], coeffs[14], coeffs[11] = [10, 20, 30], [40, 0, 4], [0, 50, -5]
        m, t = placement((0, 0, 0), (100, 200, 300), 90, .5)
        after, added = replace_patches(records, 7, [coeffs] * 3, m, t)
        self.assertEqual([e['rid'] for e, _ in added], [7, 20, 21])
        self.assertEqual([r for r in after if r[0]['kind'] != 1], [other])
        for e, p in added:
            self.assertEqual(struct.unpack_from('<I', p, 336)[0], e['rid'] << 8 | 8)
            cs = [struct.unpack_from('<4f', p, 64 + 16 * j)[:3] for j in range(16)]
            corners = [struct.unpack_from('<3f', p, 368 + 12 * j) for j in range(4)]
            self.assertLess(patch_corner_error(cs, corners), 1e-4)
        sdb = synthetic_sdb(records)
        out, owner = update_sdb(sdb, 0, records, after)
        parsed = parse_sdb(out)
        self.assertEqual(owner['name'], 'ARA1')
        self.assertEqual(parsed['groups'][0]['count'], 4)
        self.assertEqual(parsed['groups'][0]['memsize'], 3 * 440 + 12)
        self.assertEqual(parsed['locations'][0]['kind_counts'], {1: 3, 3: 1})
        self.assertEqual(out[176 + 4:176 + 8], sdb[176 + 4:176 + 8])

    def test_shrinking_updates_counts(self):
        before, after = [patch(1), patch(2)], [patch(1)]
        out, _ = update_sdb(synthetic_sdb(before), 0, before, after)
        self.assertEqual(parse_sdb(out)['groups'][0]['memsize'], 440)

    def test_removing_instances_updates_location_and_group(self):
        instance = (dict(kind=3, track=8, rid=4, size=4), b'prop')
        before, after = [patch(), instance], [patch()]
        out, _ = update_sdb(synthetic_sdb(before), 0, before, after)
        parsed = parse_sdb(out)
        self.assertEqual(parsed['locations'][0]['kind_counts'], {1: 1})
        self.assertEqual(parsed['groups'][0]['kind_counts'], {1: 1})
        self.assertEqual(parsed['groups'][0]['count'], 1)
        self.assertEqual(parsed['groups'][0]['memsize'], 440)

    def test_refuses_bad_inputs(self):
        for scale in (0, -1, float('nan')):
            with self.assertRaises(ValueError):
                placement((0, 0, 0), (0, 0, 0), 0, scale)
        with self.assertRaises(ValueError):
            update_sdb(synthetic_sdb([patch()]), 0, [patch(), patch(8)], [patch()])
