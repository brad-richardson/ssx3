"""Scenery pointer/vertex validation using authored synthetic bytes."""
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_scenery import TrickyScenery, buffer_group, instance_gameplay, post_countdown_hidden
from gamecube_scenery_import import eligibility, geometry_parts


def gameplay_fixture(flags=1):
    # One NoCountDown function calls one instance effect, which hides it.
    b = bytearray(168)
    struct.pack_into('>I', b, 0, 0x00021e00)
    struct.pack_into('>10I', b, 36, 1, 100, 1, 76, 1, 140, 1, 164, 0, 168)
    struct.pack_into('>2I16s', b, 76, 1, 0, b'NoCountDown')
    struct.pack_into('>2I', b, 100, 1, 16)
    struct.pack_into('>4I', b, 108, 7, 16, 0, 0)
    struct.pack_into('>4I', b, 124, 0, 16, 5, 2)
    # U2 differs deliberately, to catch the PS2/GC halfword order trap.
    struct.pack_into('>2f2HI4h', b, 140, 0, .5, flags, 0x1234, 0xffffffff, 0, -1, -1, 0)
    return b


def fixture():
    b = bytearray(580)
    h = [0]*40
    h[0] = 0x00161d03
    h[3] = h[5] = h[6] = h[11] = 1
    h[18], h[19], h[20], h[21], h[22] = 160, 300, 300, 372, 380
    h[26], h[27], h[28], h[33], h[34], h[35], h[36] = 380, 384, 500, 500, 532, 550, 562
    struct.pack_into('>40I', b, 0, *h)
    struct.pack_into('>16f', b, 160, *[float(i % 5 == 0) for i in range(16)])
    struct.pack_into('>i', b, 368, -1)
    struct.pack_into('>2I', b, 372, 1, 0)
    struct.pack_into('>7I', b, 384, 116, 1, 28, 0, 0, 0, 0)
    struct.pack_into('>6I', b, 412, 0xffffffff, 24, 24, 24, 0, 0xffffffff)
    struct.pack_into('>I6f4I', b, 436, 64, 0, 0, 0, 1, 1, 1, 0, 1, 1, 44)
    struct.pack_into('>5I', b, 480, 4, 16, 0, 0, 32)
    struct.pack_into('>BH9H', b, 500, 0x9a, 3, 0, 0, 0, 1, 1, 1, 2, 2, 2)
    struct.pack_into('>9h', b, 532, 0, 0, 0, 4, 0, 0, 0, 4, 0)
    struct.pack_into('>6h', b, 550, 0, 0, 4096, 0, 0, 4096)
    struct.pack_into('>9h', b, 562, 0, 0, 16384, 0, 0, 16384, 0, 0, 16384)
    return b


def part(meshes=1, animated=False, matrix=None, parent=0xffffffff):
    """A donor model part; an empty one stands for the transform-free root."""
    mesh = {'material': 0, 'strips': [{'opcode': 0x9a, 'vertices': [((0, 0, 0), 0)]}]}
    return {'parent': parent, 'matrix': matrix, 'animated': animated,
            'meshes': [dict(mesh) for _ in range(meshes)], 'bounds': (0,)*6}


class EligibilityTests(unittest.TestCase):
    """Every multipart donor model carries one meshless root node."""

    def test_a_meshless_transform_free_root_is_not_a_second_part(self):
        model = {'rid': 132, 'parts': [part(meshes=0), part()]}
        self.assertEqual(len(geometry_parts(model)), 1)
        self.assertIsNone(eligibility(model))

    def test_a_meshless_part_carrying_a_matrix_still_counts(self):
        # An empty part with its own matrix is a real transform, not a root.
        model = {'rid': 49, 'parts': [part(meshes=0, matrix=(1,)*16), part()]}
        self.assertEqual(len(geometry_parts(model)), 2)
        self.assertEqual(eligibility(model), 'multipart')

    def test_two_geometry_parts_are_still_multipart(self):
        self.assertEqual(eligibility({'rid': 49, 'parts': [part(meshes=0), part(), part()]}),
                         'multipart')

    def test_a_single_geometry_part_is_still_judged_on_its_own_properties(self):
        root = part(meshes=0)
        self.assertEqual(eligibility({'rid': 269, 'parts': [root, part(animated=True)]}),
                         'animated')
        self.assertEqual(eligibility({'rid': 280, 'parts': [root, part(matrix=(1,)*16)]}),
                         'local matrix')


class SceneryTests(unittest.TestCase):
    def test_gc_flipbook_is_a_signed_word_and_frames_have_checked_extents(self):
        b = fixture()
        # Insert a flipbook before the model pointers; model-relative offsets
        # remain intact while the header's absolute geometry offsets move.
        struct.pack_into('>I', b, 10*4, 1)
        struct.pack_into('>I', b, 13*4, 74)
        struct.pack_into('>I', b, 25*4, 380)
        for index in (26, 27, 28, 33, 34, 35, 36):
            struct.pack_into('>I', b, index*4, struct.unpack_from('>I', b, index*4)[0]+24)
        b[380:380] = struct.pack('>6I', 5, 69, 70, 71, 72, 73)
        struct.pack_into('>i', b, 368, 0)
        scene = TrickyScenery(b)
        self.assertEqual(scene.flipbooks, [(69, 70, 71, 72, 73)])
        self.assertEqual(scene.materials[0]['flipbook'], 0)
        # A halfword reader at +70 would incorrectly accept this as ID zero.
        struct.pack_into('>i', b, 368, 0x10000)
        with self.assertRaisesRegex(ValueError, 'outside flipbook'):
            TrickyScenery(b)
        struct.pack_into('>i', b, 368, 0)
        struct.pack_into('>I', b, 400, 74)
        with self.assertRaisesRegex(ValueError, 'outside texture'):
            TrickyScenery(b)
        struct.pack_into('>I', b, 400, 73)
        struct.pack_into('>I', b, 380, 6)
        with self.assertRaisesRegex(ValueError, 'Scenery span'):
            TrickyScenery(b)

    def test_gameplay_visibility_uses_gc_flags_not_ps2_halfword_order(self):
        gsf = gameplay_fixture(0x1020)
        p = instance_gameplay(gsf, 1)[0]
        self.assertFalse(p['visible'])
        self.assertTrue(p['player_collision'])
        struct.pack_into('>H', gsf, 148, 1)
        self.assertTrue(instance_gameplay(gsf, 1)[0]['visible'])
        struct.pack_into('>I', gsf, 164, 1)
        with self.assertRaisesRegex(ValueError, 'outside property'):
            instance_gameplay(gsf, 1)

    def test_post_countdown_state_follows_authored_instance_effect(self):
        gsf = gameplay_fixture()
        self.assertEqual(post_countdown_hidden(gsf, 1), [0])
        initial = TrickyScenery(fixture(), gsf)
        racing = TrickyScenery(fixture(), gsf, phase='racing')
        self.assertTrue(initial.instances[0]['gameplay']['visible'])
        self.assertFalse(racing.instances[0]['gameplay']['visible'])
        # Unknown commands must not be silently treated as hide commands.
        struct.pack_into('>I', gsf, 136, 9)
        with self.assertRaisesRegex(ValueError, 'Unsupported post-countdown'):
            post_countdown_hidden(gsf, 1)

    def test_visibility_rejects_malformed_extents_and_recursive_functions(self):
        with self.assertRaisesRegex(ValueError, 'extents'):
            instance_gameplay(gameplay_fixture(), 2)
        gsf = gameplay_fixture()
        struct.pack_into('>3I', gsf, 108, 21, 12, 0)
        with self.assertRaisesRegex(ValueError, 'Cyclic'):
            post_countdown_hidden(gsf, 1)

    def test_buffer_references_match_loader_with_distinct_ids(self):
        data = buffer_group(position=0x08000002, uv=0x08000009, normal=0x08000007)
        # Loader order, deliberately different from the stored order.
        self.assertEqual(struct.unpack_from('>I', data, 0)[0], 0x08000002)
        self.assertEqual(struct.unpack_from('>I', data, 8)[0], 0x08000007)
        self.assertEqual(struct.unpack_from('>I', data, 4)[0], 0x08000009)

    def test_model_relative_pointers_and_attribute_order(self):
        scene = TrickyScenery(fixture())
        mesh = scene.models[0]['parts'][0]['meshes'][0]
        self.assertEqual(mesh['strips'][0]['vertices'], [(0, 0, 0), (1, 1, 1), (2, 2, 2)])
        self.assertEqual(scene.instances[0]['model'], 0)
        self.assertEqual(scene.positions[1], (4, 0, 0))
        self.assertEqual(scene.uvs[1], (4096, 0))
        self.assertEqual(scene.normals[1], (0, 0, 16384))

    def test_preserves_alternate_position_format(self):
        b = fixture()
        b[500] = 0x9b
        self.assertEqual(TrickyScenery(b).models[0]['parts'][0]['meshes'][0]['strips'][0]['opcode'], 0x9b)

    def test_rejects_pointer_outside_owning_model(self):
        b = fixture()
        struct.pack_into('>I', b, 480, 100)
        with self.assertRaisesRegex(ValueError, 'span'):
            TrickyScenery(b)

    def test_rejects_truncated_strip_and_bad_vertex_indices(self):
        for offset, fmt, value in [(501, 'H', 65535), (503, 'H', 3), (505, 'H', 3), (507, 'H', 3)]:
            with self.subTest(offset=offset):
                b = fixture()
                struct.pack_into('>'+fmt, b, offset, value)
                with self.assertRaises(ValueError):
                    TrickyScenery(b)

    def test_rejects_invalid_instance_and_cyclic_parent(self):
        for offset, value in [(224, 1), (412, 0)]:
            b = fixture()
            struct.pack_into('>I', b, offset, value)
            with self.assertRaises(ValueError):
                TrickyScenery(b)

    def test_rejects_nonfinite_transform(self):
        b = fixture()
        struct.pack_into('>f', b, 160, float('nan'))
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            TrickyScenery(b)
