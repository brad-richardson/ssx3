#!/usr/bin/env python3
"""Audit a CLOSED quiet E7 source without inventing its event-driven footer."""
import gzip,hashlib,json,re
from pathlib import Path
from e13_io import read_capture
E=Path(__file__).resolve().parent
RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')
R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
result=json.loads((E/'e13a-result.json').read_text())
caps=json.loads((E/'e13a-closed-caps.json').read_text())
assert result['release_utc'] and result['rc']==0 and caps['all_caps_pass']
data=read_capture(RUN/'e13a-join/e7-events.txt');lines=data.decode().splitlines()
assert data.endswith(b'\n') and lines[0].startswith('# E7 observation only;')
assert '# E7 COMPLETE' not in data.decode()
events=[]
for line in lines[1:]:
    assert line.startswith('seq=') and len(line)<1024
    row={}
    for part in line.split():
        k,v=part.split('=',1)
        try:row[k]=int(v,0)
        except ValueError:row[k]=v
    events.append(row)
assert [r['seq'] for r in events]==list(range(1,len(events)+1))
assert max(r['tick'] for r in events)<599
boot_bytes=sum(len((line+'\n').encode()) for line in lines[1:])
assert boot_bytes<4*1024**2
progress=json.loads((E/'e13a-progress.json').read_text())
assert progress['function_mismatches']==0 and not progress['function_live_stack']
assert next(t for t in progress['threads'] if t['id']==1)['wait_reason_name']=='Mpeg'
assert next(t for t in progress['threads'] if t['id']==5)['wait_id']==32
live=[json.loads(l) for l in (E/'e13a-liveness.txt').read_text().splitlines()]
samples=[r for r in live if 'bytes' in r and r['elapsed_s']>=15]
assert samples and len({r['bytes']['e7_dir'] for r in samples})==1
history=read_capture(RUN/'e13a-1/e4-history.txt').decode()
assert 'kind=present' in history and 'kind=draw' not in history and 'entries=1' in history
# Bound every E7 event format, independently of the missing footer flags.
# All formats are fixed literal strings with integer substitutions.
paths=['include/ps2_e7.h','src/lib/ps2_runtime.cpp','src/lib/ps2_memory.cpp','src/lib/ps2_vif1_interpreter.cpp']
source_rows=[];formats=[]
out=E/'observation-sources';out.mkdir(exist_ok=True)
for rel in paths:
    source=R/'ps2xRuntime'/rel;dest=out/(source.name+'.gz')
    if dest.exists():raw=gzip.decompress(dest.read_bytes())
    else:
        raw=source.read_bytes();dest.write_bytes(gzip.compress(raw,mtime=0))
    source_rows.append(dict(path=str(source),retained=str(dest.relative_to(E)),sha256=hashlib.sha256(raw).hexdigest()))
    for n,line in enumerate(raw.decode().splitlines(),1):
        if not re.search(r'(?:ps2_e7::)?\bevent\(',line):continue
        for fmt in re.findall(r'"([^"\n]*%[^"\n]*)"',line):
            def width(m):
                spec=m[0];size=20 if 'll' in spec or 'z' in spec else 11 if spec.endswith('d') else 8 if spec.endswith('x') else 10
                return 'X'*size
            worst=re.sub(r'%(?:ll|z)?[xud]',width,fmt)
            assert '%' not in worst and len(worst)<768,(source,n,fmt)
            formats.append(dict(file=source.name,line=n,format=fmt,worst_body_bytes=len(worst)))
assert formats and max(r['worst_body_bytes'] for r in formats)<768
assert max(r['worst_body_bytes'] for r in formats)+100<1024
rec=dict(raw_sha256=hashlib.sha256(data).hexdigest(),raw_bytes=len(data),events=len(events),
         complete_newline=True,contiguous_sequences=True,first=events[0],last=events[-1],
         footer_present=False,footer_reason='Footer is emitted only on a subsequent event(tick>603), not on shutdown. The source went quiet at tick248; no later event invokes that branch.',
         boot_event_bytes=boot_bytes,boot_budget=4*1024**2,boundary_events=0,packet_files=0,
         source_sizes_constant_after_s=15,observed_through_s=samples[-1]['elapsed_s'],
         max_format_body_bytes=max(r['worst_body_bytes'] for r in formats),formats=formats,sources=source_rows,
         interpretation='Closed, contiguous observed prefix with balanced call exits and no byte/format-cap mechanism triggered; no artificial runtime footer and no claim of a live copy at tick600.',
         late_history='one Present and zero draws',function_trace_balanced=True)
(E/'e13a-observation-closure.json').write_text(json.dumps(rec,indent=2)+'\n')
print('closed E7 events',len(events),'last tick',events[-1]['tick'],'bytes',len(data),'footer absent; explicitly retained')
print('worst possible formatted body',rec['max_format_body_bytes'],'<768; byte budget not approached; source quiet after15s')
print('# E13 OBSERVATION AUDIT TAIL COMPLETE; raw remains unchanged')
