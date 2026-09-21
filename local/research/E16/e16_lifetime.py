"""Same-run lifetime guards; retain post-reuse stores without object interpretation."""
from e16_common import *
from e16_closed_events import tap

events,tail=tap(P/'run/e16a-join/e7-events.txt')
constructors=[r for r in events if r['kind']=='mc-constructor']
pointers=[r for r in events if r['kind']=='mc-ui-pointer']
intervals=[]
for c in constructors:
    endings=[r for r in events if r['seq']>c['seq'] and r['kind']=='mc-write' and r['addr']==c['MC'] and r['value']!=0x486f78]
    end=endings[0] if endings else None
    pointers_here=[p for p in pointers if p['MC']==c['MC'] and p['guard']==1 and p['seq']>=c['seq'] and (end is None or p['seq']<end['seq'])]
    assert pointers_here
    intervals.append(dict(MC=hex(c['MC']),constructor=c,end=end,ui_pointers=pointers_here,
        later_raw_stores=[r for r in events if end and r['seq']>=end['seq'] and r['kind']=='mc-write' and r['MC']==c['MC']],
        interpretation='MC object fields and associated guarded UI transitions interpreted only before end.seq; later stores are raw'))
guarded=[]
for r in events:
    if r['kind'] not in ('mc-call','mc-return') or r['target'] not in (0x2c5140,0x2c5300,0x2c5358):continue
    windows=[i for i in intervals if int(i['MC'],16)==r['MC'] and i['constructor']['seq']<=r['seq'] and (i['end'] is None or r['seq']<i['end']['seq'])]
    assert len(windows)==1 and r['VT']==0x486f78, r
    guarded.append(r['seq'])
aligns=[r for r in events if r['kind']=='e15-align']
for a in aligns:
    assert any(int(i['MC'],16)==a['MC'] and i['constructor']['seq']<a['seq'] and (i['end'] is None or a['seq']<i['end']['seq']) and any(p['UI']==a['UI'] and p['seq']<a['seq'] for p in i['ui_pointers']) for i in intervals)
save('e16a-lifetime.json',dict(intervals=intervals,guarded_card_event_count=len(guarded),guarded_card_event_sequences=guarded,aligned_triggers=aligns,shutdown=tail))
print('dynamic lifetimes',len(intervals),'guarded card events',len(guarded),'alignments',len(aligns))
print('# E16 LIFETIME TAIL COMPLETE — post-reuse stores remain raw')
