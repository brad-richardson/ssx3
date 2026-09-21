"""Measure guarded E15/E7/E4 alignment without assuming E17's image or counters recur."""
import hashlib,json,re,struct
from pathlib import Path
from e18_io import read_capture,resolve
from e18_closed_events import tap,fields
from e18_packet import packet
from e18_frame import surface,census,field_surface,read_png,fnv32
E=Path(__file__).resolve().parent;RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run');LABEL='e18a'
def save(x):(E/'e18a-graphics.json').write_text(json.dumps(x,indent=2)+'\n')
def originals(pattern,folder):
    root=RUN/folder
    if root.exists():return sorted(root.glob(pattern))
    import fnmatch
    manifest=json.loads((E/f'{LABEL}-retained.json').read_text())
    return [Path(r['original']) for r in manifest['files'] if Path(r['original']).parent==root and fnmatch.fnmatch(Path(r['original']).name,pattern)]
def fnv64(data):
    h=14695981039346656037
    for x in data:h=((h^x)*1099511628211)&0xffffffffffffffff
    return h
def main():
    events,footer=tap(RUN/f'{LABEL}-join/e7-events.txt',allow_missing_footer=True)
    result=dict(source_footer=footer is not None,gaps=[])
    result['constructors']=[r for r in events if r['kind']=='mc-constructor']
    result['ui_pointers']=[r for r in events if r['kind']=='mc-ui-pointer']
    result['singletons']=[r for r in events if r['kind']=='singleton']
    counters=[r for r in events if r['kind']=='field-before' and r['off']==0x5a74 and r['pc']==0x382b30]
    result['counter']=dict(count=len(counters),first=counters[:1],last=counters[-1:],continuous=[r['lo'] for r in counters]==list(range(1,len(counters)+1)),tuples=sorted({tuple(r[k] for k in ('M','G','A','B','P','D')) for r in counters}))
    align=[r for r in events if r['kind']=='e15-align'];result['align']=align
    if len(align)!=1:
        result['gaps'].append('Expected one guarded UI3-to-6 alignment event; observed '+str(len(align)));save(result);print(json.dumps(result));return
    a=align[0];arm=a['arm'];freeze=a['freeze'];result.update(arm=arm,freeze=freeze,
        object_guard=bool(a['guard']==1 and any(p['UI']==a['UI'] and p['MC']==a['MC'] and p['guard']==1 for p in result['ui_pointers']) and any(c['MC']==a['MC'] and c['value']==0x486f78 for c in result['constructors'])))
    if not result['object_guard'] or freeze!=arm+1:result['gaps'].append('Object or one-tick freeze guard missing')
    copies=[r for r in events if r['kind']=='gif-dma' and r['source']==0x4ffcc0]
    joins=[dict(copy=c,gs=[r for r in events if r['kind']=='gs-enter' and r['tick']==c['tick'] and r['fnv64']==c['fnv64'] and r['bytes']==c['bytes'] and r['seq']>c['seq']]) for c in copies]
    result.update(all_copy_count=len(copies),all_copy_gs_join_count=sum(len(j['gs'])==1 for j in joins),aligned_copies=[j for j in joins if arm<=j['copy']['tick']<=freeze])
    packets=[]
    for path in originals('e7-copy-*.bin',f'{LABEL}-join'):
        data=read_capture(path);p=packet(path);tick=int(re.search(r'tick(\d+)-',path.name)[1]);p.update(tick=tick,fnv64=hex(fnv64(data)),copy_join=[j for j in joins if j['copy']['tick']==tick and j['copy']['fnv64']==fnv64(data)])
        packets.append(p)
    result['packets']=packets
    result['packet_parse_complete']=bool(packets) and all(p['parsed_end']==p['bytes'] for p in packets)
    if footer:
        end=fields(footer);result['packet_source_count_match']=end['packetFiles']==len(packets) and end['packetBytes']==sum(len(read_capture(p)) for p in originals('e7-copy-*.bin',f'{LABEL}-join'))
    try:
        present=read_capture(RUN/f'{LABEL}-1/e4-present.txt').decode();result['present_raw']=present
        smode=int(re.search(r'smode2=0x([0-9a-f]+)',present)[1],16);pmode=int(re.search(r'pmode=0x([0-9a-f]+)',present)[1],16);db=int(re.search(r'dispfb1=0x([0-9a-f]+)',present)[1],16)
        mode_guard=smode&3==1 and pmode&3==1 and db==0x9070
        result['present_mode_guard']=mode_guard
        vramArm=read_capture(RUN/f'{LABEL}-1/e4-vram-arm.bin');vram=read_capture(RUN/f'{LABEL}-1/e4-vram-freeze.bin')
        w,h=512,448;prod=surface(vram,0,8,w,h);disp=surface(vram,112,8,w,h);initial=surface(vramArm,0,8,w,h)
        shifted=b''.join(prod[((y+1)*w+1)*4:((y+2)*w)*4]+b'\0\0\0\xff' for y in range(h-1))+b'\0\0\0\xff'*w
        different=sum(shifted[i:i+3]!=disp[i:i+3] for i in range(0,len(disp),4))
        result.update(producer=census(prod,w,h),display=census(disp,w,h),arm_producer=census(initial,w,h),source_changed_pixels=sum(prod[i:i+3]!=initial[i:i+3] for i in range(0,len(prod),4)),shifted_copy_different_pixels=different,whole_vram_arm_freeze_identical=vramArm==vram)
        presentEvents=[r for r in events if r['kind']=='e15-present'];primary=[j for j in joins if j['copy']['tick']==arm and len(j['gs'])==1];uploads=[]
        for path in originals('upload-*.txt',f'frames-{LABEL}-1'):
            meta=fields(read_capture(path).decode());tick=meta['tick']
            if not arm<=tick<=freeze:continue
            png=path.with_suffix('.png');pw,ph,rgba=read_png(resolve(png));matched=[r for r in presentEvents if r['tick']==tick and r['upload']==meta['seq'] and r['fnv32']==fnv32(rgba)]
            uploads.append(dict(file=str(png),metadata=meta,dimensions=[pw,ph],event=matched,png_sha256=hashlib.sha256(read_capture(png)).hexdigest(),after_arm_copy=bool(matched and primary and matched[0]['seq']>primary[-1]['gs'][0]['seq']),exact_field_match=(pw,ph)==(w,h) and rgba==field_surface(disp,w,h,tick&1)))
        result.update(uploads=uploads,positive_packet_source_display_present_join=mode_guard and bool(primary) and different==0 and any(p['exact_field_match'] and p['after_arm_copy'] for p in uploads),temporal_limit='E4 VRAM interval is [arm,freeze); freeze-tick copies do not independently prove frozen-source contents.')
        history=read_capture(RUN/f'{LABEL}-1/e4-history.txt').decode();rows=[fields(l) for l in history.splitlines() if l.startswith('[e4:ev]')]
        result['history']=dict(entries=len(rows),sequences_contiguous=[r['seq'] for r in rows]==list(range(1,len(rows)+1)),ticks=sorted({r['tick'] for r in rows}),display_draws=[r for r in rows if r['kind']=='draw' and r['fbp']==112])
    except (FileNotFoundError,ValueError,KeyError) as exc:
        result['gaps'].append(type(exc).__name__+': '+str(exc))
    save(result);print(json.dumps({k:result.get(k) for k in ('arm','freeze','object_guard','all_copy_count','all_copy_gs_join_count','packet_parse_complete','packet_source_count_match','positive_packet_source_display_present_join','gaps')}));print('# E18 GRAPHICS JOIN TAIL COMPLETE')
if __name__=='__main__':main()
