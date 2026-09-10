import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from inspect_disc import Region, iso_files  # noqa: E402
from relocate_archive import build, directory_records, rewritten_record  # noqa: E402

SECTOR = 2048


def record(name, extent, size, directory=False):
    name = name.encode('ascii')
    body = bytearray(33 + len(name))
    body[1] = 0
    struct.pack_into('<I', body, 2, extent)
    struct.pack_into('>I', body, 6, extent)
    struct.pack_into('<I', body, 10, size)
    struct.pack_into('>I', body, 14, size)
    body[25] = 2 if directory else 0
    struct.pack_into('<H', body, 28, 1)
    struct.pack_into('>H', body, 30, 1)
    body[32] = len(name)
    body[33:] = name
    if len(body) % 2:
        body.append(0)
    body[0] = len(body)
    return bytes(body)


def synthetic_iso():
    """Sectors: 16 PVD, 17 terminator, 18 root directory, 20-21 PAD0.000, 22 WORLD.BIG."""
    sectors = 24
    image = bytearray(sectors * SECTOR)
    root = record('\0', 18, SECTOR, True) + record('\1', 18, SECTOR, True)
    root += record('PAD0.000;1', 20, 2 * SECTOR) + record('WORLD.BIG;1', 22, 700) + record('OTHER.TXT;1', 23, 5)
    image[18 * SECTOR:18 * SECTOR + len(root)] = root
    pvd = bytearray(SECTOR)
    pvd[:7] = b'\x01CD001\x01'
    pvd[40:72] = b'TEST'.ljust(32)
    struct.pack_into('<H', pvd, 128, SECTOR)
    struct.pack_into('>H', pvd, 130, SECTOR)
    root_rec = record('\0', 18, SECTOR, True)
    pvd[156:156 + len(root_rec)] = root_rec
    image[16 * SECTOR:17 * SECTOR] = pvd
    image[17 * SECTOR] = 255
    image[17 * SECTOR + 1:17 * SECTOR + 6] = b'CD001'
    image[20 * SECTOR:22 * SECTOR] = b'\xaa' * (2 * SECTOR)
    image[22 * SECTOR:22 * SECTOR + 700] = (bytes(range(256)) * 3)[:700]
    image[23 * SECTOR:23 * SECTOR + 5] = b'hello'
    return bytes(image)


class RelocateTests(unittest.TestCase):
    def test_records_and_rewrite(self):
        image = synthetic_iso()
        with tempfile.TemporaryDirectory() as tmp:
            iso = Path(tmp) / 'test.iso'
            iso.write_bytes(image)
            with iso.open('rb') as f:
                region = Region(f, 0, len(image))
                _, files = iso_files(region)
                records = directory_records(region)
            self.assertEqual({f['path'] for f in files}, {'PAD0.000', 'WORLD.BIG', 'OTHER.TXT'})
            offset, rec = records['WORLD.BIG']
            self.assertEqual(int.from_bytes(rec[2:6], 'little'), 22)
            new = rewritten_record(rec, 20, 1000)
            self.assertEqual(struct.unpack_from('<I', new, 2)[0], 20)
            self.assertEqual(struct.unpack_from('>I', new, 6)[0], 20)
            self.assertEqual(struct.unpack_from('<I', new, 10)[0], 1000)
            self.assertEqual(struct.unpack_from('>I', new, 14)[0], 1000)
            self.assertEqual(new[18:], rec[18:])

    def test_build_relocates_into_padding(self):
        image = synthetic_iso()
        archive = bytes(range(200, 256)) * 30  # 1680 bytes, larger than the original 700
        with tempfile.TemporaryDirectory() as tmp:
            iso, arc, out = Path(tmp) / 'test.iso', Path(tmp) / 'WORLD.BIG', Path(tmp) / 'out'
            iso.write_bytes(image)
            arc.write_bytes(archive)
            build(iso, arc, out, 'WORLD.BIG', 'PAD0.000')
            result = (out / 'SSX3-relocated.iso').read_bytes()
            self.assertEqual(len(result), len(image))
            self.assertEqual(result[20 * SECTOR:20 * SECTOR + len(archive)], archive)
            with (out / 'SSX3-relocated.iso').open('rb') as f:
                _, files = iso_files(Region(f, 0, len(result)))
            by_path = {f['path']: f for f in files}
            self.assertEqual(by_path['WORLD.BIG'], dict(path='WORLD.BIG', offset=20 * SECTOR, size=len(archive)))
            self.assertEqual(by_path['PAD0.000'], dict(path='PAD0.000', offset=20 * SECTOR, size=2 * SECTOR))
            self.assertEqual(by_path['OTHER.TXT']['offset'], 23 * SECTOR)
            # Everything outside the record and the padding target is untouched.
            changed = [i for i in range(len(image)) if image[i] != result[i]]
            self.assertTrue(all(20 * SECTOR <= i < 20 * SECTOR + len(archive) or 18 * SECTOR <= i < 19 * SECTOR for i in changed))
            self.assertEqual(image[22 * SECTOR:23 * SECTOR], result[22 * SECTOR:23 * SECTOR])
            self.assertTrue((out / 'image.json').exists())

    def test_build_refuses_oversized_archive(self):
        image = synthetic_iso()
        with tempfile.TemporaryDirectory() as tmp:
            iso, arc, out = Path(tmp) / 'test.iso', Path(tmp) / 'WORLD.BIG', Path(tmp) / 'out'
            iso.write_bytes(image)
            arc.write_bytes(b'x' * (2 * SECTOR + 1))
            with self.assertRaises(ValueError):
                build(iso, arc, out, 'WORLD.BIG', 'PAD0.000')
            self.assertFalse((out / 'SSX3-relocated.iso').exists())


if __name__ == '__main__':
    unittest.main()
