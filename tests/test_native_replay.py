import unittest
from tools.native_replay import validate_sequence


class ReplayValidation(unittest.TestCase):
    def test_sequence_start_state_is_explicit_and_bounded(self):
        for anchor in ("runtime_running","main_menu"):
            sequence={"duration":20,"start_when":anchor,"events":[]}
            self.assertIs(validate_sequence(sequence),sequence)
        for anchor in (None,"riding",True,0):
            with self.subTest(anchor=anchor),self.assertRaises(ValueError):
                validate_sequence({"duration":20,"start_when":anchor,"events":[]})

    def test_press_release_and_stick_are_valid(self):
        sequence = {"duration": 2, "events": [
            {"at": 0, "commands": "PRESS A\nSET MAIN 0.75 0.5\n"},
            {"at": .5, "commands": "RELEASE A\nSET MAIN 0.5 0.5\n"}]}
        self.assertIs(validate_sequence(sequence), sequence)

    def test_rejects_invalid_or_unbounded_timing(self):
        for sequence in ({"duration": float("nan"), "events": []},
                         {"duration": 2, "events": [{"at": 3, "commands": "PRESS A\n"}]},
                         {"duration": 2, "events": [{"at": 1, "commands": "PRESS A\n"},
                                                    {"at": 0, "commands": "RELEASE A\n"}]}):
            with self.assertRaises(ValueError):
                validate_sequence(sequence)

    def test_rejects_unknown_commands_and_out_of_range_axes(self):
        for commands in ("PRESS BAD\n", "SET MAIN 2 0.5\n", "SET MAIN nan 0.5\n", "LOAD arbitrary\n"):
            with self.assertRaises(ValueError):
                validate_sequence({"duration": 1, "events": [{"at": 0, "commands": commands}]})


if __name__ == "__main__":
    unittest.main()
