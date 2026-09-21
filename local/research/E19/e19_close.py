"""Retain failed observation and re-audit protected state after the stop rule."""
import collections,gzip,subprocess
from e19_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert (E/'stop-rule.json').exists()
assert not (E/'boot-attempt.json').exists() and not (E/'q1-complete.json').exists()
raw=E/'raw';raw.mkdir(exist_ok=False)
retained=[]
for name in ['parser-events.txt','parser-input.bin']:
    p=E/'.suite-observer/parser-observer'/name
    canonical=raw/('failed-observer-'+name+'.gz')
    original=pin(p)
    with p.open('rb') as f,gzip.open(canonical,'wb') as out:
        while b:=f.read(1024*1024):out.write(b)
    with gzip.open(canonical,'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==original['sha256']
    retained.append(dict(original=original,canonical=str(canonical.relative_to(E)),compressed=pin(canonical)))
save('retained.json',dict(utc=utc(),files=retained,originals_preserved=True))
text=(E/'.suite-observer/parser-observer/parser-events.txt').read_text()
lines=text.splitlines();kinds=collections.Counter()
for line in lines:
    for field in line.split():
        if field.startswith('kind='):kinds[field[5:]]+=1
enters=[line for line in lines if 'kind=parse-enter ' in line]
kept=sum(int(f.split('=',1)[1]) for line in enters for f in line.split() if f.startswith('kept='))
save('observer-failure-analysis.json',dict(utc=utc(),suite_rc=-11,last_named_case='E18 R3',
    source_footer_present='# E19 PARSER CLOSURE' in text,final_newline=text.endswith('\n'),
    event_lines=len(lines),event_kinds=dict(kinds),first_event=lines[0],last_event=lines[-1],
    retained_input_bytes=kept,payload_limit=2*M,
    zero_kept_enters=sum('kept=0 ' in line for line in enters),
    inference='Repeated observed_parse stack frames plus repeated parse-enter/no parse-return demonstrate recursion in the new observer forwarding path. No host-parser packet result is established.',
    threshold_eligible=False,closure_eligible=False,boot_eligible=False))
before=json.loads((E/'checkpoint.json').read_text())
sources=[]
for row in before['inputs_sources']:
    p=pin(row['path']);assert p['sha256']==row['sha256'],p;sources.append(p)
generated=json.loads((E/'before-generated.json').read_text())
actual=[pin(p) for p in sorted((R/'ps2xRuntime/src/runner').iterdir())
        if p.suffix in ('.cpp','.h') and not p.name.startswith('._')]
assert len(actual)==9457 and {r['path']:r['sha256'] for r in actual}=={r['path']:r['sha256'] for r in generated}
protected=json.loads((E/'protected-build-before.json').read_text())
for row in protected:assert sha(row['path'])==row['sha256'],row['path']
commands=[['git','-C',str(R),'rev-parse','HEAD','refs/remotes/fork/ssx3'],
          ['git','-C',str(R),'ls-remote','fork','refs/heads/ssx3'],
          ['git','-C',str(R),'status','--short']]
receipts=[]
for command in commands:
    p=subprocess.run(command,text=True,capture_output=True,check=True)
    receipts.append(dict(argv=command,rc=p.returncode,stdout=p.stdout,stderr=p.stderr))
assert receipts[0]['stdout'].splitlines()==[BASE_SHA,BASE_SHA]
assert receipts[1]['stdout'].split()[0]==BASE_SHA
assert receipts[2]['stdout']=='?? ps2_log.txt\n'
resources=sample();assert not bound(resources),resources
save('final-audit.json',dict(utc=utc(),fork=BASE_SHA,fork_commands=receipts,fork_source_changes=0,fork_commits=0,
    generated_count=9457,all_generated_hashes_equal=True,protected_build_files=len(protected),all_protected_hashes_equal=True,
    inputs_sources=sources,runner=pin(B/'ps2xRuntime/ps2EntryRunner'),suite=pin(B/'ps2xTest/ps2x_tests'),
    fixture=pin(P/'e18-fixtures/after/binding-test'),title_boots=0,lease_claims=0,
    q1_complete=False,q2_opened=False,q3_opened=False,resources=resources))
print('Final audit: fork unchanged;9457 generated and1725 protected hashes agree;0 boots/claims/fork commits.')
print('# E19 FINAL AUDIT TAIL COMPLETE')
