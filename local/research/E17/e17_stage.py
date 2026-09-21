"""Force-stage only standalone E17 evidence and receipt its allocation/scope."""
import json, os, subprocess
from pathlib import Path
from e17_common import E, R, save, sample, size, bound, utc

assert os.environ.get('COPYFILE_DISABLE')=='1'
repo=E.parents[2]
def git(*args,cwd=repo):
    p=subprocess.run(['git',*args],cwd=cwd,capture_output=True,text=True)
    assert p.returncode==0,(args,p.stdout,p.stderr)
    return p.stdout
existing=git('diff','--cached','--name-only').splitlines()
assert all(p.startswith('local/research/E17/') for p in existing),existing
status_before=git('status','--short')
git('add','-f','--','local/research/E17')
names=git('diff','--cached','--name-only').splitlines()
assert names and all(p.startswith('local/research/E17/') for p in names)
authored=sorted(str(p.relative_to(repo)) for p in list(E.glob('e17_*.py'))+[E/'e17_binding_test.cpp']+list(E.glob('*.md')))
git('diff','--cached','--check','--',*authored)
baseline=json.loads((E/'main-git-allocation-before.json').read_text())
old={**baseline['files'],**baseline.get('directories',{})}
growth=sum(max(0,p.stat().st_blocks*512-old.get(str(p.relative_to(repo)),0)) for p in (repo/'.git').rglob('*'))
assert growth<32*1024**2
resources=sample()
assert not bound(resources) and resources['internal_allocated']+growth<5.5*1024**3
fork_head=git('rev-parse','HEAD',cwd=R).strip()
assert fork_head==json.loads((E/'fork-push.json').read_text())['head']
assert git('diff','--cached','--name-only',cwd=R)==''
save('staging-receipt.json',dict(utc=utc(),only_e17=True,staged_count=len(names),staged_names=names,
    status_before=status_before,main_git_positive_growth=growth,main_git_growth_cap=32*1024**2,
    resources=resources,internal_total_with_git_growth=resources['internal_allocated']+growth,
    fork_head=fork_head,fork_status=git('status','--short',cwd=R),fork_index_empty=True,
    note='Scope checked before commit. This receipt, the final inventory and tail receipts are then added through the same E17-only path.'))
print('E17-only staged files',len(names),'main Git positive growth',growth,'internal total',resources['internal_allocated']+growth)
print('# E17 STAGING TAIL COMPLETE')
