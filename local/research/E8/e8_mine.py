#!/usr/bin/env python3
"""Mine completed E8 captures only. Standard library; no guest execution."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
from e8_io import read_capture

EVIDENCE=Path(__file__).resolve().parent
RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')
WATCH=re.compile(r'\[diag:watch\] addr=0x([0-9a-f]+) width=(\d+) value=0x([0-9a-f]+) pc=0x([0-9a-f]+) thread=(-?\d+) ra=0x([0-9a-f]+) sp=0x([0-9a-f]+)')
DISPLAY={0x12000000:'PMODE',0x12000020:'SMODE2',0x12000070:'DISPFB1',0x12000080:'DISPLAY1',0x12000090:'DISPFB2',0x120000a0:'DISPLAY2',0x120000e0:'BGCOLOR'}


def read(path):
    return read_capture(path)


def counts(values):
    return {str(k):v for k,v in Counter(values).items()}


def tap(path):
    rows=[]
    text=read_capture(path).decode()
    for line in text.splitlines():
        if not line.startswith('seq='): continue
        row={}
        for item in line.split():
            key,value=item.split('=',1)
            try: row[key]=int(value,0)
            except ValueError: row[key]=value
        rows.append(row)
    assert [r['seq'] for r in rows]==list(range(1,len(rows)+1)), 'tap sequence gap'
    tail=text.splitlines()[-1]
    assert tail.startswith('# E7 COMPLETE'), 'missing tap completion'
    assert all(x in tail for x in ['bootTruncated=0','boundaryTruncated=0','packetTruncated=0']), tail
    return rows,tail


def packet(path):
    data=read_capture(path); pos=0;tags=[];regs=[]
    while pos+16<=len(data):
        lo,hi=struct.unpack_from('<QQ',data,pos)
        nloop=lo&0x7fff;flg=(lo>>58)&3;nreg=(lo>>60)&15 or 16
        tag=dict(offset=pos,nloop=nloop,flg=flg,nreg=nreg,eop=(lo>>15)&1,lo=hex(lo),hi=hex(hi))
        tags.append(tag);pos+=16
        count=nloop*nreg
        if flg==0:
            end=pos+count*16
            if end>len(data): tag['truncated']=True;break
            for i in range(count):
                reg=(hi>>((i%nreg)*4))&15
                if reg==14:
                    value,address=struct.unpack_from('<QQ',data,pos+i*16)
                    item=dict(offset=pos+i*16,reg=hex(address&255),value=hex(value))
                    if address&255 in [0x4c,0x4d]: item.update(fbp=value&511,fbw=(value>>16)&63,psm=(value>>24)&63)
                    if address&255 in [0x06,0x07]: item.update(tbp=value&0x3fff,tbw=(value>>14)&63,psm=(value>>20)&63)
                    regs.append(item)
            pos=end
        elif flg==1: pos+=(count*8+15)&~15
        elif flg==2: pos+=nloop*16
        else: tag['unsupported']=True;break
    return dict(file=path.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),parsed_end=pos,tags=tags,registers=regs)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['a','b','c','d']);args=ap.parse_args()
    label='e8'+args.phase
    result=json.loads((EVIDENCE/f'{label}-result.json').read_text())
    assert result.get('release_utc') and not result.get('lease_ownership_error'), 'analysis requires completed owned release'
    data=read(RUN/f'boot-{label}-1.log');text=data.decode(errors='replace');lines=text.splitlines()
    summary=dict(label=label,raw_bytes=len(data),raw_sha256=hashlib.sha256(data).hexdigest(),raw_lines=len(lines),result=result)
    rows=[];bad=[];armed=frozen=None
    for n,line in enumerate(lines,1):
        if '[e4:armed]' in line: armed=n
        if '[e4:frozen]' in line: frozen=n
        found=list(WATCH.finditer(line))
        if line.count('[diag:watch]')!=len(found): bad.append(dict(line=n,text=line))
        for m in found:
            a,w,v,pc,th,ra,sp=m.groups()
            rows.append(dict(line=n,addr=int(a,16),width=int(w),value=int(v,16),pc=int(pc,16),thread=int(th),ra=int(ra,16),sp=int(sp,16)))
    summary.update(watch_markers=text.count('[diag:watch]'),parsed_watch=len(rows),damaged_watch_lines=len(bad),armed_line=armed,frozen_line=frozen)
    (EVIDENCE/f'{label}-damaged-watch.json').write_text(json.dumps(bad,indent=2)+'\n')
    summary['singleton']=[r for r in rows if r['addr']==0x4a289c]
    summary['raw_display_values']={name:counts(hex(r['value']) for r in rows if r['addr']==a) for a,name in DISPLAY.items()}
    summary['boundary_watch']=[r for r in rows if armed and frozen and armed<r['line']<frozen]
    summary['damaged_boundary_lines']=[r for r in bad if armed and frozen and armed<r['line']<frozen]
    compact=[]
    for row in rows:
        key={k:v for k,v in row.items() if k!='line'}
        if compact and compact[-1]['key']==key:
            compact[-1]['copies']+=1
        else: compact.append(dict(line=row['line'],key=key,copies=1))
    with (EVIDENCE/f'{label}-watch-series.txt').open('w') as f:
        f.write('# line addr width value pc thread ra copies; identical-run grouping only, not a RAM guest-store count\n')
        for r in compact:
            d=r['key'];f.write(f'{r["line"]} 0x{d["addr"]:x} {d["width"]} 0x{d["value"]:x} 0x{d["pc"]:x} {d["thread"]} 0x{d["ra"]:x} x{r["copies"]}\n')
        f.write('# E8 WATCH SERIES TAIL COMPLETE\n')
    disp=[r for r in compact if r['key']['addr']==0x12000070]
    summary['display_bursts_grouped']=len(disp)
    summary['display_pc_ra']=counts((hex(r['key']['pc']),hex(r['key']['ra']),r['key']['thread']) for r in disp)
    history=read(RUN/f'{label}-1/e4-history.txt').decode()
    summary['history_headers']=history.splitlines()[:3]
    summary['history_kinds']=counts(re.findall(r'kind=(\w+)',history))
    summary['draw_fbps']=counts(re.findall(r'kind=draw .*?fbp=(\d+)',history))
    summary['frame2_events']=len(re.findall(r'reg=0x4d:',history))
    present=read(RUN/f'{label}-1/e4-present.txt')
    summary['present_sha256']=hashlib.sha256(present).hexdigest()
    summary['present']=present.decode().splitlines()
    if True:
        path=RUN/f'{label}-join/e7-events.txt'
        events,tail=tap(path)
        summary['tap_tail']=tail
        summary['tap_kinds']=counts(r['kind'] for r in events)
        c=[r for r in events if r['kind']=='field-before' and r['pc']==0x382b30]
        summary['counter']={'n':len(c),'first':c[0] if c else None,'last':c[-1] if c else None,
            'continuous':bool(c) and [r['lo'] for r in c]==list(range(1,len(c)+1)),
            'pre_matches':all(r['C']+1==r['lo'] for r in c),
            'M':counts(r['M'] for r in c),'G':counts(r['G'] for r in c),
            'pairs':counts((r['A'],r['B'],r['P'],r['D']) for r in c if r['C']>0)}
        summary['gate_writers']=counts((hex(r['pc']),r['lo']) for r in events if r['kind']=='field-before' and r['off']==0xf44)
        summary['mode_writers']=[r for r in events if r['kind']=='field-before' and r['off']==0x59e8]
        summary['mask_events']=[r for r in events if r['kind']=='vif-mask']
        summary['boundary_events']=[r for r in events if 599<=r['tick']<=603]
        boundary=[r for r in events if r['tick']==600]
        summary['tick600_kinds']=counts(r['kind'] for r in boundary)
        summary['tick600_copy']=[r for r in boundary if r['kind'] in ['cpu-fifo','fifo-before','fifo-after','gif-start','gif-dma','path3-queue','path3-send','path3-flush','gif-complete']]
        copies=[r for r in boundary if r['kind']=='gif-dma' and r['source']==0x4ffcc0]
        summary['tick600_copy_gs_matches']=[{'copy':r,'gs_matches':[x for x in boundary if x['kind']=='gs-enter' and x['fnv64']==r['fnv64'] and x['bytes']==r['bytes']]} for r in copies]
        pp=RUN/f'{label}-join'
        packets=sorted(pp.glob('e7-copy-*.bin'))
        if not packets:
            manifest=json.loads((EVIDENCE/f'{label}-retained.json').read_text())
            packets=sorted(Path(r['original']) for r in manifest['files']
                           if Path(r['original']).parent==pp and Path(r['original']).name.startswith('e7-copy-'))
        summary['packets']=[packet(p) for p in packets]
        with (EVIDENCE/f'{label}-burst-series.txt').open('w') as f:
            f.write('# call tick seq S C-before G M A B P D; snapshot before C increment\n')
            for r in c: f.write(' '.join(str(r[x]) for x in ['lo','tick','seq','S','C','G','M','A','B','P','D'])+'\n')
            f.write('# E8 BURST SERIES TAIL COMPLETE\n')
    path=EVIDENCE/f'{label}-summary.json'
    path.write_text(json.dumps(summary,indent=2)+'\n')
    for key in ['label','raw_bytes','watch_markers','parsed_watch','damaged_watch_lines','armed_line','frozen_line','singleton','display_bursts_grouped','history_kinds','draw_fbps','frame2_events','present_sha256','tap_tail','tap_kinds','counter','gate_writers','mode_writers','tick600_kinds','tick600_copy_gs_matches']:
        if key in summary: print(key,json.dumps(summary[key]))
    print('# E8 MINER TAIL COMPLETE',path)


if __name__=='__main__': main()
