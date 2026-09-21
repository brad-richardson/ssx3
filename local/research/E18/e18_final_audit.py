import subprocess,zlib
from e18_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
push=json.loads((E/'fork-push.json').read_text());head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip();assert head==push['head']
assert subprocess.check_output(['git','-C',str(R),'diff','--name-only'],text=True)==''
assert subprocess.check_output(['git','-C',str(R),'diff','--cached','--name-only'],text=True)==''
audit=json.loads((E/'precommit-scope.json').read_text())
for r in audit['source']:assert sha(r['path'])==r['sha256']
changed={r['path'] for r in audit['source']};unchanged=[]
for r in json.loads((E/'checkpoint.json').read_text())['inputs_sources']:
    if r['path'] not in changed:assert sha(r['path'])==r['sha256'];unchanged.append(r)
generated=json.loads((E/'before-generated.json').read_text());root=R/'ps2xRuntime/src/runner'
assert {r['path'] for r in generated}=={str(p) for p in root.iterdir() if p.suffix in ('.cpp','.h') and not p.name.startswith('._')}
for r in generated:assert sha(r['path'])==r['sha256']
protected=json.loads((E/'protected-build-before.json').read_text())
for r in protected:assert sha(r['path'])==r['sha256']
build=json.loads((E/'built-binaries.json').read_text())
for r in (build['runner'],build['suite']):assert sha(r['path'])==r['sha256']
fixture=json.loads((E/'after-fixture-binary.json').read_text());assert sha(fixture['path'])==fixture['sha256']
assert not OUT.exists() and not Path('/tmp/ssx3-p-lane-lease').exists()
record=dict(utc=utc(),fork=head,fork_push_agreement=push['agreement'],fork_status=subprocess.check_output(['git','-C',str(R),'status','--short'],text=True),generated_count=len(generated),all_generated_hashes_equal=True,protected_build_count=len(protected),protected_build_hashes_equal=True,codegen_invocations=0,inputs_sources=unchanged,behavior_sources=audit['source'],runner=build['runner'],suite=build['suite'],fixture=fixture,allocation=sample(),title_boots=1,lease_absent=True)
assert not bound(record['allocation']);save('final-audit.json',record)
print(json.dumps({k:record[k] for k in ['utc','fork','generated_count','protected_build_count','fork_status','title_boots','lease_absent']}))
print('# E18 FINAL SOURCE/BUILD AUDIT TAIL COMPLETE')
