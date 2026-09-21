#!/usr/bin/env python3
"""Join E17 query calls/returns to same-run constructor and UI-pointer guards."""
import argparse,json
from collections import Counter
from pathlib import Path
from e17_closed_events import tap
E=Path(__file__).resolve().parent;RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['a','b']);args=ap.parse_args();label='e17'+args.phase
    result=json.loads((E/f'{label}-result.json').read_text());assert result.get('release_utc')
    events,tail=tap(RUN/f'{label}-join/e7-events.txt',allow_missing_footer=False)
    rows=[r for r in events if r['kind'].startswith('mc-')]
    constructors=[r for r in rows if r['kind']=='mc-constructor'];pointers=[r for r in rows if r['kind']=='mc-ui-pointer']
    calls=[r for r in rows if r['kind']=='mc-call'];returns=[r for r in rows if r['kind']=='mc-return']
    objects={r['MC'] for r in constructors};queries=[r for r in calls if r['target']==0x2c5140]
    qreturns=[r for r in returns if r['target']==0x2c5140]
    assert constructors and pointers and queries and qreturns
    assert all(r['pc']==0x2c3fc4 and r['value']==0x486f78 and r['width']==4 for r in constructors)
    assert all(r['pc']==0x23d5c8 and r['guard']==1 and r['value'] in objects for r in pointers)
    assert all(r['a0'] in objects and r['MC']==r['a0'] and r['VT']==0x486f78 for r in queries+qreturns)
    # Pair by thread/target/source in LIFO order; log C++ exits separately from guest returns.
    stacks={};pairs=[];unmatched=[]
    for row in rows:
        if row['kind'] not in ['mc-call','mc-return']:continue
        key=(row['thread'],row['target'],row['source']);stack=stacks.setdefault(key,[])
        if row['kind']=='mc-call':stack.append(row)
        elif not stack:unmatched.append(row)
        else:
            start=stack.pop();pairs.append(dict(call=start,exit=row,guest_return=row['pc']==row['source']+8))
    qpairs=[p for p in pairs if p['call']['target']==0x2c5140]
    assert len(qpairs)==len(queries)==len(qreturns) and all(p['guest_return'] for p in qpairs)
    assert all(p['call']['a0']==p['exit']['a0'] and p['call']['sp']==p['exit']['sp'] and
               p['exit']['v0']==int(bool(p['call']['state'] or p['call']['outstanding'])) for p in qpairs)
    truth=Counter((p['call']['source'],p['call']['state'],p['call']['outstanding'],p['exit']['v0'],p['exit']['pc']) for p in qpairs)
    ui={r['UI'] for r in pointers}
    pending=[r for r in rows if r['kind']=='mc-write' and r['addr'] in {u+0x338 for u in ui}]
    ppairs=[p for p in pairs if p['call']['target']==0x2c5300]
    for pair in ppairs:
        a,b=pair['call'],pair['exit']
        assert pair['guest_return'] and a['a0']==b['a0'] and a['a1']==b['a1'] and a['sp']==b['sp']
        assert a['MC']==a['a0'] and a['a0'] in objects and a['VT']==b['VT']==0x486f78
        assert a['a1'] in (0,1)
        assert b['v0']==int(a['slot'+str(a['a1'])]==-10002),(a,b)
    ui344=[r for r in rows if r['kind']=='mc-write' and r['addr'] in {u+off for u in ui for off in [0x344,0x424]}]
    leafpairs=[p for p in pairs if p['call']['target']==0x2c5358]
    true_statuses={-10001,-7,-5,-4,-3,-2,-1,0}
    for pair in leafpairs:
        a,b=pair['call'],pair['exit']
        assert pair['guest_return'] and a['a0']==b['a0'] and a['a1']==b['a1'] and a['sp']==b['sp']
        assert a['MC']==a['a0'] and a['a0'] in objects and a['VT']==b['VT']==0x486f78 and a['a1'] in (0,1)
        assert b['v0']==int(a['slot'+str(a['a1'])] in true_statuses),(a,b)
    wrapperpairs=[p for p in pairs if p['call']['target']==0x2d3810]
    flagpairs=[p for p in pairs if p['call']['target'] in (0x241b20,0x241cd8)]
    uiflags=[r for r in rows if r['kind']=='mc-write' and r['addr'] in {u+off for u in ui for off in (0x43c,0x440)}]
    uistates=[r for r in rows if r['kind']=='mc-write' and r['addr'] in {u+off for u in ui for off in (0x130,0xb8,0x748)}]
    routes=[p for p in pairs if p['call']['source'] in (0x23eb68,0x23e7e4,0x23e800,0x23e528) or p['call']['target'] in (0x23e540,0x23eb50,0x23cf38,0x23d570)]

    table=dict(label=label,constructors=constructors,ui_pointers=pointers,query_calls=len(queries),query_returns=len(qreturns),
               truth=[dict(source=hex(k[0]),state=k[1],outstanding=k[2],v0=k[3],return_pc=hex(k[4]),count=v) for k,v in truth.items()],
               target_counts={hex(k):v for k,v in Counter(r['target'] for r in calls).items()},
               port_query_pairs=[p for p in qpairs if p['call']['source']==0x2c44a8],pending_writes=pending,
               api_pairs=[p for p in pairs if p['call']['target'] in [0x40a498,0x40a360]],
               sibling_missing=[r for r in rows if r['kind']=='mc-missing'],
               predicate_pairs=ppairs,predicate_calls=len(ppairs),ui344_writes=ui344,
               leaf_pairs=leafpairs,leaf_calls=len(leafpairs),wrapper_pairs=wrapperpairs,flag_pairs=flagpairs,ui_flag_writes=uiflags,ui_state_writes=uistates,state_routes=routes,
               nonreturn_exits=[p for p in pairs if not p['guest_return']],unmatched_returns=unmatched,
               unclosed_calls=[r for stack in stacks.values() for r in stack],tap_tail=tail,
               source_shutdown_complete=tail is not None,
               closure_gap='Runtime destructor bypassed by main std::_Exit(0); source shutdown counters unavailable' if tail is None else None)
    (E/f'{label}-card.json').write_text(json.dumps(table,indent=2)+'\n')
    (E/f'{label}-card-events.json').write_text(json.dumps(rows,indent=2)+'\n')
    with (E/f'{label}-card.txt').open('w') as f:
        for key in ['constructors','ui_pointers','query_calls','query_returns','truth','target_counts','port_query_pairs','pending_writes','predicate_pairs','leaf_pairs','wrapper_pairs','flag_pairs','ui_flag_writes','ui_state_writes','state_routes','ui344_writes','unmatched_returns','unclosed_calls']:
            f.write(key+' '+json.dumps(table[key],sort_keys=True)+'\n')
        f.write('# E17 CARD TAIL COMPLETE: same-run objects and query truth/return joins\n')
    print(label,'queries',len(queries),'objects',[hex(x) for x in sorted(objects)],'targets',table['target_counts'])
    print('# E17 CARD TAIL COMPLETE')
if __name__=='__main__':main()
