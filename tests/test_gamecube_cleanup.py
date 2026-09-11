"""GameCube cleanup ports on synthetic big-endian records."""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_cleanup import (clear_removed_instance_references, clear_script_bindings,  # noqa: E402
                              disable_course_scripts, instance_id)


def entry(kind, rid, track=8):
    return dict(kind=kind, size=0, track=track, rid=rid)


class CleanupTests(unittest.TestCase):
    def test_instance_id_uses_track_high_byte(self):
        self.assertEqual(instance_id(entry(3, 0x371)), 0x08000371)

    def test_kind13_rows_and_kind18_slots_are_blanked(self):
        removed = [(entry(3, 5), b''), (entry(3, 9), b'')]
        rows = [(0x08000005, 88), (0x08000007, 96), (0x08000009, 104)]  # data offsets past the 88-byte table
        table = bytearray(b'\x01' + b'\xcc' * 11 + struct.pack('>I', len(rows)))
        for oid, off in rows:
            table += struct.pack('>IIIIII', 1, 2, 3, oid, off, 0)
        table += bytes(64)
        nis = struct.pack('>18I', 0x08000009, 0x08000001, *([0xffffffff] * 16))
        out, changes = clear_removed_instance_references(
            [(entry(13, 0), bytes(table)), (entry(18, 0), nis), (entry(1, 0), b'keep')], removed)
        ids = [struct.unpack_from('>I', out[0][1], 28 + i * 24)[0] for i in range(3)]
        self.assertEqual(ids, [0xffffffff, 0x08000007, 0xffffffff])
        self.assertEqual(struct.unpack_from('>2I', out[1][1]), (0xffffffff, 0x08000001))
        self.assertEqual(len(changes), 3)
        self.assertEqual(out[2][1], b'keep')

    def make_script(self):
        # Header 92 bytes: magic bytes, tables at 56 (programs), 64 (base), 68 (kind-3 binding), 76 (defs), 84 (splines).
        head = bytearray(92)
        head[:4] = b'\x00\x10\x00\x00'
        empty = struct.pack('>4I', 0x4e554c, 20, 36, 36) + b'\x2a\xff\x00\x00' + bytes(16)
        full = struct.pack('>4I', 0x4e554c, 24, 40, 40) + bytes(24)
        table_at = 92
        programs_at = table_at + 12
        programs = empty + empty + full
        defs_at = programs_at + len(programs)
        definition = struct.pack('>4I', 1, 0, 0, 0x08000002)  # collision id track 8 rid 2
        def_index_at = defs_at + 16
        struct.pack_into('>3I', head, 56, 3, table_at, defs_at)
        struct.pack_into('>I', head, 64, defs_at)  # base for definition offsets
        struct.pack_into('>II', head, 68, 2, 0)   # kind-3 binding table of 2 ordinals
        struct.pack_into('>II', head, 76, 1, def_index_at)
        struct.pack_into('>II', head, 84, 0, 0)
        body = struct.pack('>3I', programs_at, programs_at + 36, programs_at + 72) + programs + definition + struct.pack('>I', 0)
        return bytes(head) + body

    def test_script_bindings_and_programs(self):
        script = self.make_script()
        removed = [(entry(3, 0), b''), (entry(3, 1), b''), (entry(12, 2), b'')]
        out, edits = clear_script_bindings([(entry(16, 0), script)], removed)
        self.assertEqual([e['action'] for e in edits], ['disable_binding_table', 'disable_collision_definition'])
        self.assertEqual(struct.unpack_from('>I', out[0][1], 68)[0], 0)
        out, changes = disable_course_scripts(out)
        self.assertEqual(len(changes), 1)
        count, table, end = struct.unpack_from('>3I', out[0][1], 56)
        third = struct.unpack_from('>I', out[0][1], table + 8)[0]
        self.assertEqual(struct.unpack_from('>4I', out[0][1], third), (0x4e554c, 20, 36, 36))

    def test_partial_binding_removal_is_rejected(self):
        script = self.make_script()
        with self.assertRaises(ValueError):
            clear_script_bindings([(entry(16, 0), script)], [(entry(3, 0), b'')])


if __name__ == '__main__':
    unittest.main()
