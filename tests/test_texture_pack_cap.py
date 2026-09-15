"""Capping a pack's upscaled texture size."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import texture_pack_cap as cap

from PIL import Image


class ScaleTests(unittest.TestCase):
    def test_a_texture_within_the_cap_is_left_alone(self):
        self.assertIsNone(cap.capped_scale((128, 128), (512, 512), 512))

    def test_a_texture_over_the_cap_drops_to_the_next_power_of_two(self):
        self.assertEqual(cap.capped_scale((256, 128), (1024, 512), 512), 2)

    def test_the_floor_is_never_crossed(self):
        """A 216x368 source cannot reach 512 at 2x, and must not fall to 1x.

        Without the floor the search walks all the way down and hands back the
        guest's own art, throwing the remaster away to save memory on one
        texture.
        """
        self.assertEqual(cap.capped_scale((216, 368), (864, 1472), 512), 2)

    def test_a_texture_already_at_the_floor_is_left_alone(self):
        self.assertIsNone(cap.capped_scale((256, 256), (512, 512), 128))

    def test_the_longest_side_decides(self):
        # 64x512 at 4x is 256x2048: the height is what breaks the cap.
        self.assertEqual(cap.capped_scale((64, 512), (256, 2048), 1024), 2)

    def test_an_unparsable_name_has_no_guest_size(self):
        self.assertIsNone(cap.guest_size('notatexture.png'))
        self.assertEqual(cap.guest_size('tex1_32x16_m_abc_14.png'), (32, 16))


class PackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pack = Path(self.tmp.name) / 'pack'
        self.pack.mkdir()
        # One texture over the cap with a mip chain, one already within it.
        self.big = 'tex1_256x256_aa_14.png'
        self.small = 'tex1_64x64_bb_14.png'
        Image.new('RGBA', (1024, 1024), (10, 20, 30, 255)).save(self.pack / self.big)
        for level, side in enumerate((512, 256, 128), start=1):
            Image.new('RGBA', (side, side), (10, 20, 30, 255)).save(
                self.pack / f'tex1_256x256_aa_14_mip{level}.png')
        Image.new('RGBA', (256, 256), (40, 50, 60, 255)).save(self.pack / self.small)
        Image.new('RGBA', (128, 128), (40, 50, 60, 255)).save(
            self.pack / 'tex1_64x64_bb_14_mip1.png')

    def tearDown(self):
        self.tmp.cleanup()

    def test_capping_reduces_the_base_and_drops_its_stale_chain(self):
        report = cap.cap_pack(self.pack, 512)
        self.assertEqual(report['capped'], 1)
        self.assertEqual(report['kept'], 1)
        self.assertEqual(report['mips_removed'], 3)
        with Image.open(self.pack / self.big) as image:
            self.assertEqual(image.size, (512, 512))
        # The capped texture's chain is gone, so pack_mipmaps rebuilds it.
        self.assertFalse((self.pack / 'tex1_256x256_aa_14_mip1.png').exists())
        # The texture within the cap keeps both its base and its chain.
        with Image.open(self.pack / self.small) as image:
            self.assertEqual(image.size, (256, 256))
        self.assertTrue((self.pack / 'tex1_64x64_bb_14_mip1.png').exists())

    def test_a_dry_run_changes_nothing(self):
        before = {p.name: p.stat().st_size for p in self.pack.glob('*.png')}
        report = cap.cap_pack(self.pack, 512, dry_run=True)
        self.assertEqual(report['capped'], 1)
        after = {p.name: p.stat().st_size for p in self.pack.glob('*.png')}
        self.assertEqual(before, after)

    def test_writing_out_of_place_leaves_the_original_pack_untouched(self):
        out = Path(self.tmp.name) / 'out'
        cap.cap_pack(self.pack, 512, output_dir=out)
        with Image.open(self.pack / self.big) as image:
            self.assertEqual(image.size, (1024, 1024))
        with Image.open(out / self.big) as image:
            self.assertEqual(image.size, (512, 512))
        self.assertTrue((self.pack / 'tex1_256x256_aa_14_mip1.png').exists())
        self.assertFalse((out / 'tex1_256x256_aa_14_mip1.png').exists())
        # An untouched texture is carried across whole, chain included.
        self.assertTrue((out / self.small).exists())
        self.assertTrue((out / 'tex1_64x64_bb_14_mip1.png').exists())


if __name__ == '__main__':
    unittest.main()
