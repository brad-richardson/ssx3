"""Donor texture/lightmap import into GameCube SSX 3 world records (synthetic data)."""
import struct
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_textures import (shape_images, world_image_record, tricky_bindings, bind_patch,  # noqa: E402
                               decode, PALETTE_HEADER, WORLD_HEADER, import_course_textures)
from gamecube_materials import convert_lightmap


def shape_container(images):
    """Build a SHPG with the observed entry layout: 16-byte image header, pixels, optional 0x32 palette."""
    body = bytearray()
    table = bytearray()
    base = 16 + 8 * len(images)
    for i, (kind, w, h, pixels, palette) in enumerate(images):
        table += f'{i:04}'.encode() + struct.pack('>I', base + len(body))
        size = 32 + len(pixels) if kind == 0x19 else 16 + len(pixels)
        body += bytes([kind]) + size.to_bytes(3, 'big') + struct.pack('>HHI', w, h, 0) + struct.pack('<I', 0x20) + pixels
        if kind == 0x19:
            body += bytes(16) + bytes([0x32]) + (528).to_bytes(3, 'big') + struct.pack('>HH', 256, 1) + bytes(8) + palette
        body += bytes([0x70]) + bytes(31)
    return b'SHPG' + struct.pack('<I', base + len(body)) + struct.pack('>I', len(images)) + b'TAG!' + table + body


def synthetic_nbd(patches, n_textures=4):
    header = bytearray(160)
    struct.pack_into('>I', header, 8, len(patches))
    struct.pack_into('>I', header, 52, n_textures)
    struct.pack_into('>I', header, 68, 160)
    body = bytearray()
    for tex, lm, rect, uv in patches:
        rec = bytearray(448)
        struct.pack_into('>4f', rec, 0, *rect)
        for k, (u, v) in enumerate(uv):
            struct.pack_into('>4f', rec, 16 + 16 * k, u, v, 1.0, 1.0)
        struct.pack_into('>hh', rec, 428, tex, lm)
        body += rec
    return bytes(header + body)


class TextureImportTests(unittest.TestCase):
    def test_import_keeps_stock_textures_and_resolves_identically_in_either_load_order(self):
        def record(kind, rid, payload):
            return (dict(kind=kind, track=255, rid=rid), payload)
        groups = {0: [record(9, 5, b'stock shared texture')],
                  1: [record(9, 1, b'pinned texture'), record(10, 2, b'pinned lightmap')],
                  2: [], 3: [record(9, 5, b'stock shared texture')]}
        world = SimpleNamespace(index=dict(global_kind_counts={9: 6, 10: 3}, groups=[
                                    dict(index=i, kind_counts={e['kind']: 1 for e, _ in records})
                                    for i, records in groups.items()]),
                                records=lambda i: list(groups[i]),
                                location=lambda _: dict(group_start=0, last_group=2))
        img = dict(type=0x1e, width=8, height=8, pixels=bytes(32), palette=None)
        lm = dict(type=0x14, width=8, height=8, pixels=bytes([0xff]) * 128, palette=None)
        binding = dict(texture=0, lightmap=0, uv=[(0, -1), (0, 0), (1, -1), (1, 0)],
                       lightmap_rect=(0, 0, 1, 1))
        added = [(dict(kind=1, track=8, rid=0), bytes(430))]
        replaced, patches, report = import_course_textures(world, 'A', 1, added, [binding], [img], [lm])
        self.assertEqual(set(replaced), {1})
        self.assertEqual(replaced[1][:2], groups[1])
        texture_rid, lightmap_rid = struct.unpack_from('>HH', patches[0][1], 416)
        self.assertEqual((texture_rid, lightmap_rid), (6, 3))
        self.assertEqual(report['dropped_stock_records'], {})
        for order in [(replaced[1], groups[0], groups[3]), (groups[3], groups[0], replaced[1])]:
            loaded = {(e['kind'], e['rid']): p for group in order for e, p in group}
            self.assertEqual(loaded[9, texture_rid], world_image_record(img))
            self.assertEqual(loaded[10, lightmap_rid], world_image_record(convert_lightmap(lm)[0]))
            self.assertEqual(loaded[9, 5], b'stock shared texture')

    def test_shape_images_reads_each_format(self):
        cmpr = bytes(range(32))                 # 8x8 CMPR = 4 blocks of 8 bytes
        rgb = struct.pack('>16H', *[0x8000 | (i * 31 // 15) << 10 for i in range(16)])  # 4x4 RGB5A3, red ramp
        ci8 = bytes(range(32))                  # 8x4 CI8
        palette = struct.pack('>256H', *[0x8000 | i >> 3 for i in range(256)])
        data = shape_container([(0x1e, 8, 8, cmpr, None), (0x15, 4, 4, rgb, None), (0x19, 8, 4, ci8, palette)])
        images = shape_images(data)
        self.assertEqual([(i['type'], i['width'], i['height'], len(i['pixels'])) for i in images],
                         [(0x1e, 8, 8, 32), (0x15, 4, 4, 32), (0x19, 8, 4, 32)])
        self.assertEqual(images[2]['palette'], palette)
        self.assertEqual(decode(images[1])[0], (0, 0, 0, 255))
        self.assertEqual(decode(images[1])[15], (255, 0, 0, 255))
        self.assertEqual(decode(images[2])[8 * 3 + 7], (0, 0, 3 * 255 // 31, 255))  # index 31 -> palette blue 3

    def test_world_record_header_matches_stock_layout(self):
        img = dict(type=0x1e, width=32, height=32, pixels=bytes(512), palette=None)
        rec = world_image_record(img)
        self.assertEqual(len(rec), WORLD_HEADER + 512)
        self.assertEqual(rec[:20], bytes.fromhex('1e000000002000200000000030000000') + struct.pack('>I', 0x20))
        self.assertEqual(rec[20:32], bytes(12))
        ci8 = dict(type=0x19, width=8, height=8, pixels=bytes(64), palette=bytes(512))
        rec = world_image_record(ci8)
        self.assertEqual(int.from_bytes(rec[1:4], 'big'), WORLD_HEADER + 64)
        self.assertEqual(rec[WORLD_HEADER + 64:WORLD_HEADER + 64 + 32], PALETTE_HEADER)
        self.assertEqual(len(rec), WORLD_HEADER + 64 + 32 + 512)
        with self.assertRaises(ValueError):
            world_image_record(dict(type=0x1e, width=32, height=32, pixels=bytes(100), palette=None))

    def test_tricky_bindings_read_texture_lightmap_and_uv(self):
        uv = [(0, 0), (1, 0), (0, -1), (1, -1)]
        nbd = synthetic_nbd([(2, 1, (0.5, 0.25, 0.0625, 0.0625), uv), (0, 0, (0, 0, 0.0625, 0.0625), uv)])
        b = tricky_bindings(nbd)
        self.assertEqual([(x['texture'], x['lightmap']) for x in b], [(2, 1), (0, 0)])
        self.assertEqual(b[0]['lightmap_rect'], (0.5, 0.25, 0.0625, 0.0625))
        self.assertEqual([tuple(p) for p in b[0]['uv']], uv)
        with self.assertRaises(ValueError):
            tricky_bindings(synthetic_nbd([(9, 0, (0, 0, 0, 0), uv)]))

    def test_bind_patch_writes_words_and_shifts_v(self):
        payload = bytes(430)
        out = bind_patch(payload, 300, 90, 31, [(0, 0), (1, 0), (0, -1), (1, -1)], (0.5, 0.25, 0.0625, 0.0625))
        self.assertEqual(struct.unpack_from('>8f', out, 32), (0, 1, 1, 1, 0, 0, 1, 0))
        u, v, w, h = struct.unpack_from('>4f', out, 16)
        self.assertAlmostEqual(u, 0.5 + 0.5 / 128)
        self.assertAlmostEqual(v, 0.25 + 0.5 / 128)
        self.assertAlmostEqual(w, 7 / 128)
        self.assertEqual(struct.unpack_from('>I', out, 412)[0], 0x80000 | 31)
        self.assertEqual(struct.unpack_from('>HH', out, 416), (300, 90))
        self.assertEqual(len(out), 430)



if __name__ == '__main__':
    unittest.main()
