"""Foliage rework: the silhouette may lose area, never gain it."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import foliage_detail as foliage

try:
    from PIL import Image
    import numpy as np
    HAVE_PIL = True
except ImportError:  # pragma: no cover
    HAVE_PIL = False


@unittest.skipUnless(HAVE_PIL, 'Pillow and numpy are required')
class CoverageTests(unittest.TestCase):
    def test_the_threshold_matches_a_wanted_coverage(self):
        alpha = np.linspace(0, 255, 256).reshape(16, 16)
        cut = foliage.coverage_threshold(alpha, 0.5)
        self.assertAlmostEqual(float((alpha >= cut).mean()), 0.5, delta=0.02)

    def test_distance_grows_inward(self):
        mask = np.zeros((16, 16), dtype=bool)
        mask[4:12, 4:12] = True
        distance = foliage.distance_inside(mask)
        self.assertEqual(distance[0, 0], 0)          # outside
        self.assertEqual(distance[4, 4], 1)          # on the edge
        self.assertGreater(distance[7, 7], distance[5, 5])

    def test_thickness_separates_a_canopy_from_a_twig(self):
        canopy = np.zeros((32, 32), dtype=bool); canopy[8:24, 8:24] = True
        twig = np.zeros((32, 32), dtype=bool); twig[:, 15:17] = True
        self.assertGreater(foliage.thickness(canopy, reach=6)[16, 16],
                           foliage.thickness(twig, reach=6)[16, 16])


@unittest.skipUnless(HAVE_PIL, 'Pillow and numpy are required')
class ReworkTests(unittest.TestCase):
    def card(self, size=32, solid=True):
        """A dense canopy blob, or a two-pixel twig."""
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        pixels = image.load()
        for y in range(size):
            for x in range(size):
                inside = (abs(x - size // 2) < size // 4 and abs(y - size // 2) < size // 4
                          if solid else abs(x - size // 2) < 1)
                if inside:
                    shade = 80 + 60 * ((x + y) % 3)
                    pixels[x, y] = (30, shade, 40, 255)
        return image

    def upscaled(self, source, scale=4, grow=2):
        """Stand in for the model: scaled up and fattened, as the model does."""
        big = source.resize((source.width * scale, source.height * scale), Image.LANCZOS)
        alpha = np.asarray(big.getchannel('A'), dtype=float)
        grown = np.clip(alpha + grow * 40, 0, 255)
        out = np.asarray(big, dtype=float).copy()
        out[..., 3] = grown
        return Image.fromarray(out.astype('uint8'), 'RGBA')

    def coverage(self, image):
        return float((np.asarray(image.convert('RGBA'))[..., 3] >= 128).mean())

    def test_coverage_returns_to_the_source(self):
        source = self.card()
        fat = self.upscaled(source)
        self.assertGreater(self.coverage(fat), self.coverage(source) + 0.01)
        fixed = foliage.rework(fat, source, fringe=0.0, depth=0.0)
        self.assertAlmostEqual(self.coverage(fixed), self.coverage(source), delta=0.01)

    def test_the_fringe_only_removes_area(self):
        source = self.card()
        fixed = foliage.rework(self.upscaled(source), source, fringe=0.5, depth=0.0)
        self.assertLessEqual(self.coverage(fixed), self.coverage(source) + 0.005)

    def test_a_twig_card_keeps_its_area(self):
        """Thin cards are protected: opening their outline would delete them."""
        source = self.card(solid=False)
        fixed = foliage.rework(self.upscaled(source), source, fringe=0.8, depth=0.2)
        self.assertAlmostEqual(self.coverage(fixed), self.coverage(source), delta=0.01)

    def test_depth_keeps_the_mean_brightness(self):
        source = self.card()
        fat = self.upscaled(source)
        fixed = foliage.rework(fat, source, fringe=0.0, depth=0.3)
        def mean(image):
            a = np.asarray(image.convert('RGBA'), dtype=float)
            visible = a[..., 3] >= 128
            return float(a[..., :3][visible].mean())
        self.assertAlmostEqual(mean(fixed), mean(fat), delta=6.0)

    def test_hidden_pixels_keep_a_colour(self):
        source = self.card()
        fixed = foliage.rework(self.upscaled(source), source, fringe=0.5, depth=0.1)
        a = np.asarray(fixed, dtype=float)
        hidden = a[..., 3] < 128
        self.assertTrue(hidden.any())
        # Whatever leaks past an alpha test must not be black.
        self.assertGreater(a[..., :3][hidden].max(), 20)


if __name__ == '__main__':
    unittest.main()
