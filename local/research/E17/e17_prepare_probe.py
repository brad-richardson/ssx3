"""Require all new-map regression gates before the one E17 title allowance."""
import subprocess
from e17_common import *
closed=json.loads((E/'current-closure-validation.json').read_text());assert len(closed['cases'])==6 and all(c['rc']==0 for c in closed['cases'])
binding=json.loads((E/'current-binding-validation.json').read_text());prior=binding['cases'][0]
assert prior['rc']==0 and [c['rc'] for c in binding['cases'][1:]]==[1,1]
assert (prior['leaf'],prior['consumer'],prior['predicate'],prior['query'],prior['drop'])==(24,3,14,4,True)
assert json.loads((E/'current-suite.json').read_text())['rc']==0
presence=json.loads((E/'after-presence.json').read_text());assert len(presence['cases'])==10 and all(r['rc']==r['expected_rc'] for r in presence['cases'])
save('entry-preflight.json',dict(utc=utc(),suite_rc=0,binding_rc=0,leaf_cases=24,consumer_cases=3,predicate_cases=14,query_cases=4,leaf_present=True,mpeg_fail_before_cases=2,run_exit_cases=6,new_exact_bindings=5,fixture=binding['binary']))
build=json.loads((E/'built-binaries.json').read_text())
assert sha(B/'ps2xRuntime/ps2EntryRunner')==build['runner']['sha256'] and sha(B/'ps2xTest/ps2x_tests')==build['suite']['sha256']
def git(*args):return subprocess.check_output(['git','-C',str(R),*args],text=True)
head=git('rev-parse','HEAD').strip();assert head==BASE_SHA
assert git('diff','--cached','--name-only')==''
record=dict(utc=utc(),fork_head=head,fork_status=git('status','--short'),test_count=452,bin_size=build['runner']['bytes'],bin_sha=build['runner']['sha256'],test_size=build['suite']['bytes'],test_sha=build['suite']['sha256'])
save('e17a-build.json',record)
print('All gates pinned; fork MAP commit follows the probe as instructed.')
print('# E17 PREPARE PROBE TAIL COMPLETE')
