"""GameCube world index/resource helpers on synthetic data (no game bytes)."""
import struct
import math
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_world import (parse_gdb, resource_records, serialize_resources, update_group_index,
                           unused_global_rids, validate_global_images,
                           validate_resource_capacities)  # noqa: E402
from gamecube_terrain import make_record, replace_patches, terrain_bounds, GC_PATCH_SIZE  # noqa: E402
from patch_geometry import outward_float32  # noqa: E402
from probe_worlds import patch_point  # noqa: E402


def synthetic_gdb(byteorder='big'):
    e = '>' if byteorder == 'big' else '<'
    n_loc, n_spatial, n_group = 2, 3, 3
    gdb = bytearray(80)
    struct.pack_into(e + 'III', gdb, 8, n_loc, n_spatial, n_group)
    # Location A: groups 0-1, location B: group 2.
    for i, (name, spatial, groups, last, start, kinds) in enumerate((
            ('A', 2, 2, 1, 0, {1: 5, 9: 4}), ('B', 1, 1, 2, 2, {1: 7}))):
        rec = bytearray(88)
        rec[:len(name)] = name.encode()
        struct.pack_into(e + 'IIII', rec, 16, spatial, groups, last, start)
        counts = [kinds.get(k, 0) for k in range(24)]
        struct.pack_into(e + '24H', rec, 32, *counts)
        gdb += rec
    gdb += bytes(-len(gdb) % 16)
    gdb += bytes(96 * n_spatial)
    for i, (count, offset, mem, kinds) in enumerate(((4, 0, 100, {9: 4}), (5, 32768, 200, {1: 5}), (7, 65536, 300, {1: 7}))):
        rec = bytearray(68)
        struct.pack_into(e + 'HHII', rec, 0, count, i, offset, mem)
        struct.pack_into(e + '14H', rec, 12, *[kinds.get(k, 0) for k in range(14)])
        gdb += rec
    return bytes(gdb)


class GameCubeWorldTests(unittest.TestCase):
    def test_parse_gdb_big_endian_matches_ps2_layout(self):
        parsed = parse_gdb(synthetic_gdb())
        self.assertEqual([l['name'] for l in parsed['locations']], ['A', 'B'])
        self.assertEqual(parsed['locations'][0]['group_start'], 0)
        self.assertEqual(parsed['locations'][1]['group_start'], 2)
        self.assertEqual(parsed['groups'][1]['stream_offset'], 32768)
        self.assertEqual(parsed['groups'][2]['location'], 'B')
        self.assertEqual(parsed['groups'][1]['kind_counts'], {1: 5})

    def test_resource_round_trip_is_big_endian(self):
        records = [(dict(kind=1, size=3, track=8, rid=0x010203), b'abc'),
                   (dict(kind=12, size=1, track=2, rid=7), b'z')]
        blob = serialize_resources(records)
        self.assertEqual(blob[:8], bytes([1, 0, 0, 3, 8, 1, 2, 3]))
        back = list(resource_records(blob))
        self.assertEqual([(e['kind'], e['track'], e['rid']) for e, _ in back], [(1, 8, 0x010203), (12, 2, 7)])
        self.assertEqual([p for _, p in back], [b'abc', b'z'])

    def test_update_group_index_recounts_group_and_location(self):
        gdb = synthetic_gdb()
        records = [(dict(kind=1, size=2, track=8, rid=i), b'xy') for i in range(9)] + \
                  [(dict(kind=13, size=1, track=8, rid=0), b'q')]
        out = update_group_index(gdb, 1, records)
        parsed = parse_gdb(out)
        self.assertEqual(parsed['groups'][1]['count'], 10)
        self.assertEqual(parsed['groups'][1]['memsize'], 9 * 10)  # kind 13 excluded from memsize
        self.assertEqual(parsed['groups'][1]['kind_counts'], {1: 9, 13: 1})
        self.assertEqual(parsed['locations'][0]['kind_counts'], {1: 9, 9: 4, 13: 1})
        self.assertEqual(parsed['locations'][1]['kind_counts'], {1: 7})
        self.assertEqual(len(out), len(gdb))

    def test_make_record_layout(self):
        template = bytes(range(256)) + bytes(GC_PATCH_SIZE - 256)
        coeffs = [[0.0, 0.0, 0.0] for _ in range(16)]
        coeffs[15] = [10.0, 20.0, 30.0]  # constant term: a flat patch at one point
        rec = make_record(template, coeffs, 0x1234, 8)
        self.assertEqual(len(rec), GC_PATCH_SIZE)
        self.assertEqual(rec[:64], template[:64])
        self.assertEqual(struct.unpack_from('>4f', rec, 64 + 15 * 16), (10.0, 20.0, 30.0, 1.0))
        self.assertEqual(struct.unpack_from('>3f', rec, 336), (10.0, 20.0, 30.0))
        self.assertEqual(struct.unpack_from('>3f', rec, 384), (10.0, 20.0, 30.0))
        self.assertEqual(struct.unpack_from('>3f', rec, 396), (10.0, 20.0, 30.0))
        self.assertEqual(struct.unpack_from('>I', rec, 408)[0], (8 << 24) | 0x1234)
        self.assertEqual(rec[412:], template[412:])

    def test_scenery_array_capacities_grow_and_preserve_reservations(self):
        for byteorder in ('big', 'little'):
            with self.subTest(byteorder=byteorder):
                gdb = synthetic_gdb(byteorder)
                records = [(dict(kind=k, track=0, rid=k - 20), b'array')
                           for k in range(23, 28)]
                out = update_group_index(gdb, 1, records, byteorder)
                counts = parse_gdb(out, byteorder)['locations'][0]['kind_counts']
                self.assertEqual({k: counts[k] for k in range(23, 28)},
                                 {k: k - 19 for k in range(23, 28)})
                out = update_group_index(out, 1, [], byteorder)
                self.assertEqual(parse_gdb(out, byteorder)['locations'][0]['kind_counts'][27], 8)
                self.assertEqual(len(out), len(gdb))

    def test_scenery_capacity_overflow_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'capacity'):
            update_group_index(synthetic_gdb(), 1,
                               [(dict(kind=27, track=0, rid=0x7fff), b'array')])

    def test_sparse_model_ids_need_capacity_beyond_record_count(self):
        out = update_group_index(synthetic_gdb(), 1,
                                 [(dict(kind=2, track=0, rid=17), b'model')])
        parsed = parse_gdb(out)
        self.assertEqual(parsed['groups'][1]['kind_counts'][2], 1)
        self.assertEqual(parsed['locations'][0]['kind_counts'][2], 18)
        # Repacking the sibling texture page must preserve the sparse model
        # reservation established by the first update in the same assembly.
        out = update_group_index(out, 0, [(dict(kind=9, track=255, rid=4), b'image')])
        self.assertEqual(parse_gdb(out)['locations'][0]['kind_counts'][2], 18)

    def test_archive_capacity_audit_checks_arrays_without_group_counters(self):
        rows = [(dict(kind=26, track=0, rid=1), b'normals')]
        world = SimpleNamespace(index=dict(global_kind_counts={},
                                locations=[dict(index=0, kind_counts={26: 1})],
                                groups=[dict(index=0, kind_counts={})]), records=lambda _: rows)
        with self.assertRaisesRegex(ValueError, 'kind 26.*capacity'):
            validate_resource_capacities(world)
        world.index['locations'][0]['kind_counts'][26] = 2
        self.assertEqual(validate_resource_capacities(world), 1)
        rows[0][0]['track'] = 1
        with self.assertRaisesRegex(ValueError, 'missing location'):
            validate_resource_capacities(world)

    def test_global_capacity_is_max_rid_plus_one_and_never_shrinks(self):
        for endian, byteorder in [('>', 'big'), ('<', 'little')]:
            with self.subTest(byteorder=byteorder):
                gdb = bytearray(synthetic_gdb(byteorder))
                struct.pack_into(endian + 'HH', gdb, 42, 788, 662)
                records = [(dict(kind=9, track=255, rid=819), b'x'),
                           (dict(kind=10, track=255, rid=80), b'y'),
                           (dict(kind=1, track=8, rid=900), b'z')]
                out = update_group_index(bytes(gdb), 0, records, byteorder)
                self.assertEqual(parse_gdb(out, byteorder)['global_kind_counts'], {9: 820, 10: 662})
                # Group count is one; location keeps its four reserved slots,
                # while the separate global lookup needs 820 slots.
                self.assertEqual(parse_gdb(out, byteorder)['groups'][0]['kind_counts'][9], 1)
                self.assertEqual(parse_gdb(out, byteorder)['locations'][0]['kind_counts'][9], 4)
                out = update_group_index(out, 0, records[1:], byteorder)
                self.assertEqual(parse_gdb(out, byteorder)['global_kind_counts'][9], 820)

    def test_unused_ids_check_other_locations_and_reserved_capacity(self):
        world = SimpleNamespace(index=dict(global_kind_counts={9: 800}, groups=[dict(index=0, kind_counts={9: 1})]),
                                records=lambda _: [(dict(kind=9, track=255, rid=810), b'x')])
        self.assertEqual(unused_global_rids(world, 9, 3), [811, 812, 813])
        world.index['global_kind_counts'][9] = 900
        self.assertEqual(unused_global_rids(world, 9, 2), [900, 901])

    def test_global_capacity_overflow_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'capacity'):
            update_group_index(synthetic_gdb(), 0, [(dict(kind=9, track=255, rid=0x7fff), b'x')])
        world = SimpleNamespace(index=dict(global_kind_counts={9: 0x7fff}, groups=[]))
        with self.assertRaisesRegex(ValueError, 'capacity'):
            unused_global_rids(world, 9, 1)

    def test_global_image_audit_rejects_conflicts_and_undersized_tables(self):
        records = {0: [(dict(kind=9, track=255, rid=3), b'snow')],
                   1: [(dict(kind=9, track=255, rid=3), b'snow')]}
        world = SimpleNamespace(index=dict(global_kind_counts={9: 4}, groups=[
                                    dict(index=i, kind_counts={9: 1}) for i in records]),
                                records=lambda i: records[i])
        self.assertEqual(validate_global_images(world), {9: 1, 10: 0})
        records[1] = [(dict(kind=9, track=255, rid=3), b'rock')]
        with self.assertRaisesRegex(ValueError, 'Conflicting global image'):
            validate_global_images(world)
        records[1] = [(dict(kind=9, track=255, rid=4), b'rock')]
        with self.assertRaisesRegex(ValueError, 'capacity'):
            validate_global_images(world)

    def test_curved_patch_bounds_enclose_crest_between_grid_samples(self):
        c = [[0., 0., 0.] for _ in range(16)]
        c[14] = [100., 0., 1000.]  # x=100u, z=1000(u-u^3)
        c[11] = [0., 100., 0.]    # y=100v
        c[12][2] = -1000.
        rec = make_record(bytes(GC_PATCH_SIZE), c, 0, 8)
        low, high = terrain_bounds([(dict(kind=1), rec)])
        sphere = struct.unpack_from('>4f', rec, 320)
        crest = patch_point(c, 1 / math.sqrt(3), .37)
        self.assertGreater(crest[2], max(patch_point(c, i / 8, 0)[2] for i in range(9)))
        for u in [i / 37 for i in range(38)] + [1 / math.sqrt(3)]:
            for v in (0., .37, 1.):
                p = patch_point(c, u, v)
                self.assertTrue(all(low[k] <= p[k] <= high[k] for k in range(3)))
                self.assertLessEqual(math.dist(sphere[:3], p), sphere[3])

    def test_outward_rounding_handles_signs_and_underflow(self):
        for value in (0., 1e-46, -1e-46, 1 / 3, -1 / 3, 123456.789, -123456.789):
            self.assertLessEqual(outward_float32(value, False), value)
            self.assertGreaterEqual(outward_float32(value, True), value)

    def test_bounds_use_serialized_coefficients_after_cancellation(self):
        c = [[0., 0., 0.] for _ in range(16)]
        c[15][0], c[14][0] = -100000.003, 100000.001
        rec = make_record(bytes(GC_PATCH_SIZE), c, 0, 8)
        stored = [struct.unpack_from('>4f', rec, 64 + 16 * j)[:3] for j in range(16)]
        endpoint = patch_point(stored, 1, 0)
        low, high = terrain_bounds([(dict(kind=1), rec)])
        self.assertTrue(all(low[k] <= endpoint[k] <= high[k] for k in range(3)))
        self.assertEqual(struct.unpack_from('>3f', rec, 360), endpoint)

    def test_replacement_discards_host_occluders_and_preserves_other_resources(self):
        terrain = (dict(kind=1, rid=7, track=8), bytes(GC_PATCH_SIZE))
        curtain = (dict(kind=11, rid=0, track=8), bytes(208))
        other = (dict(kind=2, rid=0, track=8), b'model')
        identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        records, _ = replace_patches([terrain, curtain, other], 7, [[[0., 0., 0.]] * 16], identity, [0, 0, 0])
        self.assertEqual([e['kind'] for e, _ in records], [1, 2])
        self.assertEqual(records[-1], other)


if __name__ == '__main__':
    unittest.main()
