#!/usr/bin/env python3
"""Join this E16 run's dynamic registration/request, guards, packets and images."""
import hashlib,json,re,struct
from collections import Counter
from pathlib import Path
from e16_io import read_capture,resolve
from e16_closed_events import tap,fields
from e16_packet import packet
from e16_frame import surface,census,field_surface,read_png,write_png,fnv32
E=Path(__file__).resolve().parent;RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')
LABEL='e16a'
def dump(name,x):(E/name).write_text(json.dumps(x,indent=2)+'\n')
def fnv64(data):
    h=14695981039346656037
    for x in data:h=((h^x)*1099511628211)&0xffffffffffffffff
    return h
def originals(pattern,folder):
    p=RUN/folder
    if p.exists():return sorted(p.glob(pattern))
    import fnmatch
    manifest=json.loads((E/f'{LABEL}-retained.json').read_text())
    return [Path(r['original']) for r in manifest['files'] if Path(r['original']).parent==p and fnmatch.fnmatch(Path(r['original']).name,pattern)]
def main():
    end=json.loads((E/f'{LABEL}-result.json').read_text());assert end.get('release_utc') and end['rc']==0
    data=read_capture(RUN/f'{LABEL}-join/e7-events.txt');events,tail=tap(RUN/f'{LABEL}-join/e7-events.txt',allow_missing_footer=False)
    closure=fields(data.decode().splitlines()[-2]) if tail else None;shutdown=fields(tail) if tail else None
    kinds=dict(Counter(r['kind'] for r in events));calls=[r for r in events if r['kind']=='mpeg-call']
    returns={r['id']:r for r in events if r['kind'] in ['mpeg-return','mpeg-unwind']}
    assert len(calls)==len(returns) and all(c['id'] in returns for c in calls)
    if closure:assert len(calls)==closure['calls']
    joins=[dict(call=c,exit=returns[c['id']]) for c in calls]
    create=[r for r in joins if r['call']['target']==0x4027b8]
    register=[r for r in joins if r['call']['target']==0x402c08]
    request=[r for r in joins if r['call']['target']==0x402a10]
    wait=[r for r in events if r['kind']=='mpeg-wait']
    assert len(create)==len(register)==len(request)==len(wait)==1
    assert closure['registrations']==len(register)==1
    assert sorted(c['id'] for c in calls)==list(range(1,len(calls)+1))
    assert all(returns[c['id']]['target']==c['target'] and returns[c['id']]['entryA0']==c['a0'] for c in calls)
    obj=create[0]['call']['a0'];reg=register[0]['call'];req=request[0]['call']
    assert obj==reg['a0']==req['a0']==wait[0]['token']
    assert reg['a1']==1 and reg['a2']==0x3b0b10
    assert create[0]['exit']['kind']=='mpeg-return' and create[0]['exit']['v0']!=0
    assert register[0]['exit']['kind']=='mpeg-return' and 0<register[0]['exit']['v0']<0x80000000
    shadows=[r for r in events if r['kind']=='mpeg-request-registration' and r['id']==req['id']]
    assert len(shadows)==1
    assert (shadows[0]['mpeg'],shadows[0]['type'],shadows[0]['func'],shadows[0]['userdata'],shadows[0]['handle'])==(obj,reg['a1'],reg['a2'],reg['a3'],register[0]['exit']['v0'])
    assert wait[0]['pc']==req['ra']==0x3b1028 and wait[0]['reason']==6
    assert request[0]['exit']['kind']=='mpeg-unwind'
    targets=dict(Counter(hex(r['target']) for r in calls))
    park=json.loads(read_capture(RUN/f'park-{LABEL}-1/park-snapshot.json'))
    hot={int(r['pc'],16):r for r in park['hot_pc']}
    raw=read_capture(RUN/f'boot-{LABEL}-1.log');lines=raw.decode(errors='replace').splitlines()
    waiting=[dict(line=n,text=l) for n,l in enumerate(lines,1) if '[MPEG:GetPicture] waiting' in l]
    assert len(waiting)==1 and f'mpeg=0x{obj:x} ended=0 failed=0 sawInput=0' in waiting[0]['text']
    if closure:assert closure['selections']==closure['invocations']==0
    callback_calls=[r for r in calls if r.get('callback')==1]
    add_bs_calls=[r for r in calls if r['target']==0x4029d0]
    callback_returns=[r for r in returns.values() if r.get('callback')==1 and r['kind']=='mpeg-return']
    assert not callback_calls and not add_bs_calls and not callback_returns
    assert not any(p in hot for p in (0x3b0b10,0x3b0b40,0x4029d0))
    mainThread=next(t for t in park['threads'] if t['id']==1)
    assert mainThread['wait_reason_name']=='Mpeg' and mainThread['pc']=='0x3b1028'
    mpeg=dict(dynamic_mpeg=hex(obj),create=create,registration=register,request=request,wait=wait,existing_private_state_receipt=waiting,
        target_dispatch_counts=targets,selection_events=[r for r in events if r['kind']=='mpeg-selected'],
        request_registration_shadows=shadows,
        eligibility=dict(api_type=reg['a1'],api_function=hex(reg['a2']),api_userdata=hex(reg['a3']),current_implementation_stream_flag=False,existing_private_selector_requires_stream=True,evidence='unchanged MPEG.cpp: API storage and selector source; private map selection is not directly tapped'),
        actual_callback_dispatches=len(callback_calls),callback_returns=callback_returns,valid_no_input_returns=0,add_bs_dispatches=len(add_bs_calls),
        input_events=[r for r in events if r['kind']=='mpeg-input'],completion_events=[r for r in events if r['kind']=='mpeg-complete'],
        lifetime=[r for r in joins if r['call']['target'] in [0x402708,0x4027b8,0x4029c8,0x402b58]],main_thread=mainThread,
        source_shutdown_complete=tail is not None,
        private_queue_reading='empty implied by the pinned GetPicture wait branch; sawInput/end/fail from existing runtime log; no new private MPEG accessor',
        limits=['Selection inside the private callback map is not tapped; eligibility follows the pinned selector source. Scheduler selection and target dispatch are independently observed.',
                'No actual callback means no guest source/input/decoder/completion behavior was exercised. Zero valid-no-input returns is absence of such returns, not an observed no-input outcome.',
                'Real run-exit source footers are required; observed pairs and independent logs do not substitute for them.'])
    dump('e16a-mpeg.json',mpeg)
    constructors=[r for r in events if r['kind']=='mc-constructor'];pointers=[r for r in events if r['kind']=='mc-ui-pointer']
    singleton=[r for r in events if r['kind']=='singleton'];svals={r['value'] for r in singleton if r['value']}
    assert len(svals)==1 and not any(r['value']==0 for r in singleton)
    counter=[r for r in events if r['kind']=='field-before' and r['off']==0x5a74 and r['pc']==0x382b30]
    steady=[r for r in counter if r['C']>0];assert steady
    assert all(r['S'] in svals and (r['M'],r['G'],r['A'],r['B'],r['P'],r['D'])==(1,0,0,112,0,112) for r in steady)
    aligns=[r for r in events if r['kind']=='e15-align'];assert len(aligns)==1
    align=aligns[0];arm=align['arm'];freeze=align['freeze'];assert align['guard']==1 and freeze==arm+1
    assert any(p['UI']==align['UI'] and p['MC']==align['MC'] and p['guard']==1 for p in pointers)
    assert any(c['MC']==align['MC'] and c['value']==0x486f78 for c in constructors)
    assert f'[e4:armed] tick={arm} ' in raw.decode() and f'[e4:frozen] tick={freeze} ' in raw.decode()
    copies=[r for r in events if r['kind']=='gif-dma' and r['source']==0x4ffcc0]
    copyJoins=[]
    for c in copies:
        matches=[r for r in events if r['kind']=='gs-enter' and r['tick']==c['tick'] and r['fnv64']==c['fnv64'] and r['bytes']==c['bytes'] and r['seq']>c['seq']]
        copyJoins.append(dict(copy=c,gs=matches))
    assert all(len(r['gs'])==1 for r in copyJoins)
    packets=[]
    for path in originals('e7-copy-*.bin',f'{LABEL}-join'):
        pk=packet(path);binary=read_capture(path);tick=int(re.search(r'tick(\d+)-',path.name)[1]);pk['tick']=tick;pk['fnv64']=hex(fnv64(binary))
        pk['copy_join']=[j for j in copyJoins if j['copy']['tick']==tick and j['copy']['fnv64']==fnv64(binary)]
        assert arm<=tick<=freeze and pk['parsed_end']==len(binary) and pk['copy_join']
        xy=next(int(r['value'],16) for r in pk['registers'] if r['reg']=='0x18');xyoff=(xy&0xffff,(xy>>32)&0xffff)
        strips=[]
        for i in range(17):
            u0,x0,u1,x1=struct.unpack_from('<QQQQ',binary,240+32*i)
            uv=lambda v:[(v&0x3fff)/16,((v>>16)&0x3fff)/16]
            xy=lambda v:[((v&0xffff)-xyoff[0])/16,(((v>>16)&0xffff)-xyoff[1])/16]
            strips.append(dict(uv0=uv(u0),uv1=uv(u1),xy0=xy(x0),xy1=xy(x1)))
        pk['strips']=strips;packets.append(pk)
    assert packets
    assert shutdown['packetFiles']==len(packets)
    assert shutdown['packetBytes']==sum(len(read_capture(p)) for p in originals('e7-copy-*.bin',f'{LABEL}-join'))
    vramArm=read_capture(RUN/f'{LABEL}-1/e4-vram-arm.bin');vram=read_capture(RUN/f'{LABEL}-1/e4-vram-freeze.bin')
    w,h=512,448;prod=surface(vram,0,8,w,h);disp=surface(vram,112,8,w,h);initial=surface(vramArm,0,8,w,h)
    shifted=b''.join(prod[((y+1)*w+1)*4:((y+2)*w)*4]+b'\0\0\0\xff' for y in range(h-1))+b'\0\0\0\xff'*w
    different=sum(shifted[i:i+3]!=disp[i:i+3] for i in range(0,len(disp),4))
    present=read_capture(RUN/f'{LABEL}-1/e4-present.txt').decode()
    smode=int(re.search(r'smode2=0x([0-9a-f]+)',present)[1],16);pmode=int(re.search(r'pmode=0x([0-9a-f]+)',present)[1],16)
    db=int(re.search(r'dispfb1=0x([0-9a-f]+)',present)[1],16);assert smode&3==1 and pmode&3==1 and db==0x9070
    fieldsRGBA=[field_surface(disp,w,h,p) for p in (0,1)];uploads=[]
    primary=[j for j in copyJoins if j['copy']['tick']==arm]
    assert len(primary)==1
    presentEvents=[r for r in events if r['kind']=='e15-present']
    for p in originals('upload-*.txt',f'frames-{LABEL}-1'):
        meta=fields(read_capture(p).decode());tick=meta['tick']
        if not arm<=tick<=freeze:continue
        png=p.with_suffix('.png');pw,ph,rgba=read_png(resolve(png));assert (pw,ph)==(w,h)
        joined=[r for r in presentEvents if r['tick']==tick and r['upload']==meta['seq']]
        assert len(joined)==1 and joined[0]['fnv32']==fnv32(rgba)
        uploads.append(dict(file=str(png),metadata=meta,png_sha256=hashlib.sha256(read_capture(png)).hexdigest(),
            event=joined[0],after_primary_copy=joined[0]['seq']>primary[0]['gs'][0]['seq'],
            rgba=census(rgba,pw,ph),exact_field_match=rgba==fieldsRGBA[tick&1]))
    history=read_capture(RUN/f'{LABEL}-1/e4-history.txt').decode();hl=history.splitlines()
    historyRows=[fields(l) for l in hl if l.startswith('[e4:ev]')]
    assert [r['seq'] for r in historyRows]==list(range(1,len(historyRows)+1))
    assert all(r['tick']==arm for r in historyRows)
    dDraws=[r for r in historyRows if r['kind']=='draw' and r['fbp']==112]
    assert len(dDraws)==17 and all(r['tex0'].startswith('0,8,0x0,') for r in dDraws)
    assert vramArm==vram
    graphics=dict(align=align,arm=arm,freeze=freeze,packet_count=len(packets),packets=packets,all_copy_count=len(copies),all_copy_gs_join_count=len(copyJoins),
        aligned_copies=[j for j in copyJoins if arm<=j['copy']['tick']<=freeze],
        primary_copy_tick=arm,primary_copies=[j for j in copyJoins if j['copy']['tick']==arm],
        freeze_tick_copies=[j for j in copyJoins if j['copy']['tick']==freeze],
        temporal_limit='E4 VRAM interval is [arm,freeze); copies at freeze are outside the frozen-source proof. Match Present order explicitly.',
        producer=census(prod,w,h),display=census(disp,w,h),
        arm_producer=census(initial,w,h),source_changed_pixels=sum(prod[i:i+3]!=initial[i:i+3] for i in range(0,len(prod),4)),
        shifted_copy_different_pixels=different,present_mode=dict(smode2=hex(smode),pmode=hex(pmode),dispfb1=hex(db)),uploads=uploads,
        aligned_present_events=presentEvents,history_entries=len(historyRows),history_display_draws=len(dDraws),
        whole_vram_arm_freeze_identical=vramArm==vram,
        positive_packet_source_display_present_join=bool(primary) and different==0 and any(r['exact_field_match'] and r['after_primary_copy'] for r in uploads),
        pixel_graphics_join=bool(uploads) and different==0 and all(r['exact_field_match'] for r in uploads),
        source_shutdown_complete=tail is not None)
    for label,rgba in [('producer',prod),('display',disp)]:
        path=E/(label+'-'+hashlib.sha256(rgba).hexdigest()+'.png');write_png(path,w,h,rgba);graphics[label+'_png']=path.name
    dump('e16a-graphics.json',graphics)
    audit=dict(raw_sha256=hashlib.sha256(data).hexdigest(),raw_bytes=len(data),events=len(events),kinds=kinds,closure=closure,shutdown=shutdown,
        source_shutdown_complete=tail is not None,
        closure_gap='Required footers absent: main calls std::_Exit(0), bypassing PS2Runtime destructor' if tail is None else None,
        newlines_complete=True,sequences_contiguous=True,observed_call_pairs=len(joins),constructors=constructors,ui_pointers=pointers,singleton=singleton,
        s=hex(next(iter(svals))),counter_count=len(counter),counter_first=counter[0],counter_last=counter[-1],
        counter_continuous=[r['lo'] for r in counter]==list(range(1,len(counter)+1)),steady_tuple=[1,0,0,112,0,112])
    dump('e16a-observation-closure.json',audit)
    print('MPEG',hex(obj),'registration/request joined; callback selections/dispatch/AddBs=0; typed wait',mainThread['pc'])
    print('aligned',arm,freeze,'packets',len(packets),'copies consumed',len(copyJoins),'uploads',len(uploads),'pixel join',graphics['pixel_graphics_join'])
    print('observed events',len(events),'paired scopes',len(joins),'source closure',closure,'shutdown',shutdown)
    if tail is None:print('MEASUREMENT GAP: required runtime shutdown counters/flags unavailable; positive rows only')
    print('# E16 JOIN MINER TAIL COMPLETE')
if __name__=='__main__':main()
