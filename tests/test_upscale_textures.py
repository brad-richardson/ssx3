"""Alpha handling in the upscaler: the model never sees alpha, and cutouts keep their edges."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from upscale_textures import opaque_fill, upscale

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:  # pragma: no cover
    HAVE_PIL = False


@unittest.skipUnless(HAVE_PIL, 'Pillow is required')
class AlphaTests(unittest.TestCase):
    def cutout(self):
        """A red square on a transparent field whose hidden pixels are blue."""
        image = Image.new('RGBA', (8, 8), (0, 0, 255, 0))
        for y in range(2, 6):
            for x in range(2, 6):
                image.putpixel((x, y), (255, 0, 0, 255))
        return image

    def test_transparent_pixels_take_the_visible_colour(self):
        filled = opaque_fill(self.cutout())
        # The pixel just outside the square is transparent either way, but its
        # colour is now red rather than the blue that would bleed inward.
        self.assertEqual(filled.getpixel((1, 3))[:3], (255, 0, 0))
        self.assertEqual(filled.getpixel((1, 3))[3], 0)
        self.assertEqual(filled.getpixel((3, 3)), (255, 0, 0, 255))

    def test_a_fully_opaque_image_is_returned_unchanged(self):
        opaque = Image.new('RGBA', (4, 4), (1, 2, 3, 255))
        self.assertIs(opaque_fill(opaque), opaque)

    def test_lanczos_mode_scales_both_channels_and_keeps_the_cutout(self):
        out = upscale(self.cutout(), None, 4, 'cpu')
        self.assertEqual(out.size, (32, 32))
        self.assertEqual(out.mode, 'RGBA')
        # Lanczos rings on a feature this small, so assert the cutout survives
        # rather than exact values: opaque in the middle, clear in the corner.
        self.assertGreater(out.getpixel((16, 16))[3], 200)
        self.assertLess(out.getpixel((0, 0))[3], 32)
        # No blue survives anywhere visible: the fill removed the hidden colour.
        pixels = out.load()
        visible = [pixels[x, y] for y in range(out.height) for x in range(out.width)
                   if pixels[x, y][3] > 128]
        self.assertTrue(visible)
        self.assertTrue(all(p[2] < 64 for p in visible), 'hidden blue bled into the visible area')

    def test_an_rgb_image_stays_rgb(self):
        out = upscale(Image.new('RGB', (4, 4), (9, 9, 9)), None, 2, 'cpu')
        self.assertEqual((out.mode, out.size), ('RGB', (8, 8)))


if __name__ == '__main__':
    unittest.main()
