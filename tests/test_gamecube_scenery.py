"""Scenery pointer/vertex validation using authored synthetic bytes."""
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gamecube_scenery import TrickyScenery, buffer_group, instance_gameplay, post_countdown_hidden
from gamecube_scenery_import import (compile_static, composed_matrices, composition, eligibility,
                                     geometry_parts, needs_composition, screen_compositions)


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

    def test_animated_as_static_admits_only_a_single_animated_geometry_part(self):
        root = part(meshes=0)
        animated = {'rid': 269, 'parts': [root, part(animated=True)]}
        self.assertEqual(eligibility(animated), 'animated')
        self.assertIsNone(eligibility(animated, animated_as_static=True))

    def test_animated_as_static_does_not_excuse_a_matrix_or_extra_parts(self):
        root = part(meshes=0)
        # Models 280-282: animated single part that also carries a matrix.
        self.assertEqual(eligibility({'rid': 280, 'parts': [root, part(animated=True, matrix=(1,)*16)]},
                                     animated_as_static=True), 'local matrix')
        # Models 49/86/90 stay multipart however the flag is set.
        self.assertEqual(eligibility({'rid': 49, 'parts': [root, part(), part(animated=True)]},
                                     animated_as_static=True), 'multipart')

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


IDENTITY = (1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1.)
# Row-vector layout, verified against the donor: rows 0-2 are the basis and
# row 3 the translation, the same convention instance_record already reads.
SPIN_Z = (0., 1., 0., 0., -1., 0., 0., 0., 0., 0., 1., 0., 10., 20., 30., 1.)


def geometry_part(vertices, matrix=None, parent=0xffffffff, material=0, animated=False):
    """A part whose one mesh draws one strip of (position, normal, uv) triples."""
    return {'parent': parent, 'matrix': matrix, 'animated': animated, 'bounds': (0.,)*6,
            'meshes': [{'material': material,
                        'strips': [{'opcode': 0x9a, 'vertices': list(vertices)}]}]}


class Scene:
    """The subset of TrickyScenery the static compiler reads."""

    def __init__(self, models, positions, instances=None):
        self.models = [dict(rid=i, parts=parts) for i, parts in enumerate(models)]
        self.positions = list(positions)
        self.uvs = [(0, 0)] * 4
        self.normals = [(16384, 0, 0), (0, 16384, 0)]
        self.materials = [dict(texture=5, flipbook=-1)]
        self.instances = instances if instances is not None else [
            dict(model=i, matrix=IDENTITY, bounds=(0.,)*6, gameplay=dict(visible=True))
            for i in range(len(models))]


def display_positions(payload):
    """Every position index the compiled model's display lists reference.

    Each mesh's list is padded to 32 bytes, so skip the NOPs between them.
    """
    at, out = struct.unpack_from('>I', payload, 28)[0], []
    while at < len(payload):
        if payload[at] != 0x9a:
            at += 1
            continue
        count = struct.unpack_from('>H', payload, at+1)[0]
        at += 3
        out += [struct.unpack_from('>HBHH', payload, at+7*i)[0] for i in range(count)]
        at += 7*count
    return out


def compile_scene(scene, **kwargs):
    records, report = compile_static(scene, [], {5: 700}, [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                                     [0, 0, 0], 8, 0x0008001f, list(range(len(scene.models))),
                                     **kwargs)
    models = [p for e, p in records if e['kind'] == 2]
    shared = [v for e, p in records if e['kind'] == 25
              for v in struct.iter_unpack('>3h', p)]
    return models, shared, report


class LocalMatrixTests(unittest.TestCase):
    """(a3): part matrices baked into transformed vertex copies."""

    def test_the_flag_is_what_admits_a_matrix_or_a_second_part(self):
        one = {'rid': 280, 'parts': [part(meshes=0), part(matrix=SPIN_Z)]}
        many = {'rid': 49, 'parts': [part(meshes=0), part(), part(matrix=SPIN_Z)]}
        self.assertEqual(eligibility(one), 'local matrix')
        self.assertEqual(eligibility(many), 'multipart')
        self.assertTrue(needs_composition(one) and needs_composition(many))
        self.assertIsNone(eligibility(one, compose_local_matrices=True))
        self.assertIsNone(eligibility(many, compose_local_matrices=True))

    def test_a_scaling_matrix_is_refused_rather_than_rotating_its_normals(self):
        stretched = list(IDENTITY)
        stretched[0] = 2.0
        model = {'rid': 7, 'parts': [part(matrix=tuple(stretched))]}
        self.assertEqual(eligibility(model, compose_local_matrices=True),
                         'non-orthonormal local matrix')

    def test_a_single_parts_matrix_is_applied_to_its_own_position_copies(self):
        # Donor quarter units: stored (4, 0, 0) is the donor-unit point (1, 0, 0).
        # SPIN_Z turns it a quarter turn about Z and adds (10, 20, 30).
        scene = Scene([[geometry_part([(0, 0, 0), (1, 0, 0), (2, 1, 0)])],
                       [geometry_part([(0, 0, 0), (1, 0, 0), (2, 1, 0)], matrix=SPIN_Z)]],
                      [(0, 0, 0), (4, 0, 0), (0, 4, 0)])
        composed = composition(scene, scene.models[1])
        self.assertEqual(composed['vertices'][0, 0], (40, 80, 120))
        self.assertEqual(composed['vertices'][0, 1], (40, 84, 120))
        self.assertEqual(composed['vertices'][0, 2], (36, 80, 120))
        self.assertEqual(composed['parts'], 1)
        self.assertIsNone(composition(scene, scene.models[0]))
        models, shared, report = compile_scene(scene, compose_local_matrices=True)
        # The shared array keeps its original entries: every other model still
        # indexes them. The transformed copies are appended after them.
        self.assertEqual(shared[:3], [(0, 0, 0), (4, 0, 0), (0, 4, 0)])
        self.assertEqual(shared[3:], [(40, 80, 120), (40, 84, 120), (36, 80, 120)])
        self.assertEqual(display_positions(models[0]), [0, 1, 2])
        self.assertEqual(display_positions(models[1]), [3, 4, 5])
        self.assertEqual(report['local_matrix_composed'], {'1': 1})
        # Bounds follow the transformed copies, in the model's local units.
        self.assertEqual(struct.unpack_from('>6f', models[1], 56), (9., 20., 30., 10., 21., 30.))

    def test_an_out_of_range_composition_is_refused_and_reported(self):
        far = list(IDENTITY)
        far[12] = 9000.0  # Donor units; the 1x encoding stores quarter units.
        scene = Scene([[geometry_part([(0, 0, 0)], matrix=tuple(far))]], [(0, 0, 0)])
        with self.assertRaisesRegex(ValueError, 'signed 16-bit'):
            composition(scene, scene.models[0])
        omitted = {}
        self.assertIn('signed 16-bit', screen_compositions(scene, omitted)[0])
        self.assertEqual(omitted, {0: 'local matrix out of range'})
        with self.assertRaisesRegex(ValueError, 'signed 16-bit'):
            compile_scene(scene, compose_local_matrices=True)

    def test_a_child_part_composes_through_its_parent(self):
        child = list(IDENTITY)
        child[12], child[13] = 5.0, 0.0
        parts = [geometry_part([(0, 0, 0)]),
                 geometry_part([(1, 0, 0)], matrix=SPIN_Z, parent=0),
                 geometry_part([(1, 0, 0)], matrix=tuple(child), parent=1)]
        scene = Scene([parts], [(0, 0, 0), (4, 0, 0)])
        matrices = composed_matrices(scene.models[0])
        self.assertEqual(matrices[0], IDENTITY)
        self.assertEqual(matrices[1], SPIN_Z)
        # child x parent: the child's +5 X is spun onto +Y before the parent's
        # own translation, so (1,0,0) lands at (10, 20+5+1, 30).
        self.assertEqual(tuple(round(v, 6) for v in matrices[2][12:15]), (10., 25., 30.))
        composed = composition(scene, scene.models[0])
        self.assertEqual(composed['vertices'][0, 0], (0, 0, 0))
        self.assertEqual(composed['vertices'][1, 1], (40, 84, 120))
        self.assertEqual(composed['vertices'][2, 1], (40, 104, 120))
        self.assertEqual(composed['parts'], 3)
        # One rigid target part carries every composed part's meshes.
        models, shared, report = compile_scene(scene, compose_local_matrices=True)
        self.assertEqual(struct.unpack_from('>I', models[0], 4)[0], 1)
        # The untransformed copy is the value the shared array already holds,
        # so it is reused instead of appended.
        self.assertEqual(display_positions(models[0]), [0, 2, 3])
        self.assertEqual(shared[2:], [(40, 84, 120), (40, 104, 120)])
        self.assertEqual(report['local_matrix_composed'], {'0': 3})

    def test_composition_is_off_unless_asked_for(self):
        scene = Scene([[geometry_part([(0, 0, 0)], matrix=SPIN_Z)]], [(0, 0, 0)])
        with self.assertRaisesRegex(ValueError, 'local matrix'):
            compile_scene(scene)
