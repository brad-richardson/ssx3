#!/usr/bin/env python3
"""Reproduce the closed-capture caller advance and the out-of-scope low-bit wall."""
import hashlib
import json
from pathlib import Path

from e12_io import read_capture
from e12_progress import stream
from e12_static import Elf, ROOT

E=Path(__file__).resolve().parent
RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')

def main():
    card=json.loads((E/'e12a-card.json').read_text())
    raw=read_capture(RUN/'boot-e12a-1.log')
    lines=raw.decode().splitlines()
    predicates=card['predicate_pairs']
    assert len(predicates)==2
    assert {p['call']['source'] for p in predicates}=={0x242150,0x2d37f8}
    assert all(p['call']['slot0']==0 and p['call']['a1']==0 and p['exit']['v0']==0 for p in predicates)
    stores=card['ui344_writes']
    init=[r for r in stores if r['pc']==0x242110]
    clears=[r for r in stores if r['pc']==0x2421b4]
    assert len(init)==1 and init[0]['value']==1 and not clears
    sibling=card['sibling_missing']
    assert len(sibling)==113 and all(r['slot0']==r['slot1']==0 and r['a1']==0 and r['v0']==0x2c5358 for r in sibling)
    last=sibling[-1]
    assert last['tick']==225 and last['source']==0x2d3828
    selected=[]
    for n,line in enumerate(lines,1):
        if '[guest-branch:missing-target]' in line and 'target=0x2c5358 ' in line and ' -> 0x241b20 -> ' in line:
            assert 'sp='+hex(last['sp'])+' ' in line and 'a0='+hex(last['a0'])+' ' in line
            assert 'a1=0x0 ' in line and 'v0=0x2c5358 ' in line and 'policy=1 ' in line
            assert line.endswith(' -> 0x2d3810')
            selected.append(dict(line=n,text=line))
    assert len(selected)==1
    # Raw words independently pin the slot, wrapper, low-bit consumer and state-4 route.
    elf=Elf(ROOT)
    words={0x48711c:0x2c5358,0x487124:0x2d3810,0x241c48:0x38420001,
           0x241c4c:0x30420001,0x241c58:0x000210c0,0x241d10:0xae04043c,
           0x23e600:0x1040000a,0x23e608:0x0c08fad4,0x23eb54:0x24050004}
    for pc,w in words.items():assert elf.word(pc)==w,(hex(pc),elf.word(pc),w)
    # Preserve complete function-call blocks, including indentation and raw line numbers.
    targets={'sub_002420C8_0x2420c8','sub_0023E540_0x23e540'}
    chunks=[];current=None;root=None
    with stream(RUN/'ps2_log-e12a-1.txt') as f:
        for n,line in enumerate(f,1):
            a=line.split()
            if len(a)<2:continue
            if current is None and a[0]=='>>' and a[1] in targets:
                root=a[1];current=[]
            if current is not None:current.append(dict(line=n,text=line.rstrip()))
            if current is not None and a[:2]==['<<',root]:
                chunks.append(dict(root=root,rows=current));current=None
    assert current is None and len(chunks)==3
    caller=chunks[0]
    assert caller['root']=='sub_002420C8_0x2420c8'
    caller_text='\n'.join(r['text'] for r in caller['rows'])
    assert caller_text.index('sub_002C5300')<caller_text.index('sub_002C63E8')<caller_text.index('sub_002C53B0')
    selector=chunks[-1];selector_text='\n'.join(r['text'] for r in selector['rows'])
    assert selector_text.index('sub_00241B20')<selector_text.index('sub_0023EB50')<selector_text.index('sub_0023CDB0')
    # This is an ELF/source-derived consequence, not a claim that UI+0x43c was watched.
    bit=lambda v:((v^1)&1)<<3
    result=dict(outcome='ii',raw_sha256=hashlib.sha256(raw).hexdigest(),predicate_pairs=predicates,
                ui344_initialization=init,ui344_clear_count=len(clears),sibling_count=len(sibling),
                decisive_missing=last,raw_missing=selected[0],
                raw_word_guards={hex(k):hex(v) for k,v in words.items()},
                consumer=dict(pc='0x241c48..0x241c64',expression='((v0 ^ 1) & 1) << 3',
                              observed_stale=hex(last['v0']),observed_derived_bit3=bit(last['v0']),
                              guest_status=0,guest_required_result=1,guest_derived_bit3=bit(1)),
                downstream=dict(flag_store='0x241d10: UI+0x43c',observed_call='0x23e608 -> 0x23eb50',
                                state_argument='0x23eb54 sets a1=4; 0x23eb68 dispatches to UI state handler',
                                trace_observed=True,flag_word_directly_watched=False),
                function_chunks=chunks,
                qualification='The even stale value and exact low-bit consumer force a wrong bit-3 contribution. Function traces reach the subsequent state-4 route. The flag word and state-handler argument were not directly tapped; those links are code-derived. No claim that every pixel or later wait has only this cause.',
                next_action='A separately authorized single-entry 0x2c5358 repair with exact-result and low-bit-consumer regressions, plus direct UI flag/state probes. No repair executed in E12.')
    (E/'e12a-residual-join.json').write_text(json.dumps(result,indent=2)+'\n')
    with (E/'e12a-residual-receipts.txt').open('w') as f:
        f.write(f"# Closed boot sha256={result['raw_sha256']}\n")
        f.write(f"{selected[0]['line']} {selected[0]['text']}\n")
        for chunk in chunks:
            f.write('\n# '+chunk['root']+'\n')
            for row in chunk['rows']:f.write(f"{row['line']} {row['text']}\n")
        f.write('# E12 RESIDUAL RECEIPTS TAIL COMPLETE\n')
    print('predicate returns 2/2 correct; UI344 init=1 clear=0; sibling113; low-bit contribution stale8 versus guest0')
    print('decisive missing raw line',selected[0]['line'],'tick',last['tick'],'seq',last['seq'])
    print('# E12 RESIDUAL JOIN TAIL COMPLETE')

if __name__=='__main__':main()
