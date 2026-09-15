"""Dump-name parsing, the ride-phase split, and the selection."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from texture_dump_inventory import is_framebuffer, parse, run_boundaries


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def dumped(self, name, size=64):
        path = self.tmp / name
        path.write_bytes(b'\0' * size)
        return path

    def test_name_with_and_without_a_palette_hash(self):
        plain = parse(self.dumped('tex1_128x64_0123456789abcdef_4.png'))
        self.assertEqual((plain['width'], plain['height'], plain['format']), (128, 64, 4))
        self.assertEqual(plain['format_name'], 'RGB565')
        self.assertIsNone(plain['tlut_hash'])
        paletted = parse(self.dumped('tex1_256x256_aaaaaaaaaaaaaaaa_bbbbbbbbbbbbbbbb_9.png'))
        self.assertEqual(paletted['tlut_hash'], 'bbbbbbbbbbbbbbbb')
        self.assertEqual(paletted['format_name'], 'C8')
        self.assertFalse(paletted['arbitrary_mips'])
        self.assertTrue(parse(self.dumped('tex1_32x32_deadbeefdeadbeef_5_arb.png'))['arbitrary_mips'])

    def test_mipmapped_names_and_their_sidecars(self):
        base = parse(self.dumped('tex1_128x128_m_015e396b80054909_14.png'))
        self.assertTrue(base['mipmapped'])
        self.assertEqual(base['mip_level'], 0)
        self.assertEqual((base['width'], base['format']), (128, 14))
        self.assertEqual(base['texture_hash'], '015e396b80054909')
        level = parse(self.dumped('tex1_128x128_m_015e396b80054909_14_mip3.png'))
        self.assertEqual(level['mip_level'], 3)
        self.assertTrue(level['mipmapped'])
        self.assertFalse(parse(self.dumped('tex1_64x64_0123456789abcdef_5.png'))['mipmapped'])

    def test_unrelated_files_are_ignored(self):
        self.assertIsNone(parse(self.dumped('screenshot.png')))
        self.assertIsNone(parse(self.dumped('tex1_broken.png')))

    def test_framebuffer_copies_are_recognized_by_shape_and_format(self):
        self.assertTrue(is_framebuffer(dict(format=9, width=640, height=480)))
        self.assertTrue(is_framebuffer(dict(format=10, width=320, height=240)))
        self.assertFalse(is_framebuffer(dict(format=9, width=256, height=256)))
        self.assertFalse(is_framebuffer(dict(format=14, width=640, height=480)))


class RaceStartTests(unittest.TestCase):
    def run_with(self, rows):
        directory = Path(tempfile.mkdtemp()) / 'run'
        directory.mkdir()
        (directory / 'rider.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
        return directory

    def test_boundaries_are_the_first_sample_and_the_first_movement(self):
        rows = [dict(t=0, wall_time=99.0, x=0, y=0, z=0),
                dict(t=1, wall_time=101.0, x=5, y=5, z=5),
                dict(t=2, wall_time=102.0, x=5, y=5, z=5),
                dict(t=3, wall_time=103.0, x=9, y=5, z=5)]
        self.assertEqual(run_boundaries(self.run_with(rows)), (99.0, 103.0))

    def test_a_run_without_movement_is_refused(self):
        with self.assertRaises(ValueError):
            run_boundaries(self.run_with([dict(t=0, wall_time=1.0, x=0, y=0, z=0)]))
        with self.assertRaises(ValueError):
            run_boundaries(self.run_with([dict(t=0, wall_time=1.0, x=4, y=0, z=0)]))


if __name__ == '__main__':
    unittest.main()
