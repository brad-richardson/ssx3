"""Compile the grab translation header and check its invariants."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("clang++"), "requires Clang")
class GrabMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        probe = Path(cls.temp.name) / "probe"
        subprocess.run(["/usr/bin/clang++", "-std=c++20", "-O2", "-I", str(ROOT / "native/ios"),
                        str(ROOT / "tests/native_grab_probe.cpp"), "-o", str(probe)], check=True)
        cls.rows = {}
        for line in subprocess.check_output([probe], text=True).splitlines():
            mask, gc, exact, *name = line.split(" ", 3)
            cls.rows[int(mask)] = (int(gc), exact == "1", name[0] if name else "")

    def test_every_ps2_combination_is_named_and_mapped(self):
        self.assertEqual(self.rows[0], (0, False, ""))
        for mask in range(1, 16):
            gc, _, name = self.rows[mask]
            self.assertTrue(name, mask)
            self.assertNotEqual(gc, 0, mask)

    def test_exact_grabs_cover_every_gamecube_combination(self):
        exact = {gc for gc, is_exact, _ in self.rows.values() if is_exact}
        self.assertEqual(exact, set(range(1, 8)))

    def test_single_buttons_match_ps2_names(self):
        self.assertEqual({self.rows[1][2], self.rows[2][2], self.rows[4][2], self.rows[8][2]},
                         {"Method", "Mute", "Stalefish", "Indy"})

    def test_approximations_are_the_union_of_their_buttons(self):
        for mask in range(1, 16):
            gc, is_exact, _ = self.rows[mask]
            if is_exact:
                continue
            union = 0
            for bit in (1, 2, 4, 8):
                if mask & bit:
                    union |= self.rows[bit][0]
            self.assertEqual(gc, union, mask)


if __name__ == "__main__":
    unittest.main()
