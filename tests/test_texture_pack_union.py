"""Union semantics: one entry per distinct texture, grouped by family, with its courses."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from texture_pack_union import course_textures, parse_course


class ParseCourseTests(unittest.TestCase):
    def test_argument_shape(self):
        code, dump, run = parse_course('ASS1=a/b:c/d')
        self.assertEqual((code, str(dump), str(run)), ('ASS1', 'a/b', 'c/d'))
        for bad in ('ASS1', 'ASS1=only-dump', 'a/b:c/d'):
            with self.assertRaises(Exception):
                parse_course(bad)


class CourseTextureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.dump = self.tmp / 'dump'
        self.dump.mkdir()
        self.run = self.tmp / 'run'
        self.run.mkdir()
        # Briefing at wall 100, race start at wall 110.
        rows = [dict(t=0, wall_time=100.0, x=0, y=0, z=0),
                dict(t=1, wall_time=105.0, x=5, y=0, z=0),
                dict(t=2, wall_time=110.0, x=99, y=0, z=0)]
        (self.run / 'rider.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))

    def dumped(self, name, mtime):
        path = self.dump / name
        path.write_bytes(b'\0' * 16)
        import os
        os.utime(path, (mtime, mtime))
        return path

    def test_only_course_art_after_the_briefing_survives(self):
        self.dumped('tex1_64x64_1111111111111111_14.png', 90.0)    # frontend
        self.dumped('tex1_64x64_2222222222222222_14.png', 105.0)   # course load
        self.dumped('tex1_64x64_3333333333333333_14.png', 115.0)   # ride
        self.dumped('tex1_640x480_4444444444444444_5555555555555555_9.png', 115.0)  # framebuffer
        self.dumped('tex1_64x64_m_6666666666666666_14_mip2.png', 115.0)             # sidecar
        self.dumped('notes.txt', 115.0)
        entries, keep = course_textures(self.dump, self.run)
        self.assertEqual(len(entries), 5)
        self.assertEqual({e['texture_hash'] for e in keep},
                         {'2222222222222222', '3333333333333333'})
        self.assertEqual({e['phase'] for e in keep}, {'course load', 'ride'})

    def test_a_mipmapped_base_is_kept(self):
        self.dumped('tex1_64x64_m_7777777777777777_14.png', 115.0)
        _, keep = course_textures(self.dump, self.run)
        self.assertEqual(len(keep), 1)
        self.assertTrue(keep[0]['mipmapped'])


if __name__ == '__main__':
    unittest.main()
