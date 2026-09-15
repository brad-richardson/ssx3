"""Slot facts read out of a terrain record and a race-line record."""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import gamecube_slot_probe as probe


class PatchTests(unittest.TestCase):
    def record(self, track=11, rid=63, page=0x000b002a, texture=295, lightmap=142):
        payload = bytearray(probe.PATCH_SIZE)
        struct.pack_into('>I', payload, probe.ORDINAL_AT, (track << 24) | rid)
        struct.pack_into('>I', payload, probe.PAGE_AT, page)
        struct.pack_into('>HH', payload, probe.BINDING_AT, texture, lightmap)
        return bytes(payload)

    def test_the_ordinal_splits_into_track_and_rid(self):
        facts = probe.patch_facts(self.record())
        self.assertEqual(facts['track'], 11)
        self.assertEqual(facts['rid'], 63)

    def test_the_page_word_is_track_and_texture_group(self):
        """ASS1's own template: page 0x000b002a is track 11, texture group 42."""
        facts = probe.patch_facts(self.record())
        self.assertEqual(facts['page_track'], 11)
        self.assertEqual(facts['texture_group'], 42)

    def test_image_bindings_are_read(self):
        facts = probe.patch_facts(self.record())
        self.assertEqual((facts['texture'], facts['lightmap']), (295, 142))


class RaceLineTests(unittest.TestCase):
    def record(self, nodes=3, markers=((0, 0.0), (2, 1000.0), (1, 250.0), (1, 700.0))):
        payload = bytearray(struct.pack('>4I', nodes, 20, len(markers), nodes * 20))
        payload += bytes(nodes * 20)
        payload += struct.pack('>f', 1000.0)
        for tag, distance in markers:
            payload += struct.pack('>If', tag, distance)
        return bytes(payload)

    def test_a_slopestyle_trailer_yields_its_marker_fractions(self):
        line = probe.race_line(self.record())
        self.assertEqual(line['nodes'], 3)
        self.assertEqual(line['markers'], 4)
        self.assertEqual(line['total_distance'], 1000.0)
        self.assertEqual(line['marker_fractions'], [0.25, 0.7])

    def test_a_race_trailer_has_no_type_one_markers(self):
        line = probe.race_line(self.record(markers=((0, 0.0), (2, 1000.0))))
        self.assertEqual(line['markers'], 2)
        self.assertEqual(line['marker_fractions'], [])
        self.assertEqual(line['trailer'], [(0, 0.0), (2, 1000.0)])


if __name__ == '__main__':
    unittest.main()


class PageWordTests(unittest.TestCase):
    """The page word a patch carries must name its own slot's track."""

    def test_bind_patch_writes_the_target_track(self):
        import struct as _struct
        from gamecube_textures import bind_patch
        payload = bytes(probe.PATCH_SIZE)
        out = bind_patch(payload, 852, 672, 42, [(0.0, 0.0)] * 4, (0, 0, 1, 1), track=11)
        facts = probe.patch_facts(out)
        self.assertEqual(facts['page'], 0x000b002a)   # ASS1: track 11, group 42
        self.assertEqual(facts['page_track'], 11)
        self.assertEqual(facts['texture_group'], 42)

    def test_the_garibaldi_lineage_is_unchanged(self):
        """ARA1 is track 8, which is what the old hard-coded 0x80000 meant."""
        from gamecube_textures import bind_patch
        out = bind_patch(bytes(probe.PATCH_SIZE), 1, 2, 0x1f, [(0.0, 0.0)] * 4, (0, 0, 1, 1), track=8)
        self.assertEqual(probe.patch_facts(out)['page'], 0x0008001f)
