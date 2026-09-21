#!/usr/bin/env python3
"""Assert the two E8 copy/frame joins and the observed busy-query wall."""
import hashlib
import json
from pathlib import Path
import re
from e8_io import read_capture, resolve
from e8_frame import read_png, census

HERE=Path(__file__).resolve().parent
RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')


def load(name):return json.loads((HERE/name).read_text())


def main():
    out=[]
    def emit(name,value):out.append(name+' '+json.dumps(value,sort_keys=True))
    for label,arm in [('e8a',6000),('e8b',600)]:
        s=load(label+'-summary.json');f=load(label+'-frame.json');p=load(label+'-progress.json')
        assert len(s['singleton'])==1 and s['singleton'][0]['value']==0x61ba60
        assert not s['damaged_boundary_lines']
        assert s['counter']['continuous'] and s['counter']['pre_matches']
        assert s['counter']['M']=={'1':561} and s['counter']['G']=={'0':561}
        emit(label+'-guard',dict(singleton=s['singleton'],counter=s['counter'],
             damaged_console=s['damaged_watch_lines'],damaged_boundary=len(s['damaged_boundary_lines'])))
        copies=[]
        for tick in range(599,604):
            edge=[r for r in s['boundary_events'] if r['tick']==tick]
            dma=[r for r in edge if r['kind']=='gif-dma' and r['source']==0x4ffcc0]
            assert len(dma)==1
            d=dma[0];matches=[r for r in edge if r['kind']=='gs-enter' and
                             r['bytes']==d['bytes'] and r['fnv64']==d['fnv64']]
            assert d['mask']==0 and d['queued']==0 and len(matches)==1
            copies.append(dict(tick=tick,source=hex(d['source']),bytes=d['bytes'],fnv64=hex(d['fnv64']),
                               dma_seq=d['seq'],gs_seq=matches[0]['seq']))
        assert {p['sha256'] for p in s['packets']}=={'79f3582fce45dc36a25c454003206a43bbfd001c340a92459a8726fbd0512e31'}
        assert len(s['packets'])==5
        emit(label+'-copy-joins',copies)
        pk=next(p for p in s['packets'] if 'tick600-' in p['file'])
        emit(label+'-copy-packet',dict(bytes=pk['bytes'],sha256=pk['sha256'],parsed_end=pk['parsed_end'],
             tags=pk['tags'],essential_registers=[r for r in pk['registers'] if r['reg'] in ['0x4c','0x4d','0x6','0x18']]))
        assert {k:v for k,v in s['history_kinds'].items() if k!='present'}=={'gif':52,'reg':80,'draw':155}
        assert s['draw_fbps']=={'112':17,'0':138} and s['frame2_events']==1
        emit(label+'-history',dict(arm=arm,headers=s['history_headers'],kinds=s['history_kinds'],draws=s['draw_fbps']))
        assert f['vram_sha256']=='532288fdaa9cf5e2aa43f628dd9975b4f7cdecf12ac8beac7fdd8897ac4c78e5'
        assert f['display']['rgb_nonblack']==12358
        assert f['copy_content_comparison']['full_rgb_different_pixels']==0
        assert f['host_latest_equals_expected_display_field']
        assert all(r['matches'] for r in f['field_present_matches'])
        emit(label+'-frame',f)
        survey=RUN/f'frames-{label}-1/survey-index.jsonl'
        try:rows=[json.loads(line) for line in read_capture(survey).decode().splitlines()]
        except FileNotFoundError:rows=[]
        checked=[]
        for row in rows:
            path=resolve(survey.parent/row['png']);w,h,rgba=read_png(path)
            parity=int(row['metadata']['tick'])&1
            got=census(rgba,w,h)
            assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
            assert (w,h)==(512,448)
            assert got['rgba_sha256']==f['display_fields'][parity]['rgba_sha256']
            checked.append(dict(elapsed_s=row['elapsed_s'],tick=row['metadata']['tick'],png_sha256=row['sha256'],
                                rgba_sha256=got['rgba_sha256'],canonical=str(path.relative_to(HERE))))
        emit(label+'-host-survey',checked)
        emit(label+'-function-tail',dict(lines=p['function_lines'],distinct=p['function_distinct'],
             mismatches=p['function_mismatches'],live_stack=p['function_live_stack']))
        assert p['function_mismatches']==0 and not p['function_live_stack']
        emit(label+'-tap-tail',s['tap_tail'])
    p=load('e8b-progress.json')
    assert p['missing_markers']==p['parsed_missing']==3834 and not p['damaged_missing']
    query=[r for r in p['missing_groups'] if r['target']=='0x2c5140']
    assert {r['source']:r['count'] for r in query}=={'0x2c44a8':2,'0x23d6a4':1249}
    for r in query:
        for k,v in [('policy','1'),('a0','0xb851a0'),('a0[0]','0x486f78'),('a0[4]','0x0'),('v0','0x2c5140')]:
            assert r['values'][k]=={v:r['count']}
    emit('e8b-query-wall',query)
    for label in ['e8a','e8b']:
        hot=load(label+'-progress.json')['hot_pc']
        mc=[r for r in hot if 0x409940<=int(r['pc'],16)<=0x40b028]
        assert len(mc)==1 and mc[0]['pc']=='0x409940' and mc[0]['count']==1
        emit(label+'-memory-card-api',mc)
    emit('e8b-other-missing-targets',[r for r in p['missing_groups'] if r['target']!='0x2c5140'])
    out.append('# E8 JOIN TAIL COMPLETE: both guarded S series; 5/5 copies per boot; D=12358; exact field Present; complete missing-query records; coverage wall only')
    (HERE/'e8-join.txt').write_text('\n'.join(out)+'\n')
    print(out[-1])


if __name__=='__main__':main()
