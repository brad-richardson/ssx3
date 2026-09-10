import io
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from inspect_disc import Region, big_members
from probe_worlds import refpack, resource_records, patch_point


def packed(size, commands):
    return b'\x10\xfb' + size.to_bytes(3, 'big') + commands


class FormatTests(unittest.TestCase):
    def test_refpack_literals_and_padding(self):
        encoded = packed(7, b'\xe0ABCD\xffEFG')
        self.assertEqual(refpack(encoded + bytes(20)), (b'ABCDEFG', len(encoded)))

    def test_refpack_overlapping_matches_all_forms(self):
        # Literal A then repeat it using each of the three match encodings.
        cases = [(4, b'\x01\0A\xfc'), (5, b'\x80\x40\0A\xfc'), (6, b'\xc1\0\0\0A\xfc')]
        for size, commands in cases:
            self.assertEqual(refpack(packed(size, commands))[0], b'A' * size)

    def test_refpack_rejects_corruption(self):
        for data in [packed(3, b'\0\0\xfc'), packed(4, b'\xe0AB'), packed(5, b'\xe0ABCD\xfc'), packed(2, b'\xffABC')]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                refpack(data)

    def test_bigf_and_c0fb_directory(self):
        payload = b'example'
        for kind in ['BIGF', 'C0FB']:
            if kind == 'BIGF':
                table = struct.pack('>II', 64, len(payload)) + b'file.bin\0'
                head = b'BIGF' + struct.pack('<I', 64 + len(payload)) + struct.pack('>II', 1, 16 + len(table))
            else:
                table = (64).to_bytes(3, 'big') + len(payload).to_bytes(3, 'big') + b'file.bin\0'
                head = b'\xc0\xfb' + struct.pack('>HH', len(table), 1)
            data = (head + table).ljust(64, b'\0') + payload
            region = Region(io.BytesIO(data), 0, len(data))
            actual, entries = big_members(region)
            self.assertEqual(actual, kind)
            self.assertEqual(entries[0]['path'], 'file.bin')
            self.assertEqual(entries[0]['prefix_hex'], payload.hex())

    def test_region_bounds(self):
        region = Region(io.BytesIO(b'123'), 0, 3)
        with self.assertRaises(ValueError):
            region.read(2, 2)
        with self.assertRaises(ValueError):
            region.child(-1, 2)

    def test_resource_bounds(self):
        data = b'\x01\x03\0\0\x02\x05\0\0abc'
        entries = list(resource_records(data))
        self.assertEqual(entries[0][0]['rid'], 5)
        self.assertEqual(entries[0][1], b'abc')
        with self.assertRaises(ValueError):
            list(resource_records(data[:-1]))

    def test_patch_plane(self):
        c = [(0, 0, 0)] * 16
        c[0], c[1], c[4] = (1, 2, 3), (4, 0, 0), (0, 5, 0)
        self.assertEqual(patch_point(list(reversed(c)), .5, .5), (3, 4.5, 3))


if __name__ == '__main__':
    unittest.main()
