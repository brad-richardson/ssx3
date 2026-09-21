"""One named observation commit. Intentionally no push."""
import subprocess
from e16_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
name='ps2xRuntime/src/lib/ps2_runtime.cpp'
assert sha(R/name)=='b2c269a4c8bf54beaccafa371366fd0d33a13976812ff18086e896027a703260'
assert all(r['rc']==0 for r in json.loads((E/'closure-after-validation.json').read_text())['cases'])
assert json.loads((E/'repaired-suite.json').read_text())['rc']==0
assert [r['rc'] for r in json.loads((E/'current-binding-validation.json').read_text())['cases']]==[0,1,1]
commands=[]
def git(args):
    argv=['git','-C',str(R)]+args;p=subprocess.run(argv,capture_output=True,text=True)
    rec=dict(argv=argv,rc=p.returncode,stdout=p.stdout,stderr=p.stderr);commands.append(rec);save('fork-commit-commands.json',commands)
    assert p.returncode==0,rec
    return p.stdout.strip()
before=git(['rev-parse','HEAD']);assert before==BASE_SHA
assert not git(['diff','--cached','--name-only'])
status_before=git(['status','--short'])
git(['add','--',name]);assert git(['diff','--cached','--name-only'])==name
git(['diff','--cached','--check'])
git(['commit','-F',str(E/'fork-commit-message.txt')])
head=git(['rev-parse','HEAD']);assert git(['diff-tree','--no-commit-id','--name-only','-r',head])==name
status_after=git(['status','--short'])
record=dict(utc=utc(),classification='OBSERVATION',before=before,head=head,named_files=[name],status_before=status_before,status_after=status_after,pushed=False,reason='User instructed no push; orchestrator publishes at poll',source=pin(R/name))
save('fork-commit.json',record);print(json.dumps(record,indent=2));print('# E16 FORK COMMIT TAIL COMPLETE — local only')
