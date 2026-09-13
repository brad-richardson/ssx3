import struct
import unittest

from gamecube_surfaces import source_patches, transfer_surfaces
from gamecube_terrain import make_record
from import_terrain import transform_coefficients

MATRIX = [[0., -.55, 0.], [.55, 0., 0.], [0., 0., .55]]
TRANSLATION = [100., -200., 300.]


def fixture(surfaces=(0, 5, 1)):
    raw = bytearray(160 + 448 * len(surfaces))
    struct.pack_into('>I', raw, 0, 0x00161d03)
    struct.pack_into('>I', raw, 8, len(surfaces))
    struct.pack_into('>2I', raw, 68, 160, len(raw))
    records = [(dict(kind=2, track=8, rid=0, size=3), b'foo')]
    template = bytearray(430)
    struct.pack_into('>3H', template, 8, 0, 9, 0x12)
    for i, surface in enumerate(surfaces):
        coeffs = [[0., 0., 0.] for _ in range(16)]
        coeffs[14] = [200., 0., -25.]
        coeffs[15] = [i * 1000., 200., -300.]
        for j, c in enumerate(coeffs):
            struct.pack_into('>4f', raw, 160+448*i+80+16*j, *c, 1.)
        struct.pack_into('>I', raw, 160+448*i+360, surface)
        p = make_record(template, transform_coefficients(coeffs, MATRIX, TRANSLATION), i+40, 8)
        records.append((dict(kind=1, track=8, rid=i+40, size=430), p))
    return bytes(raw), records


class SurfaceTests(unittest.TestCase):
    def test_reset_mapping_preserves_flags_geometry_and_other_records(self):
        raw, records = fixture()
        out, report = transfer_surfaces(records, raw, MATRIX, TRANSLATION)
        self.assertEqual(out[0], records[0])
        self.assertEqual(out[2:], records[2:])
        self.assertEqual(out[1][1], records[1][1][:8] + b'\0\0\0\x0b' + records[1][1][12:])
        self.assertEqual(report['geometry_matches'], 3)
        self.assertEqual(report['changed_source_patches'], [0])
        self.assertEqual(report['retained_template_surface_counts'], {1: 1, 5: 1})
        again, receipt = transfer_surfaces(out, raw, MATRIX, TRANSLATION)
        self.assertEqual(again, out)
        self.assertEqual(receipt['changed_source_patches'], [])

    def test_migrate_legacy_wipeout_surface_to_direct_reset(self):
        raw, records = fixture()
        e,p = records[1]
        records[1] = (e,p[:8]+b'\0\x12'+p[10:])
        out, _ = transfer_surfaces(records, raw, MATRIX, TRANSLATION)
        self.assertEqual(struct.unpack_from('>2H',out[1][1],8),(0,11))

    def test_reordered_or_wrong_placement_fails_before_ordinal_assignment(self):
        raw, records = fixture()
        for bad in [records[:-2]+records[-2:][::-1], records[:-1]]:
            with self.assertRaises(ValueError):
                transfer_surfaces(bad, raw, MATRIX, TRANSLATION)
        with self.assertRaisesRegex(ValueError, 'geometry differs'):
            transfer_surfaces(records, raw, MATRIX, [0, 0, 0])

    def test_template_control_is_identical_and_explicit_limit_is_checked(self):
        raw, records = fixture()
        out, report = transfer_surfaces(records, raw, MATRIX, TRANSLATION, profile='template')
        self.assertEqual(out, records)
        self.assertEqual(report['mapped_reset_patches'], [])
        out, report = transfer_surfaces(records[:2], raw, MATRIX, TRANSLATION, limit=1)
        self.assertEqual(report['geometry_matches'], 1)
        with self.assertRaises(ValueError):
            transfer_surfaces(records, raw, MATRIX, TRANSLATION, limit=4)

    def test_malformed_source_extents_and_nonfinite_geometry_fail(self):
        raw, _ = fixture()
        variants = [raw[:159], raw[:-1], b'\0'*len(raw)]
        bad = bytearray(raw); struct.pack_into('>I', bad, 72, len(raw)-4); variants.append(bad)
        bad = bytearray(raw); struct.pack_into('>f', bad, 240, float('nan')); variants.append(bad)
        for bad in variants:
            with self.assertRaises(ValueError):
                source_patches(bad)

    def test_unknown_profile_and_duplicate_ids_fail(self):
        raw, records = fixture()
        with self.assertRaises(ValueError):
            transfer_surfaces(records, raw, MATRIX, TRANSLATION, profile='guess')
        records[2] = (dict(records[2][0], rid=records[1][0]['rid']), records[2][1])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            transfer_surfaces(records, raw, MATRIX, TRANSLATION)
