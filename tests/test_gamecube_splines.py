"""Authored curves exercise topology, coordinate and distance ABI boundaries."""
import math
import struct
import unittest

from gamecube_splines import (NULL, audit_conversion, curve_bounds, curve_point, encode_spline,
                              polynomial, read_tricky_splines, similarity_scale)
from gamecube_spline_import import replace_splines


def fixture():
    # Three straight segments, deliberately stored out of traversal order.
    nbd = bytearray(208 + 3*128)
    header = [0]*40
    header[0], header[8], header[9] = 0x00161d03, 1, 3
    header[23:26] = [160, 208, len(nbd)]
    struct.pack_into('>40I', nbd, 0, *header)
    struct.pack_into('>6f4I', nbd, 160, 0, 0, 0, 300, 0, 0, 0, 3, 2, NULL)
    order = [2, 0, 1]
    for j, i in enumerate(order):
        o = 208 + 128*i
        c = [0, 0, 0, 0]*2 + [100, 0, 0, 0, j*100, 0, 0, 1]
        struct.pack_into('>20f3I8fI', nbd, o, *c, 0, 0, 1, 0,
                         order[j-1] if j else NULL, order[j+1] if j < 2 else NULL, 0,
                         j*100, 0, 0, (j+1)*100, 0, 0, 100, j*100, 0)
    gsf = bytearray(84)
    struct.pack_into('>I', gsf, 0, 0x00021e00)
    struct.pack_into('>IIHHI', gsf, 68, 1, 76, 1, 1, 13)
    return nbd, gsf


TEMPLATE = bytes(136) + bytes.fromhex('157259000f000000')
IDENTITY = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


class SplineTests(unittest.TestCase):
    def test_reader_traverses_links_instead_of_storage_order(self):
        source = read_tricky_splines(*fixture())
        self.assertEqual([s['index'] for s in source[0]['segments']], [2, 0, 1])
        self.assertFalse(source[0]['closed'])
        data = encode_spline(source[0], IDENTITY, [0, 0, 0], 0x08000003, TEMPLATE)
        self.assertEqual(len(data), 48+3*144)
        # The GC runtime rebuilds a sequential linked list; encode that order.
        for j in range(3):
            o = 48+144*j
            self.assertEqual(struct.unpack_from('>3I', data, o+92),
                             (j-1 if j else NULL, j+1 if j < 2 else NULL, 0x08000003))
            self.assertEqual(struct.unpack_from('>f', data, o+60)[0], j*100)

    def test_reader_rejects_shared_wrong_parent_and_nonreciprocal_edges(self):
        for offset, value in [(208+128*2+84, 2), (208+128*2+88, 1), (208+80, NULL)]:
            nbd, gsf = fixture()
            struct.pack_into('>I', nbd, offset, value)
            with self.assertRaises(ValueError):
                read_tricky_splines(nbd, gsf)

    def test_closed_loop_wraps_both_links(self):
        nbd, gsf = fixture()
        # Last stored segment (index 1) returns from x=200 to x=0.
        struct.pack_into('>f', nbd, 208+128+32, -200)
        struct.pack_into('>f', nbd, 208+128+116, 200)
        struct.pack_into('>f', nbd, 208+128+72, .5)
        struct.pack_into('>I', nbd, 208+128*2+80, 1)
        struct.pack_into('>I', nbd, 208+128+84, 2)
        spline = read_tricky_splines(nbd, gsf)[0]
        self.assertTrue(spline['closed'])
        data = encode_spline(spline, IDENTITY, [0, 0, 0], 0, TEMPLATE)
        self.assertEqual(struct.unpack_from('>I', data, 48+92)[0], 2)
        self.assertEqual(struct.unpack_from('>I', data, 48+2*144+96)[0], 0)

    def test_reader_rejects_bad_extents_nonfinite_and_mismatched_style_table(self):
        nbd, gsf = fixture()
        for broken_nbd, broken_gsf in [(nbd[:-1], gsf), (nbd, gsf[:-1])]:
            with self.assertRaises(ValueError):
                read_tricky_splines(broken_nbd, broken_gsf)
        struct.pack_into('>f', nbd, 208+12, math.nan)
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            read_tricky_splines(nbd, gsf)

    def test_curve_and_all_inverse_distance_powers_transform_consistently(self):
        spline = read_tricky_splines(*fixture())[0]
        seg = spline['segments'][0]
        seg['coefficients'] = [(2, 4, -3, 0), (-5, 2, 9, 0), (100, 30, 20, 0), (2, 3, 4, 1)]
        seg['inverse_distance'] = [.012, -.034, .7, .02]
        matrix, translation, scale = [[0, -.55, 0], [.55, 0, 0], [0, 0, .55]], [1e5, -2e5, 3e5], .55
        data = encode_spline(spline, matrix, translation, 0x08000001, TEMPLATE)
        values = struct.unpack_from('>16f', data, 60)
        encoded = [values[k:k+4] for k in range(0, 16, 4)]
        inverse = struct.unpack_from('>4f', data, 48+76)
        for step in range(101):
            t = step/100
            source = curve_point(seg['coefficients'], t)
            actual = curve_point(encoded, t)
            expected = [translation[0]-scale*source[1], translation[1]+scale*source[0], translation[2]+scale*source[2]]
            for a, b in zip(actual, expected):
                self.assertAlmostEqual(a, b, delta=.02)
            distance = step*2.4
            self.assertAlmostEqual(polynomial(inverse, distance*scale),
                                   polynomial(seg['inverse_distance'], distance/100), delta=1e-6)

    def test_bounds_enclose_hidden_mid_curve_crest_after_float_rounding(self):
        # Both endpoints are at y=0; endpoint bounds lose the entire crest.
        c = [(0, 0, 0), (0, -400, 0), (100, 400, 0), (1e6, 1e6, 0)]
        low, high = curve_bounds(c)
        self.assertGreaterEqual(high[1], 1e6+100)
        for step in range(1001):
            p = curve_point(c, step/1000)
            self.assertTrue(all(low[k] <= p[k] <= high[k] for k in range(3)))

    def test_audit_rejects_damaged_emitted_bounds_and_distance_units(self):
        source = read_tricky_splines(*fixture())
        encoded = encode_spline(source[0], IDENTITY, [0, 0, 0], 0, TEMPLATE)
        report = audit_conversion(source, [encoded], IDENTITY, [0, 0, 0])
        self.assertEqual(report['samples'], 3*257)
        for offset, value in [(48+116, 50), (48+84, 1)]:
            bad = bytearray(encoded)
            struct.pack_into('>f', bad, offset, value)
            with self.assertRaisesRegex(ValueError, 'audit failed'):
                audit_conversion(source, [bad], IDENTITY, [0, 0, 0])

    def test_shear_nonuniform_scale_and_unknown_style_fail_closed(self):
        for m in [[[1, .1, 0], [0, 1, 0], [0, 0, 1]], [[1, 0, 0], [0, 2, 0], [0, 0, 1]]]:
            with self.assertRaisesRegex(ValueError, 'uniform'):
                similarity_scale(m, [0, 0, 0])
        spline = read_tricky_splines(*fixture())[0]
        spline['style'] = (1, 1, 999)
        with self.assertRaisesRegex(ValueError, 'style'):
            encode_spline(spline, IDENTITY, [0, 0, 0], 0, TEMPLATE)

    def test_replacement_updates_binding_count_and_preserves_unrelated_resources(self):
        source = read_tricky_splines(*fixture())
        host = encode_spline(source[0], IDENTITY, [0, 0, 0], 0x08000000, TEMPLATE)
        script = bytearray(140)
        script[:4] = bytes.fromhex('00100000')
        struct.pack_into('>3I', script, 56, 1, 92, 132)
        struct.pack_into('>2I', script, 84, 2, 132)
        struct.pack_into('>I', script, 92, 96)
        script[96:132] = bytes.fromhex('004e554c0000001400000024000000242aff0000ffffffec000000000000000200000000')
        script[132:] = bytes.fromhex('0003000a00030009')
        def row(kind, rid, data):
            return dict(kind=kind, track=8, rid=rid), bytes(data)
        original = [row(1, 0, b'terrain'), row(8, 0, host), row(8, 1, host),
                    row(16, 0, script), row(22, 0, b'')]
        result, report = replace_splines(original, source, IDENTITY, [10, 20, 30], 8)
        self.assertEqual(report['replaced_host_splines'], 2)
        self.assertEqual(report['added_splines'], 1)
        self.assertEqual(result[0], original[0])
        self.assertEqual(result[-1], original[-1])
        changed = next(p for e, p in result if e['kind'] == 16)
        self.assertEqual(struct.unpack_from('>II', changed, 84), (1, 132))
        self.assertEqual(changed[132:], bytes.fromhex('0003000a'))
        self.assertEqual(changed[:84], script[:84])
        self.assertEqual(changed[88:132], script[88:132])
        # An active host event program must not be rebound to a donor rail.
        script[112] = 1
        original[-2] = row(16, 0, script)
        with self.assertRaisesRegex(ValueError, 'Disable host'):
            replace_splines(original, source, IDENTITY, [0, 0, 0], 8)


if __name__ == '__main__':
    unittest.main()
