"""Synthetic GX register fixtures for material comparison boundaries."""
import json
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_draw_trace import terrain_pair, compare


def draw(scale=0, texture='snow', lightmap='sheet', stage1=0x08f80f):
    bp = [0] * 256
    bp[0] = 1 << 10
    bp[0xc0] = 0x08fff8
    bp[0xc2] = stage1 | scale << 20
    bp[0x28] = 0x3c93c0
    return dict(id=1, bp=struct.pack('<256I', *bp).hex(), textures=[
        dict(unit=0, hash=texture), dict(unit=1, hash=lightmap)])


class DrawTraceTests(unittest.TestCase):
    def test_recognizes_lighting_scale_without_confusing_other_materials(self):
        for scale in range(4):
            self.assertEqual(terrain_pair(draw(scale)), ('snow', 'sheet'))
        self.assertIsNone(terrain_pair(draw(stage1=0x08f8af)))  # raster-lit object
        row = draw()
        row['textures'].pop()
        self.assertIsNone(terrain_pair(row))

    def test_pairs_image_identity_and_reports_both_scales(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a, b, report = (root / p for p in ('a.jsonl', 'b.jsonl', 'report.json'))
            a.write_text(json.dumps(draw()) + '\n')
            b.write_text(json.dumps(draw(1)) + '\n' + json.dumps(draw(1, lightmap='different')) + '\n')
            compare(SimpleNamespace(source=a, target=b, output=report))
            result = json.loads(report.read_text())
            self.assertEqual(result['matched_image_pairs'], 1)
            self.assertEqual(result['matches'][0]['source']['lightmap_scales'], [1])
            self.assertEqual(result['matches'][0]['target']['lightmap_scales'], [2])

    def test_no_matching_images_is_inconclusive(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a, b = root / 'a.jsonl', root / 'b.jsonl'
            a.write_text(json.dumps(draw()) + '\n')
            b.write_text(json.dumps(draw(1, texture='unrelated')) + '\n')
            with self.assertRaisesRegex(ValueError, 'inconclusive'):
                compare(SimpleNamespace(source=a, target=b, output=root / 'result.json'))


if __name__ == '__main__':
    unittest.main()
