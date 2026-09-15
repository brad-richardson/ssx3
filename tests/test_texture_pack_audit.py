"""The pack audit flags what a model got wrong and leaves legitimate gains alone."""
import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import texture_pack_audit as audit

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:  # pragma: no cover
    HAVE_PIL = False


@unittest.skipUnless(HAVE_PIL, 'Pillow is required')
class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.source = Path(self.tmp.name) / 'source'
        self.pack = Path(self.tmp.name) / 'pack'
        self.source.mkdir()
        self.pack.mkdir()
        random.seed(11)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, directory, name, image):
        path = directory / name
        image.save(path)
        return path

    def noisy_texture(self, size=16):
        """Something with real structure, so the source is not flat."""
        image = Image.new('RGBA', (size, size))
        for y in range(size):
            for x in range(size):
                value = random.randrange(256)
                image.putpixel((x, y), (value, value // 2, 255 - value, 255))
        return image

    def nearest(self, image, scale=4):
        return image.resize((image.width * scale, image.height * scale), Image.NEAREST)

    def measure(self, name, source, packed):
        s = self.write(self.source, name, source)
        p = self.write(self.pack, name, packed)
        return audit.measure(s, p)

    def test_a_faithful_upscale_is_not_flagged(self):
        source = self.noisy_texture()
        result = self.measure('tex1_16x16_00_14.png', source, self.nearest(source))
        self.assertEqual(result['flags'], [])
        self.assertEqual(result['scale'], 4)
        self.assertAlmostEqual(result['rms'], 0.0, places=6)

    def test_a_brightened_upscale_is_a_colour_shift(self):
        source = self.noisy_texture()
        packed = self.nearest(source).point(lambda v: min(255, v + 20))
        result = self.measure('tex1_16x16_01_14.png', source, packed)
        self.assertIn('colour-shift', result['flags'])
        self.assertGreater(result['max_bias'], audit.COLOUR_SHIFT)

    def test_moved_structure_is_structure_drift(self):
        source = self.noisy_texture()
        packed = self.nearest(source).transpose(Image.FLIP_LEFT_RIGHT)
        result = self.measure('tex1_16x16_02_14.png', source, packed)
        self.assertIn('structure-drift', result['flags'])

    def test_a_chewed_cutout_is_alpha_drift(self):
        source = Image.new('RGBA', (16, 16), (200, 30, 30, 0))
        for y in range(4, 12):
            for x in range(4, 12):
                source.putpixel((x, y), (200, 30, 30, 255))
        packed = self.nearest(source)
        for y in range(packed.height):
            for x in range(packed.width):
                r, g, b, a = packed.getpixel((x, y))
                packed.putpixel((x, y), (r, g, b, 255 if a else 0) if x % 8 else (r, g, b, 0))
        result = self.measure('tex1_16x16_03_5.png', source, packed)
        self.assertIn('alpha-drift', result['flags'])

    def test_grain_added_to_a_flat_fill_is_flat_invention(self):
        source = Image.new('RGBA', (16, 16), (40, 40, 40, 255))
        packed = self.nearest(source)
        for y in range(packed.height):
            for x in range(packed.width):
                jitter = random.randrange(-25, 26)
                value = max(0, min(255, 40 + jitter))
                packed.putpixel((x, y), (value, value, value, 255))
        result = self.measure('tex1_16x16_04_14.png', source, packed)
        self.assertIn('flat-invention', result['flags'])
        self.assertGreater(result['invented'], audit.FLAT_INVENTION)

    def test_a_mask_carried_glyph_sheet_is_not_flat_invention(self):
        """White-on-transparent art has zero colour variance and is still real art."""
        source = Image.new('RGBA', (16, 16), (255, 255, 255, 0))
        for y in range(2, 14):
            for x in range(2, 14):
                if (x + y) % 3:
                    source.putpixel((x, y), (255, 255, 255, 255))
        packed = self.nearest(source)
        for y in range(packed.height):
            for x in range(packed.width):
                r, g, b, a = packed.getpixel((x, y))
                jitter = random.randrange(-25, 26)
                value = max(0, min(255, 255 + jitter))
                packed.putpixel((x, y), (value, value, value, a))
        result = self.measure('tex1_16x16_05_8.png', source, packed)
        self.assertEqual(result['source_std'], 0.0)
        self.assertGreater(result['alpha_std'], audit.FLAT_SOURCE_STD)
        self.assertNotIn('flat-invention', result['flags'])

    def test_a_non_integer_scale_is_reported_rather_than_measured(self):
        source = self.noisy_texture()
        packed = source.resize((source.width * 3, source.height * 4), Image.NEAREST)
        result = self.measure('tex1_16x16_06_14.png', source, packed)
        self.assertEqual(result['flags'], ['scale-mismatch'])
        self.assertNotIn('rms', result)

    def test_the_report_counts_flags_and_unreplaced_textures(self):
        source = self.noisy_texture()
        self.write(self.source, 'tex1_16x16_07_14.png', source)
        self.write(self.pack, 'tex1_16x16_07_14.png', self.nearest(source))
        self.write(self.source, 'tex1_16x16_08_14.png', source)  # never replaced
        # +8 clears the colour-shift threshold without also tripping drift.
        shifted = self.nearest(source).point(lambda v: min(255, v + 8))
        self.write(self.source, 'tex1_16x16_09_14.png', source)
        self.write(self.pack, 'tex1_16x16_09_14.png', shifted)
        report = audit.audit(self.source, self.pack)
        self.assertEqual(report['textures'], 2)
        self.assertEqual(report['unreplaced'], 1)
        self.assertEqual(report['flagged'], 1)
        self.assertEqual(report['flag_counts'], {'colour-shift': 1})
        self.assertIn('tex1_16x16_08_14.png', report['missing'])

    def test_families_under_the_source_directory_are_found(self):
        family = self.source / 'block-compressed'
        family.mkdir()
        source = self.noisy_texture()
        self.write(family, 'tex1_16x16_10_14.png', source)
        self.write(self.pack, 'tex1_16x16_10_14.png', self.nearest(source))
        report = audit.audit(self.source, self.pack)
        self.assertEqual(report['textures'], 1)
        self.assertEqual(report['flagged'], 0)


if __name__ == '__main__':
    unittest.main()
