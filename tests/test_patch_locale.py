import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from patch_locale import parse_locale, replace_strings, write_patched_image


def locale(strings, hashed=True):
    base = 36 + 8 * len(strings) if hashed else 20
    data = bytearray()
    offsets = []
    for text in strings:
        offsets.append(16 + 4 * len(strings) + len(data))
        data += text.encode('utf-16le') + bytes(4)
    raw = struct.pack('<4s4I', b'LOCH', 20, 0, 1, base)
    if hashed:
        raw += struct.pack('<4s3I', b'LOCT', 16, 1234, 0)
        raw += b''.join(struct.pack('<II', 100 + i, i) for i in range(len(strings)))
    raw += struct.pack('<4s3I', b'LOCL', 16 + 4 * len(strings) + len(data), 0, len(strings))
    return raw + struct.pack(f'<{len(strings)}I', *offsets) + data


class LocaleTests(unittest.TestCase):
    def test_utf16_and_untouched_bytes(self):
        raw = locale(['Original description', 'Snow \U0001f3c2', ''])
        out, edits = replace_strings(raw, {0: 'Garibaldi'})
        self.assertEqual([e['text'] for e in parse_locale(out)], ['Garibaldi', 'Snow \U0001f3c2', ''])
        start, size = edits[0]['offset'], edits[0]['size']
        self.assertEqual(len(raw), len(out))
        self.assertEqual(raw[:start], out[:start])
        self.assertEqual(raw[start + size:], out[start + size:])
        self.assertEqual(parse_locale(out)[0]['hashes'], [100])

    def test_without_hash_table(self):
        self.assertEqual(parse_locale(locale(['text'], False))[0]['text'], 'text')

    def test_empty_string_can_occupy_two_bytes(self):
        raw = bytearray(locale([''], False))
        del raw[-2:]
        struct.pack_into('<I', raw, 24, len(raw) - 20)
        self.assertEqual(parse_locale(raw)[0]['text'], '')
        self.assertEqual(replace_strings(raw, {0: ''})[0], raw)
        with self.assertRaises(ValueError):
            replace_strings(raw, {0: 'x'})

    def test_bad_edits(self):
        raw = locale(['small'])
        for edits in ({0: 'too long'}, {0: 'a\0b'}, {-1: 'x'}, {1: 'x'}):
            with self.assertRaises(ValueError):
                replace_strings(raw, edits)

    def test_bad_offsets_and_termination(self):
        raw = bytearray(locale(['sample']))
        base = struct.unpack_from('<I', raw, 16)[0]
        for offset in (0, 21, 100000):
            broken = bytearray(raw)
            struct.pack_into('<I', broken, base + 16, offset)
            with self.assertRaises(ValueError):
                parse_locale(broken)
        raw[-4:] = b'abcd'
        with self.assertRaises(ValueError):
            parse_locale(raw)

    def test_shared_slot_requires_explicit_aliases(self):
        raw = bytearray(locale(['shared', 'other']))
        base = struct.unpack_from('<I', raw, 16)[0]
        raw[base + 20:base + 24] = raw[base + 16:base + 20]
        with self.assertRaises(ValueError):
            replace_strings(raw, {0: 'new'})
        out, _ = replace_strings(raw, {0: 'new', 1: 'new'})
        self.assertEqual([e['text'] for e in parse_locale(out)], ['new', 'new'])

    def test_image_boundary_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / 'in.iso', Path(tmp) / 'out.iso'
            raw = b'x' * ((4 << 20) + 50)
            src.write_bytes(raw)
            at = (4 << 20) - 2
            result = write_patched_image(src, dst, [(at, b'HELLO')])
            self.assertTrue(result['full_readback_verified'])
            self.assertEqual(dst.read_bytes(), raw[:at] + b'HELLO' + raw[at + 5:])
            self.assertEqual(src.read_bytes(), raw)
            with self.assertRaises(FileExistsError):
                write_patched_image(src, dst, [])
            with self.assertRaises(ValueError):
                write_patched_image(src, Path(tmp) / 'bad.iso', [(1, b'abc'), (2, b'd')])
