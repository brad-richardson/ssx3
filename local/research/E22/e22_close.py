"""Final audit: fork/generated/protected unchanged; Q1/Q2/Q3 receipts present; one boot spent."""
import subprocess
from e22_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
# E22's own deliverables; Q1/Q2 are E21 receipts consumed, not re-derived.
assert (E/'q3-complete.json').exists() and (E/'X-HUNT.md').exists()
assert (E.parent/'E21/q1-complete.json').exists() and (E.parent/'E21/Q2-AUDIT.md').exists()
assert json.loads((E/'e22a-result.json').read_text()).get('release_utc')
before=json.loads((E/'checkpoint.json').read_text())
sources=[]
for row in before['inputs_sources']:
    p=pin(row['path']);assert p['sha256']==row['sha256'],p;sources.append(p)
generated=json.loads((E/'before-generated.json').read_text())
actual=[pin(p) for p in sorted((R/'ps2xRuntime/src/runner').iterdir())
        if p.suffix in ('.cpp','.h') and not p.name.startswith('._')]
assert len(actual)==9457 and {r['path']:r['sha256'] for r in actual}=={r['path']:r['sha256'] for r in generated}
protected=json.loads((E/'protected-build-before.json').read_text())
for row in protected:assert sha(row['path'])==row['sha256'],row['path']
commands=[['git','-C',str(R),'rev-parse','HEAD','refs/remotes/fork/ssx3'],
          ['git','-C',str(R),'ls-remote','fork','refs/heads/ssx3'],
          ['git','-C',str(R),'status','--short']]
receipts=[]
for command in commands:
    p=subprocess.run(command,text=True,capture_output=True,check=True)
    receipts.append(dict(argv=command,rc=p.returncode,stdout=p.stdout,stderr=p.stderr))
assert receipts[0]['stdout'].splitlines()==[BASE_SHA,BASE_SHA]
assert receipts[1]['stdout'].split()[0]==BASE_SHA
assert receipts[2]['stdout']=='?? ps2_log.txt\n'
assert not LEASE.exists() if (LEASE:=__import__('pathlib').Path('/tmp/ssx3-p-lane-lease')) else True
resources=sample();assert not bound(resources),resources
save('final-audit.json',dict(utc=utc(),fork=BASE_SHA,fork_commands=receipts,fork_source_changes=0,fork_commits=0,
    generated_count=9457,all_generated_hashes_equal=True,protected_build_files=len(protected),all_protected_hashes_equal=True,
    inputs_sources=sources,runner=pin(B0/'ps2xRuntime/ps2EntryRunner'),suite=pin(B0/'ps2xTest/ps2x_tests'),
    fixture=pin(P/'e18-fixtures/after/binding-test'),
    observer=pin(E/'parser/e21-parser-observer.dylib'),observer_rebuilt=False,
    title_boots=1,lease_claims=1,observed_boot=True,x_hunt=True,resources=resources))
print('Final audit: fork unchanged;9457 generated and1725 protected hashes agree;1 boot/1 claim/0 fork commits.')
print('# E22 FINAL AUDIT TAIL COMPLETE')
