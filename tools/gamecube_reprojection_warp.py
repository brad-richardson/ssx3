#!/usr/bin/env python3
"""Offline camera/depth warp proof (requires numpy and Pillow).

The warp is a depth-tested forward splat; holes remain visible in magenta. Each
source pixel can splat as a point or as its screen-space footprint, which
approximates rasterizing the depth buffer as a mesh and separates sampling
cracks from real disocclusion. Neither is a realtime backend, an inpainted
image, or a latency benchmark.
The HUD residual image is diagnostic only: it cannot recover alpha from one composite.
"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from PIL import Image, ImageDraw


def matrix34(values):
    result=np.eye(4);result[:3]=np.asarray(values,dtype=float).reshape(3,4)
    if not np.isfinite(result).all() or abs(np.linalg.det(result[:3,:3]))<1e-8:
        raise ValueError('Invalid view matrix')
    return result


def predict_view(previous,current,alpha=.5):
    """Constant translation/angular velocity extrapolation of rigid camera poses."""
    a,b=np.linalg.inv(previous),np.linalg.inv(current)
    for rotation in (a[:3,:3],b[:3,:3]):
        if not np.allclose(rotation.T@rotation,np.eye(3),atol=1e-3) or np.linalg.det(rotation)<0:
            raise ValueError('Camera candidate is not a proper rigid transform')
    delta=b[:3,:3]@a[:3,:3].T
    angle=np.arccos(np.clip((np.trace(delta)-1)/2,-1,1))
    distance=np.linalg.norm(b[:3,3]-a[:3,3])
    if angle>.35 or distance>500:
        raise ValueError('Camera cut/teleport: skip synthesis')
    if angle<1e-8:half=np.eye(3)
    else:
        axis=np.array([delta[2,1]-delta[1,2],delta[0,2]-delta[2,0],delta[1,0]-delta[0,1]])/(2*np.sin(angle))
        x,y,z=axis;cross=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
        half=np.eye(3)+np.sin(alpha*angle)*cross+(1-np.cos(alpha*angle))*(cross@cross)
    predicted=b.copy();predicted[:3,:3]=half@b[:3,:3]
    predicted[:3,3]=b[:3,3]+alpha*(b[:3,3]-a[:3,3])
    return np.linalg.inv(predicted)


def depth_range(meta):
    wd,ht,zrange,xorig,yorig,far=meta['viewport']
    low,high=(far-zrange)/16777216,far/16777216
    if meta['vertex_depth_range']:
        low,high=(16777215/16777216,0) if zrange<0 and meta['reversed_depth'] else (0,16777215/16777216)
    return (high,low) if meta['reversed_depth'] else (1-high,1-low)


def project_pixels(depth,meta,delta):
    """Invert pinned Dolphin GX projection/depth/viewport then project a camera delta."""
    height,width=depth.shape
    wd,ht,zrange,xorig,yorig,far=meta['viewport']
    offx,offy=meta['scissor_offset'];cx,cy,cz,cw=meta['pixel_center_correction']
    if wd<=0 or ht>=0 or cz==0:
        raise ValueError('Unsupported mirrored/degenerate viewport')
    x,y=np.meshgrid(np.arange(width)+.5,np.arange(height)+.5)
    # EFB dimensions are 640 x 528 at scale 1; raw viewport coords include scissor origin.
    ndcx=((x*640/width-(xorig-offx))/wd)+cx
    ndcy=((y*528/height-(yorig-offy))/ht)+cy
    near,far=depth_range(meta)
    if abs(far-near)<1e-8:raise ValueError('Degenerate depth range')
    gxz=(cw-(depth-near)/(far-near))/cz
    clip=np.stack((ndcx,ndcy,gxz,np.ones_like(depth)),axis=-1).reshape(-1,4)
    projection=np.asarray(meta['projection']).reshape(4,4)
    view=clip@np.linalg.inv(projection).T
    moved=view@delta.T
    target=moved@projection.T
    with np.errstate(divide='ignore',invalid='ignore'):
        ndc=target[:,:3]/target[:,3:4]
        tx=((ndc[:,0]-cx)*wd+xorig-offx)*width/640-.5
        ty=((ndc[:,1]-cy)*ht+yorig-offy)*height/528-.5
        distance=-moved[:,2]/moved[:,3]
    return tx,ty,distance


FOOTPRINT_LIMIT=2.0  # Cap the splat so a mapping singularity cannot smear the frame.
SURFACE_DEPTH_RATIO=.02  # Neighbours farther apart than this in depth are separate surfaces.


def footprint_radius(tx,ty,distance,shape,limit=FOOTPRINT_LIMIT):
    """Half-extent each source pixel covers after the warp, from its own neighbours.

    A depth discontinuity is a silhouette rather than a stretched surface, so the
    step across it is discarded instead of splatting foreground over background.
    """
    height,width=shape
    x,y,z=(a.reshape(height,width) for a in (tx,ty,distance))
    radius=np.full((height,width),.5)
    for axis in (0,1):
        step=np.maximum(np.abs(np.diff(x,axis=axis)),np.abs(np.diff(y,axis=axis)))
        lo,hi=(z[:-1],z[1:]) if axis==0 else (z[:,:-1],z[:,1:])
        same=np.abs(hi-lo)<=SURFACE_DEPTH_RATIO*np.minimum(np.abs(lo),np.abs(hi))
        step=np.where(np.isfinite(step)&same,step/2,0)
        low=np.s_[:-1,:] if axis==0 else np.s_[:,:-1]
        high=np.s_[1:,:] if axis==0 else np.s_[:,1:]
        radius[low]=np.maximum(radius[low],step);radius[high]=np.maximum(radius[high],step)
    return np.clip(radius,.5,limit).ravel()


def splat(color,tx,ty,distance,shape,radius=None):
    """Depth-tested forward scatter. Closest source wins each destination pixel.

    Deterministic: ties in distance are broken by source index, never by write
    order, so this never depends on a texture gather that reverses the mapping.
    """
    height,width=shape
    valid=np.isfinite(tx)&np.isfinite(ty)&np.isfinite(distance)&(distance>0)
    reach=0. if radius is None else radius
    valid&=(tx>=-.5-reach)&(tx<width-.5+reach)&(ty>=-.5-reach)&(ty<height-.5+reach)
    index=np.flatnonzero(valid)
    px,py=np.rint(tx[index]).astype(int),np.rint(ty[index]).astype(int)
    if radius is None:
        source,dest=index,py*width+px
    else:
        span=int(np.ceil(FOOTPRINT_LIMIT))
        reach=radius[index];sources=[];dests=[]
        for oy in range(-span,span+1):
            for ox in range(-span,span+1):
                cx,cy=px+ox,py+oy
                # A radius of at least half a pixel always keeps the point splat.
                covers=((np.abs(cx-tx[index])<=reach)&(np.abs(cy-ty[index])<=reach)&
                        (cx>=0)&(cx<width)&(cy>=0)&(cy<height))
                sources.append(index[covers]);dests.append(cy[covers]*width+cx[covers])
        source,dest=np.concatenate(sources),np.concatenate(dests)
    order=np.lexsort((source,distance[source],dest))
    sorted_dest=dest[order]
    winners=order[np.r_[True,sorted_dest[1:]!=sorted_dest[:-1]]]
    result=np.empty_like(color);result[:]=[255,0,255,255]
    covered=np.zeros(height*width,dtype=bool)
    result.reshape(-1,4)[dest[winners]]=color.reshape(-1,4)[source[winners]]
    covered[dest[winners]]=True
    return result,covered.reshape(height,width)


def warp(color,depth,meta,delta,footprint=False):
    tx,ty,distance=project_pixels(depth,meta,delta)
    height,width=depth.shape
    radius=footprint_radius(tx,ty,distance,(height,width)) if footprint else None
    result,covered=splat(color,tx,ty,distance,(height,width),radius)
    motion=np.hypot(tx-np.tile(np.arange(width),height),ty-np.repeat(np.arange(height),width))
    return result,covered,motion


def load_capture(path):
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    frames=[r for r in rows if r['event']=='frame']
    if len(frames)!=1:
        raise ValueError('Expected exactly one completed XFB frame')
    frame=frames[0]
    expected=f"frame-{frame['frame_id']}"
    if path.stem!=expected:
        raise ValueError('Manifest name does not match its XFB frame ID')
    split=next((r for r in rows if r['event']=='split'),None)
    if split is None or not split['color_ok'] or not split['depth_ok'] or not frame['final_ok']:
        raise ValueError(f'Incomplete matched capture: {path}')
    images={r['file'].rsplit('-',1)[-1]:r for r in rows if r['event']=='image'}
    result=dict(frame=frame,split=split,path=str(path))
    for key,label in [('world.rgba','world'),('final.rgba','final'),('depth.f32','depth')]:
        row=images[key]
        if row['file']!=f'{expected}-{key}' or row['width']<=0 or row['height']<=0:
            raise ValueError('Attachment name/dimensions do not match frame')
        if row['format'] not in ((11,) if label=='depth' else (0,1)):
            raise ValueError('Unsupported attachment format')
        dtype='<f4' if label=='depth' else np.uint8
        array=np.fromfile(path.parent/row['file'],dtype=dtype)
        shape=(row['height'],row['width'])+(() if label=='depth' else (4,))
        array=array.reshape(shape)
        if label!='depth' and row['format']==1:array=array[:,:,[2,1,0,3]]
        result[label]=array
    if (not np.isfinite(result['depth']).all() or np.ptp(result['depth'])<1e-9 or
            result['depth'].min()<0 or result['depth'].max()>1):
        raise ValueError('Missing or invalid scene depth')
    if result['depth'].shape!=result['world'].shape[:2] or result['world'].shape!=result['final'].shape:
        raise ValueError('Capture attachments differ in dimensions')
    return result


def analyze(previous,current,output):
    output.mkdir(parents=True,exist_ok=False)
    a,b=load_capture(previous),load_capture(current)
    if b['frame']['frame_id']!=a['frame']['frame_id']+1:
        raise ValueError('Prediction requires consecutive XFB frame IDs')
    if not a['split']['camera_valid'] or not b['split']['camera_valid']:
        raise ValueError('No matched GPU palette-zero camera candidate')
    for key in ('projection','viewport','scissor_offset','pixel_center_correction'):
        if not np.allclose(a['split'][key],b['split'][key],rtol=1e-6,atol=1e-7):
            raise ValueError(f'Projection/viewport change requires reset: {key}')
    previous_view=matrix34(a['split']['view']);current_view=matrix34(b['split']['view'])
    predicted=predict_view(previous_view,current_view)
    half_step=predicted@np.linalg.inv(current_view)
    started=time.monotonic()
    result,coverage,motion=warp(b['world'],b['depth'],b['split'],half_step)
    elapsed=time.monotonic()-started
    started=time.monotonic()
    rastered,rastered_coverage,_=warp(b['world'],b['depth'],b['split'],half_step,footprint=True)
    rastered_elapsed=time.monotonic()-started
    identity,identity_mask,_=warp(b['world'],b['depth'],b['split'],np.eye(4))
    residual=b['final'].astype(np.int16)-b['world'].astype(np.int16)
    changed=np.any(residual[:,:,:3]!=0,axis=2)
    approximate=np.clip(result.astype(np.int16)+residual,0,255).astype(np.uint8)
    depth=b['depth'];finite=np.isfinite(depth)
    lo,hi=np.percentile(depth[finite],[1,99]);visual=np.clip((depth-lo)/max(hi-lo,1e-9)*255,0,255).astype(np.uint8)
    depth_rgb=np.dstack([visual]*3+[np.full_like(visual,255)])
    mask_rgb=np.dstack([changed.astype(np.uint8)*255]*3+[np.full_like(visual,255)])
    artifacts=[('Real composite',b['final']),('Before candidate HUD',b['world']),('Depth (percentile range)',depth_rgb),
               ('Predicted half-step point splat',result),('Predicted half-step footprint splat',rastered),
               ('Residual added: diagnostic approximation',approximate)]
    crop=b['frame']['xfb_rect'];h,w=depth.shape
    left,top,right,bottom=[int(v*s) for v,s in zip(crop,[w/640,h/528,w/640,h/528])]
    if not (0<=left<right<=w and 0<=top<bottom<=h):
        raise ValueError('Invalid XFB crop')
    region=np.s_[top:bottom,left:right]
    sheet=Image.new('RGB',(640*3,472*2),(25,25,25));draw=ImageDraw.Draw(sheet)
    for i,(label,array) in enumerate(artifacts):
        im=Image.fromarray(array[region]).convert('RGB');im.thumbnail((640,448))
        x=(i%3)*640;y=(i//3)*472
        sheet.paste(im,(x,y+24));draw.text((x+8,y+6),label,fill='white')
    sheet.save(output/'contact-sheet.png')
    for name,array in [('world',b['world']),('final',b['final']),('half-step',result),
                       ('half-step-footprint',rastered),('hud-residual-mask',mask_rgb),('residual-approximation',approximate)]:
        Image.fromarray(array).save(output/f'{name}.png')
    if not coverage[region].any():
        raise ValueError('Prediction has no covered output pixels')
    identity_ok=bool(identity_mask[region].all() and np.array_equal(identity[region],b['world'][region]))
    forward=current_view@np.linalg.inv(previous_view)
    aligned,aligned_mask,_=warp(a['world'],a['depth'],a['split'],forward)
    rastered_aligned,rastered_aligned_mask,_=warp(a['world'],a['depth'],a['split'],forward,footprint=True)
    Image.fromarray(aligned[region]).save(output/'previous-to-current.png')
    Image.fromarray(rastered_aligned[region]).save(output/'previous-to-current-footprint.png')
    # Explicit static-wall candidate ROIs, away from rider, HUD and distant sky.
    # Scene-specific evidence, not an automatic semantic guarantee.
    static=[]
    ch,cw=bottom-top,right-left
    for label,bounds in [('left-wall',[.03,.42,.25,.88]),('right-wall',[.76,.42,.96,.88])]:
        x0,y0,x1,y1=bounds
        roi=np.s_[top+int(y0*ch):top+int(y1*ch),left+int(x0*cw):left+int(x1*cw)]
        valid=aligned_mask[roi]
        reference=b['world'][roi][:,:,:3].astype(float)
        def mae(image,mask):
            error=np.abs(image[roi][:,:,:3].astype(float)-reference).mean(axis=2)
            # Scored only where that splat covered the region, so coverage and
            # colour accuracy stay separate measurements.
            return float(error[mask[roi]].mean())
        static.append(dict(region=label,normalized_bounds=bounds,covered_fraction=float(valid.mean()),
                           warped_mae=mae(aligned,aligned_mask),unwarped_mae=float(
                               np.abs(a['world'][roi][:,:,:3].astype(float)-reference).mean(axis=2)[valid].mean()),
                           rastered_covered_fraction=float(rastered_aligned_mask[roi].mean()),
                           rastered_warped_mae=mae(rastered_aligned,rastered_aligned_mask)))
    report=dict(schema=1,static_wall_motion_comparison=static,previous=str(previous),current=str(current),frame_id=b['frame']['frame_id'],
        capture_matching='GPU decoder order and same-XFB attachments',camera_source='GX indexed XF_A palette slot zero, stride 48',
        camera_semantics_verified=False,identity_reconstruction_exact=identity_ok,
        camera_palette_bases=[a['split']['camera_base'],b['split']['camera_base']],
        hud_candidate_tail_only=b['frame']['late_perspective']==0,hud_alpha_layer=False,
        hud_residual_changed_fraction=float(changed[region].mean()),
        holes_fraction=float(1-coverage[region].mean()),
        rastered_holes_fraction=float(1-rastered_coverage[region].mean()),
        cracks_closed_fraction=float((rastered_coverage[region]&~coverage[region]).mean()),
        rastered_warp_seconds=rastered_elapsed,motion_pixels_p50_p95=np.nanpercentile(motion.reshape(h,w)[region],[50,95]).tolist(),
        depth_min_max=[float(depth.min()),float(depth.max())],
        offline_warp_seconds=elapsed,timing_representative=False,live_120hz_ready=False,
        limitations=['Palette zero provenance is matched but camera semantics need scene validation.',
                     'Orthographic tail is only a HUD candidate; alpha cannot be recovered by color subtraction.',
                     'Point-splat holes include sampling cracks and disocclusion; no filling is applied.',
                     'The footprint splat only approximates mesh rasterization. Its remaining holes are '
                     'not proven to be disocclusion, and widening a splat can overdraw a true silhouette.',
                     'Rider, objects, particles and transparency have no independent motion vectors.',
                     'Readbacks block the GPU; capture FPS and NumPy time are not a phone GPU budget.'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('previous',type=Path);p.add_argument('current',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();analyze(args.previous,args.current,args.output)
if __name__=='__main__':main()
