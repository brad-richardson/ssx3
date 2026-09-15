"""Class routing: each texture goes to the model its own shape calls for."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import texture_pack_plan as plan

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:  # pragma: no cover
    HAVE_PIL = False


class FormatTests(unittest.TestCase):
    def test_the_format_is_the_last_field_of_the_name(self):
        self.assertEqual(plan.texture_format('tex1_128x128_m_abc_14.png'), 14)
        self.assertEqual(plan.texture_format('tex1_64x64_m_abc_def_9.png'), 9)
        self.assertEqual(plan.texture_format('not-a-texture.png'), -1)


@unittest.skipUnless(HAVE_PIL, 'Pillow is required')
class ClassifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, image):
        path = self.dir / name
        image.save(path)
        return path

    def photo(self, size=32, seed=3):
        """Detail on a ramp: like a photographic texture, it does not wrap.

        Pure noise would not do - noise is statistically seamless, so the tile
        detector would (correctly) call it a tile.
        """
        import random
        random.seed(seed)
        image = Image.new('RGBA', (size, size))
        for y in range(size):
            for x in range(size):
                v = int(20 + 200 * x / (size - 1)) + random.randrange(-12, 13)
                v = max(0, min(255, v))
                image.putpixel((x, y), (v, v // 2, 255 - v, 255))
        return image

    def test_a_flat_fill_is_flat(self):
        klass, _ = plan.classify(self.write('tex1_16x16_00_14.png',
                                            Image.new('RGBA', (16, 16), (7, 7, 7, 255))))
        self.assertEqual(klass, 'flat')

    def test_a_soft_gradient_sprite_is_a_soft_sprite(self):
        image = Image.new('RGBA', (32, 32))
        for y in range(32):
            for x in range(32):
                r = ((x - 16) ** 2 + (y - 16) ** 2) ** 0.5
                alpha = max(0, min(255, int(255 - r * 14)))
                image.putpixel((x, y), (240, 240, 255, alpha))
        klass, measures = plan.classify(self.write('tex1_32x32_01_5.png', image))
        self.assertEqual(klass, 'soft-sprite')
        self.assertGreater(measures['partial_alpha'], plan.SOFT_ALPHA_FRACTION)

    def test_a_wrapping_texture_is_a_tile(self):
        """A tile's left edge continues into its right edge."""
        import math
        image = Image.new('RGBA', (32, 32))
        for y in range(32):
            for x in range(32):
                v = int(128 + 100 * math.sin(2 * math.pi * x / 32) * math.cos(2 * math.pi * y / 32))
                image.putpixel((x, y), (v, v, v, 255))
        klass, measures = plan.classify(self.write('tex1_32x32_02_14.png', image))
        self.assertEqual(klass, 'tile')
        self.assertTrue(measures['tiles'])

    def test_non_tiling_cmpr_is_block_compressed(self):
        klass, measures = plan.classify(self.write('tex1_32x32_03_14.png', self.photo()))
        self.assertEqual(klass, 'block-compressed')
        self.assertFalse(measures['tiles'])

    def test_non_tiling_paletted_art_is_paletted(self):
        klass, _ = plan.classify(self.write('tex1_32x32_04_9.png', self.photo(seed=9)))
        self.assertEqual(klass, 'paletted')

    def test_anything_else_is_direct_colour(self):
        klass, _ = plan.classify(self.write('tex1_32x32_05_5.png', self.photo(seed=11)))
        self.assertEqual(klass, 'direct-colour')

    def test_every_class_names_a_model_and_a_wrap_mode(self):
        for name, choice in plan.MODELS.items():
            self.assertIn(choice['mode'], ('model', 'lanczos'), name)
            self.assertIn(choice['wrap'], ('auto', 'always', 'never'), name)
            if choice['mode'] == 'model':
                self.assertTrue(choice['model'], name)

    def test_the_plan_copies_each_texture_into_its_class(self):
        self.write('tex1_16x16_06_14.png', Image.new('RGBA', (16, 16), (7, 7, 7, 255)))
        self.write('tex1_32x32_07_14.png', self.photo(seed=5))
        out = self.dir / 'plan'
        report = plan.plan(self.dir, out)
        self.assertEqual(report['textures'], 2)
        self.assertEqual(report['classes'], {'flat': 1, 'block-compressed': 1})
        self.assertTrue((out / 'flat/tex1_16x16_06_14.png').is_file())
        self.assertTrue((out / 'block-compressed/tex1_32x32_07_14.png').is_file())
        self.assertIn('flat', report['models'])

    def test_mip_sidecars_are_not_planned(self):
        self.write('tex1_32x32_08_14.png', self.photo(seed=7))
        self.write('tex1_32x32_08_14_mip1.png', self.photo(size=16, seed=7))
        report = plan.plan(self.dir, self.dir / 'plan2')
        self.assertEqual(report['textures'], 1)


if __name__ == '__main__':
    unittest.main()
