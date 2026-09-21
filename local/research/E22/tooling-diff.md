# E22 tooling provenance — itemized diffs for the four intentionally changed scripts

Method: E21/E22 lane tokens unified to EXX/exx, then diffed against the E21 original.
The nine pure-rename files (rename-proof.json) have byte-empty normalized diffs.

## e22_prepare_probe.py
```diff
13c13,16
< iso=json.loads((E/'isolation-proof.json').read_text())
---
> # Inherited EXX receipts: isolation forwarding, Q1 threshold, Q2 static audit.
> # The instrument is the same binary, re-hashed; nothing here is re-derived.
> PRIOR=E.parent/'EXX'
> iso=json.loads((PRIOR/'isolation-proof.json').read_text())
16,17c19,23
< q1=json.loads((E/'q1-complete.json').read_text());assert q1['cases']==9 and q1['EOF_flushes']==0
< assert (E/'Q2-AUDIT.md').is_file()
---
> q1=json.loads((PRIOR/'q1-complete.json').read_text());assert q1['cases']==9 and q1['EOF_flushes']==0
> assert (PRIOR/'Q2-AUDIT.md').is_file()
> proven=json.loads((PRIOR/'parser-build.json').read_text())['observer']
> assert sha(E/'parser/exx-parser-observer.dylib')==proven['sha256'],'reused instrument re-sha missed'
> assert obs['observer']['sha256']==proven['sha256']
26c32,33
<     new_regression_cases=6,isolation_identical=True,loaded_regression_green=True,q1_cases=9,q2_audit=True))
---
>     new_regression_cases=6,isolation_identical=True,loaded_regression_green=True,q1_cases=9,q2_audit=True,
>     instrument_reused_sha=proven['sha256'],instrument_rebuilt=False,inherited_from='EXX'))
```

## e22_capture.py
```diff
84c84
<                                   (EVIDENCE/'parser/exx-parser-observer.dylib',None,json.loads((EVIDENCE/'parser-build.json').read_text())['observer']['sha256'])]:
---
>                                   (EVIDENCE/'parser/exx-parser-observer.dylib',None,json.loads((EVIDENCE.parent/'EXX/parser-build.json').read_text())['observer']['sha256'])]:
176c176,178
<     config=dict(label=label,argv=['stdbuf','-o0','-e0',str(BIN),str(ELF)],cwd=str(RUN),
---
>     boot_argv=[str(BIN),str(ELF)]
>     assert not any('stdbuf' in x for x in boot_argv), 'EXX forbids stdbuf in the boot argv'
>     config=dict(label=label,argv=boot_argv,cwd=str(RUN),
178a181,182
>                 stdbuf_free=True,dyld_insert=env.get('DYLD_INSERT_LIBRARIES'),
>                 argv0_is_runner=boot_argv[0]==str(BIN),
```

## e22_mine.py
```diff
47a48,61
>         rows=pr['rows']
>         # EXX's target measurement: per-call parser timing INSIDE the title
>         # window. Every observer event carries ns= since observer init and tid=.
>         enters={r['call']:r for r in rows if r['kind']=='parse-enter'}
>         timeline=[]
>         for r in rows:
>             if r['kind']!='parse-return':continue
>             e=enters[r['call']]
>             timeline.append(dict(call=r['call'],tid=e['tid'],enter_ns=e['ns'],return_ns=r['ns'],
>                 duration_ns=r['ns']-e['ns'],offered=e['size'],used=r['used'],packetSize=r['packetSize'],
>                 payloadOffset=e['payloadOffset'],first64=str(e['first64'])[:32]))
>         sends=[dict(kind=r['kind'],ns=r['ns'],tid=r['tid'],**{k:v for k,v in r.items() if k in ('rc','eof','size')})
>                for r in rows if r['kind'].startswith(('send-','receive-'))]
>         parse_ns=[x['enter_ns'] for x in timeline]
49,50c63,70
<             marks=[{k:m[k] for k in ('label','bytes','parseCalls','consumed','packets','frames')} for m in pr['rows'] if m['kind']=='mark'],
<             first_packet=next((dict(call=r['call'],used=r['used'],packetSize=r['packetSize']) for r in pr['rows'] if r['kind']=='parse-return' and r['packetSize']>0),None))
---
>             marks=[{k:m[k] for k in ('label','bytes','parseCalls','consumed','packets','frames')} for m in rows if m['kind']=='mark'],
>             first_packet=next((dict(call=r['call'],used=r['used'],packetSize=r['packetSize']) for r in rows if r['kind']=='parse-return' and r['packetSize']>0),None),
>             timeline=timeline,send_receive=sends,
>             threads=sorted({x['tid'] for x in timeline}),
>             first_parse_ns=min(parse_ns) if parse_ns else None,
>             last_parse_ns=max(parse_ns) if parse_ns else None,
>             parse_span_ns=(max(parse_ns)-min(parse_ns)) if parse_ns else None,
>             bindings=[{k:r[k] for k in ('api','valid','nextIsReplacement') if k in r} for r in rows if r['kind']=='binding'])
65a86,88
>     summary={k:v for k,v in parser.items() if k not in ('timeline','send_receive')}
>     summary['timeline_calls']=len(parser.get('timeline',[]))
>     save('exxa-observed.json',dict(utc=end['release_utc'],label=LABEL,parser=parser))
67c90
<         e7_events=len(events),e7_footer=tail is not None,parser=parser,
---
>         e7_events=len(events),e7_footer=tail is not None,parser=summary,
69c92
<     print(json.dumps(dict(objects=verdict,targets=result['target_dispatch_counts'],parser=parser,footer=tail is not None),indent=2))
---
>     print(json.dumps(dict(objects=verdict,targets=result['target_dispatch_counts'],parser=summary,footer=tail is not None),indent=2))
```

## e22_close.py
```diff
5c5,7
< assert (E/'q1-complete.json').exists() and (E/'Q2-AUDIT.md').exists() and (E/'q3-complete.json').exists()
---
> # EXX's own deliverables; Q1/Q2 are EXX receipts consumed, not re-derived.
> assert (E/'q3-complete.json').exists() and (E/'X-HUNT.md').exists()
> assert (E.parent/'EXX/q1-complete.json').exists() and (E.parent/'EXX/Q2-AUDIT.md').exists()
32,33c34,36
<     fixture=pin(P/'e18-fixtures/after/binding-test'),threshold_fixture=pin(P/'exx-fixtures/threshold/binding-test'),
<     title_boots=1,lease_claims=1,q1_complete=True,q2_opened=True,q3_opened=True,resources=resources))
---
>     fixture=pin(P/'e18-fixtures/after/binding-test'),
>     observer=pin(E/'parser/exx-parser-observer.dylib'),observer_rebuilt=False,
>     title_boots=1,lease_claims=1,observed_boot=True,x_hunt=True,resources=resources))
```

## e22_observer_regression.py
```diff
6c6,13
< assert (E/'isolation-proof.json').exists()
---
> # EXX inherits EXX's isolation proof by binary identity: the instrument is the
> # SAME file, re-hashed here, not a rebuild. Re-proving forwarding would require
> # rebuilding the proven dylib, which the brief forbids.
> inherited=json.loads((E.parent/'EXX/isolation-proof.json').read_text())
> assert inherited['feed']['identical'] and inherited['exit']['plain_rc']==inherited['exit']['loaded_rc']==3
> assert all(b['valid']==1 for b in inherited['addrs']['observer_bindings'])
> proven=json.loads((E.parent/'EXX/parser-build.json').read_text())['observer']
> assert sha(E/'parser/exx-parser-observer.dylib')==proven['sha256'],'reused instrument re-sha missed'
```

# E22 TOOLING DIFF TAIL COMPLETE pure=9 changed=5
