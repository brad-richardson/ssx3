#!/usr/bin/env python3
"""Reproduce E12 progression and missing-query receipts from closed captures."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re

from e12_io import resolve, read_capture

HERE=Path(__file__).resolve().parent
RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')
MARK='[guest-branch:missing-target] '
FIELDS=re.compile(r'([^ =]+)=([^ ]+)')


def stream(path):
    path=resolve(path)
    return gzip.open(path,'rt') if path.suffix=='.gz' else path.open()


def function_census(label):
    entries=Counter();roots=Counter();stack=[];samples=[];mismatches=[];n=0
    contexts=Counter();sample_counts=Counter()
    with stream(RUN/f'ps2_log-{label}-1.txt') as f:
        for n,line in enumerate(f,1):
            assert line.endswith('\n'), (n,'unterminated function trace')
            parts=line.split()
            if not parts:continue
            if parts[0]=='>>':
                name=parts[1];entries[name]+=1
                if not stack:roots[name]+=1
                if name.startswith(('sub_002C5570','sub_002C4410','sub_00241380','sub_0023D660')):
                    parent=' > '.join(stack);contexts[(name,parent)]+=1
                    if sample_counts[(name,parent)]<2:
                        samples.append(dict(line=n,name=name,parents=stack.copy()))
                        sample_counts[(name,parent)]+=1
                stack.append(name)
            elif parts[0]=='<<':
                if not stack or stack[-1]!=parts[1]:mismatches.append((n,parts[1],stack.copy()))
                elif stack:stack.pop()
    assert not mismatches and not stack,(mismatches[:2],stack)
    result=dict(lines=n,entries=dict(entries),roots=dict(roots),samples=samples,
                contexts=[dict(name=k[0],parents=k[1],count=v) for k,v in contexts.items()],
                mismatches=len(mismatches),live_stack=stack)
    (HERE/f'{label}-function-census.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['a','b','c','d']);args=ap.parse_args()
    label='e12'+args.phase
    end=json.loads((HERE/f'{label}-result.json').read_text());assert end.get('release_utc')
    raw=read_capture(RUN/f'boot-{label}-1.log');lines=raw.decode(errors='replace').splitlines()
    missing=[];damaged=[];progress=[]
    for n,line in enumerate(lines,1):
        if any(x in line for x in ['[diag:threads]','[diag:thread]','[diag:stubs]',
                                  '[diag:syscalls]','[IOP/RPC trace:unhandled]','[diag:drop]']):
            progress.append(f'{n} {line}')
        if MARK in line:
            pos=line.index(MARK);row=dict(FIELDS.findall(line[pos+len(MARK):].split(' trace=',1)[0]))
            required=['kind','source','target','pc','ra','sp','a0','s0','v0','v1','a0[0]','a0[4]','policy']
            item=dict(line=n,fields=row,text=line)
            if all(k in row for k in required) and re.search(r' trace=0x[0-9a-f]+(?: -> 0x[0-9a-f]+)*$',line):
                missing.append(item)
            else:damaged.append(item)
    (HERE/f'{label}-progress-lines.txt').write_text('\n'.join(progress)+'\n# E12 PROGRESS TAIL COMPLETE\n')
    groups=defaultdict(list)
    for row in missing:groups[(row['fields']['target'],row['fields']['source'])].append(row)
    rows=[]
    for (target,source),group in groups.items():
        rows.append(dict(target=target,source=source,count=len(group),first=group[0]['line'],last=group[-1]['line'],
                         values={k:dict(Counter(r['fields'].get(k) for r in group)) for k in
                                 ['kind','policy','a0','a0[0]','a0[4]','a0[c]','v0','s0']}))
    card=[r for r in missing if r['fields']['target']=='0x2c5140']
    selected=[]
    for (target,source),group in groups.items():
        if target=='0x2c5140':
            selected.extend(group[:2]);selected.extend(group[-1:])
    selected={r['line']:r for r in selected}
    with (HERE/f'{label}-missing-query.txt').open('w') as f:
        f.write(f'# {label} boot log SHA256={hashlib.sha256(raw).hexdigest()} bytes={len(raw)} lines={len(lines)}\n')
        for n,row in sorted(selected.items()):f.write(f'{n} {row["text"]}\n')
        f.write(f'# missing markers={raw.count(MARK.encode())} parsed={len(missing)} damaged={len(damaged)} query={len(card)}\n')
        f.write('# E12 MISSING QUERY TAIL COMPLETE\n')
    park=json.loads(read_capture(RUN/f'park-{label}-1/park-snapshot.json'))
    hot=[r for r in park['hot_pc'] if 0x2c3fa8<=int(r['pc'],16)<0x2c6130 or
         0x409940<=int(r['pc'],16)<=0x40b028 or int(r['pc'],16) in [0x23d660,0x241380,0x382af0]]
    census=function_census(label)
    result=dict(label=label,raw_sha256=hashlib.sha256(raw).hexdigest(),raw_lines=len(lines),
                missing_markers=raw.count(MARK.encode()),parsed_missing=len(missing),damaged_missing=damaged,
                missing_groups=rows,card_query_count=len(card),hot_pc=hot,threads=park['threads'],
                semaphores=park['semaphores'],gs=park['gs'],sched_counts=park['sched_counts'],
                drops=park['drops'],sif_rpc_overflow=park['sif_rpc_overflow'],
                function_lines=census['lines'],function_distinct=len(census['entries']),
                function_mismatches=census['mismatches'],function_live_stack=census['live_stack'])
    (HERE/f'{label}-progress.json').write_text(json.dumps(result,indent=2)+'\n')
    print(label,'missing markers',result['missing_markers'],'parsed',len(missing),'damaged',len(damaged),
          'card query',len(card),'function lines',census['lines'],'distinct',len(census['entries']))
    for row in rows:
        if row['target']=='0x2c5140':print(json.dumps(row))
    print('# E12 PROGRESSION MINER TAIL COMPLETE')


if __name__=='__main__':main()
