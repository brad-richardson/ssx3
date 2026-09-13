import struct
import unittest

from gamecube_telemetry import RIDER, decode_messages, initial_values, valid_rider


class TelemetryTests(unittest.TestCase):
    def test_halfword_terrain_flags_and_byte_reset_request(self):
        data=f'{RIDER} 2ac\n004b1234\n{RIDER} 718 2d8\n01000000\n'.encode()
        self.assertEqual(decode_messages(data),dict(terrain_flags=75,reset_path_requested=1))
    def test_unchanged_zero_surface_is_valid_after_pointer_arrives(self):
        values = initial_values()
        self.assertFalse(valid_rider(values))
        values.update(decode_messages(f'{RIDER}\n81048820\n'.encode()))
        self.assertTrue(valid_rider(values))
        self.assertEqual(values['surface'], 0)
        self.assertEqual(values['state'], 0)

    def test_pointer_and_float_messages(self):
        x = struct.unpack('>I', struct.pack('>f', -113024.25))[0]
        data = f'{RIDER}\n81048820\n{RIDER} f0\n{x:x}\n{RIDER} 718 d30\n9\n\0'.encode()
        self.assertEqual(decode_messages(data), dict(rider=0x81048820, x=-113024.25, state=9))

    def test_reject_incomplete_and_unknown_chains(self):
        for data in [b'803da1f8\n', b'12345678\n1\n', f'{RIDER}\n100000000\n'.encode()]:
            with self.assertRaises(ValueError):
                decode_messages(data)

    def test_unloaded_pointer_chain_is_not_a_rider(self):
        values = dict(rider=0x81048820, x=10., y=20., z=-100., surface=0)
        self.assertTrue(valid_rider(values))
        for changes in [dict(rider=0), dict(surface=0x80463e00), dict(x=float('nan')), dict(z=1e30), dict(state=0x80001000)]:
            self.assertFalse(valid_rider(dict(values, **changes)))
