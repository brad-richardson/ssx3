"""Separate exact guest entry observations from generated owner log labels."""
import json
from collections import Counter
from e16_common import E, P, save
from e16_closed_events import tap
from e16_progress import stream

sources=json.loads((E/'function-owner-alias-source.json').read_text())['sources']
owner='sub_003B0B40_0x3b0b40'
owner_lines={r['line']:r['text'] for r in sources[0]['excerpts']}
assert 'PS_LOG_ENTRY' in owner_lines[18] and 'switch (ctx->pc)' in owner_lines[21]
assert 'case 0x3b0c58u: goto label_3b0c58;' in owner_lines[92]
assert 'label_3b0c58:' in owner_lines[811]
assert all(owner in r['text'] for r in sources[2]['excerpts'])
events,_=tap(P/'run/e16a-join/e7-events.txt')
calls=[r for r in events if r['kind']=='mpeg-call']
setup=[r for r in calls if r['target']==0x3b0c58]
assert len(setup)==1 and setup[0]['source']==0x3b0520 and setup[0]['callback']==0
returned=[r for r in events if r['kind']=='mpeg-return' and r['id']==setup[0]['id']]
assert len(returned)==1 and returned[0]['pc']==0x3b0528
assert not [r for r in calls if r['target'] in (0x3b0b10,0x3b0b40,0x4029d0)]
counts=Counter();stack=[];hits=[];n=0
with stream(P/'run/ps2_log-e16a-1.txt') as f:
    for n,line in enumerate(f,1):
        assert line.endswith('\n')
        parts=line.split()
        if not parts:continue
        if parts[0]=='>>':
            counts[parts[1]]+=1
            if parts[1]==owner:hits.append(dict(line=n,kind='enter',parents=stack.copy()))
            stack.append(parts[1])
        elif parts[0]=='<<':
            assert stack and stack[-1]==parts[1],n
            if parts[1]==owner:hits.append(dict(line=n,kind='exit',parents=stack[:-1]))
            stack.pop()
assert not stack and counts[owner]==1 and len(hits)==2
assert hits[0]['parents'][-1]=='sub_003B04F8_0x3b04f8'
selected={k:counts[k] for k in [owner,'sub_003B0B10_0x3b0b10','sub_004029D0_0x4029d0']}
assert selected['sub_003B0B10_0x3b0b10']==selected['sub_004029D0_0x4029d0']==0
result=dict(function_lines=n,counts=selected,owner_occurrences=hits,setup_call=setup[0],setup_return=returned[0],
    registry_rows=sources[2]['excerpts'],exact_callback_dispatches=0,exact_helper_dispatches=0,add_bs_dispatches=0,
    interpretation='Owner logging precedes its entry-PC switch. The one owner label is the observed 0x3b0c58 setup entry, not an exact 0x3b0b40 callback helper dispatch.',
    scope='Source excerpts, exact dispatch rows, and complete balanced function census; no callback inferred from an owner label.')
save('function-owner-alias-audit.json',result)
print(json.dumps({k:v for k,v in result.items() if k not in ('owner_occurrences','setup_call','setup_return','registry_rows')},indent=2))
print('# E16 OWNER ALIAS AUDIT TAIL COMPLETE')
