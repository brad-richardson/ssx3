"""Target encoding checks using an authored triangle and distinct resource IDs."""
import struct
import unittest
from tests.test_gamecube_scenery import fixture, gameplay_fixture
from gamecube_scenery import TrickyScenery
from gamecube_scenery_import import (compile_static, eligibility, model_record, untextured_materials,
                                     validate_reclamation, prune_geometry_texture_page)
from types import SimpleNamespace

IDENTITY_PLACEMENT = ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [0, 0, 0])


def untextured_scene(flags=1):
    """The authored triangle plus a second mesh on an untextured material."""
    source = TrickyScenery(fixture(), gameplay_fixture(flags))
    source.materials.append(dict(texture=0xffff, flipbook=-1, raw=b''))
    meshes = source.models[0]['parts'][0]['meshes']
    meshes.append(dict(material=len(source.materials)-1, strips=list(meshes[0]['strips'])))
    return source


class StaticSceneryImportTests(unittest.TestCase):
    def test_hidden_trigger_geometry_is_not_instantiated(self):
        source = TrickyScenery(fixture(), gameplay_fixture(0x1020))
        result, report = compile_static(source, [], {0: 0}, *IDENTITY_PLACEMENT, 0, 31, [0])
        self.assertFalse(any(e['kind'] == 3 for e, _ in result))
        self.assertEqual(report['hidden_source_instances'], [0])
        self.assertEqual(report['added_instances'], 0)
        self.assertEqual(report['instance_source_ids'], {})

    def test_the_source_map_names_the_donor_instance_behind_each_placement(self):
        # Visibility is applied here, so the map is not the identity and no
        # later pass can rebuild it: donor instance 0 is hidden and absent.
        source = TrickyScenery(fixture(), gameplay_fixture())
        hidden = dict(source.instances[0])
        hidden['gameplay'] = dict(hidden['gameplay'], visible=False)
        source.instances.insert(0, hidden)
        existing = [(dict(kind=3, rid=4, track=0), b'host')]
        _, report = compile_static(source, existing, {0: 0}, *IDENTITY_PLACEMENT, 0, 31, [0])
        self.assertEqual(report['hidden_source_instances'], [0])
        self.assertEqual(report['added_instances'], 1)
        # Keyed by the target RID the importer allocated, past the host's.
        self.assertEqual(report['instance_source_ids'], {'5': 1})

    def test_an_untextured_material_drops_its_mesh_and_not_the_model(self):
        source = untextured_scene()
        skip = untextured_materials(source)
        self.assertEqual(skip, {1})
        self.assertIsNone(eligibility(source.models[0], skip_materials=skip))
        records, report = compile_static(source, [], {0: 99}, *IDENTITY_PLACEMENT, 0, 31, [0],
                                         skip_materials=skip)
        self.assertEqual(report['untextured_materials'], [1])
        self.assertEqual(report['untextured_meshes_skipped'], {'0': 1})
        # One target material, referring to the one imported image, and one
        # mesh left in the model's geometry header.
        materials = [p for e, p in records if e['kind'] == 0]
        self.assertEqual([struct.unpack_from('>4H', p) for p in materials],
                         [(99, 65535, 65535, 65535)])
        model = next(p for e, p in records if e['kind'] == 2)
        geometry = struct.unpack_from('>I', model, 8)[0] + 16
        self.assertEqual(struct.unpack_from('>I', model, geometry + 28)[0], 1)

    def test_a_wholly_untextured_model_is_refused_rather_than_emitted_empty(self):
        source = untextured_scene()
        del source.models[0]['parts'][0]['meshes'][0]
        skip = untextured_materials(source)
        self.assertEqual(eligibility(source.models[0], skip_materials=skip),
                         'untextured material only')
        with self.assertRaisesRegex(ValueError, 'untextured material only'):
            model_record(source.models[0], lambda r: r, 0, 0, {}, skip_materials=skip)
        # Without the sentinel set it is still a perfectly ordinary model, so
        # the refusal comes from the target encoding, not from the geometry.
        self.assertIsNone(eligibility(source.models[0]))

    def test_donor_geometry_flag_does_not_enable_target_dynamic_path(self):
        source = TrickyScenery(fixture())
        source.models[0]['parts'][0]['flags'] = 1
        result, _, _ = model_record(source.models[0], lambda r: r, 0, 0, {0: 0})
        objects = struct.unpack_from('>I', result, 8)[0]
        geometry = struct.unpack_from('>I', result, objects + 4)[0]
        self.assertEqual(struct.unpack_from('>I', result, geometry + 24)[0], 0)

    def test_texture_residency_follows_cross_group_users_and_preserves_other_pages(self):
        def row(kind, rid, payload, track=8):
            return dict(kind=kind, rid=rid, track=track), bytes(payload)
        patch = bytearray(448)
        struct.pack_into('>IHH', patch, 412, 0x8001f, 901, 71)
        instance = bytearray(160)
        struct.pack_into('>II', instance, 116, 0x8001f, 0x08000007)
        model = bytearray(40)
        struct.pack_into('>I', model, 12, 32)
        struct.pack_into('>II', model, 32, 1, 0x08000009)
        images = [row(9, 901, b'terrain', 255), row(9, 902, b'scenery', 255),
                  row(9, 903, b'old host', 255), row(10, 71, b'lightmap', 255)]
        groups = {31: images, 32: [images[2]], 36: [row(1, 0, patch)],
                  37: [row(3, 0, instance), row(2, 7, model),
                       row(0, 9, struct.pack('>4H', 902, 65535, 65535, 65535))]}
        world = SimpleNamespace(index={'groups': [dict(index=i, kind_counts={e['kind']: 1 for e, _ in rs})
                                                  for i, rs in groups.items()]}, records=groups.__getitem__)
        kept, report = prune_geometry_texture_page(world, {}, 31)
        self.assertEqual([e['rid'] for e, _ in kept], [901, 902, 71])
        self.assertEqual(report['geometry_users'], 2)
        self.assertEqual(groups[32], [images[2]])
        with self.assertRaisesRegex(ValueError, 'Missing model'):
            prune_geometry_texture_page(world, {37: [row(3, 0, instance)]}, 31)

    def test_exact_vertex_indices_and_independent_buffer_ids(self):
        source = TrickyScenery(fixture())
        # Occupied target IDs differ by kind. A single shared next-ID counter
        # or swapped UV/normal fields would point at an unrelated buffer.
        original = [(dict(kind=k, rid=r, track=0), b'old') for k, r in
                    [(0, 8), (2, 11), (3, 10), (23, 7), (24, 9), (25, 4), (26, 2), (27, 6)]]
        terminal = (dict(kind=22, rid=0, track=0), b'')
        original.append((dict(kind=13, rid=0, track=0), b'metadata'))
        original.append(terminal)
        identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        records, report = compile_static(source, original, {0: 99}, identity, [10, 20, 30], 0, 31, [0])
        self.assertEqual(report['added_instances'], 1)
        self.assertEqual(records[-1], terminal)
        kinds = [e['kind'] for e, _ in records]
        buffers = [i for i, k in enumerate(kinds) if k >= 23]
        geometry = [i for i, k in enumerate(kinds) if k <= 12]
        metadata = [i for i, k in enumerate(kinds) if 13 <= k <= 22]
        self.assertLess(max(buffers), min(geometry))
        self.assertLess(max(geometry), min(metadata))
        lookup = {(e['kind'], e['rid']): p for e, p in records}
        self.assertEqual(struct.unpack('>3I', lookup[23, 8]), (5, 7, 3))
        model = lookup[2, 12]
        dl = struct.unpack_from('>I', model, 28)[0]
        self.assertEqual(struct.unpack_from('>BH', model, dl), (0x9a, 3))
        self.assertEqual([struct.unpack_from('>HBHH', model, dl+3+7*i) for i in range(3)],
                         [(0, 0, 0, 0), (1, 1, 1, 1), (2, 2, 2, 2)])
        instance = lookup[3, 11]
        self.assertEqual(struct.unpack_from('>3f', instance, 56), (10, 20, 30))
        self.assertEqual(struct.unpack_from('>2I', instance, 152), (10, 0))
        for key, payload in [((e['kind'], e['rid']), p) for e, p in original]:
            self.assertEqual(lookup[key], payload)

    def test_whole_unit_geometry_compensates_target_quarter_unit_format(self):
        data = fixture()
        data[500] = 0x9b
        model = TrickyScenery(data).models[0]
        result, _, scale = model_record(model, lambda r: r, 0, 0, {0: 0})
        self.assertEqual(scale, 4)
        geometry = struct.unpack_from('>I', result, 8)[0] + 16
        self.assertEqual(struct.unpack_from('>6f', result, geometry), (0, 0, 0, .25, .25, .25))

    def test_animated_model_is_rejected_instead_of_silently_freezing(self):
        source = TrickyScenery(fixture())
        source.models[0]['parts'][0]['animated'] = True
        with self.assertRaisesRegex(ValueError, 'animated'):
            model_record(source.models[0], lambda r: r, 0, 0, {0: 0})

    def test_reclaim_keeps_new_ids_separate_from_retired_host_ids(self):
        source = TrickyScenery(fixture())
        identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        original = [(dict(kind=2, rid=11, track=0), b'old')]
        records, report = compile_static(source, original, {0: 0}, identity, [0, 0, 0], 0, 31, [0], True)
        self.assertEqual([e['rid'] for e, _ in records if e['kind'] == 2], [12])
        self.assertEqual(report['reclaimed_host_bytes'], 3)
        original.append((dict(kind=3, rid=0, track=0), b'instance'))
        with self.assertRaisesRegex(ValueError, 'host instances'):
            compile_static(source, original, {0: 0}, identity, [0, 0, 0], 0, 31, [0], True)

    def test_reclaim_rejects_a_reference_from_another_location(self):
        instance = bytearray(160)
        struct.pack_into('>I', instance, 120, 0x0800000b)
        records = {0: [(dict(kind=2, rid=11, track=8), b'model')],
                   1: [(dict(kind=3, rid=0, track=9), bytes(instance))]}
        world = SimpleNamespace(index=dict(groups=[dict(index=0, kind_counts={2: 1}),
                                                   dict(index=1, kind_counts={3: 1})]),
                                records=lambda i: records[i])
        with self.assertRaisesRegex(ValueError, 'Retained resource.*retired kind 2'):
            validate_reclamation(world, 0, 8)


if __name__ == '__main__':
    unittest.main()
