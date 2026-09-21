"""Actual-binding and run-exit fixture receipts. No title ELF invocation."""
import selectors, signal, subprocess, sys, time
from e19_common import *

def observer(env,dest):
    library=os.environ.get('E19_OBSERVER_DYLIB')
    if library:
        directory=dest/'parser-observer';directory.mkdir(exist_ok=False)
        env.update(DYLD_INSERT_LIBRARIES=library,PS2X_E19_PARSER_DIR=str(directory))
    return env

def logged(argv,env,cwd,log,wall=45,scratch=None):
    t=time.monotonic();seen=0;stop=None;peak=0
    with log.open('wb') as f:
        p=subprocess.Popen(argv,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
        sel=selectors.DefaultSelector();sel.register(p.stdout,selectors.EVENT_READ)
        while p.poll() is None or sel.get_map():
            for k,_ in sel.select(timeout=.05):
                b=os.read(k.fileobj.fileno(),65536)
                if not b:sel.unregister(k.fileobj);continue
                n=min(len(b),max(0,4*M-seen));f.write(b[:n]);seen+=len(b)
                if seen>=4*M:stop='stdout'
            if time.monotonic()-t>=wall:stop=stop or 'wall'
            if scratch is not None:
                peak=max(peak,size(scratch))
                if peak>=28*M:stop=stop or 'APFS_scratch'
            if stop and p.poll() is None:
                os.killpg(p.pid,signal.SIGTERM)
                try:p.wait(timeout=10)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=5)
    assert stop is None,dict(argv=argv,stop=stop)
    return p.returncode,log.read_text(),dict(argv=list(map(str,argv)),cwd=str(cwd),env={k:v for k,v in env.items() if k.startswith('PS2X_') or k in ('TMPDIR','DYLD_INSERT_LIBRARIES')},elapsed_s=time.monotonic()-t,stdout_bytes=seen,scratch_peak_allocated=peak)

def suite(label):
    scratch=E/('.suite-'+label);scratch.mkdir(exist_ok=False)
    env={k:v for k,v in os.environ.items() if not k.startswith('PS2X_')};env['TMPDIR']=str(scratch)+'/'
    observer(env,scratch)
    rc,txt,record=logged([str(B/'ps2xTest/ps2x_tests')],env,R,E/(label+'-suite.txt'),60,scratch)
    record.update(rc=rc,remaining_allocated=size(scratch),test=pin(B/'ps2xTest/ps2x_tests'),scratch_cap=32*M)
    assert record['remaining_allocated']<32*M
    save(label+'-suite.json',record)
    count=458
    assert rc==0 and f'Total Tests: {count}' in txt and 'Failed: 0' in txt,record
    print('SUITE',label,f'{count}/{count}')
    return rc,txt,record

def validate(label,binary,modes,expect_missing=False):
    result=dict(utc=utc(),binary=pin(binary),label=label,cases=[])
    for mode in modes:
        dest=P/'e19-fixtures'/label/mode;dest.mkdir(parents=True,exist_ok=False)
        env={k:v for k,v in os.environ.items() if not k.startswith('PS2X_')}
        if mode!='prior' and mode!='disabled':env.update(PS2X_E15_TRACE='1',PS2X_E7_DIR=str(dest))
        observer(env,dest)
        rc,txt,rec=logged([str(binary),mode],env,dest,E/f'{label}-{mode}.txt')
        tapfile=dest/'e7-events.txt';taps=tapfile.read_text() if tapfile.exists() else ''
        (E/f'{label}-{mode}-events.txt').write_text(taps)
        rec.update(mode=mode,rc=rc,tap_bytes=len(taps),tap_tail=taps.splitlines()[-3:])
        if mode=='prior':
            rec.update(leaf=txt.count('LEAF port='),consumer=txt.count('CONSUMER actual-binding='),predicate=txt.count('PREDICATE port='),query=txt.count('QUERY state='),drop='DROP actual-binding=' in txt)
            assert rc==0 and (rec['leaf'],rec['consumer'],rec['predicate'],rec['query'],rec['drop'])==(24,3,14,4,True)
        elif mode in ('input','no-input'):
            baseline=False  # E19 requires E18's delivered behavior at baseline
            assert rc==(1 if baseline else 0) and ('result=FAIL-BEFORE' if baseline else 'result=PASS') in txt
            assert 'manualCallbackCalls=0' in txt and 'waitReason=6' in txt and 'saved128=1' in txt
            if baseline:assert 'ram32MiB-unchanged=1' in txt
            else:
                assert 'callbackCalls=1' in txt and 'resumes=0' in txt
                assert ('validNoInputReturns=1 AddBsCalls=0 deliveredBytes=0' if mode=='no-input' else 'validNoInputReturns=0 AddBsCalls=1 deliveredBytes=16') in txt
            assert taps.count('# E15 CLOSURE')==taps.count('# E7 SHUTDOWN')==1
        elif expect_missing:
            assert rc==1 and 'result=FAIL-BEFORE' in txt and '# E15 CLOSURE' not in taps and '# E7 SHUTDOWN' not in taps
            assert 'beforeDestructor=1 runReturned=1 gameJoined=1 finalProducer=1' in txt
        elif mode=='fallback-error':
            assert rc==0 and 'callerErrorCaught=1 runCalled=0 realClosure=1' in txt
            assert taps.count('# E15 CLOSURE')==taps.count('# E7 SHUTDOWN')==1
        else:
            assert rc==0 and 'RUN-EXIT FIXTURE TAIL COMPLETE result=PASS' in txt
            assert 'ram32MiB-unchanged=1 fullContext-unchanged=1 schedule-unchanged=1' in txt
            if mode in ('disabled','unopened'):assert not taps
            else:assert taps.count('# E15 CLOSURE')==taps.count('# E7 SHUTDOWN')==1
        if '# E7 SHUTDOWN' in taps:
            from e19_closed_events import tap
            tap(tapfile)  # Same strict source counters/bytes parser used for the probe.
            def fields(line):return {k:int(v,0) for k,v in (x.split('=',1) for x in line.split() if '=' in x)}
            closure=fields(taps.splitlines()[-2]);shutdown=fields(taps.splitlines()[-1])
            rows=[x for x in taps.splitlines() if x.startswith('seq=')]
            assert taps.endswith('\n') and closure['calls']==closure['returned']+closure['unwound'] and closure['pending']==closure['registrationTruncated']==0
            assert shutdown['events']==len(rows) and shutdown['bootTruncated']==shutdown['boundaryTruncated']==shutdown['packetTruncated']==0
            assert [int(x.split()[0].split('=')[1]) for x in rows]==list(range(1,len(rows)+1))
            assert closure['calls']==sum('kind=mpeg-call ' in x for x in rows)
            if mode in ('quiescent','idempotent'):assert shutdown['tick']<603 and 'kind=e16-final-producer ' in rows[-1]
            if mode=='window-complete':assert shutdown['windowComplete']==1
            rec.update(closure=closure,shutdown=shutdown,source_count_match=True)
        result['cases'].append(rec)
        save(label+'-validation.json',result)
        print(json.dumps(rec),flush=True)
    print('# E19 VALIDATION TAIL COMPLETE')
    return result

if __name__=='__main__':
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    label=sys.argv[1]
    if sys.argv[2]=='suite':suite(label)
    else:
        binary=Path(sys.argv[2]);kind=sys.argv[3]
        modes=['prior','no-input','input'] if kind=='prior' else (['quiescent'] if kind=='before' else ['quiescent','idempotent','window-complete','disabled','unopened','fallback-error'])
        validate(label,binary,modes,kind=='before')
