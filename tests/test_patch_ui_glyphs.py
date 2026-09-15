"""Repainting SSX 3's prompt glyphs for Xbox positions, and keeping them.

The patch itself shipped in September 2026 with no test, and a re-provision of
the phone silently reverted it: provisioning copies `files/` from the pristine
disc, so the patched sheets in the device container were overwritten and the
in-game prompts went back to GameCube letters ("B for recovery" while the
overlay's button reads X). These cover both halves - the repaint, and the
provisioning step that has to re-apply it.
"""

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))

import patch_ui_glyphs as glyphs
import mobile_gamecube as mobile
from gamecube_shape import retile, rgb5a3


def build_sheet(width=256, height=256):
    """A .gsh holding one `art_` paletted image, laid out as the tool expects."""
    palette = [0x0000] + [0x8000 | (i << 5) for i in range(1, 256)]
    # Index 200 is used once so it is never the least-used entry; the tool
    # repurposes the least-used index for Xbox blue.
    linear = bytearray(width * height)
    for i in range(len(linear)):
        linear[i] = 200 if i % 7 else 1
    return palette, retile(bytes(linear), width, height), width, height


class RepaintTests(unittest.TestCase):
    def setUp(self):
        self.palette, self.pixels, self.width, self.height = build_sheet()

    def test_every_slot_is_repainted_and_nothing_else_is(self):
        pixels, palette, info = glyphs.repaint(
            self.pixels, self.palette, self.width, self.height)
        self.assertEqual(sorted(info['slots']), ['B', 'X', 'Y'])
        # The letters are swapped for the Xbox button at the same position.
        self.assertEqual(info['slots']['B']['letter'], 'X')
        self.assertEqual(info['slots']['X']['letter'], 'B')
        self.assertEqual(info['slots']['Y']['letter'], 'Y')

        from gamecube_shape import untile
        before = untile(self.pixels, self.width, self.height)
        after = untile(pixels, self.width, self.height)
        self.assertEqual(len(before), len(after))
        inside = set()
        for spec in glyphs.SLOTS.values():
            x0, y0, x1, y1 = spec['rect']
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    inside.add(y * self.width + x)
        changed = {i for i in range(len(before)) if before[i] != after[i]}
        self.assertTrue(changed, 'the repaint changed nothing at all')
        self.assertTrue(changed <= inside,
                        'the repaint wrote outside the measured glyph rectangles')

    def test_xbox_blue_replaces_the_least_used_palette_entry(self):
        _, palette, info = glyphs.repaint(
            self.pixels, self.palette, self.width, self.height)
        index = info['blue_index']
        self.assertNotEqual(index, 0, 'the transparent entry must never be repurposed')
        # RGB5A3 keeps five bits a channel, so the blue round-trips to within
        # one quantization step rather than exactly.
        stored = rgb5a3(palette[index])
        wanted = glyphs.SLOTS['B']['colour']
        self.assertEqual(stored[3], 255)
        for channel, (got, want) in enumerate(zip(stored[:3], wanted[:3])):
            self.assertLessEqual(abs(got - want), 8,
                                 f'channel {channel} of the repurposed entry is {got}, '
                                 f'not Xbox blue {want}')
        self.assertGreater(stored[2], stored[0] + 100, 'the entry is not blue')
        # Only that one entry moves; the rest of the palette is the disc's own.
        moved = [i for i, (a, b) in enumerate(zip(self.palette, palette)) if a != b]
        self.assertEqual(moved, [index])

    def test_a_sheet_without_the_art_image_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'empty.gsh'
            path.write_bytes(b'\x00' * 64)
            with self.assertRaises(Exception):
                glyphs.patch_sheet(path, Path(tmp) / 'out.gsh')


class ProvisionTests(unittest.TestCase):
    """The regression itself: provisioning must not leave stock glyphs behind."""

    def test_provision_reapplies_the_patch_over_the_pristine_sheets(self):
        calls = []
        applied = {}

        def fake_copy_to(args, source, destination, timeout=None):
            calls.append((Path(source).name, destination))

        def fake_patched_ui(game, workspace):
            out = Path(workspace) / 'ui'
            out.mkdir(parents=True, exist_ok=True)
            for name in mobile.GLYPH_SHEETS:
                (out / f'{name}.gsh').write_bytes(b'patched')
            applied['game'] = Path(game)
            return out

        class Args:
            simulator = False
            stock_glyphs = False
            game = Path('/nowhere/GXBE69')
            device = 'device'

        original = (mobile.copy_to, mobile.patched_ui, mobile.native.sha256)
        mobile.copy_to = fake_copy_to
        mobile.patched_ui = fake_patched_ui
        mobile.native.sha256 = lambda *a, **k: mobile.native.PINS['dol_sha256']
        try:
            mobile.provision(Args())
        finally:
            mobile.copy_to, mobile.patched_ui, mobile.native.sha256 = original

        destinations = [destination for _, destination in calls]
        self.assertIn('Documents/Game/files', destinations)
        self.assertIn('Documents/Game/files/data/ui', destinations)
        # Ordering is the whole point: the glyph sheets are copied *after*
        # files/, or the pristine ones overwrite them again.
        self.assertGreater(destinations.index('Documents/Game/files/data/ui'),
                           destinations.index('Documents/Game/files'))
        self.assertEqual(applied['game'], Path('/nowhere/GXBE69'))

    def test_stock_glyphs_skips_the_patch(self):
        calls = []

        def fake_copy_to(args, source, destination, timeout=None):
            calls.append(destination)

        def fail_patched_ui(game, workspace):
            raise AssertionError('--stock-glyphs must not build patched sheets')

        class Args:
            simulator = False
            stock_glyphs = True
            game = Path('/nowhere/GXBE69')
            device = 'device'

        original = (mobile.copy_to, mobile.patched_ui, mobile.native.sha256)
        mobile.copy_to = fake_copy_to
        mobile.patched_ui = fail_patched_ui
        mobile.native.sha256 = lambda *a, **k: mobile.native.PINS['dol_sha256']
        try:
            mobile.provision(Args())
        finally:
            mobile.copy_to, mobile.patched_ui, mobile.native.sha256 = original
        self.assertNotIn('Documents/Game/files/data/ui', calls)


if __name__ == '__main__':
    unittest.main()
