"""Shot alignment: offset/rate recovery on synthetic sequences, weak on junk."""
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import gamecube_shot_align as align

W, H = 48, 36
# Long enough to separate adjacent fine rates with margin: a 0.02
# rate error shifts frame i by one only past i=25, so short sequences
# tie adjacent rates (rounding absorbs them) and correctly report
# WEAK. Real trial sequences run to hundreds of frames.
N = 60


def paint_frame(index):
    """Unique frame: indexed tint plus a bright bar swept by the index.

    Every frame must differ from every other (no periodicity), or the
    true alignment ties with shifted/rate-warped impostors -- the same
    reason static real footage reports WEAK.
    """
    buf = bytearray(W * H * 3)
    bar_x = (index * 3) % (W - 4)
    # Small per-frame drift like real footage: adjacent frames stay
    # close (rate-warped pairs still match) while distant frames differ.
    tint = (index * 3) % 256
    for y in range(H):
        for x in range(W):
            if bar_x <= x < bar_x + 4:
                r, g, b = 250, 30, 30
            else:
                r, g, b = (x * 5 + tint) % 256, (y * 7) % 256, \
                    (x + y + index) % 256
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


def make_seq(count=N, start=0):
    coarse, fine = [], []
    for i in range(start, start + count):
        rgb = paint_frame(i)
        coarse.append(align.thumbnail(W, H, rgb,
                                      tw=align.COARSE_W, th=align.COARSE_H))
        fine.append(align.thumbnail(W, H, rgb))
    return coarse, fine


def run_align(seq_a, seq_b, **kwargs):
    return align.align(seq_a[0], seq_b[0], seq_a[1], seq_b[1], **kwargs)


class ShotAlignTests(unittest.TestCase):
    def test_self_alignment(self):
        seq = make_seq()
        result = run_align(seq, seq)
        self.assertEqual(result['offset'], 0)
        self.assertAlmostEqual(result['rate'], 1.0)
        self.assertAlmostEqual(result['residual'], 0.0)
        self.assertTrue(result['confident'])

    def test_shift_recovery(self):
        # B starts at A[3]: offset is in A-coordinates.
        result = run_align(make_seq(), make_seq(N - 3, start=3))
        self.assertEqual(result['offset'], 3)
        self.assertAlmostEqual(result['rate'], 1.0)
        self.assertTrue(result['confident'])

    def test_rate_recovery(self):
        # B runs at half the frame rate of A.
        seq = make_seq()
        half = (seq[0][::2], seq[1][::2])
        result = run_align(seq, half)
        self.assertAlmostEqual(result['rate'], 0.5)
        self.assertEqual(result['offset'], 0)
        self.assertTrue(result['confident'])

    def test_unrelated_is_weak(self):
        flat = lambda v, n: [bytes([v]) * n] * N
        n8 = align.COARSE_W * align.COARSE_H * 3
        n16 = align.THUMB_W * align.THUMB_H * 3
        result = run_align((flat(200, n8), flat(200, n16)),
                           (flat(20, n8), flat(20, n16)))
        self.assertGreater(result['residual'], align.CONFIDENT_SAD)
        self.assertFalse(result['confident'])

    def test_static_reports_weak(self):
        # Identical frames align at any offset: ties break to identity
        # but the zero margin reports WEAK.
        flat = lambda v, n: [bytes([v]) * n] * N
        n8 = align.COARSE_W * align.COARSE_H * 3
        n16 = align.THUMB_W * align.THUMB_H * 3
        seq = (flat(128, n8), flat(128, n16))
        result = run_align(seq, seq)
        self.assertEqual(result['offset'], 0)
        self.assertAlmostEqual(result['rate'], 1.0)
        self.assertFalse(result['confident'])

    def test_load_sequence_reads_png_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(4):
                write_png(Path(tmp) / f'shot-{i:02d}.png', W, H,
                          paint_frame(i))
            coarse, fine, names = align.load_sequence(tmp)
        self.assertEqual(len(fine), 4)
        self.assertEqual(names, sorted(names))
        self.assertEqual(len(fine[0]), align.THUMB_W * align.THUMB_H * 3)
        self.assertEqual(len(coarse[0]),
                         align.COARSE_W * align.COARSE_H * 3)


if __name__ == '__main__':
    unittest.main()
