#!/usr/bin/env python3
"""Experimental static collision candidate; native impact validation is required.

Only visible source mode-1 meshes without effect callbacks are enabled. Physics,
bounds-only shapes and callback objects remain explicit omissions. The target
response uses the common stock static property (mass 1e30, behavior 3, surface -1).
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

from course_route import ssx3_paths
from gamecube_collision import read_tricky_collision, encode_collision, read_collision, collision_instance_transform
from gamecube_cleanup import clear_removed_instance_references
from gamecube_scenery import TrickyScenery
from gamecube_scenery_import import geometry_parts, instance_record, WORLD_RESOURCE_ORDER
from gamecube_spline_import import require_disabled_programs
from gamecube_world import World, assemble, validate_resource_capacities

PROFILE = 'tricky-gc-static-rigid-transform-v3'


def segment_intersects_box(a,b,low,high):
    """Closed segment / AABB intersection, including parallel and zero axes."""
    first,last=0.,1.
    for k in range(3):
        d=b[k]-a[k]
        if abs(d)<1e-12:
            if not low[k]<=a[k]<=high[k]:return False
        else:
            x,y=sorted(((low[k]-a[k])/d,(high[k]-a[k])/d))
            first=max(first,x);last=min(last,y)
            if first>last:return False
    return True


def reset_segments(records):
    result=[]
    for e,p in records:
        if e['kind']!=14 or not p:continue
        for i,path in enumerate(ssx3_paths(p)[0]):
            if not struct.unpack_from('<I',path,24)[0]:continue
            a=struct.unpack_from('<3f',path,36)
            for j in range(struct.unpack_from('<I',path,28)[0]):
                *v,d=struct.unpack_from('<4f',path,72+16*j)
                b=tuple(a[k]+v[k]*d for k in range(3))
                result.append((i,a,b));a=b
    return result


def validate_static_bindings(records, track):
    """Reject undefined callbacks and mismatched collision/instance tables."""
    instances=sorted(e['rid'] for e,p in records if e['kind']==3 and e['track']==track)
    scripts=[p for e,p in records if e['kind']==16 and e['track']==track]
    if len(scripts)!=1 or instances!=list(range(len(instances))):
        raise ValueError('Static collision bindings require consecutive owned instance IDs')
    script=scripts[0]
    require_disabled_programs(script)
    base=struct.unpack_from('>I',script,64)[0]
    count,table,defs,offsets,splines,spline_at=struct.unpack_from('>6I',script,68)
    if (count!=len(instances) or not 92<=base<=table or table+count*2>offsets or
            offsets+defs*4!=spline_at or spline_at+splines*4!=len(script)):
        raise ValueError('Invalid static binding table extents')
    ids=struct.unpack_from('>'+str(count)+'H',script,table)
    starts=[base+v for v in struct.unpack_from('>'+str(defs)+'I',script,offsets)]
    if (not defs or any(i>=defs for i in ids) or starts[0]!=base or
            starts!=sorted(set(starts)) or starts[-1]>=table):
        raise ValueError('Invalid static definition indices')
    collisions={e['track']<<24|e['rid']:read_collision(p) for e,p in records if e['kind']==12}
    for start,end in zip(starts,starts[1:]+[table]):
        if end-start<28:raise ValueError('Truncated static definition')
        kind,flags,effect,collision=struct.unpack_from('>4I',script,start)
        if effect!=0xffffffff:
            raise ValueError('Static profile must not reference an effect callback')
        if kind==0:
            if flags!=0x00010000 or collision!=0xffffffff or end-start!=28:
                raise ValueError('Invalid non-colliding static definition')
        elif kind==1:
            if flags!=0x00210000 or collision not in collisions or end-start!=16+12*len(collisions[collision]):
                raise ValueError('Static definition and collision mesh disagree')
        else:
            raise ValueError('Unsupported static definition kind')
    models={e['track']<<24|e['rid']:struct.unpack_from('>I',p,4)[0]
            for e,p in records if e['kind']==2 and len(p)>=8}
    for e,p in records:
        if e['kind']!=3 or e['track']!=track:continue
        start=starts[ids[e['rid']]]
        if struct.unpack_from('>I',script,start)[0]!=1:continue
        collision=struct.unpack_from('>I',script,start+12)[0]
        model=struct.unpack_from('>I',p,120)[0]
        if models.get(model)!=len(collisions[collision]):
            raise ValueError('Collision parts must match render-model parts')
        collision_instance_transform(p)
    return len(ids)


def bind_static(records, scene, collisions, recipe):
    track = recipe['track']
    if any(e['kind']==12 for e,p in records):
        raise ValueError('Remove host collisions before compiling donor collision IDs')
    instances = sorted(((e,p) for e,p in records if e['kind']==3),key=lambda r:r[0]['rid'])
    source_ids = {int(k):v for k,v in recipe['scenery']['instance_source_ids'].items()}
    if (len(instances)!=len(source_ids) or set(source_ids)!={e['rid'] for e,p in instances} or
            any(e['track']!=track for e,p in instances)):
        raise ValueError('Imported instance ownership/source map mismatch')
    model_ids = sorted(e['rid'] for e,p in records if e['kind']==2)
    if len(model_ids)!=len(recipe['scenery']['source_models']):
        raise ValueError('Unexpected model ownership')
    models = dict(zip(recipe['scenery']['source_models'],model_ids))
    if any(len(p)<8 or struct.unpack_from('>I',p,4)[0]!=1 for e,p in records if e['kind']==2):
        raise ValueError('Static collision profile requires verified single-part render models')
    scripts = [(e,p) for e,p in records if e['kind']==16]
    if len(scripts)!=1 or scripts[0][0]['track']!=track:
        raise ValueError('Expected one owned binding table')
    script = scripts[0][1]
    require_disabled_programs(script)
    if struct.unpack_from('>I',script,68)[0]!=0:
        raise ValueError('Existing instance bindings require an explicit migration')
    spline_count,spline_at=struct.unpack_from('>2I',script,84)
    if spline_at+4*spline_count!=len(script):
        raise ValueError('Invalid spline binding extent')
    base=struct.unpack_from('>I',script,64)[0]
    if not 92<=base<=spline_at:
        raise ValueError('Invalid property base')
    oid=lambda rid:track<<24|rid
    added, converted, defs, def_ids, bindings, remap, new_sources = [],[],[],{},[],{},{}
    collision_ids={}; skipped=Counter(); enabled=[]
    corridors=reset_segments(records);protected=[];unsupported_transforms=[]
    for new_id,(e,p) in enumerate(instances):
        src_id=source_ids[e['rid']]
        if not 0<=src_id<len(scene.instances):raise ValueError('Source instance out of range')
        src=scene.instances[src_id]; gameplay=src['gameplay']
        if not gameplay['visible']:raise ValueError('Hidden helper must not re-enter the scene')
        model=models[src['model']]
        opcode=geometry_parts(scene.models[src['model']])[0]['meshes'][0]['strips'][0]['opcode']
        scale=4 if opcode==0x9b else 1
        color,offset=struct.unpack_from('>2I',p,152)
        if color>>24!=track or offset!=0:raise ValueError('Unexpected instance color reference')
        expected=instance_record(src,recipe['matrix'],recipe['translation'],scale,oid,e['rid'],model,
                                 color&0xffffff,struct.unpack_from('>I',p,116)[0])
        if expected!=p:raise ValueError(f'Imported placement/source mismatch at {e["rid"]}')
        collision=None
        if gameplay['player_collision']:
            bounds=struct.unpack_from('>6f',p,88)
            # Preserve verified recovery until narrow-phase object clearance
            # is available. These conservative SSX 3 rider dimensions are in
            # target units (the rider does not scale with the donor course).
            low=[bounds[0]-35,bounds[1]-35,bounds[2]-150]
            high=[bounds[3]+35,bounds[4]+35,bounds[5]+35]
            overlap=next((i for i,a,b in corridors if segment_intersects_box(a,b,low,high)),None)
            if gameplay['collision_mode']==1 and gameplay['effect_slot']==-1 and overlap is not None:
                skipped['protected-reset-corridor']+=1
                protected.append(dict(source_instance=src_id,instance=new_id,reset_path=overlap))
            elif gameplay['collision_mode']==1 and gameplay['effect_slot']==-1:
                try:
                    normalized=collision_instance_transform(p,normalize=True)
                except ValueError as error:
                    normalized=None
                    skipped['nonuniform-or-invalid-instance-transform']+=1
                    unsupported_transforms.append(dict(source_instance=src_id,instance=new_id,reason=str(error)))
                index=gameplay['collision_or_physics']
                if not 0<=index<len(collisions):raise ValueError('Source collision reference out of range')
                key=(index,scale)
                if normalized is not None and key not in collision_ids:
                    data=encode_collision(collisions[index],geometry_scale=scale)
                    read_collision(data)
                    parts=struct.unpack_from('>H',data,2)[0]
                    # GXBE69 801DDD08..801DE43C traverses render-model parts,
                    # advancing one collision mesh per part. Appending collision
                    # partitions alone silently leaves later meshes untested.
                    if parts!=1:
                        collision_ids[key]=None
                    else:
                        rid=len(added);collision_ids[key]=(rid,parts)
                        added.append((dict(kind=12,track=track,rid=rid,size=len(data)),data))
                collision=collision_ids.get(key) if normalized is not None else None
                if normalized is not None and collision_ids[key] is None:
                    skipped['multipart-collision-needs-matching-render-parts']+=1
                elif collision is not None:
                    p=normalized
                    enabled.append(dict(source_instance=src_id,instance=new_id,source_collision=index,collision=collision[0]))
            else:
                skipped[f'mode-{gameplay["collision_mode"]}/effect-{gameplay["effect_slot"]}']+=1
        if collision is not None:
            rid,parts=collision
            # +8 is an EFFECT SLOT reference, not a render-model reference.
            # GXBE69 80245F5C/80245F84 indexes the 24-byte callback table with it.
            # These source instances have no callbacks, so preserve that absence.
            definition=struct.pack('>4I',1,0x00210000,0xffffffff,oid(rid))
            definition+=struct.pack('>2f2h',1e30,0.,3,-1)*parts
        else:
            definition=struct.pack('>4I',0,0x00010000,0xffffffff,0xffffffff)
            definition+=struct.pack('>2f2h',1e30,0.,0,-1)
        if definition not in def_ids:
            def_ids[definition]=len(defs);defs.append(definition)
        bindings.append(def_ids[definition])
        changed=bytearray(p);struct.pack_into('>I',changed,112,oid(new_id))
        converted.append((dict(e,rid=new_id),bytes(changed)))
        remap[e['rid']]=new_id;new_sources[new_id]=src_id
    if len(defs)>65535:raise ValueError('Instance definition indices exceed uint16')
    data=bytearray(script[:base]);offsets=[]
    for definition in defs:
        offsets.append(len(data)-base);data+=definition
    instance_at=len(data);data+=struct.pack('>'+str(len(bindings))+'H',*bindings)
    data+=bytes(-len(data)%4)
    definition_at=len(data);data+=struct.pack('>'+str(len(offsets))+'I',*offsets)
    splines_at=len(data);data+=script[spline_at:]
    struct.pack_into('>6I',data,68,len(bindings),instance_at,len(defs),definition_at,spline_count,splines_at)
    out=[(dict(e,size=len(data)),bytes(data)) if e['kind']==16 else (e,p)
         for e,p in records if e['kind']!=3]
    out+=converted+added
    out.sort(key=lambda r:WORLD_RESOURCE_ORDER.index(r[0]['kind']))
    validate_static_bindings(out,track)
    return out,dict(profile=PROFILE,enabled_instances=enabled,collision_resources=len(added),
                    collision_bytes=sum(len(p) for e,p in added),skipped_instances=dict(skipped),
                    definitions=len(defs),instance_id_remap=remap,instance_source_ids=new_sources,
                    protected_reset_instances=protected,
                    unsupported_transform_instances=unsupported_transforms,
                    transform_profile='orthonormal-basis-plus-uniform-scale',
                    reset_clearance=dict(method='conservative instance bounds',radius=35,height=150),
                    response_profile='stock-static-behavior-3',native_impact_verified=False)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-build',required=True,type=Path)
    ap.add_argument('--nbd',required=True,type=Path)
    ap.add_argument('--gsf',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    if args.output.exists():ap.error('Use a fresh candidate output')
    recipe=json.loads((args.base_build/'experiment.json').read_text())
    if not (recipe.get('safe_reset_paths') or recipe.get('cleanup_detail',{}).get('safe_reset_paths')):
        raise ValueError('Compile grounded recovery paths before enabling static collision')
    nbd,gsf=args.nbd.read_bytes(),args.gsf.read_bytes()
    if (hashlib.sha256(nbd).hexdigest()!=recipe['donor_nbd_sha256'] or
        hashlib.sha256(gsf).hexdigest()!=recipe['visibility']['source_gsf_sha256']):
        raise ValueError('Collision source does not match imported scenery')
    scene=TrickyScenery(nbd,gsf,phase='racing');collisions=read_tricky_collision(gsf)
    world=World((args.base_build/'BAM.BIG').read_bytes());group,track=recipe['group'],recipe['track']
    loc=world.location(recipe['location'])
    if loc['index']!=track or not loc['group_start']<=group<=loc['last_group']:
        raise ValueError('Course ownership mismatch')
    records=world.records(group);instances=[(e,p) for e,p in records if e['kind']==3]
    audited=0
    for g in world.index['groups']:
        rows=records if g['index']==group else world.records(g['index'])
        if g['index']!=group and any(e['track']==track and e['kind'] in (3,12,16) for e,p in rows):
            raise ValueError('Cross-group instance/collision ownership requires an explicit migration')
        _,changes=clear_removed_instance_references(rows,instances)
        if changes:raise ValueError('Retained object/NIS references prevent instance ID compaction')
        audited+=len(rows)
    records,report=bind_static(records,scene,collisions,recipe)
    archive,_=assemble(world,{group:records});check=World(archive)
    key=lambda rows:[((e['kind'],e['track'],e['rid']),p) for e,p in rows]
    if key(check.records(group))!=key(records):raise RuntimeError('Collision archive readback differs')
    for g in world.index['groups']:
        i=g['index']
        if i!=group and check.original_group_blocks(i)!=world.original_group_blocks(i):
            raise RuntimeError('Unexpected change outside course')
    report.update(base_archive_sha256=hashlib.sha256(world.archive).hexdigest(),archive_sha256=hashlib.sha256(archive).hexdigest(),
                  audited_reference_records=audited,resource_count=validate_resource_capacities(check))
    recipe['collisions']=report;recipe['scenery']['instance_source_ids']=report['instance_source_ids'];recipe['output_sha256']=report['archive_sha256']
    args.output.mkdir(parents=True);(args.output/'BAM.BIG').write_bytes(archive)
    (args.output/'experiment.json').write_text(json.dumps(recipe,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('enabled_instances','instance_id_remap','instance_source_ids','protected_reset_instances')},indent=2))


if __name__=='__main__':main()
