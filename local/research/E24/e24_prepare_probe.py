"""Pin all behavior-regression gates before spending the single E24 title allowance."""
import subprocess
from e24_common import *
# E24 CHANGE: this tool is the gate that AUTHORIZES the boot. The brief's
# mission 1 says any red checkpoint gate -> table and stop with no boot, so the
# red check comes FIRST and refuses here rather than letting a later assert
# fail somewhere less legible.
ckpt=json.loads((E/'checkpoint.json').read_text())
if ckpt['red']:
    save('probe-authorization.json',dict(utc=utc(),authorized=False,
        reason='checkpoint RED: '+', '.join(ckpt['red_gates']),
        red_gates=ckpt['red_gates'],
        protected_build_files_present=ckpt['protected_build_files'],
        protected_build_files_expected=ckpt['protected_build_files_expected'],
        runner=ckpt['runner'],suite=ckpt['suite'],
        boot_spent=False,lease_claimed=False))
    print('BOOT NOT AUTHORIZED -- checkpoint RED:',', '.join(ckpt['red_gates']))
    print('# E24 PREPARE PROBE TAIL COMPLETE')
    raise SystemExit(0)
chk=json.loads((E/'checkpoint-complete.json').read_text())
assert chk['suite']==458 and chk['closure_cases']==6 and chk['e15_rc']==[0,0] and chk['extra_cases']==8 and chk['boot']==0
txt=(E/'checkpoint-suite.txt').read_text();assert 'Total Tests: 458' in txt and 'Failed: 0' in txt
assert 'MPEG non-stream R1' in txt and 'MPEG non-stream R6' in txt
v=json.loads((E/'checkpoint-bindings-validation.json').read_text());prior=v['cases'][0]
assert (prior['leaf'],prior['consumer'],prior['predicate'],prior['query'],prior['drop'])==(24,3,14,4,True)
obs=json.loads((E/'observer-regression.json').read_text())
assert obs['suite']==458 and obs['closure_cases']==6 and obs['boot']==0
assert all(c['footer']['pending']==0 for c in obs['closures'])
# Inherited E21 receipts: isolation forwarding, Q1 threshold, Q2 static audit.
# The instrument is the same binary, re-hashed; nothing here is re-derived.
PRIOR=E.parent/'E21'
iso=json.loads((PRIOR/'isolation-proof.json').read_text())
assert iso['feed']['identical'] and iso['exit']['plain_rc']==iso['exit']['loaded_rc']==3
assert all(b['valid']==1 for b in iso['addrs']['observer_bindings'])
q1=json.loads((PRIOR/'q1-complete.json').read_text());assert q1['cases']==9 and q1['EOF_flushes']==0
assert (PRIOR/'Q2-AUDIT.md').is_file()
proven=json.loads((PRIOR/'parser-build.json').read_text())['observer']
assert sha(E/'parser/e21-parser-observer.dylib')==proven['sha256'],'reused instrument re-sha missed'
assert obs['observer']['sha256']==proven['sha256']
# E24 gate: the boot may not be spent before the complete-feed reference lands.
cad=json.loads((E/'cadence.json').read_text())
assert len(cad['rows'])==4 and {r['feedBytes'] for r in cad['rows']}=={60,120,180,240}
assert all(r['rc']==0 and r['cadence']['producerFirings']==1 and r['cadence']['addBs']==1 for r in cad['rows'])
assert {r['outcome'] for r in cad['rows']}=={'SERVED','STALLED'},'reference needs both branches'
assert all(r['parser']['footer']['pending']==0 and r['parser']['footer']['errors']==0 for r in cad['rows'])
for lab in ('newbin-bindings','newbin-closure'):
    ctl=json.loads((E/f'{lab}-validation.json').read_text())
    assert all(c['rc']==0 for c in ctl['cases']),lab
def git(*args):return subprocess.check_output(['git','-C',str(R),*args],text=True)
head=git('rev-parse','HEAD').strip();assert head==BASE_SHA and git('diff','--cached','--name-only')==''
assert git('status','--short')=='?? ps2_log.txt\n'
ckpt=json.loads((E/'checkpoint.json').read_text())
assert sha(B0/'ps2xRuntime/ps2EntryRunner')==ckpt['runner']['sha256']
assert sha(B0/'ps2xTest/ps2x_tests')==ckpt['suite']['sha256']
save('entry-preflight.json',dict(utc=utc(),cadence_cases=len(cad['rows']),cadence_branches=2,suite_rc=0,binding_rc=0,leaf_cases=24,consumer_cases=3,
    predicate_cases=14,query_cases=4,leaf_present=True,mpeg_delivery_cases=2,run_exit_cases=6,
    new_regression_cases=6,isolation_identical=True,loaded_regression_green=True,q1_cases=9,q2_audit=True,
    instrument_reused_sha=proven['sha256'],instrument_rebuilt=False,inherited_from='E21'))
save('e24a-build.json',dict(utc=utc(),fork_head=head,fork_status='?? ps2_log.txt\n',test_count=458,
    bin_size=ckpt['runner']['bytes'],bin_sha=ckpt['runner']['sha256'],
    test_size=ckpt['suite']['bytes'],test_sha=ckpt['suite']['sha256']))
print('All E24 regression gates pinned. Fresh T13 pre-claims and atomic lease remain mandatory.')
print('# E24 PREPARE PROBE TAIL COMPLETE')
