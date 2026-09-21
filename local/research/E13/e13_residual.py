#!/usr/bin/env python3
"""Name the next observed wait from the closed run; no second repair."""
import gzip,hashlib,json,re
from pathlib import Path
from e13_io import read_capture
E=Path(__file__).resolve().parent;RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')
def main():
    raw=read_capture(RUN/'boot-e13a-1.log');lines=raw.decode().splitlines()
    card=json.loads((E/'e13a-card.json').read_text())
    functions=json.loads((E/'e13a-function-census.json').read_text())
    park=json.loads(read_capture(RUN/'park-e13a-1/park-snapshot.json'))
    waiting=[dict(line=n,text=l) for n,l in enumerate(lines,1) if '[MPEG:GetPicture] waiting' in l]
    assert len(waiting)==1 and 'mpeg=0x587b30 ended=0 failed=0 sawInput=0' in waiting[0]['text']
    hot={int(r['pc'],16):r for r in park['hot_pc']}
    assert hot[0x402a10]['count']==1 and hot[0x402a10]['first_ra']=='0x3b1028'
    assert hot[0x402c08]['count']==1 and hot[0x402c08]['first_ra']=='0x3b0f6c'
    assert 0x4029d0 not in hot and 0x3b0b10 not in hot and 0x3b0b40 not in hot
    assert functions['entries'].get('sub_003B0B10_0x3b0b10',0)==0
    assert functions['entries'].get('sub_003B0B40_0x3b0b40',0)==1
    assert hot[0x3b0c58]['count']==1 # Enclosing owner log is constructor entry, not callback-helper entry.
    blocks=[];block=None
    for n,l in enumerate(lines,1):
        if '[diag:threads]' in l:block=int(re.search(r'block=(\d+)',l)[1])
        if '[diag:thread] id=1 ' in l:
            f=dict(re.findall(r'(\w+)=([^ ]+)',l));blocks.append(dict(block=block,line=n,**f))
    late=[r for r in blocks if r['block']>=2]
    assert late and all(r['waitReason']=='6' and r['pc']=='0x3b1028' and r['scheduled']=='0' for r in late)
    main=next(t for t in park['threads'] if t['id']==1)
    assert main['wait_reason_name']=='Mpeg' and main['pc']=='0x3b1028'
    source_rows=json.loads((E/'residual-source-manifest.json').read_text())
    for r in source_rows:assert hashlib.sha256(gzip.decompress((E/r['retained']).read_bytes())).hexdigest()==r['sha256']
    cpp=gzip.decompress((E/'residual-sources/MPEG.cpp.gz').read_bytes()).decode()
    readers=[dict(line=n,text=l) for n,l in enumerate(cpp.splitlines(),1) if 'callbacksByMpeg' in l]
    assert 'if (callback.stream && callback.type == streamType)' in cpp
    assert 'MpegRegisteredCallback{callbackType, 0u, callbackFunc, callbackData, handle, false}' in cpp
    callback=gzip.decompress((E/'residual-sources/sub_003B0B40_0x3b0b40.cpp.gz').read_bytes()).decode()
    assert '0x4029D0u' in callback
    registry=gzip.decompress((E/'after/register_functions.cpp.gz').read_bytes()).decode()
    bindings={hex(pc):[l for l in registry.splitlines() if l.rstrip().endswith('// '+hex(pc))] for pc in [0x3b0b10,0x3b0b40,0x3b0c58,0x402c08,0x4029d0,0x402a10]}
    assert all(len(v)==1 for v in bindings.values())
    rec=dict(outcome='ii',wait=waiting[0],main_thread=main,thread1_blocks=blocks,
        registration=hot[0x402c08],get_picture=hot[0x402a10],callback_entry_count=0,callback_helper_entry_count=0,callback_helper_owner_log_count=1,constructor_in_owner=hot[0x3b0c58],add_bs_hot_count=0,
        registered_callback_arguments='ELF at3b0f54..68 fixes type1, func3b0b10 and a3=s2; actual original argument capture remains next-probe guard',
        callback_body='3b0b10 reorders callback a0/a1/a2 into helper3b0b40; helper obtains guest data, pads/copies it, then calls4029d0 sceMpegAddBs',
        callbacks_map_references=readers,bindings=bindings,
        hypothesis='Non-stream type1 callback is stored but has no dispatcher in this runtime; GetPicture parks before that guest bitstream producer can call AddBs.',
        limits=['No new menu or meaningful-frame claim.','Fixed599..603 packet capture occurs after copy source quiesces; early content bytes are not retained.','Runtime registration args and callback ABI delivery need a guarded next probe/fixture before any MPEG fix.','Nearby successful CD reads are not joined to MPEG input; no CD/SIF/storage/input fix promoted.'],
        next_action='One MPEG callback1→3b0b10→3b0b40→sceMpegAddBs→GetPicture wait/delivery probe and actual-binding fixture, with event-aligned graphics capture; no regen or additional map entry.')
    (E/'e13a-residual-join.json').write_text(json.dumps(rec,indent=2)+'\n')
    chosen=set(range(waiting[0]['line']-5,waiting[0]['line']+2))|{r['line'] for r in blocks}
    with (E/'e13a-residual-receipts.txt').open('w') as f:
        f.write('raw SHA256='+hashlib.sha256(raw).hexdigest()+'\n')
        for n in sorted(chosen):f.write(f'{n} {lines[n-1]}\n')
        f.write('# E13 RESIDUAL RECEIPTS TAIL COMPLETE\n')
    print('GetPicture once at RA3b1028, sawInput0; callback registration once at RA3b0f6c; callback/AddBs executions0')
    print('T1 remains Mpeg-wait through',len(late),'complete late blocks; first remaining wall tabled, no second fix')
    print('# E13 RESIDUAL TAIL COMPLETE')
if __name__=='__main__':main()
