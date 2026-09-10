from pathlib import Path
import random
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from probe_worlds import refpack
from refpack_encode import encode
from build_world_experiment import bump_patch, coefficients, control_points, serialize_resources
from build_test_images import replace_ranges
from probe_worlds import patch_point, resource_records


class EncodeTests(unittest.TestCase):
    def test_known_encodings(self):
        self.assertEqual(encode(b''), b'\x10\xfb\0\0\0\xfc')
        self.assertEqual(encode(b'ABC'), b'\x10\xfb\0\0\3\xffABC')
        self.assertEqual(encode(b'AAAA'), b'\x10\xfb\0\0\4\x01\0A\xfc')

    def test_roundtrips_varied_inputs(self):
        rng = random.Random(42)
        examples = [rng.randbytes(n) for n in (1, 4, 111, 112, 113, 1028, 32760)]
        examples += [bytes(81920), b'abcdefgh' * 2000, bytes(range(256)) * 400]
        # Exercise long-distance references with a source prefix that does not
        # recur within the short or medium command distance limits.
        for distance in (1024, 1025, 16384, 16385, 131072):
            prefix = rng.randbytes(distance)
            examples.append(prefix + prefix[:512])
        for data in examples:
            with self.subTest(length=len(data)):
                packed = encode(data)
                actual, consumed = refpack(packed)
                self.assertEqual(actual, data)
                self.assertEqual(consumed, len(packed))


class RebuildTests(unittest.TestCase):
    def patch(self):
        # A 1000 x 1000 plane at Z=0, with intentionally generous existing bounds.
        p = bytearray(432)
        struct.pack_into('<4f',p,64+14*16,1000,0,0,0)
        struct.pack_into('<4f',p,64+11*16,0,1000,0,0)
        struct.pack_into('<4f',p,320,500,500,0,1000)
        struct.pack_into('<6f',p,344,0,0,-200,1000,1000,200)
        return bytes(p)

    def test_bump_preserves_edges_and_unknown_bytes(self):
        p = self.patch()
        result, info = bump_patch(p,100)
        c = coefficients(result)
        self.assertEqual(patch_point(c,.5,.5),(500,500,100))
        self.assertEqual(info['max_edge_displacement'],0)
        changed = {i for record in info['float_changes'] for i in range(record['offset'],record['offset']+4)}
        self.assertTrue(all(a==b for i,(a,b) in enumerate(zip(p,result)) if i not in changed))
        self.assertTrue(all(-200<=pt[2]<=200 for pt in control_points(c)))

    def test_bump_rejects_expansion_and_invalid_height(self):
        for height in (500,float('nan'),float('inf'),0):
            with self.subTest(height=height),self.assertRaises(ValueError):
                bump_patch(self.patch(),height)

    def test_resource_serialization_preserves_unknown_types(self):
        raw=b'\xee\3\0\0\x04\x56\x34\x12abc'
        self.assertEqual(serialize_resources(list(resource_records(raw))),raw)

    def test_iso_range_substitution_across_copy_boundaries(self):
        source=b'abcdefghijklmno'
        replacements=[(3,b'XYZ123'),(12,b'!!')]
        actual=b''.join(replace_ranges(source[i:i+4],i,replacements) for i in range(0,len(source),4))
        self.assertEqual(actual,b'abcXYZ123jkl!!o')


if __name__ == '__main__':
    unittest.main()
