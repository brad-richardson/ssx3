"""Lighting transfer regression: clipping, GX tiling and quantization bounds."""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_materials import convert_lightmap, LIGHTMAP_PROFILE
from gamecube_textures import decode, world_image_record, rgb565


class MaterialTransferTests(unittest.TestCase):
    def test_every_rgb565_color_survives_transfer_with_one_code_error(self):
        source = dict(type=0x14, width=256, height=256,
                      pixels=struct.pack('>65536H', *range(65536)), palette=None)
        before = dict(source)
        converted, receipt = convert_lightmap(source)
        original = decode(source)
        actual = decode(converted)
        self.assertEqual(source, before)
        self.assertEqual(receipt['profile'], LIGHTMAP_PROFILE)
        self.assertEqual(receipt['max_reconstructed_channel_error'], 1)
        for src, dst in zip(original, actual):
            self.assertEqual(dst[3], 255)
            for s, d in zip(src[:3], dst[:3]):
                self.assertLessEqual(abs(s - min(255, 2 * d)), 1)
        payload = world_image_record(converted)
        self.assertEqual(payload[0], 0x16)
        self.assertEqual(payload[32:], converted['pixels'])

    def test_rgba8_planes_and_tiles_match_gx_layout(self):
        # Two adjacent tiles with distinct R/G/B values catch plane/tile swaps.
        source = dict(type=0x14, width=8, height=4,
                      pixels=struct.pack('>32H', *([0xf800] * 16 + [0x07ff] * 16)), palette=None)
        converted, _ = convert_lightmap(source)
        self.assertEqual(converted['pixels'],
                         bytes([255, 128]) * 16 + bytes([0, 0]) * 16 +
                         bytes([255, 0]) * 16 + bytes([128, 128]) * 16)
        pixels = decode(converted)
        for y in range(4):
            self.assertEqual(pixels[y * 8:y * 8 + 8],
                             [(128, 0, 0, 255)] * 4 + [(0, 128, 128, 255)] * 4)

    def test_snow_detail_does_not_clip_under_target_scale(self):
        source = dict(type=0x14, width=4, height=4,
                      pixels=struct.pack('>16H', *([0xad55] * 16)), palette=None)
        converted, _ = convert_lightmap(source)
        src, dst = decode(source)[0], decode(converted)[0]
        for s, d in zip(src[:3], dst[:3]):
            reference = 230 * s / 255
            old = min(255, 2 * reference)
            corrected = min(255, 230 * d / 255 * 2)
            self.assertEqual(old, 255)
            self.assertLess(abs(reference - corrected), 1)
            self.assertLess(corrected, 180)

    def test_gx_rgb565_expands_by_bit_replication(self):
        self.assertEqual(rgb565((4 << 11) | (16 << 5) | 4), (33, 65, 33, 255))

    def test_raw_control_and_unverified_formats(self):
        source = dict(type=0x14, width=4, height=4, pixels=bytes(32), palette=None)
        raw, receipt = convert_lightmap(source, 'raw')
        self.assertEqual(raw, source)
        self.assertFalse(receipt['converted'])
        converted, _ = convert_lightmap(source)
        for image in (converted, dict(source, type=0x1e), dict(source, width=3),
                      dict(source, pixels=bytes(31))):
            with self.assertRaises(ValueError):
                convert_lightmap(image)
        with self.assertRaises(ValueError):
            convert_lightmap(source, 'guess')


if __name__ == '__main__':
    unittest.main()
