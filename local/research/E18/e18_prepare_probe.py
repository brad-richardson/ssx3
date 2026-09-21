"""Pin all behavior-regression gates before spending the single E18 title allowance."""
import subprocess
from e18_common import *
closed=json.loads((E/'current-closure-validation.json').read_text());assert len(closed['cases'])==6 and all(c['rc']==0 for c in closed['cases'])
binding=json.loads((E/'current-binding-validation.json').read_text());prior=binding['cases'][0]
assert all(c['rc']==0 for c in binding['cases']) and len(binding['cases'])==3
assert (prior['leaf'],prior['consumer'],prior['predicate'],prior['query'],prior['drop'])==(24,3,14,4,True)
suite=json.loads((E/'current-suite.json').read_text());assert suite['rc']==0
text=(E/'current-suite.txt').read_text();assert 'Total Tests: 458' in text and 'Failed: 0' in text
assert 'MPEG non-stream R1' in text and 'MPEG non-stream R6' in text
assert json.loads((E/'after-build-scope.json').read_text())['all_prior_test_bytes_equal']
extra=json.loads((E/'current-extra-validation.json').read_text());assert len(extra['cases'])==8 and all(c['rc']==0 for c in extra['cases'])
audit=json.loads((E/'after-generated-audit.json').read_text());assert audit['count']==9457 and audit['all_hashes_match']
save('entry-preflight.json',dict(utc=utc(),suite_rc=0,binding_rc=0,leaf_cases=24,consumer_cases=3,predicate_cases=14,query_cases=4,leaf_present=True,mpeg_delivery_cases=2,run_exit_cases=6,new_regression_cases=6,fixture=binding['binary']))
build=json.loads((E/'built-binaries.json').read_text())
assert sha(B/'ps2xRuntime/ps2EntryRunner')==build['runner']['sha256'] and sha(B/'ps2xTest/ps2x_tests')==build['suite']['sha256']
def git(*args):return subprocess.check_output(['git','-C',str(R),*args],text=True)
head=git('rev-parse','HEAD').strip();assert head==BASE_SHA and git('diff','--cached','--name-only')==''
save('e18a-build.json',dict(utc=utc(),fork_head=head,fork_status=git('status','--short'),test_count=458,bin_size=build['runner']['bytes'],bin_sha=build['runner']['sha256'],test_size=build['suite']['bytes'],test_sha=build['suite']['sha256']))
print('All E18 regression gates pinned. T13 and atomic lease remain mandatory.')
print('# E18 PREPARE PROBE TAIL COMPLETE')
