import copy
import struct
import unittest

from gamecube_collision import encode_collision, read_collision, read_tricky_collision, collision_instance_transform
from gamecube_collision_import import bind_static, validate_static_bindings, segment_intersects_box
from gamecube_scenery import TrickyScenery
from gamecube_scenery_import import composition, instance_record
from race_course import path_geometry
from tests.test_gamecube_scenery import fixture, gameplay_fixture


def mesh(count=3):
    return dict(vertices=[(float(i),float(i%3),0.,1.) for i in range(count)],
                triangles=[(i,i+1,i+2) for i in range(0,count-2,3)],
                normals=[(0.,0.,1.,0.) for i in range(0,count-2,3)])


def expanded(parts):
    return [(tuple(part['vertices'][i] for i in tri),normal) for part in parts
            for tri,normal in zip(part['triangles'],part['normals'])]


class CollisionTests(unittest.TestCase):
    def test_uniform_scale_preserves_rendering_and_repairs_rigid_collision_inverse(self):
        data=bytearray(160)
        matrix=[0.,.55,0.,0., -.55,0.,0.,0., 0.,0.,.55,0., -113459.,17177.,-228594.,1.]
        struct.pack_into('>16f',data,8,*matrix);struct.pack_into('>f',data,124,1.)
        struct.pack_into('>I',data,112,0x08000258)
        with self.assertRaisesRegex(ValueError,'orthonormal'):collision_instance_transform(data)
        fixed=collision_instance_transform(data,normalize=True)
        original=struct.unpack_from('>16f',data,8);basis=struct.unpack_from('>16f',fixed,8)
        scale=struct.unpack_from('>f',fixed,124)[0]
        point=[100.,-200.,25.]
        world=[original[12+k]+sum(original[4*j+k]*point[j] for j in range(3)) for k in range(3)]
        transformed=[basis[12+k]+scale*sum(basis[4*j+k]*point[j] for j in range(3)) for k in range(3)]
        for before,after in zip(world,transformed):self.assertAlmostEqual(before,after,places=5)
        # Match the engine's transpose-based inverse followed by 1/scalar.
        local=[sum(basis[4*j+k]*(world[k]-basis[12+k]) for k in range(3))/scale for j in range(3)]
        wrong=[sum(original[4*j+k]*(world[k]-original[12+k]) for k in range(3)) for j in range(3)]
        for before,after in zip(point,local):self.assertAlmostEqual(before,after,places=5)
        self.assertGreater(abs(wrong[0]-point[0]),50)
        self.assertEqual(fixed[:8],data[:8]);self.assertEqual(fixed[72:124],data[72:124])
        self.assertEqual(fixed[128:],data[128:])

    def test_nonuniform_scale_and_shear_require_separate_conversion(self):
        for matrix in ([1.,0.,0.,0.,0.,2.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.],
                       [1.,0.,0.,0.,.1,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]):
            data=bytearray(160);struct.pack_into('>16f',data,8,*matrix);struct.pack_into('>f',data,124,1.)
            with self.assertRaisesRegex(ValueError,'nonuniform scale or shear'):
                collision_instance_transform(data,normalize=True)

    def test_reset_corridor_intersection_checks_segment_interior_and_parallel_axes(self):
        low,high=[-1,-1,-1],[1,1,1]
        self.assertTrue(segment_intersects_box([-10,0,0],[10,0,0],low,high))
        self.assertTrue(segment_intersects_box([0,0,0],[0,0,0],low,high))
        self.assertFalse(segment_intersects_box([-10,2,0],[10,2,0],low,high))
        self.assertFalse(segment_intersects_box([2,0,0],[3,0,0],low,high))
    def test_partition_preserves_triangles_normals_and_geometry_compensation(self):
        source=mesh(300)
        out=read_collision(encode_collision([source],geometry_scale=4))
        self.assertEqual(len(out),2)
        self.assertTrue(all(len(p['vertices'])<=256 for p in out))
        for p in out:p['vertices']=[tuple(v*4 for v in q[:3])+(1.,) for q in p['vertices']]
        self.assertEqual(expanded(out),[( (points[0],points[2],points[1]),normal)
                                        for points,normal in expanded([source])])

    def test_target_winding_reverses_indices_but_preserves_outward_normal(self):
        source=dict(vertices=[(0.,0.,0.,1.),(10.,0.,0.,1.),(0.,10.,0.,1.)],
                    triangles=[(0,1,2)],normals=[(0.,0.,1.,0.)])
        encoded=encode_collision([source]);out=read_collision(encoded)[0]
        self.assertEqual(out['triangles'],[(0,2,1)])
        self.assertEqual(out['normals'],source['normals'])
        bad=bytearray(encoded);bad[36:39]=bytes([0,1,2])
        with self.assertRaisesRegex(ValueError,'winding'):read_collision(bad)

    def test_bbox_and_index_corruption_fail(self):
        data=encode_collision([mesh(33)])
        bad=bytearray(data);bad[36]=255
        with self.assertRaisesRegex(ValueError,'absent vertex'):read_collision(bad)
        bad=bytearray(data);bbox=16+struct.unpack_from('>I',data,24)[0]
        struct.pack_into('>f',bad,bbox,10000.)
        with self.assertRaisesRegex(ValueError,'bounds miss'):read_collision(bad)
        with self.assertRaises(ValueError):read_collision(data[:-1])

    def test_empty_malformed_and_nonfinite_source_meshes_fail(self):
        for source in [dict(vertices=[],triangles=[],normals=[]),
                       dict(mesh(),triangles=[(0,1,99)]),
                       dict(mesh(),normals=[(float('nan'),0.,0.,0.)])]:
            with self.assertRaises(ValueError):encode_collision([source])
        with self.assertRaises(ValueError):read_tricky_collision(bytes(76))

    def test_source_pointer_extent_and_triangle_reference_validation(self):
        raw=bytearray(208)
        struct.pack_into('>I',raw,0,0x00021e00)
        struct.pack_into('>2I',raw,28,1,76);struct.pack_into('>I',raw,48,88)
        struct.pack_into('>3I',raw,76,128,80,1)
        struct.pack_into('>3I',raw,128,1,3,0)
        struct.pack_into('>3I',raw,140,0,1,2)
        for i,p in enumerate(mesh()['vertices']):struct.pack_into('>4f',raw,152+16*i,*p)
        # Use a correctly sized body (12+12+48+16 = 88).
        raw+=bytes(8);struct.pack_into('>I',raw,80,88)
        struct.pack_into('>4f',raw,200,0.,0.,1.,0.)
        self.assertEqual(read_tricky_collision(raw),[[mesh()]])
        bad=bytearray(raw);struct.pack_into('>I',bad,140,3)
        with self.assertRaisesRegex(ValueError,'absent vertex'):read_tricky_collision(bad)
        with self.assertRaises(ValueError):read_tricky_collision(raw[:-1])

    def test_dense_instance_bindings_preserve_positions_and_rail_bytes(self):
        scene=TrickyScenery(fixture(),gameplay_fixture(0x21))
        scene.instances.append(copy.deepcopy(scene.instances[0]))
        for src in scene.instances:src['gameplay'].update(collision_mode=1,collision_or_physics=0,effect_slot=-1)
        identity=[[1,0,0],[0,1,0],[0,0,1]];translation=[10,20,30]
        recipe=dict(track=8,matrix=identity,translation=translation,
                    scenery=dict(source_models=[0],instance_source_ids={5:0,9:1}))
        rows=[(dict(kind=2,rid=7,track=8,size=8),struct.pack('>2I',0x08000007,1))]
        for rid in [5,9]:
            p=instance_record(scene.instances[0],identity,translation,1,lambda i:8<<24|i,rid,7,6,31)
            rows.append((dict(kind=3,rid=rid,track=8,size=len(p)),p))
        script=bytearray(136);struct.pack_into('>I',script,0,0x00100000)
        struct.pack_into('>3I',script,56,1,92,132);struct.pack_into('>I',script,92,96)
        script[96:132]=bytes.fromhex('004e554c0000001400000024000000242aff0000ffffffec000000000000000200000000')
        struct.pack_into('>2I',script,84,1,132);script[132:]=bytes.fromhex('0003000a')
        rows.append((dict(kind=16,rid=0,track=8,size=len(script)),bytes(script)))
        out,report=bind_static(rows,scene,[[mesh()]],recipe)
        instances=[(e,p) for e,p in out if e['kind']==3]
        self.assertEqual([e['rid'] for e,p in instances],[0,1])
        for (_,p),(_,old) in zip(instances,rows[1:3]):
            self.assertEqual(p[:112],old[:112]);self.assertEqual(p[116:],old[116:])
        self.assertEqual(report['collision_resources'],1)
        bindings=next(p for e,p in out if e['kind']==16)
        self.assertEqual(struct.unpack_from('>I',bindings,68)[0],2)
        prop_base=struct.unpack_from('>I',bindings,64)[0]
        self.assertEqual(struct.unpack_from('>I',bindings,prop_base+8)[0],0xffffffff)
        self.assertEqual(bindings[-4:],script[-4:])
        corrupted=bytearray(bindings);struct.pack_into('>I',corrupted,prop_base+8,0x08000007)
        invalid=[(e,bytes(corrupted)) if e['kind']==16 else (e,p) for e,p in out]
        with self.assertRaisesRegex(ValueError,'effect callback'):validate_static_bindings(invalid,8)
        _,multipart=bind_static(rows,scene,[[mesh(),mesh()]],recipe)
        self.assertEqual(multipart['enabled_instances'],[])
        self.assertEqual(multipart['collision_resources'],0)
        self.assertEqual(multipart['skipped_instances']['multipart-collision-needs-matching-render-parts'],2)
        bounds=struct.unpack_from('>6f',rows[1][1],88)
        y,z=(bounds[1]+bounds[4])/2,(bounds[2]+bounds[5])/2
        points=[(bounds[0]-1000,y,z),(bounds[3]+1000,y,z)]
        route=struct.pack('<9I',2,100,4,50,101,4,1,1,0)+path_geometry(points)
        aip=struct.pack('<2I',0x69696969,1)+route+struct.pack('<3I',0,0,0)
        guarded,protection=bind_static(rows+[(dict(kind=14,rid=0,track=8,size=len(aip)),aip)],scene,[[mesh()]],recipe)
        self.assertEqual(protection['enabled_instances'],[])
        self.assertEqual(len(protection['protected_reset_instances']),2)
        self.assertEqual(next(p for e,p in guarded if e['kind']==14),aip)
        scene.instances[0]['gameplay']['visible']=False
        with self.assertRaisesRegex(ValueError,'Hidden helper'):bind_static(rows,scene,[[mesh()]],recipe)


class ComposedLocalMatrixTests(unittest.TestCase):
    """A composed model's placement must be re-derived the same way here."""

    # Row-vector: a quarter turn about Z, then a translation.
    SPIN = (0., 1., 0., 0., -1., 0., 0., 0., 0., 0., 1., 0., 10., 20., 30., 1.)

    def rows(self, scene, bounds):
        identity, translation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], [10, 20, 30]
        recipe = dict(track=8, matrix=identity, translation=translation,
                      scenery=dict(source_models=[0], instance_source_ids={0: 0}))
        p = instance_record(scene.instances[0], identity, translation, 1, lambda i: 8 << 24 | i,
                            0, 7, 6, 31, bounds)
        script = bytearray(136)
        struct.pack_into('>I', script, 0, 0x00100000)
        struct.pack_into('>3I', script, 56, 1, 92, 132)
        struct.pack_into('>I', script, 92, 96)
        script[96:132] = bytes.fromhex('004e554c0000001400000024000000242aff0000ffffffec000000000000000200000000')
        struct.pack_into('>2I', script, 84, 1, 132)
        script[132:] = bytes.fromhex('0003000a')
        return [(dict(kind=2, rid=7, track=8, size=8), struct.pack('>2I', 0x08000007, 1)),
                (dict(kind=3, rid=0, track=8, size=len(p)), p),
                (dict(kind=16, rid=0, track=8, size=len(script)), bytes(script))], recipe

    def scene(self):
        scene = TrickyScenery(fixture(), gameplay_fixture(0x21))
        scene.models[0]['parts'][0]['matrix'] = self.SPIN
        scene.instances[0]['gameplay'].update(collision_mode=1, collision_or_physics=0, effect_slot=-1)
        return scene

    def test_composed_bounds_agree_and_the_donor_authored_ones_do_not(self):
        scene = self.scene()
        composed = composition(scene, scene.models[0])
        rows, recipe = self.rows(scene, composed['bounds'])
        _, report = bind_static(rows, scene, [[mesh()]], recipe)
        self.assertEqual(report['local_matrix_composed_models'], [0])
        self.assertEqual(len(report['enabled_instances']), 1)
        # The donor's authored instance bounds predate the part matrix, so a
        # placement built from them must not be accepted as this one.
        stale, recipe = self.rows(scene, None)
        with self.assertRaisesRegex(ValueError, 'placement/source mismatch'):
            bind_static(stale, scene, [[mesh()]], recipe)
