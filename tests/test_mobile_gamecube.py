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


if __name__ == "__main__":
    unittest.main()
