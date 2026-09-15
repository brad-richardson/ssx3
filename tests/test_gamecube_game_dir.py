"""Directory-only BIGF renames, and a staged game directory that is symlinks plus worlds."""
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from gamecube_game_dir import rename_world_members, stage, parse_world, world_members

ALIGN = 2048
TRAILER = b'L231'


def bigf(names=('data/worlds/bam.gdb', 'data/worlds/bam.gsb', 'data/worlds/bam.ghm',
                'data/worlds/bam.gsm', 'data/worlds/serial.txt'), first=256):
    """A minimal BIGF whose member data is one distinct page per entry."""
    table = bytearray()
    for i, name in enumerate(names):
        table += struct.pack('>II', first + i * ALIGN, ALIGN) + name.encode('ascii') + b'\0'
    table += TRAILER
    end = 16 + len(table)
    assert end <= first
    header = bytearray(b'BIGF' + b'\0' * 12)
    struct.pack_into('<I', header, 4, first + len(names) * ALIGN)
    struct.pack_into('>II', header, 8, len(names), end)
    data = bytes(header) + bytes(table) + bytes(first - end)
    for i in range(len(names)):
        data += bytes([i + 1]) * ALIGN
    return data


class RenameTests(unittest.TestCase):
    def test_same_length_rename_touches_only_the_name_bytes(self):
        original = bigf()
        renamed = rename_world_members(original, 'alo')
        self.assertEqual(len(renamed), len(original))
        self.assertEqual(renamed[256:], original[256:])
        self.assertEqual(struct.unpack_from('>I', renamed, 12), struct.unpack_from('>I', original, 12))
        self.assertEqual([e['path'] for e in world_members(renamed)[0]],
                         ['data/worlds/alo.gdb', 'data/worlds/alo.gsb', 'data/worlds/alo.ghm',
                          'data/worlds/alo.gsm', 'data/worlds/serial.txt'])
        self.assertEqual(sum(a != b for a, b in zip(original, renamed)), 12)

    def test_longer_rename_keeps_member_offsets_sizes_and_data(self):
        original = bigf()
        renamed = rename_world_members(original, 'alohaice')
        self.assertEqual(renamed[256:], original[256:])
        self.assertEqual([(e['offset'], e['size']) for e in world_members(renamed)[0]],
                         [(e['offset'], e['size']) for e in world_members(original)[0]])
        self.assertEqual(struct.unpack_from('>I', renamed, 12)[0],
                         struct.unpack_from('>I', original, 12)[0] + 4 * 5)
        self.assertEqual(renamed[struct.unpack_from('>I', renamed, 12)[0] - len(TRAILER):
                                 struct.unpack_from('>I', renamed, 12)[0]], TRAILER)

    def test_rename_round_trips(self):
        original = bigf()
        self.assertEqual(rename_world_members(rename_world_members(original, 'alohaice'), 'bam'), original)
        self.assertIs(rename_world_members(original, 'bam'), original)

    def test_directory_must_still_end_before_the_first_member(self):
        # This directory ends at 163, so a tight first member leaves room for
        # one more character across the four renamed names.
        original = bigf(first=168)
        self.assertEqual(rename_world_members(original, 'alod')[168:], original[168:])
        with self.assertRaises(ValueError) as caught:
            rename_world_members(original, 'alohaicejam')
        self.assertIn('basename of 4 characters', str(caught.exception))

    def test_rejects_mixed_basenames_and_unusable_names(self):
        with self.assertRaises(ValueError):
            rename_world_members(bigf(names=('data/worlds/bam.gdb', 'data/worlds/other.gsb')), 'alo')
        for name in ('', 'a/b', 'al.o', 'alo\x80', 'al oha'):
            with self.assertRaises(ValueError):
                rename_world_members(bigf(), name)

    def test_non_bigf_container_is_refused(self):
        with self.assertRaises(ValueError):
            rename_world_members(b'\xc0\xfb' + bytes(300), 'alo')


ROOT = Path(__file__).resolve().parents[1]
STOCK_WORLD = ROOT / 'local/game/gxbe69-stock/files/data/worlds/bam.big'
RIDDEN_RENAME = ROOT / 'local/research/course-redirect/ala.big'


class RealArchiveTests(unittest.TestCase):
    @unittest.skipUnless(STOCK_WORLD.exists() and RIDDEN_RENAME.exists(),
                         'stock and renamed world archives are local evidence')
    def test_reproduces_the_archive_that_rode(self):
        """ala.big is the hand-renamed archive run-ala-001 booted (docs/course-selection.md)."""
        stock = STOCK_WORLD.read_bytes()
        self.assertEqual(rename_world_members(stock, 'ala'), RIDDEN_RENAME.read_bytes())
        self.assertEqual(rename_world_members(rename_world_members(stock, 'aloha'), 'bam'), stock)


class StageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.stock = self.tmp / 'stock'
        (self.stock / 'sys').mkdir(parents=True)
        (self.stock / 'files/data/worlds').mkdir(parents=True)
        (self.stock / 'sys/main.dol').write_bytes(b'dol')
        (self.stock / 'files/data/worlds/bam.big').write_bytes(bigf())
        (self.stock / 'files/data/worlds/irrngc.dat').write_bytes(b'irr')
        self.build = self.tmp / 'build'
        self.build.mkdir()
        (self.build / 'BAM.BIG').write_bytes(bigf()[:-1] + b'\xff')

    def staged(self, worlds, **kw):
        out = self.tmp / f'game{len(list(self.tmp.iterdir()))}'
        return out, stage(out, self.stock, worlds, **kw)

    def test_stock_entries_are_links_and_the_named_world_is_installed(self):
        out, receipt = self.staged({'bam': self.build / 'BAM.BIG'})
        self.assertEqual(receipt['entries'], 3)
        self.assertTrue((out / 'sys/main.dol').is_symlink())
        self.assertTrue((out / 'files/data/worlds/irrngc.dat').is_symlink())
        world = out / 'files/data/worlds/bam.big'
        self.assertTrue(world.is_symlink())
        self.assertEqual(world.resolve(), (self.build / 'BAM.BIG').resolve())
        self.assertFalse(receipt['worlds']['bam']['members_renamed'])

    def test_a_second_basename_is_renamed_and_stock_bam_survives(self):
        out, receipt = self.staged({'alo': self.build / 'BAM.BIG'})
        added = out / 'files/data/worlds/alo.big'
        self.assertFalse(added.is_symlink())
        self.assertEqual([e['path'] for e in world_members(added.read_bytes())[0]][0],
                         'data/worlds/alo.gdb')
        self.assertTrue((out / 'files/data/worlds/bam.big').is_symlink())
        self.assertTrue(receipt['worlds']['alo']['members_renamed'])
        self.assertNotEqual(receipt['worlds']['alo']['installed_sha256'],
                            receipt['worlds']['alo']['source_sha256'])

    def test_dol_is_copied_not_linked(self):
        patched = self.tmp / 'patched.dol'
        patched.write_bytes(b'patched')
        out, receipt = self.staged({'bam': self.build / 'BAM.BIG'}, dol=patched)
        self.assertFalse((out / 'sys/main.dol').is_symlink())
        self.assertEqual((out / 'sys/main.dol').read_bytes(), b'patched')
        self.assertEqual(receipt['dol']['source'], str(patched))

    def test_world_argument_accepts_a_build_directory(self):
        self.assertEqual(parse_world(f'ALO={self.build}'), ('alo', self.build / 'BAM.BIG'))
        self.assertEqual(parse_world(str(self.build / 'BAM.BIG'))[0], 'bam')


if __name__ == '__main__':
    unittest.main()
