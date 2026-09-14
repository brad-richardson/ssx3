"""Paired-background HUD alpha controls; optional NumPy/Pillow live in a private venv."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
try:
    import numpy as np
    from gamecube_reprojection_hud import analyze,background,same_frame,solve
except ImportError:
    np=None

WIDTH=HEIGHT=8


def write_capture(folder,frame_id,world,final,depth,clear,**frame):
    """One capture manifest and its attachments, as the GPU hook writes them."""
    folder.mkdir(parents=True,exist_ok=True)
    name=f'frame-{frame_id}'
    manifest=folder/f'{name}.jsonl'
    rows=[dict(event='frame',schema=1,frame_id=frame_id,final_ok=True,xfb_rect=[0,0,640,528],
               draws=10,perspective=8,ortho=2,late_perspective=0,**frame),
          dict(event='split',color_ok=True,depth_ok=True,camera_valid=True,camera_base=1,
               view=[1,0,0,0,0,1,0,0,0,0,1,0],projection=[1]*16,viewport=[320,-264,1,0,0,1],
               scissor_offset=[0,0],vertex_depth_range=False,reversed_depth=True,
               pixel_center_correction=[0,0,1,0],efb_pixel_format=0,hud_clear=clear)]
    for suffix,array in (('world.rgba',world),('final.rgba',final),('depth.f32',depth)):
        rows.append(dict(event='image',file=f'{name}-{suffix}',width=WIDTH,height=HEIGHT,
                         format=11 if suffix.endswith('f32') else 0))
        array.tofile(folder/f'{name}-{suffix}')
    manifest.write_text('\n'.join(json.dumps(r) for r in rows))
    return manifest


def composite(world,foreground,transmission):
    return np.clip(foreground+transmission*world,0,255).astype(np.uint8)


@unittest.skipIf(np is None,'Offline HUD proof requires NumPy/Pillow')
class HudAlphaTests(unittest.TestCase):
    def setUp(self):
        rng=np.random.default_rng(7)
        # load_capture rejects a constant depth buffer as a missing scene.
        self.depth=np.linspace(.2,.8,HEIGHT*WIDTH,dtype='<f4').reshape(HEIGHT,WIDTH)
        self.world=np.dstack([rng.integers(0,256,(HEIGHT,WIDTH,3),dtype=np.uint8),
                              np.full((HEIGHT,WIDTH,1),255,np.uint8)])
        # A left half that hides the scene, a right half that half-covers it.
        self.transmission=np.zeros((HEIGHT,WIDTH,3));self.transmission[:,4:]=.5
        self.foreground=np.zeros((HEIGHT,WIDTH,3));self.foreground[:,:4]=200;self.foreground[:,4:]=40
        self.opaque=np.full((HEIGHT,WIDTH,1),255,np.uint8)

    def capture(self,folder,clear,frame_id=5,world=None):
        world=self.world if world is None else world
        background=np.zeros((HEIGHT,WIDTH,3)) if clear is None else np.array(
            [(clear>>16)&255,(clear>>8)&255,clear&255],dtype=float)
        under=world[:,:,:3].astype(float) if clear is None else np.broadcast_to(
            background,(HEIGHT,WIDTH,3))
        final=np.dstack([composite(under,self.foreground,self.transmission),self.opaque])
        return write_capture(folder,frame_id,world,final,self.depth,clear)

    def test_recovers_alpha_and_agrees_with_the_untouched_run(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            dark=self.capture(folder/'dark',0x000000)
            light=self.capture(folder/'light',0xffffff)
            natural=self.capture(folder/'natural',None)
            report=analyze(dark,light,natural,folder/'out')
            self.assertTrue(report['hud_alpha_layer'])
            self.assertLessEqual(report['reconstruction_check']['max_abs_error'],2)
            # Half the frame is opaque, half transmits 50%: mean alpha is 0.75.
            self.assertAlmostEqual(report['alpha_mean_where_covered'],.75,places=2)
            self.assertAlmostEqual(report['covered_fraction'],1.,places=6)

    def test_a_blend_that_reads_the_background_non_linearly_fails_the_check(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            dark=self.capture(folder/'dark',0x000000)
            light=self.capture(folder/'light',0xffffff)
            natural=self.capture(folder/'natural',None)
            # A multiply blend is affine in neither background constant.
            rows=(folder/'natural'/'frame-5.jsonl').read_text()
            product=(self.world[:,:,:3].astype(float)**2/255)
            np.dstack([product.astype(np.uint8),self.opaque]).tofile(
                folder/'natural'/'frame-5-final.rgba')
            (folder/'natural'/'frame-5.jsonl').write_text(rows)
            report=analyze(dark,light,natural,folder/'out')
            self.assertFalse(report['hud_alpha_layer'])
            self.assertGreater(report['reconstruction_check']['max_abs_error'],2)

    def test_rejects_unpaired_uncleared_and_divergent_captures(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            dark=self.capture(folder/'dark',0x000000)
            with self.assertRaisesRegex(ValueError,'too close'):
                solve(*[__import__('gamecube_reprojection_warp').load_capture(p) for p in
                        (dark,self.capture(folder/'near',0x202020))])
            plain=self.capture(folder/'plain',None)
            with self.assertRaisesRegex(ValueError,'known background'):
                background(__import__('gamecube_reprojection_warp').load_capture(plain))
            other=self.capture(folder/'other',0xffffff,world=self.world[::-1])
            load=__import__('gamecube_reprojection_warp').load_capture
            with self.assertRaisesRegex(ValueError,'different world'):
                same_frame(load(dark),load(other))
            elsewhere=self.capture(folder/'elsewhere',0xffffff,frame_id=6)
            with self.assertRaisesRegex(ValueError,'different frames'):
                same_frame(load(dark),load(elsewhere))


if __name__=='__main__':
    unittest.main()
