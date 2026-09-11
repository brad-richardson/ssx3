"""GameCube world index/resource helpers on synthetic data (no game bytes)."""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_world import parse_gdb, resource_records, serialize_resources, update_group_index  # noqa: E402
from gamecube_terrain import make_record, GC_PATCH_SIZE  # noqa: E402


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


if __name__ == '__main__':
    unittest.main()
