#!/usr/bin/env python3
"""Run the actual post-build fixture and suite; this never boots an ELF."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
E=Path(__file__).resolve().parent
R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
B=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/e13-binding-tests/entry/binding-test')
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert json.loads((E/'entry-build-bounded-result.json').read_text())['rc']==0
assert json.loads((E/'entry-link-bounded-result.json').read_text())['rc']==0
assert not (E/'entry-preflight.json').exists()
results={}
for name,argv in [('binding',[str(B),'present']),('suite',['/tmp/p1-link/runtime/ps2xTest/ps2x_tests'])]:
    p=subprocess.run(argv,cwd=R,capture_output=True,text=True)
    output=p.stdout+p.stderr
    (E/f'entry-{name}.txt').write_text(output)
    results[name]=dict(argv=argv,cwd=str(R),rc=p.returncode,tail=output.splitlines()[-7:])
    (E/'entry-validation-results.json').write_text(json.dumps(results,indent=2)+'\n')
    assert p.returncode==0,(name,p.returncode,output[-3000:])
text=(E/'entry-binding.txt').read_text()
counts={key:sum(s.startswith(prefix) for s in text.splitlines()) for key,prefix in
        [('query_cases','QUERY state='),('predicate_cases','PREDICATE port='),('leaf_cases','LEAF port='),('consumer_cases','CONSUMER actual-binding=')]}
assert counts==dict(query_cases=4,predicate_cases=14,leaf_cases=24,consumer_cases=3),counts
assert 'LEAF hasFunction=1 expected=1' in text
assert 'sub_002C5358_0x2c5358' in text
assert 'input=0x2c5358 flags=0x1b bit3=8' in text
assert text.count('input=0x1 flags=0x13 bit3=0')==2
assert text.count('DROP actual-binding=')==1
assert 'E13 ACTUAL BINDING TEST COMPLETE success=1 boot=0' in text
suite=(E/'entry-suite.txt').read_text()
assert 'Total Tests: 452' in suite and 'Failed: 0' in suite
with B.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),suite_rc=0,binding_rc=0,
            **counts,leaf_present=True,drop_preserved=True,fixture_sha256=digest,
            preservation='supplied RA, unchanged SP, full callee-save128, whole32MiB RAM, zero GetInfo/Sync',
            consumer='actual registered interior 0x241c48; next virtual call is a test stop hook')
(E/'entry-preflight.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
print('# E13 ENTRY REGRESSION TAIL COMPLETE')
