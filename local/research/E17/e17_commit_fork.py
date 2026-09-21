"""Commit the named five-row map/generated delta after the one guarded probe."""
import subprocess
from e17_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
def git(*args):
    p=subprocess.run(['git','-C',str(R),*args],capture_output=True,text=True)
    commands.append(dict(argv=['git','-C',str(R),*args],rc=p.returncode,stdout=p.stdout,stderr=p.stderr))
    save('fork-commit-commands.json',commands)
    assert p.returncode==0,(args,p.stdout,p.stderr)
    return p.stdout
commands=[]
assert git('rev-parse','HEAD').strip()==BASE_SHA
assert git('diff','--cached','--name-only')==''
assert (E/'boot-attempt.json').exists()
end=json.loads((E/'e17a-result.json').read_text());assert end.get('release_utc') and not end.get('lease_ownership_error')
assert not Path('/tmp/ssx3-p-lane-lease').exists()
assert (E/'boot-analysis-summary.json').exists(), 'Probe joins or exact missing receipts must be tabled before MAP commit'
for label in ['current-suite','current-binding','current-closure','five-present']:
    d=json.loads((E/(label+'-bounded-result.json')).read_text());assert d['rc']==0 and d['bound'] is None
audit=json.loads((E/'precommit-source-audit.json').read_text());assert audit['protected_build_unchanged'] and audit['all_five_new_exact_slots']
scope=json.loads((E/'generation-scope.json').read_text())
files=['games/ssx3/ssx3-functions.sweep.csv']+['ps2xRuntime/src/runner/'+name for name in scope['added']+scope['changed']]
assert len(files)==8
git('add','-f','--',*files)
staged=git('diff','--cached','--name-only').splitlines();assert sorted(staged)==sorted(files),staged
git('diff','--cached','--check')
message='[E17] Absorb five verified I-lane map entries\n\nAdd exact rows at 0x14f2a8, 0x156750, 0x243a80, 0x395730, and 0x3a0158.\nRetain existing query/predicate/leaf rows and stage the matching generated\nentries, declarations, and registry. No runtime or MPEG behavior edits.\n\nOrchestrated-By: Muse Code\n'
(E/'fork-commit-message.txt').write_text(message)
git('commit','-F',str(E/'fork-commit-message.txt'))
head=git('rev-parse','HEAD').strip()
assert sorted(git('diff-tree','--no-commit-id','--name-only','-r',head).splitlines())==sorted(files)
save('fork-commit.json',dict(utc=utc(),classification='MAP',before=BASE_SHA,head=head,named_files=files,status_after=git('status','--short'),pushed=False))
git('push','fork','HEAD:refs/heads/ssx3')
remote=git('ls-remote','fork','refs/heads/ssx3');assert remote.split()[0]==head
assert git('rev-parse','refs/remotes/fork/ssx3').strip()==head
save('fork-push.json',dict(utc=utc(),head=head,remote_sha=remote.split()[0],agreement=True,remote='fork',ref='refs/heads/ssx3',named_files=files,main_repo_pushed=False))
print('Fork MAP commit',head,'remote agrees; named files',len(files))
print('# E17 FORK COMMIT/PUSH TAIL COMPLETE')
