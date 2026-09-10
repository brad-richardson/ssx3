import io
import random
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from inspect_disc import Region, big_members, file_region  # noqa: E402
from probe_worlds import refpack  # noqa: E402
from relayout_stream import BLOCK, CAPACITY, pack_group, write_bigf  # noqa: E402


class RelayoutTests(unittest.TestCase):
    def test_bigf_round_trip(self):
        members = [('data/worlds/bam.sdb', b'S' * 100), ('data/worlds/bam.ssb', b'B' * 5000), ('data/worlds/serial.txt', b'x' * 128)]
        # template: a hand-built BIGF with the same member names, a version trailer, 2048-aligned members
        table = b''.join(struct.pack('>II', 0, 0) + p.encode() + b'\0' for p, _ in members) + b'L231\0'
        header = b'BIGF' + struct.pack('<I', 0) + struct.pack('>II', len(members), 16 + len(table)) + table
        template = bytearray(header + bytes(2048 - len(header)))
        pos, off = 16, 2048
        for p, d in members:
            struct.pack_into('>II', template, pos, off, len(d)); pos += 8 + len(p) + 1
            template += d + bytes((-len(d)) % 2048); off += (len(d) + 2047) // 2048 * 2048
        template = bytes(template)
        archive, offsets = write_bigf(members, template)
        self.assertEqual(struct.unpack_from('<I', archive, 4)[0], len(archive))
        self.assertEqual(archive[:16 + len(table)][16 + len(table) - 5:], b'L231\0')
        # unchanged members reproduce the template except for the unpadded tail and the size word
        self.assertEqual(archive[8:2048], template[8:2048])
        kind, parsed = big_members(Region(io.BytesIO(archive), 0, len(archive)))
        self.assertEqual(kind, 'BIGF')
        self.assertEqual([m['path'] for m in parsed], [p for p, _ in members])
        for (path, data), m, offset in zip(members, parsed, offsets):
            self.assertEqual(m['offset'], offset)
            self.assertEqual(m['offset'] % 2048, 0)
            self.assertEqual(m['size'], len(data))
            self.assertEqual(file_region(Region(io.BytesIO(archive), 0, len(archive)), parsed, path).read(0, len(data)), data)

    def test_pack_group_blocks_and_tags(self):
        rnd = random.Random(5)
        words = [bytes(rnd.randrange(256) for _ in range(rnd.randrange(4, 60))) for _ in range(300)]
        raw = b''.join(rnd.choice(words) for _ in range(6000))  # ~200 KB, moderately compressible
        index, data, count = pack_group((7, raw, 81920, 96))
        self.assertEqual(index, 7)
        self.assertEqual(len(data), count * BLOCK)
        decoded, pos = b'', 0
        for i in range(count):
            block = data[pos:pos + BLOCK]
            tag, size = struct.unpack_from('<4sI', block, 0)
            self.assertEqual(size, BLOCK)
            self.assertEqual(tag, b'CEND' if i == count - 1 else b'CBXS')
            chunk, consumed = refpack(block[8:])
            self.assertLessEqual(consumed, CAPACITY)
            self.assertLessEqual(len(chunk), 81920)
            self.assertEqual(block[8 + consumed:], bytes(CAPACITY - consumed))
            decoded += chunk
            pos += BLOCK
        self.assertEqual(decoded, raw)
        self.assertGreater(count, 1)


if __name__ == '__main__':
    unittest.main()
