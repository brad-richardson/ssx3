import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from patch_executable import RECORD, COUNT, find_table, parse_table, rename_bytes  # noqa: E402


def fake_elf():
    codes = ['ARA1', 'BRA2', 'CRA3'] + [f'X{i:03d}' for i in range(3, 17)] + ['A', 'B', 'C', 'D', 'E', 'dbg', '']
    table = bytearray()
    for i, code in enumerate(codes):
        r = bytearray(RECORD)
        struct.pack_into('<5I', r, 0, 0, 0, 0, 0, i)
        r[20:20 + len(code) * 2] = (code * 2).encode()
        r[52:52 + len(code)] = code.encode()
        r[68:68 + len(code)] = code.encode()
        r[84:87] = b'BAM'
        table += r
    return bytes(1234) + bytes(table) + bytes(500)


class PatchExecutableTests(unittest.TestCase):
    def test_find_and_rename(self):
        elf = fake_elf()
        base = find_table(elf)
        self.assertEqual(base, 1234)
        self.assertEqual(len(parse_table(elf, base)), COUNT)
        patched, edits = rename_bytes(elf, base, {'ARA1': ('Garibaldi', 'Gari'), 'A': ('Tricky Base', None)})
        self.assertEqual(len(patched), len(elf))
        t = parse_table(patched, base)
        self.assertEqual((t[0]['display'], t[0]['short'], t[0]['code']), ('Garibaldi', 'Gari', 'ARA1'))
        self.assertEqual((t[17]['display'], t[17]['short']), ('Tricky Base', 'A'))
        self.assertEqual(t[1], parse_table(elf, base)[1])
        self.assertEqual(len(edits), 3)
        # only the named fields differ
        diff = [i for i in range(len(elf)) if elf[i] != patched[i]]
        self.assertTrue(all(base <= i < base + RECORD * 18 for i in diff))
        with self.assertRaises(ValueError):
            rename_bytes(elf, base, {'ARA1': ('x' * 32, None)})
        with self.assertRaises(ValueError):
            rename_bytes(elf, base, {'ZZZZ': ('x', None)})
        with self.assertRaises(ValueError):
            find_table(bytes(5000))


if __name__ == '__main__':
    unittest.main()
