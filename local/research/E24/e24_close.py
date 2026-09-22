"""E24 final audit: fork/generated/sources unchanged; the red gate recorded;
zero boots, zero lease claims, zero mutations."""
import subprocess
from pathlib import Path
from e24_common import *

assert os.environ.get('COPYFILE_DISABLE')=='1'
LEASE=Path('/tmp/ssx3-p-lane-lease')

# E24's own deliverables must all exist.
for name in ('CONTRACT.md','BOOT-DESIGN.md','env-audit.json','checkpoint.json',
             'dims.json','picture-completeness.json','payload-tail.json',
             'sema-mine.json','signaller-closure.json','watch-set.json',
             'probe-authorization.json','capture-gate-proof.json','fix-gate.json',
             'rename-proof-hexsafe.json','tooling-changes.json','capture-changes.json',
             'observed/parser-input.bin','cadence.json','observer-regression.json'):
    assert (E/name).exists(), name

# No boot may have been spent.
assert not (E/'boot-attempt.json').exists(), 'a boot was attempted'
assert not list(E.glob('e24?-result.json')), 'a boot produced a result'
assert not LEASE.exists(), 'lease present at close'
auth=json.loads((E/'probe-authorization.json').read_text())
assert auth['authorized'] is False and auth['boot_spent'] is False

# Inputs unchanged end to end.
before=json.loads((E/'checkpoint.json').read_text())
sources=[]
for row in before['inputs_sources']:
    p=pin(row['path']);assert p['sha256']==row['sha256'],p;sources.append(p)
generated=json.loads((E/'before-generated.json').read_text())
actual=[pin(p) for p in sorted((R/'ps2xRuntime/src/runner').iterdir())
        if p.suffix in ('.cpp','.h') and not p.name.startswith('._')]
assert len(actual)==9457 and {r['path']:r['sha256'] for r in actual}=={r['path']:r['sha256'] for r in generated}

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

# The surviving binaries this lane DID use, re-pinned at close.
used=dict(fixture=pin(P/'e18-fixtures/after/binding-test'),
          cadence_fixture=pin(P/'e23-fixtures/complete/binding-test'),
          observer=pin(E/'parser/e21-parser-observer.dylib'))
env=json.loads((E/'env-audit.json').read_text())
for key,expect in (('fixture',env['key_binaries']['fixture']['expected_sha']),
                   ('cadence_fixture',env['key_binaries']['cadence_fixture']['expected_sha']),
                   ('observer',env['instrument']['expected_sha'])):
    assert used[key]['sha256']==expect,key

resources=sample();assert not bound(resources),resources
save('final-audit.json',dict(utc=utc(),fork=BASE_SHA,fork_commands=receipts,
    fork_source_changes=0,fork_commits=0,pushes=0,
    generated_count=9457,all_generated_hashes_equal=True,inputs_sources=sources,
    protected_build_files_present=0,protected_build_files_expected=1725,
    protected_build_status='BLOCKED (host restart wiped /tmp; no snapshot, no copy)',
    binaries_used=used,observer_rebuilt=False,
    title_boots=0,lease_claims=0,boot_authorized=False,
    red_gates=before['red_gates'],
    build_inputs_intact=True,
    build_inputs_note='fork at BASE_SHA, 9,457 generated sources and all E18 '
                      'behavior sources are hash-equal, so the lost trees are '
                      'DERIVED output and are rebuildable from intact inputs; a '
                      'rebuilt runner will NOT match the pinned SHA, which is the '
                      'orchestrator\'s call, not this lane\'s',
    errata=['E21-E1','E23-E1','E23-E2','E24-E1'],resources=resources))
print('Final audit: fork unchanged; 9,457 generated + all source hashes equal;')
print('0 boots / 0 lease claims / 0 fork commits; checkpoint RED recorded.')
print('# E24 FINAL AUDIT TAIL COMPLETE')
