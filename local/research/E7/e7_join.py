#!/usr/bin/env python3
"""Read-only cross-run E7 join, including E5 burst ordinal and full tails."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct

P=Path(__file__).resolve().parent


def read_json(name):
    return json.loads((P/name).read_text())


def emit(label,value):
    print(label,json.dumps(value,sort_keys=True))


def function_census(phase):
    path=P/'raw'/f'ps2_log-e7{phase}-1.txt.gz'
    count=Counter();digest=hashlib.sha256();size=0
    pattern=re.compile(rb'sub_(00382AF0|00371940)_0x[0-9a-f]+ (enter|exit)')
    with gzip.open(path,'rb') as f:
        for line in f:
            digest.update(line);size+=len(line)
            match=pattern.search(line)
            if match:count[b'/'.join(match.groups()).decode()]+=1
    return {'bytes':size,'sha256':digest.hexdigest(),'counts':dict(count)}


def main():
    e5file=P.parent/'E5/e5-watch-series.txt'
    e5=[r.split() for r in e5file.read_text().splitlines() if r and not r.startswith('#')]
    e5display=[r for r in e5 if r[2]=='DISPFB1']
    emit('E5',{'sha256':hashlib.sha256(e5file.read_bytes()).hexdigest(),
               'display_bursts':len(e5display),'burst558':e5display[557]})
    assert e5display[557][2:8]==['DISPFB1','8','0x9070','0x382cf0','5','0x382824']
    results={}
    for phase in 'abc':
        label='e7'+phase;s=read_json(label+'-summary.json')
        series=[r.split() for r in (P/(label+'-watch-series.txt')).read_text().splitlines() if r and not r.startswith('#')]
        display=[r for r in series if r[1]=='0x12000070']
        window=[(i+1,r) for i,r in enumerate(display) if s['armed_line']<int(r[0])<s['frozen_line']]
        assert window==[(558,display[557])]
        assert display[557][1:7]==['0x12000070','8','0x9070','0x382cf0','5','0x382824']
        assert len(s['singleton'])==1 and s['singleton'][0]['value']==0x61ba60
        assert not s['damaged_boundary_lines']
        emit(label+'-identity-burst',{'singleton':s['singleton'],'zero_teardown_null':True,
            'display_bursts':len(display),'boundary':window,'damaged_console_lines':s['damaged_watch_lines'],
            'damaged_boundary_lines':len(s['damaged_boundary_lines'])})
        census=function_census(phase);results[label+'-function-census']=census
        emit(label+'-function-census',census)
        if phase=='a':continue
        assert s['counter']['continuous'] and s['counter']['pre_matches']
        assert s['counter']['M']=={'1':561} and s['counter']['G']=={'0':561}
        emit(label+'-counter',s['counter'])
        for r in s['boundary_events']:
            if r['tick']==600 and (r['kind']!='gs-enter' or r['bytes']==1696):emit(label+'-edge',r)
        copies=[]
        for tick in range(599,604):
            edge=[r for r in s['boundary_events'] if r['tick']==tick]
            dma=[r for r in edge if r['kind']=='gif-dma' and r['source']==0x4ffcc0]
            assert len(dma)==1
            d=dma[0];matches=[r for r in edge if r['kind']=='gs-enter' and r['bytes']==d['bytes'] and r['fnv64']==d['fnv64']]
            assert len(matches)==(1 if phase=='c' else 0)
            copies.append({'tick':tick,'dma_seq':d['seq'],'mask':d['mask'],
                           'fnv64':hex(d['fnv64']),'gs_seqs':[r['seq'] for r in matches]})
        emit(label+'-five-copy-joins',copies)
        pk=next(r for r in s['packets'] if 'tick600-' in r['file'])
        emit(label+'-packet',{'bytes':pk['bytes'],'sha256':pk['sha256'],'parsed_end':pk['parsed_end'],
             'tags':pk['tags'],'essential_registers':[r for r in pk['registers'] if r['reg'] in ['0x4c','0x4d','0x6','0x18']]})
        data=(P/(label+'-packets')/pk['file']).read_bytes()
        xyoff=next(int(r['value'],16) for r in pk['registers'] if r['reg']=='0x18')
        xyoff=(xyoff&0xffff,(xyoff>>32)&0xffff)
        geometry=[]
        for strip in range(17):
            uv0,xyz0,uv1,xyz1=struct.unpack_from('<QQQQ',data,240+32*strip)
            def uv(v):return [(v&0x3fff)/16,((v>>16)&0x3fff)/16]
            def xy(v):return [((v&0xffff)-xyoff[0])/16,(((v>>16)&0xffff)-xyoff[1])/16]
            geometry.append({'strip':strip,'uv0':uv(uv0),'uv1':uv(uv1),'xy0':xy(xyz0),'xy1':xy(xyz1)})
        emit(label+'-copy-geometry',geometry)
        emit(label+'-history',{'headers':s['history_headers'],'kinds':s['history_kinds'],
                              'draw_fbps':s['draw_fbps'],'frame2_events':s['frame2_events']})
        emit(label+'-tap-tail',s['tap_tail'])
        frame=read_json(label+'-frame.json')
        emit(label+'-frame',frame)
        if phase=='c':
            assert frame['display']['rgb_nonblack']>0
            assert frame['copy_content_comparison']['full_rgb_different_pixels']==0
            assert frame['host_latest_equals_expected_display_field']
            assert all(r['matches'] for r in frame['field_present_matches'])
    (P/'e7-function-censuses.json').write_text(json.dumps(results,indent=2)+'\n')
    assert read_json('e7b-summary.json')['packets']==read_json('e7c-summary.json')['packets']
    print('# E7 JOIN TAIL COMPLETE: guarded fields; E5 burst 558; 5/5 fixed copy packets consumed; D content; both Present fields; exact latest PNG bytes')


if __name__=='__main__':main()
