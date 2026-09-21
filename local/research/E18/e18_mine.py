"""Dynamic MPEG joins; preserve observed delivery, input, completion, and absence separately."""
import hashlib,json,re,traceback
from collections import Counter
from pathlib import Path
from e18_io import read_capture
from e18_closed_events import tap,fields
E=Path(__file__).resolve().parent
RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run');LABEL='e18a'
def save(name,x):(E/name).write_text(json.dumps(x,indent=2)+'\n')
def main():
    end=json.loads((E/f'{LABEL}-result.json').read_text());assert end.get('release_utc')
    path=RUN/f'{LABEL}-join/e7-events.txt';data=read_capture(path)
    events,tail=tap(path,allow_missing_footer=True)
    lines=data.decode().splitlines();closure=fields(lines[-2]) if tail else None;shutdown=fields(tail) if tail else None
    calls=[r for r in events if r['kind']=='mpeg-call']
    exits={r['id']:r for r in events if r['kind'] in ('mpeg-return','mpeg-unwind')}
    pairs=[dict(call=c,exit=exits.get(c['id'])) for c in calls]
    missing=[c['id'] for c in calls if c['id'] not in exits]
    mismatched=[p for p in pairs if p['exit'] and (p['exit']['target']!=p['call']['target'] or p['exit']['entryA0']!=p['call']['a0'])]
    closureJoin=dict(raw_sha256=hashlib.sha256(data).hexdigest(),raw_bytes=len(data),events=len(events),kinds=dict(Counter(r['kind'] for r in events)),closure=closure,shutdown=shutdown,source_footer=tail is not None,missing_pair_ids=missing,mismatched_pairs=mismatched)
    save('e18a-observation-closure.json',closureJoin)
    targets=Counter(c['target'] for c in calls)
    raw=read_capture(RUN/f'boot-{LABEL}-1.log').decode(errors='replace');bootlines=raw.splitlines()
    def bootgrep(pattern):return [dict(line=n,text=l) for n,l in enumerate(bootlines,1) if re.search(pattern,l)]
    parkpath=RUN/f'park-{LABEL}-1/park-snapshot.json'
    try:park=json.loads(read_capture(parkpath))
    except FileNotFoundError:park=None
    creates=[p for p in pairs if p['call']['target']==0x4027b8]
    registers=[p for p in pairs if p['call']['target']==0x402c08]
    requests=[p for p in pairs if p['call']['target']==0x402a10]
    objects=[]
    for obj in sorted({p['call']['a0'] for p in creates+registers+requests}):
        regs=[p for p in registers if p['call']['a0']==obj]
        reqs=[p for p in requests if p['call']['a0']==obj]
        callbacks=[p for p in pairs if p['call'].get('callback')==1 and p['call']['a0']==obj]
        selected=[r for r in events if r['kind']=='mpeg-selected' and r['a0']==obj]
        inputcalls=[p for p in pairs if p['call']['target']==0x4029d0 and p['call']['a0']==obj]
        inputevents=[r for r in events if r['kind']=='mpeg-input' and r['mpeg']==obj]
        completion=[r for r in events if r['kind']=='mpeg-complete' and r['token']==obj]
        callbackjoins=[]
        for p in callbacks:
            c=p['call'];matching=[r for r in regs if r['call']['a2']==c['target'] and r['call']['a3']==c['a2'] and r['call']['a1']==c.get('cbType')]
            trigger=[r for r in reqs if r['call']['seq']<c['seq']]
            trigger=trigger[-1] if trigger else None
            contained=[q for q in inputcalls if p['exit'] and c['seq']<q['call']['seq']<p['exit']['seq']]
            callbackjoins.append(dict(callback=p,registrations=matching,request=trigger,thread_matches=bool(trigger) and trigger['call']['thread']==c['thread'],stack_matches=bool(trigger) and trigger['call']['sp']==c['sp'],add_bs_inside_observed_scope=contained,scope_is_single_dispatch=True))
        objects.append(dict(mpeg=hex(obj),creates=[p for p in creates if p['call']['a0']==obj],registrations=regs,requests=reqs,
            request_registration_shadows=[r for r in events if r['kind']=='mpeg-request-registration' and r['mpeg']==obj],
            selections=selected,callbacks=callbackjoins,callback_returns=[p for p in callbacks if p['exit'] and p['exit']['kind']=='mpeg-return'],
            add_bs=inputcalls,input_events=inputevents,completion_events=completion,
            matched_waiters=sum(r.get('matched',0) for r in completion),
            waits=[r for r in events if r['kind']=='mpeg-wait' and r['token']==obj],
            lifetime=[p for p in pairs if p['call']['a0']==obj and p['call']['target'] in (0x4027b8,0x4029c8,0x402b58)],
            valid_no_input_returns='Requires complete request/producer control-flow join; not inferred from callback dispatch or v0',
            requested_bytes=sum(r['requested'] for r in inputevents),returned_add_bs_bytes=sum(p['exit']['v0'] for p in inputcalls if p['exit'] and p['exit']['kind']=='mpeg-return' and p['exit']['v0']<0x80000000)))
    result=dict(objects=objects,target_dispatch_counts={hex(k):v for k,v in sorted(targets.items())},
        producer_events=[r for r in events if r['kind'] in ('mpeg-producer','mpeg-source-result')],
        init=[p for p in pairs if p['call']['target']==0x402708],
        boot_observations=bootgrep(r'\[MPEG:|[Mm]issing|[Uu]nimplemented|decoder|[Dd]ecode|\[diag:thread\]'),
        park=park,source_footer=tail is not None,
        limits=['A callback trace covers one scheduler/direct dispatch, not necessarily a complete yielding callback lifetime.','Completion event count and matched-waiter count are distinct.','Frame return/resume requires frame log and guest continuation evidence; callback v0 is never treated as EOF.'])
    save('e18a-mpeg.json',result)
    print(json.dumps(dict(objects=[dict(mpeg=o['mpeg'],requests=len(o['requests']),selections=len(o['selections']),callbacks=len(o['callbacks']),add_bs=len(o['add_bs']),input_events=len(o['input_events']),completion_events=len(o['completion_events']),matched_waiters=o['matched_waiters'],requested_bytes=o['requested_bytes'],returned_add_bs_bytes=o['returned_add_bs_bytes']) for o in objects],targets=result['target_dispatch_counts'],footer=tail is not None,pairs=len(pairs),missing_pairs=missing)))
    print('# E18 MPEG JOIN MINER TAIL COMPLETE')
if __name__=='__main__':main()
