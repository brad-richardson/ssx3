#!/usr/bin/env python3
"""Verify the inherited E13 checkpoint and run prior fixtures without a boot."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
E=Path(__file__).resolve().parent
R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert not (E/'checkpoint.json').exists()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
old=json.loads((E/'expected-generated.json').read_text())
new=json.loads((E/'before/generated.json').read_text())
assert {r['path']:r['sha256'] for r in old}=={r['path']:r['sha256'] for r in new}
oldm=json.loads((E/'expected-manifest.json').read_text())
newm=json.loads((E/'before/manifest.json').read_text())
assert oldm['executables']==newm['executables'] and oldm['inputs']==newm['inputs']
assert newm['git_head']=='83fb4d60904abb016522c477cce704c52118f95f'
csv=(R/'games/ssx3/ssx3-functions.sweep.csv').read_text()
for row in ['sub_002C5300,0x2c5300,0x2c5320,0x20','sub_002C5358,0x2c5358,0x2c53b0,0x58']:
    assert csv.splitlines().count(row)==1
result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseline_head=newm['git_head'],matching_generated_names_hashes=len(new),no_generation_repeated=True,prior_rows_present_once=True)
(E/'checkpoint-identity.json').write_text(json.dumps(result,indent=2)+'\n')
fixture=R.parent/'P1/e13-binding-tests/entry/binding-test'
assert sha(fixture)=='804cb918ee585acc8f5615b1dc50a98f1dc379214971ef6634868e90dcaeb866'
for name,argv in [('suite',['/tmp/p1-link/runtime/ps2xTest/ps2x_tests']),('prior-binding',[str(fixture),'present'])]:
    p=subprocess.run(argv,cwd=R,capture_output=True,text=True)
    (E/f'checkpoint-{name}.txt').write_text(p.stdout+p.stderr)
    result[name]=dict(argv=argv,rc=p.returncode)
    assert p.returncode==0,(name,p.returncode,p.stderr[-1000:])
suite=(E/'checkpoint-suite.txt').read_text();assert 'Total Tests: 452' in suite and 'Failed: 0' in suite
t=(E/'checkpoint-prior-binding.txt').read_text()
counts={k:sum(x.startswith(v) for x in t.splitlines()) for k,v in [('leaf_cases','LEAF port='),('consumer_cases','CONSUMER actual-binding='),('predicate_cases','PREDICATE port='),('query_cases','QUERY state=')]}
assert counts==dict(leaf_cases=24,consumer_cases=3,predicate_cases=14,query_cases=4)
result.update(suite_rc=0,suite_total=452,prior_fixture_sha256=sha(fixture),**counts)
(E/'checkpoint.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));print('# E15 CHECKPOINT TAIL COMPLETE')
