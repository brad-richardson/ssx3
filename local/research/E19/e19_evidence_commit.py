"""Stage/review/commit only standalone E19 stop evidence; never push."""
import subprocess,sys,zlib
from e19_common import *
ROOT=E.parents[2];GIT=ROOT/'.git';CAP=64*M
assert os.environ.get('COPYFILE_DISABLE')=='1'
def command(*args):
    p=subprocess.run(['git','-c','gc.auto=0','-c','maintenance.auto=false',*args],cwd=ROOT,text=True,capture_output=True)
    assert p.returncode==0,(args,p.stdout,p.stderr)
    return p.stdout
def allocations():
    return {str(p.relative_to(GIT)):p.lstat().st_blocks*512 for p in [GIT,*GIT.rglob('*')] if p.exists()}
def files():
    return sorted(p for p in E.rglob('*') if p.is_file() and not any(x.startswith('.suite-') or x=='__pycache__' for x in p.relative_to(E).parts))
def growth(before):return sum(max(0,n-before.get(p,0)) for p,n in allocations().items())
def stage():
    assert command('diff','--cached','--name-only')==''
    assert command('status','--porcelain')==''
    assert not (E/'report-tail-receipt.json').exists()
    before=allocations();head=command('rev-parse','HEAD').strip()
    save('main-git-before.json',dict(utc=utc(),head=head,allocated=before,cap=CAP))
    estimate=M
    for p in files():
        b=p.read_bytes();n=len(zlib.compress(b'blob '+str(len(b)).encode()+b'\0'+b));estimate+=(n+4095)//4096*4096
    assert estimate<CAP-M,estimate
    command('add','-f','--',*(str(p.relative_to(ROOT)) for p in files()))
    initial=command('diff','--cached','--name-only').splitlines()
    assert initial and all(p.startswith('local/research/E19/') for p in initial)
    used=growth(before);assert used<CAP-M
    save('evidence-stage.json',dict(utc=utc(),head_before=head,initial_files=initial,positive_main_git_growth=used,
        estimated_blob_allocation=estimate,cap=CAP,reserve=CAP-used,automatic_gc_disabled=True,main_push=False,
        excluded_scratch=['.suite-checkpoint','.suite-observer'],canonical_failed_raw='retained.json'))
    report=E/'REPORT.md'
    with report.open('a') as f:
        f.write('\n| Evidence publication budget | Receipt |\n|---|---|\n')
        f.write(f'| Named force-add | E19 evidence only; initial staged files{len(initial)}; main Git positive allocated growth{used} B of64 MiB cap; at least1 MiB commit reserve |\n')
        f.write('| Staged set | `evidence-stage.json` lists the exact initial set; final set includes that receipt and `report-tail-receipt.json`. Scratch remains unstaged; no fork files. |\n')
        f.write('| Publication scope | Local evidence commit only; no main or fork push; automatic Git maintenance disabled for commit. |\n')
    prefix=report.read_bytes();line_count=prefix.count(b'\n');digest=sha(report)
    with report.open('a') as f:
        f.write('\n| Tail receipt | Value |\n|---|---|\n')
        f.write(f'| Complete prefix | Lines1–{line_count}; {len(prefix)} B; SHA256 `{digest}` |\n')
        f.write('| Source-tail gap | Failed observer capture has no real closure footer and reached its payload cap; remains ineligible. Baseline E16 closure receipts remain complete and separate. |\n')
        f.write('| E19 REPORT TAIL COMPLETE | Stop gate, unanswered questions and all receipts tabled;0 title boots,0 fork edits/commits; evidence publication ends E19. |\n')
    final=report.read_bytes();assert final[:len(prefix)]==prefix and final.endswith(b'\n')
    save('report-tail-receipt.json',dict(prefix_lines=line_count,prefix_bytes=len(prefix),prefix_sha256=digest,
        report_bytes=len(final),report_sha256=sha(report),report_lines=final.count(b'\n'),newline_complete=True,
        failed_observer_footer_absent=True,experimental_work_stopped=True))
    command('add','-f','--',*(str(p.relative_to(ROOT)) for p in files()))
    staged=command('diff','--cached','--name-only').splitlines()
    assert set(staged)=={str(p.relative_to(ROOT)) for p in files()}
    command('diff','--cached','--check','--','local/research/E19/REPORT.md','local/research/E19/NEXT-BRIEF.md')
    assert growth(before)<CAP-M
    print(json.dumps(dict(stage_count=len(staged),git_growth=growth(before),report_lines=final.count(b'\n'),report_sha256=sha(report)),indent=2))
    print('# E19 EVIDENCE STAGE TAIL COMPLETE')
def commit():
    before=json.loads((E/'main-git-before.json').read_text())['allocated']
    tail=json.loads((E/'report-tail-receipt.json').read_text());report=(E/'REPORT.md').read_bytes()
    assert sha(E/'REPORT.md')==tail['report_sha256']
    assert hashlib.sha256(report[:tail['prefix_bytes']]).hexdigest()==tail['prefix_sha256']
    staged=command('diff','--cached','--name-only').splitlines()
    assert set(staged)=={str(p.relative_to(ROOT)) for p in files()}
    assert command('diff','--name-only')==''
    assert growth(before)<CAP-M
    s=sample();s['internal_allocated']+=growth(before);assert not bound(s),s
    message='[E19] Record checkpoint and parser-observer stop gate\n\nReverify fork 3adc0478, 9457 generated hashes, baseline 458/458,\nE18/E15/E16 and prior actual bindings. Preserve the observer recursion\ncrash at R3 and honor the any-red stop before threshold/demand work.\n\nZero fork edits or commits, zero title boots. Retain the exact missing\nmeasurement receipts, complete report tail and measurement-first handoff.\n\nOrchestrated-By: Muse Code\n'
    msg=Path('/tmp/e19-evidence-message.txt');assert not msg.exists();msg.write_text(message)
    command('commit','-F',str(msg))
    head=command('rev-parse','HEAD').strip();status=command('status','--porcelain');assert status==''
    assert growth(before)<CAP
    result=dict(evidence_commit=head,files=len(staged),main_status=status,main_pushed=False,fork_commits=0,title_boots=0,
        main_git_positive_growth=growth(before),git_cap=CAP,report_sha256=sha(E/'REPORT.md'),report_lines=tail['report_lines'],tail_complete=True)
    Path('/tmp/e19-evidence-final-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));print('# E19 EVIDENCE COMMIT AND TAIL RECEIPT COMPLETE')
if __name__=='__main__':
    assert sys.argv[1] in ('stage','commit')
    (stage if sys.argv[1]=='stage' else commit)()
