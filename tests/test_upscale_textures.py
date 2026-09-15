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


@unittest.skipUnless(HAVE_PIL, 'Pillow is required')
class WrapTests(unittest.TestCase):
    """A tile has to stay tileable, or every tile boundary shows a line in game."""

    def tile(self, size=16):
        import math
        image = Image.new('RGBA', (size, size))
        for y in range(size):
            for x in range(size):
                v = int(128 + 100 * math.sin(2 * math.pi * x / size)
                        * math.cos(2 * math.pi * y / size))
                image.putpixel((x, y), (v, v, v, 255))
        return image

    def ramp(self, size=16):
        image = Image.new('RGBA', (size, size))
        for y in range(size):
            for x in range(size):
                v = int(10 + 230 * x / (size - 1))
                image.putpixel((x, y), (v, v, v, 255))
        return image

    def seam(self, image):
        import numpy as np
        a = np.asarray(image.convert('RGB'), dtype=float)
        grey = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
        interior = np.abs(np.diff(grey, axis=1)).mean()
        return np.abs(grey[:, 0] - grey[:, -1]).mean() / max(interior, 1e-6)

    def test_a_tile_is_recognised_and_a_ramp_is_not(self):
        from upscale_textures import tileable
        self.assertTrue(tileable(self.tile()))
        self.assertFalse(tileable(self.ramp()))

    def test_a_flat_image_is_not_called_a_tile(self):
        from upscale_textures import tileable
        self.assertFalse(tileable(Image.new('RGBA', (16, 16), (5, 5, 5, 255))))

    def test_padding_may_be_wider_than_the_texture(self):
        from upscale_textures import wrap_pad
        padded = wrap_pad(self.tile(8), 20)
        self.assertEqual(padded.size, (48, 48))
        # column 20 of the padding is column 0 of the source, by periodicity
        self.assertEqual(padded.getpixel((20, 20)), self.tile(8).getpixel((0, 0)))

    def test_wrapping_keeps_a_tile_seamless_where_plain_scaling_does_not(self):
        from upscale_textures import upscale
        tile = self.tile(32)
        plain = upscale(tile, None, 4, 'cpu')
        wrapped = upscale(tile, None, 4, 'cpu', wrap=True)
        self.assertEqual(wrapped.size, (128, 128))
        self.assertLess(self.seam(wrapped), self.seam(plain))


@unittest.skipUnless(HAVE_PIL, 'Pillow is required')
class CutoutTests(unittest.TestCase):
    """What the guest's alpha test does to a scaled cutout."""

    def cutout(self, size=16):
        """A hard-edged shape whose hidden pixels are black, as a dump's are."""
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        for y in range(size // 4, size - size // 4):
            for x in range(size // 4, size - size // 4):
                image.putpixel((x, y), (200, 180, 120, 255))
        return image

    def test_a_hard_cutout_is_detected_and_a_soft_sprite_is_not(self):
        from upscale_textures import binary_alpha
        self.assertTrue(binary_alpha(self.cutout()))
        soft = Image.new('RGBA', (16, 16))
        for y in range(16):
            for x in range(16):
                soft.putpixel((x, y), (255, 255, 255, min(255, x * 16)))
        self.assertFalse(binary_alpha(soft))

    def test_an_opaque_image_is_not_a_cutout(self):
        from upscale_textures import binary_alpha
        self.assertFalse(binary_alpha(Image.new('RGBA', (8, 8), (1, 2, 3, 255))))

    def test_a_scaled_cutout_keeps_a_hard_edge(self):
        from upscale_textures import upscale
        out = upscale(self.cutout(), None, 4, 'cpu')
        band = out.getchannel('A')
        band.load()
        alpha = {band.getpixel((x, y)) for y in range(band.height)
                 for x in range(band.width)}
        self.assertEqual(alpha, {0, 255})

    def test_every_hidden_pixel_carries_the_art_s_colour(self):
        """So a pixel that leaks past an alpha test is not black."""
        from upscale_textures import opaque_fill
        filled = opaque_fill(self.cutout(32))
        data = filled.load()
        for point in ((0, 0), (31, 31), (0, 31), (16, 0)):
            self.assertEqual(data[point][3], 0)
            self.assertGreater(max(data[point][:3]), 50, point)


@unittest.skipUnless(HAVE_PIL, 'Pillow is required')
class ColourTests(unittest.TestCase):
    """The model may add detail; it may not change the art's colour."""

    def source(self):
        image = Image.new('RGBA', (8, 8), (200, 150, 100, 255))
        for x in range(8):
            image.putpixel((x, 0), (120, 90, 60, 255))
        return image

    def test_a_darkened_result_is_brought_back(self):
        from upscale_textures import match_colour
        source = self.source()
        darker = source.resize((32, 32), Image.NEAREST).point(lambda v: int(v * 0.8))
        fixed = match_colour(darker, source)
        import numpy as np
        want = np.asarray(source, float)[..., :3].mean(axis=(0, 1))
        got = np.asarray(fixed, float)[..., :3].mean(axis=(0, 1))
        for channel in range(3):
            self.assertAlmostEqual(got[channel], want[channel], delta=1.5)

    def test_detail_survives_the_correction(self):
        from upscale_textures import match_colour
        source = self.source()
        scaled = source.resize((32, 32), Image.NEAREST).point(lambda v: int(v * 0.8))
        fixed = match_colour(scaled, source)
        # the bright/dark split the source has is still there
        self.assertGreater(fixed.getpixel((16, 16))[0], fixed.getpixel((16, 1))[0])

    def test_transparent_pixels_do_not_drive_the_mean(self):
        from upscale_textures import match_colour
        source = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
        for y in range(4, 8):
            for x in range(8):
                source.putpixel((x, y), (200, 200, 200, 255))
        scaled = source.resize((32, 32), Image.NEAREST).point(lambda v: int(v * 0.5))
        fixed = match_colour(scaled, source)
        self.assertGreater(fixed.getpixel((16, 24))[0], 150)
