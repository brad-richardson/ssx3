"""Course presets supply only the options a caller omitted."""
import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import course_preset  # noqa: E402


def parser():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nbd', type=Path)
    ap.add_argument('--location', default='ARA1')
    ap.add_argument('--template-rid', type=int, default=1673)
    ap.add_argument('--yaw', type=float, default=0.0)
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--source-anchor')
    ap.add_argument('--target-anchor')
    ap.add_argument('--pin-texture-group', type=int)
    ap.add_argument('--race-aip', type=Path)
    ap.add_argument('--textures', type=Path)
    ap.add_argument('--lightmaps', type=Path)
    ap.add_argument('--reset-aip', type=Path)
    ap.add_argument('--preset')
    return ap


class CoursePresetTests(unittest.TestCase):
    def test_shipped_presets_are_complete_and_point_at_real_donor_files(self):
        self.assertEqual(course_preset.available(), ['aloha', 'garibaldi'])
        for name in course_preset.available():
            preset = course_preset.load(name)
            self.assertEqual(preset['name'], name)
            for key in ('nbd', 'textures', 'lightmaps', 'gsf', 'reset_paths', 'race_paths'):
                self.assertIn(key, preset['donor'], f'{name}.{key}')
            for key in ('location', 'group', 'track', 'template_rid', 'texture_group'):
                self.assertIn(key, preset['target'], f'{name}.{key}')
            placement = preset['placement']
            self.assertEqual(len(placement['source_anchor']), 3)
            self.assertEqual(len(placement['target_anchor']), 3)
            self.assertIn('derivation', placement)
            race = preset['race']
            self.assertIn(race['race_line_kind'], ('race', 'slopestyle'))
            self.assertEqual(len(race['marker_fractions']), 2 if race['race_line_kind'] == 'slopestyle' else 0)
            # The page word is the track index in its high half and the texture group in its low half.
            page = int(preset['target']['page'], 0)
            self.assertEqual(page >> 16, preset['target']['track'])
            self.assertEqual(page & 0xffff, preset['target']['texture_group'])

    def test_explicit_flags_win_over_the_preset(self):
        ap = parser()
        argv = ['--preset', 'aloha', '--location', 'DSS2', '--yaw=12.5']
        args = ap.parse_args(argv)
        receipt = course_preset.apply(ap, args, argv)
        self.assertEqual(args.location, 'DSS2')
        self.assertEqual(args.yaw, 12.5)
        self.assertNotIn('location', receipt['filled'])
        self.assertNotIn('yaw', receipt['filled'])
        # ... and everything else comes from the preset, with paths resolved under the repo root.
        self.assertEqual(args.template_rid, 63)
        self.assertEqual(args.pin_texture_group, 42)
        self.assertEqual(args.scale, 0.55)
        self.assertEqual(args.source_anchor, [-343.59, -2877.282, 58695.381])
        self.assertTrue(args.nbd.is_absolute())
        self.assertEqual(args.nbd.name, 'aloha.nbd')
        self.assertEqual(args.race_aip.name, 'aloha.sop')

    def test_no_preset_changes_nothing(self):
        ap = parser()
        args = ap.parse_args([])
        self.assertIsNone(course_preset.apply(ap, args, []))
        self.assertEqual(args.location, 'ARA1')
        self.assertEqual(args.template_rid, 1673)
        self.assertIsNone(args.nbd)

    def test_missing_sections_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'broken.json'
            path.write_text(json.dumps(dict(name='broken', donor={}, target={})))
            with self.assertRaisesRegex(ValueError, 'placement'):
                course_preset.load(path)


if __name__ == '__main__':
    unittest.main()
