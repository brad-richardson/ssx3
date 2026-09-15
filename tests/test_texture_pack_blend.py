"""Blending an over-inventing pack back toward a faithful upscale."""

import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import texture_pack_audit as audit
import texture_pack_blend as blend

from PIL import Image


def noisy(size=32, seed=5):
    """Structured art in mid-range values.

    Kept off both ends of the range on purpose: the reference's residual
    correction is exact only where it does not have to clip, and real terrain
    art does not sit at 0 or 255 either.
    """
    rng = random.Random(seed)
    image = Image.new('RGBA', (size, size))
    for y in range(size):
        for x in range(size):
            value = 64 + rng.randrange(128)
            image.putpixel((x, y), (value, 255 - value, value // 2 + 64, 255))
    return image


def recolour_half(image, shift=56):
    """The defect: one region warmed, the other cooled, mean unchanged."""
    out = image.copy()
    pixels = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = pixels[x, y]
            delta = shift if y < out.height // 2 else -shift
            pixels[x, y] = (max(0, min(255, r + delta)), g, b, a)
    return out


class WeightTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np = np
        self.source_image = noisy()
        self.source = np.asarray(self.source_image, dtype=float)
        self.scale = 4
        self.reference = blend.faithful_reference(self.source_image, self.scale)

    def test_the_reference_reduces_back_to_its_source(self):
        reduced = audit.box_down(self.reference, self.scale)
        self.assertLess(abs(reduced - self.source).max(), 1e-6)
        self.assertAlmostEqual(blend.shift_of(self.source, reduced), 0.0, places=6)

    def test_a_faithful_pack_keeps_full_strength(self):
        packed = self.reference.copy()
        weight, shift = blend.choose_weight(self.source, self.reference, packed, self.scale)
        self.assertEqual(weight, 1.0)
        self.assertLessEqual(shift, blend.TARGET)

    def test_an_inventing_pack_is_pulled_back_under_target(self):
        packed = self.np.asarray(recolour_half(
            Image.fromarray(self.reference.round().astype('uint8'), 'RGBA')), dtype=float)
        before = blend.shift_of(self.source, audit.box_down(packed, self.scale))
        self.assertGreater(before, blend.TARGET)
        weight, after = blend.choose_weight(self.source, self.reference, packed, self.scale)
        self.assertLess(weight, 1.0)
        self.assertLessEqual(after, blend.TARGET)

    def test_alpha_is_never_blended(self):
        packed = self.reference.copy()
        packed[..., 3] = 17.0
        out = blend.blend_arrays(self.reference, packed, 0.25)
        self.assertTrue((out[..., 3] == 17.0).all())


class PackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.source = root / 'source'
        self.pack = root / 'pack'
        self.out = root / 'out'
        self.classified = root / 'classified'
        for path in (self.source, self.pack):
            path.mkdir()
        (self.classified / 'block-compressed').mkdir(parents=True)
        (self.classified / 'tile').mkdir(parents=True)

        self.bad = 'tex1_32x32_aa_14.png'
        self.good = 'tex1_32x32_bb_5.png'
        for name, offend in ((self.bad, True), (self.good, False)):
            image = noisy(seed=hash(name) % 1000)
            image.save(self.source / name)
            upscaled = Image.fromarray(
                blend.faithful_reference(image, 4).round().astype('uint8'), 'RGBA')
            (recolour_half(upscaled) if offend else upscaled).save(self.pack / name)
        # The offender is in the selected class; the other is not.
        (self.classified / 'block-compressed' / self.bad).write_bytes(
            (self.source / self.bad).read_bytes())
        (self.classified / 'tile' / self.good).write_bytes(
            (self.source / self.good).read_bytes())

    def tearDown(self):
        self.tmp.cleanup()

    def test_only_the_selected_class_is_blended(self):
        names = blend.classified_names(self.classified, {'block-compressed'})
        self.assertEqual(names, {self.bad})
        report = blend.blend_pack(self.source, self.pack, self.out, names)
        self.assertEqual(report['blended'], 1)
        self.assertEqual(report['copied'], 1)
        # Untouched class is byte-identical, so nothing outside the class moved.
        self.assertEqual((self.out / self.good).read_bytes(),
                         (self.pack / self.good).read_bytes())

    def test_the_output_is_a_complete_pack_that_now_passes_the_audit(self):
        names = blend.classified_names(self.classified, {'block-compressed'})
        blend.blend_pack(self.source, self.pack, self.out, names)
        self.assertEqual(sorted(p.name for p in self.out.glob('tex1_*.png')),
                         sorted([self.bad, self.good]))
        before = audit.measure(self.source / self.bad, self.pack / self.bad)
        after = audit.measure(self.source / self.bad, self.out / self.bad)
        self.assertIn('local-shift', before['flags'])
        self.assertNotIn('local-shift', after['flags'])


if __name__ == '__main__':
    unittest.main()
