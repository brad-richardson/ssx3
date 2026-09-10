import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from probe_worlds import refpack  # noqa: E402
from refpack_encode import encode as greedy  # noqa: E402
from refpack_optimal import encode as optimal  # noqa: E402


class OptimalEncoderTests(unittest.TestCase):
    def round_trip(self, data, **kw):
        packed = optimal(data, **kw)
        decoded, consumed = refpack(packed)
        self.assertEqual(decoded, bytes(data))
        self.assertEqual(consumed, len(packed))
        return packed

    def test_small_and_edge_sizes(self):
        for n in (0, 1, 2, 3, 4, 5, 7, 8, 13, 112, 113, 115, 116):
            self.round_trip(bytes(range(n)))

    def test_repetitive_and_overlapping(self):
        self.round_trip(b'a' * 5000)
        self.round_trip(b'abc' * 2000)
        self.round_trip((b'x' * 1027 + b'y') * 4)

    def test_random_mixed_no_larger_than_greedy(self):
        rnd = random.Random(7)
        words = [bytes(rnd.randrange(256) for _ in range(rnd.randrange(1, 40))) for _ in range(50)]
        data = b''.join(rnd.choice(words) for _ in range(1500))
        data += bytes(rnd.randrange(256) for _ in range(2000))
        packed = self.round_trip(data)
        self.assertLessEqual(len(packed), len(greedy(data)))

    def test_long_distance_matches(self):
        rnd = random.Random(3)
        block = bytes(rnd.randrange(256) for _ in range(3000))
        data = block + bytes(rnd.randrange(256) for _ in range(20000)) + block
        packed = self.round_trip(data)
        self.assertLess(len(packed), len(data) + 100)

    def test_search_levels_agree(self):
        rnd = random.Random(11)
        data = bytes(rnd.choice(b'abcdefgh') for _ in range(6000))
        a = self.round_trip(data, candidates=16, skip_threshold=8)
        b = self.round_trip(data, candidates=256, skip_threshold=10**9)
        self.assertLessEqual(len(b), len(a))


if __name__ == '__main__':
    unittest.main()
