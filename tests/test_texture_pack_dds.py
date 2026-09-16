"""Block-compressed DDS output, checked against Dolphin's own parser contract.

The risk here is not that the file is a valid DDS, it is that it is valid in a
way Dolphin's `ParseDDSHeader` / `LoadDDSTexture` pair does not accept: a flag
combination that makes it reinterpret the pitch field, a chain whose levels do
not halve, or one 1x1 level too many. `parse_like_dolphin` below reimplements
those checks from `CustomTextureData.cpp` so the tests fail here rather than on
the phone.
"""

import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import texture_pack_dds as dds

from PIL import Image

DDSD_PITCH = 0x00000008
DDSD_LINEARSIZE = 0x00080000
DDS_HEADER_FLAGS_VOLUME = 0x00800000
DDS_CUBEMAP = 0x00000200


def parse_like_dolphin(data):
    """ParseDDSHeader plus the mip walk, and PurgeInvalidMips' 1x1 rule."""
    if len(data) < dds.PIL_DDS_HEADER:
        raise AssertionError('shorter than a DDS header')
    magic, size, flags, height, width, pitch, depth, mips = struct.unpack_from('<8I', data, 0)
    if magic != dds.DDS_MAGIC:
        raise AssertionError('bad magic')
    if size < 124:
        raise AssertionError('dwSize below sizeof(DDS_HEADER)')
    if flags & dds.DDSD_REQUIRED != dds.DDSD_REQUIRED:
        raise AssertionError('DDS_HEADER_FLAGS_TEXTURE not set')
    if flags & DDS_HEADER_FLAGS_VOLUME:
        raise AssertionError('volume texture')
    if not width or not height:
        raise AssertionError('zero dimension')
    if flags & DDSD_PITCH and flags & DDSD_LINEARSIZE:
        raise AssertionError('both PITCH and LINEARSIZE set; Dolphin would '
                             'reinterpret dwPitchOrLinearSize')
    pf_size, pf_flags, fourcc = struct.unpack_from('<II4s', data, 4 + 72)
    if pf_size != 32:
        raise AssertionError('pixel format size')
    if not pf_flags & dds.DDPF_FOURCC:
        raise AssertionError('not a fourCC format')
    fmt = fourcc.decode('ascii')
    if fmt not in dds.BYTES_PER_BLOCK:
        raise AssertionError(f'unsupported fourCC {fmt!r}')
    caps2, = struct.unpack_from('<I', data, 4 + 108)
    if caps2 & DDS_CUBEMAP:
        raise AssertionError('cubemap')
    count = mips if flags & dds.DDSD_MIPMAPCOUNT and mips else 1

    # Walk the levels the way LoadDDSTexture does, halving as it goes.
    offset = dds.PIL_DDS_HEADER
    levels = []
    mip_width, mip_height = width, height
    for index in range(count):
        if index:
            mip_width = max(mip_width // 2, 1)
            mip_height = max(mip_height // 2, 1)
        need = dds.level_size(mip_width, mip_height, fmt)
        if offset + need > len(data):
            raise AssertionError(f'level {index} runs past the end of the file')
        levels.append((mip_width, mip_height))
        offset += need
    if offset != len(data):
        raise AssertionError(f'{len(data) - offset} trailing bytes after the chain')
    if sum(1 for w, h in levels if w == 1 and h == 1) > 1:
        raise AssertionError('more than a single 1x1 mipmap')
    return dict(format=fmt, width=width, height=height, levels=levels)


def cutout(size=(32, 32)):
    """Hard-edged alpha, like the foliage cards the guest alpha-tests."""
    image = Image.new('RGBA', size)
    for y in range(size[1]):
        for x in range(size[0]):
            visible = (x + y) % 8 < 4
            image.putpixel((x, y), (30 + x * 3 % 200, 120, 60, 255 if visible else 0))
    return image


def gradient(size=(32, 32)):
    image = Image.new('RGBA', size)
    for y in range(size[1]):
        for x in range(size[0]):
            image.putpixel((x, y), (200, 80, 40, int(255 * x / (size[0] - 1))))
    return image


def opaque(size=(32, 32)):
    image = Image.new('RGBA', size)
    for y in range(size[1]):
        for x in range(size[0]):
            image.putpixel((x, y), (x * 7 % 256, y * 5 % 256, 90, 255))
    return image


class FormatTests(unittest.TestCase):
    def test_alpha_classes(self):
        self.assertEqual(dds.alpha_class(opaque()), 'opaque')
        self.assertEqual(dds.alpha_class(cutout()), 'binary')
        self.assertEqual(dds.alpha_class(gradient()), 'gradient')

    def test_only_a_real_gradient_costs_dxt5(self):
        self.assertEqual(dds.pick_format(opaque()), 'DXT1')
        self.assertEqual(dds.pick_format(cutout()), 'DXT1')
        self.assertEqual(dds.pick_format(gradient()), 'DXT5')

    def test_a_hard_cutout_edge_survives_dxt1(self):
        """The mask is alpha-*tested* by the guest, so it has to stay binary."""
        import io
        source = cutout()
        payload = dds.dds_header(source.width, source.height, 1, 'DXT1') \
            + dds.encode_level(source, 'DXT1')
        back = Image.open(io.BytesIO(payload)).convert('RGBA')
        alphas = {back.getpixel((x, y))[3]
                  for y in range(source.height) for x in range(source.width)}
        self.assertEqual(alphas, {0, 255})

    def test_block_counts_round_up_and_never_reach_zero(self):
        self.assertEqual(dds.blocks(4), 1)
        self.assertEqual(dds.blocks(5), 2)
        self.assertEqual(dds.blocks(2), 1)
        self.assertEqual(dds.blocks(1), 1)
        self.assertEqual(dds.level_size(1, 1, 'DXT1'), 8)
        self.assertEqual(dds.level_size(64, 64, 'DXT5'), 16 * 16 * 16)


class HeaderTests(unittest.TestCase):
    def test_the_header_is_exactly_128_bytes(self):
        self.assertEqual(len(dds.dds_header(64, 64, 7, 'DXT1')), dds.PIL_DDS_HEADER)

    def test_pitch_and_linearsize_are_never_both_claimed(self):
        flags, = struct.unpack_from('<I', dds.dds_header(64, 64, 7, 'DXT1'), 8)
        self.assertFalse(flags & DDSD_PITCH and flags & DDSD_LINEARSIZE)
        self.assertEqual(flags & dds.DDSD_REQUIRED, dds.DDSD_REQUIRED)
        self.assertTrue(flags & dds.DDSD_MIPMAPCOUNT)

    def test_a_single_level_texture_claims_no_mip_chain(self):
        header = dds.dds_header(64, 64, 1, 'DXT1')
        flags, = struct.unpack_from('<I', header, 8)
        self.assertFalse(flags & dds.DDSD_MIPMAPCOUNT)

    def test_width_and_height_are_not_transposed(self):
        # dwHeight precedes dwWidth in DDS_HEADER; a swap here would only show
        # up on non-square art.
        parsed = parse_like_dolphin(dds.dds_header(64, 16, 1, 'DXT1')
                                    + dds.encode_level(opaque((64, 16)), 'DXT1'))
        self.assertEqual((parsed['width'], parsed['height']), (64, 16))


class PackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pack = Path(self.tmp.name) / 'pack'
        self.out = Path(self.tmp.name) / 'out'
        self.pack.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, image):
        image.save(self.pack / name)

    def test_a_pack_with_sidecars_reuses_them(self):
        base = opaque((32, 32))
        self.write('tex1_8x8_aa_14.png', base)
        for index, side in enumerate((16, 8, 4, 2, 1), start=1):
            self.write(f'tex1_8x8_aa_14_mip{index}.png', opaque((side, side)))
        report = dds.convert_pack(self.pack, self.out)
        self.assertEqual(report['textures'], 1)
        self.assertEqual(report['rebuilt_chains'], 0)
        self.assertEqual(report['entries'][0]['chain'], 'sidecars')
        self.assertEqual(report['entries'][0]['levels'], 6)

    def test_a_partial_chain_is_rebuilt_whole(self):
        """Dolphin stops at the first level that is not half the one above."""
        self.write('tex1_8x8_bb_14.png', opaque((32, 32)))
        self.write('tex1_8x8_bb_14_mip1.png', opaque((16, 16)))
        report = dds.convert_pack(self.pack, self.out)
        self.assertEqual(report['rebuilt_chains'], 1)
        self.assertEqual(report['entries'][0]['chain'], 'rebuilt')
        parsed = parse_like_dolphin((self.out / 'tex1_8x8_bb_14.dds').read_bytes())
        self.assertEqual(parsed['levels'][-1], (1, 1))

    def test_every_written_file_satisfies_the_parser_contract(self):
        self.write('tex1_8x8_cc_14.png', opaque((32, 32)))
        self.write('tex1_16x8_dd_14.png', cutout((64, 32)))
        self.write('tex1_8x8_ee_5.png', gradient((32, 32)))
        report = dds.convert_pack(self.pack, self.out)
        self.assertEqual(report['textures'], 3)
        self.assertEqual(report['dxt5'], 1)
        for entry in report['entries']:
            data = (self.out / (Path(entry['name']).stem + '.dds')).read_bytes()
            parsed = parse_like_dolphin(data)
            self.assertEqual(parsed['format'], entry['format'])
            self.assertEqual(len(parsed['levels']), entry['levels'])
            self.assertEqual((parsed['width'], parsed['height']),
                             (entry['width'], entry['height']))

    def test_mip_sidecars_are_not_converted_as_textures_of_their_own(self):
        self.write('tex1_8x8_ff_14.png', opaque((32, 32)))
        self.write('tex1_8x8_ff_14_mip1.png', opaque((16, 16)))
        report = dds.convert_pack(self.pack, self.out)
        self.assertEqual(report['textures'], 1)
        self.assertFalse(list(self.out.glob('*_mip*')))

    def test_a_dry_run_writes_nothing(self):
        self.write('tex1_8x8_gg_14.png', opaque((32, 32)))
        report = dds.convert_pack(self.pack, self.out, dry_run=True)
        self.assertEqual(report['textures'], 1)
        self.assertFalse(self.out.exists() and list(self.out.iterdir()))

    def test_the_result_is_much_smaller_than_the_decoded_png(self):
        self.write('tex1_16x16_hh_14.png', opaque((64, 64)))
        report = dds.convert_pack(self.pack, self.out)
        entry = report['entries'][0]
        # DXT1 is half a byte a pixel against RGBA8's four, chain included.
        self.assertLess(entry['bytes'], entry['decoded'] / 5)


if __name__ == '__main__':
    unittest.main()
