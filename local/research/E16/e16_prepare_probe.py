"""Pin completed non-title gates and the exact repaired probe binaries."""
import subprocess
from e16_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
closed=json.loads((E/'closure-after-validation.json').read_text())
assert len(closed['cases'])==6 and all(c['rc']==0 for c in closed['cases'])
assert json.loads((E/'fixture-object-identity.json').read_text())['same_object']
binding=json.loads((E/'current-binding-validation.json').read_text());prior=binding['cases'][0]
assert prior['mode']=='prior' and prior['rc']==0 and [c['rc'] for c in binding['cases'][1:]]==[1,1]
assert (prior['leaf'],prior['consumer'],prior['predicate'],prior['query'],prior['drop'])==(24,3,14,4,True)
suite=json.loads((E/'repaired-suite.json').read_text());assert suite['rc']==0
entry=dict(utc=utc(),suite_rc=0,binding_rc=0,leaf_cases=24,consumer_cases=3,predicate_cases=14,query_cases=4,leaf_present=True,mpeg_fail_before_cases=2,run_exit_cases=6,fixture=binding['binary'])
save('entry-preflight.json',entry)
build=json.loads((E/'repaired-binaries-objects.json').read_text())
assert sha(B/'ps2xRuntime/ps2EntryRunner')==build['runner']['sha256'] and sha(B/'ps2xTest/ps2x_tests')==build['suite']['sha256']
def git(*args):return subprocess.check_output(['git','-C',str(R),*args],text=True)
head=git('rev-parse','HEAD').strip();assert head==json.loads((E/'fork-commit.json').read_text())['head']
record=dict(utc=utc(),fork_head=head,fork_status=git('status','--short'),test_count=452,bin_size=build['runner']['bytes'],bin_sha=build['runner']['sha256'],test_size=build['suite']['bytes'],test_sha=build['suite']['sha256'])
save('e16a-build.json',record);print(json.dumps(record,indent=2));print('# E16 PROBE BUILD GATES TAIL COMPLETE')
