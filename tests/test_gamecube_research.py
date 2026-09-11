import unittest

from tools.gamecube_research import address_pair, materializations, symbols


class AddressPairs(unittest.TestCase):
    def test_signed_low_half(self):
        # lis r3,0x8030; addi r4,r3,-32768
        self.assertEqual(address_pair(0x3C608030, 0x38838000), 0x802F8000)

    def test_ori_uses_different_register_fields(self):
        # lis r3,0x802f; ori r4,r3,0x8000
        self.assertEqual(address_pair(0x3C60802F, 0x60648000), 0x802F8000)

    def test_different_base_is_not_a_reference(self):
        self.assertIsNone(address_pair(0x3C608030, 0x38858000))

    def test_addi_r0_is_zero_base(self):
        self.assertIsNone(address_pair(0x3C008030, 0x38808000))

    def test_section_table_is_not_symbols(self):
        info = "| 0x80000000 | 0x400000 | 0x100\nDiscovered symbols:\n| 0x80001000 | 0x10 | main\n"
        self.assertEqual(symbols(info), [(0x80001000, 0x10, "main")])

    def test_interleaved_constant_construction(self):
        words = [0x3C608030, 0x38800001, 0x38638000]
        self.assertIn((0x108, 0x802F8000), list(materializations(words, 0x100)))

    def test_call_discards_register_assumptions(self):
        words = [0x3C608030, 0x48001001, 0x38638000]
        self.assertNotIn((0x108, 0x802F8000), list(materializations(words, 0x100)))

    def test_load_clobbers_constant(self):
        words = [0x3C608030, 0x80640000, 0x38638000]
        self.assertNotIn((0x108, 0x802F8000), list(materializations(words, 0x100)))


if __name__ == "__main__":
    unittest.main()
