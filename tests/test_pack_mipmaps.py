"""A pack's mip chain: the levels Dolphin needs, halving all the way down."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import pack_mipmaps

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:  # pragma: no cover
    HAVE_PIL = False


class ChainSizeTests(unittest.TestCase):
    def test_a_square_chain_reaches_one(self):
        self.assertEqual(pack_mipmaps.chain_sizes(8, 8),
                         [(4, 4), (2, 2), (1, 1)])

    def test_a_rectangular_chain_clamps_the_short_side(self):
        self.assertEqual(pack_mipmaps.chain_sizes(8, 2),
                         [(4, 1), (2, 1), (1, 1)])

    def test_min_size_stops_the_chain_early(self):
        self.assertEqual(pack_mipmaps.chain_sizes(64, 64, min_size=16),
                         [(32, 32), (16, 16)])

    def test_a_one_pixel_texture_has_no_levels(self):
        self.assertEqual(pack_mipmaps.chain_sizes(1, 1), [])


@unittest.skipUnless(HAVE_PIL, 'Pillow is required')
class WriteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pack = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def texture(self, name, size=(16, 16)):
        image = Image.new('RGBA', size, (10, 20, 30, 255))
        for x in range(size[0]):
            image.putpixel((x, 0), (255, 255, 255, 255))
        image.save(self.pack / name)
        return image

    def test_every_level_is_half_the_one_above(self):
        self.texture('tex1_4x4_00_14.png', (16, 16))
        report = pack_mipmaps.write_pack(self.pack)
        self.assertEqual(report['bases'], 1)
        self.assertEqual(report['levels_written'], 4)
        widths = []
        for level in range(1, 5):
            with Image.open(self.pack / f'tex1_4x4_00_14_mip{level}.png') as image:
                widths.append(image.size)
        self.assertEqual(widths, [(8, 8), (4, 4), (2, 2), (1, 1)])

    def test_levels_are_averaged_not_sampled(self):
        """A box filter, so a white row and a dark row average together."""
        self.texture('tex1_4x4_01_14.png', (16, 16))
        pack_mipmaps.write_pack(self.pack)
        with Image.open(self.pack / 'tex1_4x4_01_14_mip1.png') as level:
            top = level.getpixel((0, 0))
        self.assertGreater(top[0], 10)
        self.assertLess(top[0], 255)

    def test_a_sidecar_is_not_treated_as_a_base(self):
        self.texture('tex1_4x4_02_14.png', (8, 8))
        first = pack_mipmaps.write_pack(self.pack)
        second = pack_mipmaps.write_pack(self.pack)
        self.assertEqual(first['bases'], 1)
        self.assertEqual(second['bases'], 1)          # the _mipN files are skipped
        self.assertEqual(second['levels_written'], 0)  # and nothing is rewritten
        self.assertEqual(second['already_present'], 3)

    def test_a_dry_run_writes_nothing(self):
        self.texture('tex1_4x4_03_14.png', (8, 8))
        report = pack_mipmaps.write_pack(self.pack, dry_run=True)
        self.assertEqual(report['levels_written'], 3)
        self.assertFalse((self.pack / 'tex1_4x4_03_14_mip1.png').exists())


if __name__ == '__main__':
    unittest.main()
