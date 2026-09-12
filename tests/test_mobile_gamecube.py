import argparse
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import mobile_gamecube


class DeviceLaunch(unittest.TestCase):
    def test_app_flags_follow_argument_separator(self):
        # devicectl parsed "-ssxAutoTest" as its own "-t" option until "--" was added.
        args = argparse.Namespace(device="PHONE", simulator=False,
                                  sequence=Path("native/ios/snow-jam-smoke.json"))
        calls = []
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(mobile_gamecube, "REPORTS", Path(tmp)), \
                mock.patch.object(mobile_gamecube, "copy_to"), \
                mock.patch.object(mobile_gamecube, "command", side_effect=lambda c: calls.append(c)):
            mobile_gamecube.launch(args)
        self.assertEqual(len(calls), 1)
        command = calls[0]
        bundle = command.index(mobile_gamecube.BUNDLE)
        self.assertEqual(command[bundle + 1:], ["--", "-ssxAutoTest"])
        self.assertNotIn("--", command[:bundle])


class WorldPush(unittest.TestCase):
    def test_world_copies_one_bigf_archive_into_the_container(self):
        with tempfile.TemporaryDirectory() as tmp:
            world = Path(tmp) / "BAM.BIG"
            world.write_bytes(b"BIGF" + bytes(12))
            args = argparse.Namespace(device="PHONE", simulator=False, world=world)
            calls = []
            with mock.patch.object(mobile_gamecube, "copy_to", side_effect=lambda a, s, d, timeout=0: calls.append((s, d))):
                mobile_gamecube.world(args)
            self.assertEqual(calls, [(world, "Documents/Game/files/data/worlds/bam.big")])
            world.write_bytes(b"nope")
            with self.assertRaises(RuntimeError):
                mobile_gamecube.world(args)


if __name__ == "__main__":
    unittest.main()
