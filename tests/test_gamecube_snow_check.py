"""Ground/snow scorer: corruption signature fires, clean snow passes."""
import struct
import sys
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import gamecube_snow_check as snow

W = H = 100
BAND_X = range(25, 75, 2)
BAND_Y = range(55, 90, 2)


def paint_frame(paint):
    buf = bytearray(W * H * 3)
    for y in range(H):
        for x in range(W):
            r, g, b = paint(x, y)
            i = (y * W + x) * 3
            buf[i:i + 3] = bytes((r, g, b))
    return bytes(buf)


def write_png(path, width, height, rgb):
    def chunk(kind, payload):
        return (struct.pack('>I', len(payload)) + kind + payload +
                struct.pack('>I', zlib.crc32(kind + payload)))
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw += rgb[y * width * 3:(y + 1) * width * 3]
    Path(path).write_bytes(
        b'\x89PNG\r\n\x1a\n' +
        chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) +
        chunk(b'IDAT', zlib.compress(bytes(raw))) + chunk(b'IEND', b''))


def write_png_rgba(path, width, height, rgba):
    def chunk(kind, payload):
        return (struct.pack('>I', len(payload)) + kind + payload +
                struct.pack('>I', zlib.crc32(kind + payload)))
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw += rgba[y * width * 4:(y + 1) * width * 4]
    Path(path).write_bytes(
        b'\x89PNG\r\n\x1a\n' +
        chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)) +
        chunk(b'IDAT', zlib.compress(bytes(raw))) + chunk(b'IEND', b''))


class SnowCheckTests(unittest.TestCase):
    def test_region_geometry_locked(self):
        self.assertEqual((snow.REGION_X, snow.REGION_Y, snow.STRIDE),
                         ((0.25, 0.75), (0.55, 0.90), 2))
        self.assertEqual(snow.CORRUPT_THRESHOLD, 0.12)

    def test_classify_pixel(self):
        ok = snow.classify_pixel
        self.assertEqual(ok(235, 240, 248), 'ok')  # sunlit snow
        self.assertEqual(ok(90, 110, 170), 'ok')  # blue shadow
        self.assertEqual(ok(30, 60, 255), 'ok')  # saturated blue tape
        self.assertEqual(ok(150, 120, 200), 'ok')  # purple tint, low sat
        self.assertEqual(ok(5, 5, 8), 'black')
        self.assertEqual(ok(19, 19, 19), 'black')
        self.assertEqual(ok(20, 20, 20), 'ok')
        self.assertEqual(ok(20, 230, 30), 'psychedelic')  # green garbage
        self.assertEqual(ok(230, 20, 30), 'psychedelic')  # red garbage
        self.assertEqual(ok(250, 150, 20), 'psychedelic')  # orange streak
        self.assertEqual(ok(255, 120, 200), 'psychedelic')  # red-dominant

    def test_clean_snow_frame_passes(self):
        def paint(x, y):
            if (x, y) in ((0, 0), (99, 99), (0, 99), (99, 0)):
                return (0, 255, 0)  # out-of-band garbage must not count
            if 40 <= x <= 44:
                return (30, 60, 255)  # blue course tape inside band
            if 80 <= y <= 84:
                return (140, 155, 200)  # tree shadow
            if 48 <= x <= 52 and 60 <= y <= 70:
                return (10, 10, 12)  # dark rider suit
            if (x * y) % 37 == 0:
                return (8, 8, 10)  # sparse dark speckles
            v = (x + y) % 5
            return (225 + v, 232 + v, 242 - v)
        result = snow.score_pixels(W, H, paint_frame(paint))
        self.assertEqual(result['verdict'], 'clean')
        self.assertLess(result['corrupt'], 0.08)

    def test_black_ground_fires(self):
        def paint(x, y):
            if x in BAND_X and y in BAND_Y and (x + y) % 5:
                return (5, 5, 8)
            return (225, 232, 242)
        result = snow.score_pixels(W, H, paint_frame(paint))
        self.assertEqual(result['verdict'], 'corrupt')
        self.assertGreater(result['black'], 0.5)

    def test_psychedelic_ground_fires(self):
        def paint(x, y):
            if x in BAND_X and y in BAND_Y and (x + y) % 3:
                return (20, 230, 30) if (x // 2) % 2 else (230, 20, 30)
            return (225, 232, 242)
        result = snow.score_pixels(W, H, paint_frame(paint))
        self.assertEqual(result['verdict'], 'corrupt')
        self.assertGreater(result['psychedelic'], 0.3)

    def test_orange_streak_fires(self):
        def paint(x, y):
            if x in BAND_X and y in BAND_Y and y % 4 == 1:
                return (250, 150, 20)
            return (225, 232, 242)
        result = snow.score_pixels(W, H, paint_frame(paint))
        self.assertEqual(result['verdict'], 'corrupt')

    def test_threshold_separates(self):
        samples = [(x, y) for y in BAND_Y for x in BAND_X]

        def frame_with(fraction):
            dark = set(samples[:int(len(samples) * fraction)])

            def paint(x, y):
                return (5, 5, 8) if (x, y) in dark else (225, 232, 242)
            return paint_frame(paint)

        self.assertEqual(
            snow.score_pixels(W, H, frame_with(0.05))['verdict'], 'clean')
        self.assertEqual(
            snow.score_pixels(W, H, frame_with(0.30))['verdict'], 'corrupt')

    def test_png_round_trip(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'frame.png'
            rgb = paint_frame(lambda x, y: ((x * 3) % 256, (y * 5) % 256,
                                             (x + y) % 256))
            write_png(path, W, H, rgb)
            width, height, back = snow.read_png_rgb(path)
            self.assertEqual((width, height, back), (W, H, rgb))
            rgba = bytearray()
            for i in range(0, len(rgb), 3):
                rgba += rgb[i:i + 3] + b'\xff'
            alpha_path = Path(tmp) / 'alpha.png'
            write_png_rgba(alpha_path, W, H, bytes(rgba))
            width, height, dropped = snow.read_png_rgb(alpha_path)
            self.assertEqual((width, height, dropped), (W, H, rgb))
            bad = Path(tmp) / 'bad.png'
            bad.write_bytes(b'not a png')
            with self.assertRaisesRegex(ValueError, 'not a PNG'):
                snow.read_png_rgb(bad)

    def test_cli_exit_codes(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            clean = paint_frame(lambda x, y: (225, 232, 242))
            dirty = paint_frame(
                lambda x, y: (5, 5, 8)
                if x in BAND_X and y in BAND_Y else (225, 232, 242))
            write_png(root / 'clean.png', W, H, clean)
            write_png(root / 'dirty.png', W, H, dirty)
            self.assertEqual(snow.main([str(root / 'clean.png')]), 0)
            self.assertEqual(snow.main([str(root / 'dirty.png')]), 1)
            self.assertEqual(snow.main([str(root)]), 1)
