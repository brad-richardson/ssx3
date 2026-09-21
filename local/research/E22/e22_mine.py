"""Q3 demand-watch join: E7 MPEG events + parser-boundary receipt + second-request verdict."""
import hashlib,json,re
from collections import Counter
from pathlib import Path
from e22_io import read_capture
from e22_closed_events import tap,fields
from e22_parser_receipt import receipt
E=Path(__file__).resolve().parent
RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run');LABEL='e22a'
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
    save('e22a-observation-closure.json',dict(raw_sha256=hashlib.sha256(data).hexdigest(),raw_bytes=len(data),
        events=len(events),kinds=dict(Counter(r['kind'] for r in events)),closure=closure,shutdown=shutdown,
        source_footer=tail is not None,missing_pair_ids=missing))
    targets=Counter(c['target'] for c in calls)
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
        objects.append(dict(mpeg=hex(obj),creates=len(creates),registrations=len(regs),requests=len(reqs),
            selections=len(selected),callbacks=len(callbacks),
            callback_targets=sorted({p['call']['target'] for p in callbacks}),
            callback_returns=sum(1 for p in callbacks if p['exit'] and p['exit']['kind']=='mpeg-return'),
            add_bs=len(inputcalls),input_events=len(inputevents),completion_events=len(completion),
            matched_waiters=sum(r.get('matched',0) for r in completion),
            waits=[r for r in events if r['kind']=='mpeg-wait' and r['token']==obj],
            requested_bytes=sum(r['requested'] for r in inputevents),
            returned_add_bs_bytes=sum(p['exit']['v0'] for p in inputcalls if p['exit'] and p['exit']['kind']=='mpeg-return' and p['exit']['v0']<0x80000000),
            add_bs_v0=[p['exit']['v0'] if p['exit'] else None for p in inputcalls]))
    try:
        pr=receipt(RUN/f'{LABEL}-parser')
        rows=pr['rows']
        # E22's target measurement: per-call parser timing INSIDE the title
        # window. Every observer event carries ns= since observer init and tid=.
        enters={r['call']:r for r in rows if r['kind']=='parse-enter'}
        timeline=[]
        for r in rows:
            if r['kind']!='parse-return':continue
            e=enters[r['call']]
            timeline.append(dict(call=r['call'],tid=e['tid'],enter_ns=e['ns'],return_ns=r['ns'],
                duration_ns=r['ns']-e['ns'],offered=e['size'],used=r['used'],packetSize=r['packetSize'],
                payloadOffset=e['payloadOffset'],first64=str(e['first64'])[:32]))
        sends=[dict(kind=r['kind'],ns=r['ns'],tid=r['tid'],**{k:v for k,v in r.items() if k in ('rc','eof','size')})
               for r in rows if r['kind'].startswith(('send-','receive-'))]
        parse_ns=[x['enter_ns'] for x in timeline]
        parser=dict(closed=True,footer=pr['footer'],
            marks=[{k:m[k] for k in ('label','bytes','parseCalls','consumed','packets','frames')} for m in rows if m['kind']=='mark'],
            first_packet=next((dict(call=r['call'],used=r['used'],packetSize=r['packetSize']) for r in rows if r['kind']=='parse-return' and r['packetSize']>0),None),
            timeline=timeline,send_receive=sends,
            threads=sorted({x['tid'] for x in timeline}),
            first_parse_ns=min(parse_ns) if parse_ns else None,
            last_parse_ns=max(parse_ns) if parse_ns else None,
            parse_span_ns=(max(parse_ns)-min(parse_ns)) if parse_ns else None,
            bindings=[{k:r[k] for k in ('api','valid','nextIsReplacement') if k in r} for r in rows if r['kind']=='binding'])
    except (FileNotFoundError,AssertionError) as e:
        parser=dict(closed=False,error=f'{type(e).__name__}: {e}')
    raw=read_capture(RUN/f'boot-{LABEL}-1.log').decode(errors='replace');bootlines=raw.splitlines()
    def bootgrep(pattern):return [dict(line=n,text=l) for n,l in enumerate(bootlines,1) if re.search(pattern,l)]
    result=dict(objects=objects,target_dispatch_counts={hex(k):v for k,v in sorted(targets.items())},
        parser=parser,boot_observations=bootgrep(r'\[MPEG:|[Mm]issing|[Uu]nimplemented|decoder|[Dd]ecode|\[diag:thread\]'),
        boot_bound=end['bound'],boot_rc=end.get('rc'),source_footer=tail is not None)
    # Second-request verdict inputs: per-object callback/AddBs counts across the whole boot.
    verdict=[]
    for o in objects:
        verdict.append(dict(mpeg=o['mpeg'],registrations=o['registrations'],callbacks=o['callbacks'],
            add_bs_calls=o['add_bs'],requested_bytes=o['requested_bytes'],returned_add_bs_bytes=o['returned_add_bs_bytes'],
            completion_events=o['completion_events'],waits=len(o['waits'])))
    result['demand_verdict']=verdict
    save('e22a-mpeg.json',result)
    summary={k:v for k,v in parser.items() if k not in ('timeline','send_receive')}
    summary['timeline_calls']=len(parser.get('timeline',[]))
    save('e22a-observed.json',dict(utc=end['release_utc'],label=LABEL,parser=parser))
    save('q3-complete.json',dict(utc=end['release_utc'],label=LABEL,bound=end['bound'],rc=end.get('rc'),
        e7_events=len(events),e7_footer=tail is not None,parser=summary,
        demand=verdict,targets=result['target_dispatch_counts'],boot=1))
    print(json.dumps(dict(objects=verdict,targets=result['target_dispatch_counts'],parser=summary,footer=tail is not None),indent=2))
    print('# E22 DEMAND-WATCH MINER TAIL COMPLETE')
if __name__=='__main__':main()
