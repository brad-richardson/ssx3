#!/usr/bin/env python3
"""Run actual bindings without an ELF boot, retaining expected delivery failures."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
from e15_suite import run as run_suite
E=Path(__file__).resolve().parent;W=Path('/Volumes/Extreme SSD/ps2recomp-spike');R=W/'PS2Recomp'
BIN=W/'P1/e15-binding-tests/entry/binding-test';TEST=Path('/tmp/p1-link/runtime/ps2xTest/ps2x_tests')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1';label=sys.argv[1]
    env={k:v for k,v in os.environ.items() if not k.startswith('PS2X_')}
    result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),fixture_sha=sha(BIN),fixture_bytes=BIN.stat().st_size,cases=[])
    for mode in ['no-input','input']:
        dest=W/'P1/e15-binding-tests'/label/mode;dest.mkdir(parents=True,exist_ok=False)
        caseenv=dict(env,PS2X_E15_TRACE='1',PS2X_E7_DIR=str(dest))
        p=subprocess.run([str(BIN),mode],cwd=R,env=caseenv,capture_output=True,text=True,timeout=30)
        text=p.stdout+p.stderr;(E/f'{label}-{mode}.txt').write_text(text)
        taps=(dest/'e7-events.txt').read_text();(E/f'{label}-{mode}-events.txt').write_text(taps)
        row=dict(mode=mode,rc=p.returncode,actual_wrapper_fail_before=p.returncode==1 and 'result=FAIL-BEFORE' in text,
                 no_manual_callback='manualCallbackCalls=0' in text,request_wait='waitReason=6' in text,closure=taps.splitlines()[-2:])
        result['cases'].append(row)
        assert row['actual_wrapper_fail_before'] and row['no_manual_callback'] and row['request_wait'],row
        assert '# E15 CLOSURE' in taps and '# E7 SHUTDOWN' in taps and taps.endswith('\n')
        assert 'pending=0' in taps and 'bootTruncated=0 boundaryTruncated=0 packetTruncated=0' in taps
        print(json.dumps(row),flush=True)
    p=subprocess.run([str(BIN),'prior'],cwd=R,env=env,capture_output=True,text=True,timeout=60)
    text=p.stdout+p.stderr;(E/f'{label}-prior-binding.txt').write_text(text)
    result.update(binding_rc=p.returncode,query_cases=text.count('QUERY state='),predicate_cases=text.count('PREDICATE port='),
                  leaf_cases=text.count('LEAF port='),consumer_cases=text.count('CONSUMER actual-binding='),leaf_present='LEAF hasFunction=1 expected=1' in text,mpeg_fail_before_cases=2)
    assert p.returncode==0 and result['query_cases']==4 and result['predicate_cases']==14 and result['leaf_cases']==24 and result['consumer_cases']==3,result
    suite_rc,text,suite_environment=run_suite(label)
    result.update(suite_rc=suite_rc,test_sha=sha(TEST),suite_environment=suite_environment,suite_tail=[x for x in text.splitlines() if 'Total Tests:' in x or 'Passed:' in x or 'Failed:' in x])
    assert suite_rc==0 and 'Total Tests: 452' in text and 'Failed: 0' in text,result
    (E/f'{label}-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));print('# E15 ACTUAL WRAPPER VALIDATION TAIL COMPLETE')
if __name__=='__main__':main()
