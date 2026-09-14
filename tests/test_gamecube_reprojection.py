"""Research proof controls; optional NumPy/Pillow dependencies live in a private venv."""
import importlib.util
from pathlib import Path
import sys
import json
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
try:
    import numpy as np
    from gamecube_reprojection_warp import (matrix34,predict_view,project_pixels,warp,
                                             footprint_radius,load_capture)
except ImportError:
    np=None
from gamecube_reprojection import replace_once


class CapturePatchTests(unittest.TestCase):
    def test_injection_rejects_missing_and_duplicate_anchor(self):
        self.assertEqual(replace_once('a b','a','x'),'x b')
        for source in ('b','a a'):
            with self.assertRaises(ValueError):replace_once(source,'a','x')


@unittest.skipIf(np is None,'Offline reprojection proof requires NumPy/Pillow')
class WarpTests(unittest.TestCase):
    def setUp(self):
        p=np.zeros((4,4));p[0,0]=1;p[1,1]=1;p[2,2]=-1/99;p[2,3]=-100/99;p[3,2]=-1
        self.meta=dict(viewport=[320,-264,16777215,662,606,16777215],scissor_offset=[342,342],
                       pixel_center_correction=[0,0,1,0],vertex_depth_range=False,reversed_depth=True,projection=p.ravel().tolist())
        self.depth=np.full((12,16),.5,dtype=np.float32)
        self.color=np.arange(12*16*4,dtype=np.uint8).reshape(12,16,4)

    def test_identity_preserves_every_pixel(self):
        image,mask,motion=warp(self.color,self.depth,self.meta,np.eye(4))
        np.testing.assert_array_equal(image,self.color)
        self.assertTrue(mask.all());self.assertLess(np.max(motion),1e-10)

    def test_camera_translation_has_expected_pixel_shift(self):
        delta=np.eye(4);delta[0,3]=.1
        tx,ty,distance=project_pixels(self.depth,self.meta,delta)
        base_x=np.tile(np.arange(16),12)
        np.testing.assert_allclose(tx-base_x,16*.1/(2*distance),atol=1e-10)
        np.testing.assert_allclose(ty,np.repeat(np.arange(12),16),atol=1e-10)

    def test_known_world_plane_depth_and_shift(self):
        # Analytic GX projection for near=1, far=100: depth at z=-10.
        distance=10.0
        maximum=16777215/16777216
        self.depth[:]=maximum*(100/99)*(1-1/distance)
        delta=np.eye(4);delta[0,3]=1
        tx,ty,reconstructed=project_pixels(self.depth,self.meta,delta)
        np.testing.assert_allclose(reconstructed,distance,atol=2e-5)
        np.testing.assert_allclose(tx-np.tile(np.arange(16),12),.8,atol=2e-6)

    def test_known_plane_with_metal_vertex_depth_range(self):
        # Metal cannot reverse viewport depth. The oversized GX range uses
        # vertex correction; its stored depth is -GX NDC depth in this case.
        maximum=16777215/16777216
        self.meta.update(vertex_depth_range=True,reversed_depth=False,
                         viewport=[320,-264,16777216,662,606,16777216],
                         pixel_center_correction=[0,0,1/maximum,1-1/maximum])
        self.depth[:]=(100/10-1)/99
        delta=np.eye(4);delta[0,3]=1
        tx,_,distance=project_pixels(self.depth,self.meta,delta)
        np.testing.assert_allclose(distance,10,atol=2e-5)
        np.testing.assert_allclose(tx-np.tile(np.arange(16),12),.8,atol=2e-6)

    def test_depth_changes_translation_parallax(self):
        self.depth[:6]=.1;self.depth[6:]=.9
        delta=np.eye(4);delta[0,3]=.1
        tx,_,_=project_pixels(self.depth,self.meta,delta)
        motion=(tx-np.tile(np.arange(16),12)).reshape(12,16)
        self.assertGreater(motion[:6].mean(),motion[6:].mean()*5)

    def test_half_step_predicts_pose_not_view_translation_naively(self):
        prev=np.eye(4);curr=np.eye(4);curr[0,3]=-2
        pred=predict_view(prev,curr)
        self.assertAlmostEqual(pred[0,3],-3)
        np.testing.assert_allclose(pred[:3,:3],np.eye(3))

    def test_cut_and_nonrigid_camera_fail_closed(self):
        for current in (np.diag([2.,1,1,1]),np.array([[1.,0,0,501],[0,1,0,0],[0,0,1,0],[0,0,0,1]])):
            with self.assertRaises(ValueError):predict_view(np.eye(4),current)

    def test_capture_rejects_missing_scene_depth_and_mismatched_attachment(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);manifest=folder/'frame-1.jsonl'
            rows=[dict(event='frame',frame_id=1,final_ok=True),
                  dict(event='split',color_ok=True,depth_ok=True)]
            for suffix,format in [('world.rgba',0),('final.rgba',0),('depth.f32',11)]:
                name=f'frame-1-{suffix}'
                rows.append(dict(event='image',file=name,width=2,height=2,format=format))
                (folder/name).write_bytes(bytes(16))
            manifest.write_text('\n'.join(json.dumps(r) for r in rows))
            with self.assertRaisesRegex(ValueError,'scene depth'):load_capture(manifest)
            np.array([.1,.2,.3,.4],dtype='<f4').tofile(folder/'frame-1-depth.f32')
            rows[2]['file']='frame-2-world.rgba'
            manifest.write_text('\n'.join(json.dumps(r) for r in rows))
            with self.assertRaisesRegex(ValueError,'match frame'):load_capture(manifest)

    def test_uncovered_pixels_remain_visible(self):
        delta=np.eye(4);delta[0,3]=.5
        image,covered,_=warp(self.color,self.depth,self.meta,delta)
        self.assertFalse(covered.all())
        np.testing.assert_array_equal(image[~covered],np.tile([255,0,255,255],((~covered).sum(),1)))

    def test_footprint_splat_closes_magnification_cracks_it_cannot_lose(self):
        # Moving toward a flat wall magnifies it, so a point splat leaves cracks
        # that are sampling artifacts rather than newly exposed scenery.
        self.depth[:]=16777215/16777216*(100/99)*(1-1/10)
        delta=np.eye(4);delta[2,3]=4
        _,points,_=warp(self.color,self.depth,self.meta,delta)
        _,covered,_=warp(self.color,self.depth,self.meta,delta,footprint=True)
        self.assertFalse(points.all())
        self.assertTrue(covered[points].all(),'a footprint must still cover every point splat')
        self.assertGreater(covered.sum(),points.sum())

    def test_footprint_does_not_stretch_across_a_depth_discontinuity(self):
        # Two planes at 10 and 40, approached by 5. Each magnifies at its own
        # rate, so the step over the silhouette is wider than the far plane's.
        scale=16777215/16777216*(100/99)
        self.depth[:,:8]=scale*(1-1/10.);self.depth[:,8:]=scale*(1-1/40.)
        delta=np.eye(4);delta[2,3]=5
        tx,ty,distance=project_pixels(self.depth,self.meta,delta)
        radius=footprint_radius(tx,ty,distance,self.depth.shape).reshape(self.depth.shape)
        columns=tx.reshape(self.depth.shape)[6]
        self.assertGreater(np.diff(columns)[7],np.diff(columns)[8])
        # Each plane grows by its own magnification: 2.0 and 40/35 pixels wide.
        np.testing.assert_allclose(radius[:,:8],1.,atol=1e-6)
        np.testing.assert_allclose(radius[:,8:],40/35/2,atol=1e-6)

if __name__=='__main__':unittest.main()
