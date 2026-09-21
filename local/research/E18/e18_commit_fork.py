"""Commit only the tested E18 behavior source and regression additions; push fork only."""
import subprocess
from e18_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
commands=[]
def git(*args):
    p=subprocess.run(['git','-C',str(R),*args],capture_output=True,text=True)
    commands.append(dict(argv=['git','-C',str(R),*args],rc=p.returncode,stdout=p.stdout,stderr=p.stderr));save('fork-commit-commands.json',commands)
    assert p.returncode==0,(args,p.stdout,p.stderr)
    return p.stdout
assert git('rev-parse','HEAD').strip()==BASE_SHA
assert git('ls-remote','fork','refs/heads/ssx3').split()[0]==BASE_SHA
assert git('diff','--cached','--name-only')==''
assert (E/'boot-attempt.json').exists()
end=json.loads((E/'e18a-result.json').read_text());assert end['rc']==0 and end.get('release_utc') and not end.get('lease_ownership_error')
assert not Path('/tmp/ssx3-p-lane-lease').exists()
summary=json.loads((E/'boot-analysis-summary.json').read_text());assert summary['source_count_match'] and summary['callback_delivery']==1
for label in ['current-suite','current-binding','current-closure','current-extra','boot-analysis']:
    d=json.loads((E/(label+'-bounded-result.json')).read_text());assert d['rc']==0 and d['bound'] is None and not d['stdout_truncated']
audit=json.loads((E/'precommit-scope.json').read_text());assert audit['all_prior_test_bytes_equal']
for row in audit['source']:assert sha(row['path'])==row['sha256']
files=['ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp','ps2xTest/src/ps2_runtime_expansion_tests.cpp']
assert sorted(git('diff','--name-only').splitlines())==sorted(files)
admission(sample())
git('add','-f','--',*files)
assert sorted(git('diff','--cached','--name-only').splitlines())==sorted(files)
git('diff','--cached','--check')
save('fork-staged-set.json',dict(classification='BEHAVIOR',files=files,stat=git('diff','--cached','--stat'),numstat=git('diff','--cached','--numstat'),no_csv_generated_main_scheduler_or_header=True))
message='[E18] Deliver non-stream MPEG input callbacks on the caller\n\nSelect registered non-stream callbacks for the observed GetPicture input\nrequest, preserving caller thread/stack and registration order. Dispatch\noutside the MPEG lock with word0-only data and discard callback v0.\nInvalidate pending delivery on deletion/reset and release callback data\non completion. Add six scheduler-driven regression cases.\n\nValidation: 458/458; prior bindings and closure cases; actual-wrapper\nno-input/input rc1-to-rc0. One guarded host probe delivered 5040 bytes;\nparser output remained zero and GetPicture stayed in its typed wait.\nThe next input/progress dependency is reserved for a separate brief.\n\nOrchestrated-By: Muse Code\n'
(E/'fork-commit-message.txt').write_text(message)
git('commit','-F',str(E/'fork-commit-message.txt'))
head=git('rev-parse','HEAD').strip();assert sorted(git('diff-tree','--no-commit-id','--name-only','-r',head).splitlines())==sorted(files)
save('fork-commit.json',dict(utc=utc(),classification='BEHAVIOR',before=BASE_SHA,head=head,named_files=files,status_after=git('status','--short'),pushed=False))
git('push','fork','HEAD:refs/heads/ssx3')
remote=git('ls-remote','fork','refs/heads/ssx3');assert remote.split()[0]==head
assert git('rev-parse','refs/remotes/fork/ssx3').strip()==head
save('fork-push.json',dict(utc=utc(),head=head,remote_sha=remote.split()[0],agreement=True,remote='fork',ref='refs/heads/ssx3',named_files=files,main_repo_pushed=False))
print('Fork BEHAVIOR commit',head,'remote agrees; named files',len(files))
print('# E18 FORK COMMIT/PUSH TAIL COMPLETE')
