"""Pin all behavior-regression gates before spending the single E21 title allowance."""
import subprocess
from e21_common import *
chk=json.loads((E/'checkpoint-complete.json').read_text())
assert chk['suite']==458 and chk['closure_cases']==6 and chk['e15_rc']==[0,0] and chk['extra_cases']==8 and chk['boot']==0
txt=(E/'checkpoint-suite.txt').read_text();assert 'Total Tests: 458' in txt and 'Failed: 0' in txt
assert 'MPEG non-stream R1' in txt and 'MPEG non-stream R6' in txt
v=json.loads((E/'checkpoint-bindings-validation.json').read_text());prior=v['cases'][0]
assert (prior['leaf'],prior['consumer'],prior['predicate'],prior['query'],prior['drop'])==(24,3,14,4,True)
obs=json.loads((E/'observer-regression.json').read_text())
assert obs['suite']==458 and obs['closure_cases']==6 and obs['boot']==0
assert all(c['footer']['pending']==0 for c in obs['closures'])
iso=json.loads((E/'isolation-proof.json').read_text())
assert iso['feed']['identical'] and iso['exit']['plain_rc']==iso['exit']['loaded_rc']==3
assert all(b['valid']==1 for b in iso['addrs']['observer_bindings'])
q1=json.loads((E/'q1-complete.json').read_text());assert q1['cases']==9 and q1['EOF_flushes']==0
assert (E/'Q2-AUDIT.md').is_file()
def git(*args):return subprocess.check_output(['git','-C',str(R),*args],text=True)
head=git('rev-parse','HEAD').strip();assert head==BASE_SHA and git('diff','--cached','--name-only')==''
assert git('status','--short')=='?? ps2_log.txt\n'
ckpt=json.loads((E/'checkpoint.json').read_text())
assert sha(B0/'ps2xRuntime/ps2EntryRunner')==ckpt['runner']['sha256']
assert sha(B0/'ps2xTest/ps2x_tests')==ckpt['suite']['sha256']
save('entry-preflight.json',dict(utc=utc(),suite_rc=0,binding_rc=0,leaf_cases=24,consumer_cases=3,
    predicate_cases=14,query_cases=4,leaf_present=True,mpeg_delivery_cases=2,run_exit_cases=6,
    new_regression_cases=6,isolation_identical=True,loaded_regression_green=True,q1_cases=9,q2_audit=True))
save('e21a-build.json',dict(utc=utc(),fork_head=head,fork_status='?? ps2_log.txt\n',test_count=458,
    bin_size=ckpt['runner']['bytes'],bin_sha=ckpt['runner']['sha256'],
    test_size=ckpt['suite']['bytes'],test_sha=ckpt['suite']['sha256']))
print('All E21 regression gates pinned. Fresh T13 pre-claims and atomic lease remain mandatory.')
print('# E21 PREPARE PROBE TAIL COMPLETE')
