"""Force-add only standalone E18 evidence, with a bounded main-Git allocation receipt."""
import hashlib,subprocess,sys,zlib
from e18_common import *
ROOT=E.parents[2];GIT=ROOT/'.git';CAP=32*M
assert os.environ.get('COPYFILE_DISABLE')=='1'
def command(*args):
    p=subprocess.run(['git','-c','gc.auto=0','-c','maintenance.auto=false',*args],cwd=ROOT,text=True,capture_output=True)
    assert p.returncode==0,(args,p.stdout,p.stderr)
    return p.stdout
def allocations():
    return {str(p.relative_to(GIT)):p.lstat().st_blocks*512 for p in [GIT,*GIT.rglob('*')] if p.exists()}
assert command('diff','--cached','--name-only')==''
assert command('status','--porcelain')==''
head_before=command('rev-parse','HEAD').strip();before=allocations()
save('main-git-before.json',dict(utc=utc(),head=head_before,allocated=before,cap=CAP))
def growth():return sum(max(0,n-before.get(p,0)) for p,n in allocations().items())
# zlib blob estimate plus one allocation block per object and one MiB for refs/dirs.
files=[p for p in E.rglob('*') if p.is_file()]
estimate=M
for p in files:
    b=p.read_bytes();n=len(zlib.compress(b'blob '+str(len(b)).encode()+b'\0'+b));estimate+=(n+4095)//4096*4096
assert estimate<CAP-M,estimate
command('add','-f','--','local/research/E18')
staged=command('diff','--cached','--name-only').splitlines();assert staged and all(p.startswith('local/research/E18/') for p in staged)
used=growth();assert used<CAP-M,used
save('evidence-stage.json',dict(utc=utc(),head_before=head_before,files=len(staged),positive_main_git_growth=used,estimated_blob_allocation=estimate,cap=CAP,remaining_reserve=CAP-used,automatic_gc_disabled_for_commit=True,main_push=False))
report=E/'REPORT.md'
with report.open('a') as f:
    f.write('\n| Evidence publication budget | Receipt |\n|---|---|\n')
    f.write(f'| Named force-add | E18 only; initial staged files{len(staged)}; main Git positive allocated growth{used}B of32MiB cap; at least1MiB commit reserve |\n')
    f.write('| Git accounting | `main-git-before.json`, `evidence-stage.json`; automatic Git maintenance disabled for the commit; no main-repository push |\n')
    f.write('| Final stop | Fork3adc0478 pushed; one probe spent; parser-output/further-input edge handed off; local evidence commit ends E18 |\n')
prefix=report.read_bytes();line_count=prefix.count(b'\n');digest=hashlib.sha256(prefix).hexdigest()
with report.open('a') as f:
    f.write('\n| Tail receipt | Value |\n|---|---|\n')
    f.write(f'| Complete prefix | Lines1–{line_count}; {len(prefix)}B; SHA256 `{digest}` |\n')
    f.write('| Source tails | Real E15/E7 run-exit footers, count match, pending0/truncation0; retained file ends with newline |\n')
    f.write('| E18 REPORT TAIL COMPLETE | Tables complete; no second fix or boot; main evidence publication only |\n')
final=report.read_bytes();assert final[:len(prefix)]==prefix and final.endswith(b'\n')
save('report-tail-receipt.json',dict(prefix_lines=line_count,prefix_bytes=len(prefix),prefix_sha256=digest,report_bytes=len(final),report_sha256=hashlib.sha256(final).hexdigest(),newline_complete=True))
command('add','-f','--','local/research/E18')
staged=command('diff','--cached','--name-only').splitlines();assert all(p.startswith('local/research/E18/') for p in staged)
command('diff','--cached','--check','--','local/research/E18/REPORT.md','local/research/E18/NEXT-BRIEF.md')
assert growth()<CAP-M
s=sample();s['internal_allocated']+=growth();assert not bound(s)
message='[E18] Record MPEG caller delivery and guarded probe\n\nReverify e63f1616, audit caller ownership, and receipt fork behavior\ncommit 3adc0478. Preserve 458/458, actual-wrapper rc1-to-rc0,\nprior bindings, closure cases, one guarded boot and real source tails.\n\nThe callback delivered 5040 bytes; parser packets/frames and completion\nremained zero. Name that next dependency without a second behavior fix.\n\nOrchestrated-By: Muse Code\n'
# Message is outside evidence to avoid adding an untracked file after final stage.
msg=Path('/tmp/e18-evidence-message.txt');assert not msg.exists();msg.write_text(message)
command('commit','-F',str(msg))
head=command('rev-parse','HEAD').strip();status=command('status','--porcelain');assert status==''
assert growth()<CAP
result=dict(evidence_commit=head,head_before=head_before,files=len(staged),main_git_positive_growth=growth(),git_cap=CAP,main_status=status,main_pushed=False,report_sha256=hashlib.sha256(report.read_bytes()).hexdigest(),prefix_sha256=digest,report_lines=report.read_bytes().count(b'\n'),tail_complete=True)
Path('/tmp/e18-evidence-final-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));print('# E18 EVIDENCE COMMIT AND TAIL RECEIPT COMPLETE')
