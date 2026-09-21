"""Validate authored evidence, complete document tails, and standalone inventory."""
import ast, hashlib, json, re
from pathlib import Path
from e16_common import E, save, sha, utc

authored=list(E.glob('e16_*.py'))+[E/'e16_binding_test.cpp']+list(E.glob('*.md'))
for p in authored:
    data=p.read_text()
    assert data.endswith('\n'),p
    assert not any(l.rstrip()!=l for l in data.splitlines()),p
    if p.suffix=='.py':ast.parse(data,filename=str(p))
for p in E.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if target.startswith(('http:','https:','#')):continue
        # Inventory and tail receipts are written below in this same operation.
        if target in ('EVIDENCE.json','HYGIENE.json','TAIL-RECEIPT.md'):continue
        assert (p.parent/target).exists(),(p,target)
tails={}
for name,marker in [('REPORT.md','E16 REPORT TAIL COMPLETE'),('CONTRACT.md','E16 CONTRACT TAIL COMPLETE'),
                    ('COMMANDS.md','E16 COMMANDS TAIL COMPLETE'),('NEXT-BRIEF.md','E16 NEXT-BRIEF TAIL COMPLETE'),
                    ('E15-ABI.md','E15 ABI TAIL COMPLETE')]:
    p=E/name;lines=p.read_text().splitlines()
    assert marker in lines[-1],name
    tails[name]=dict(bytes=p.stat().st_size,lines=len(lines),sha256=sha(p),last_line=lines[-1])
report=(E/'REPORT.md').read_text()
assert all(f'E16 REPORT CHUNK {i} COMPLETE' in report for i in range(1,5))
replay=json.loads((E/'canonical-replay.json').read_text())
assert replay['canonical_only'] and len(replay['commands'])==5 and len(replay['outputs'])==9
for item in replay['outputs']:assert sha(E/item['path'])==item['sha256']
stage=json.loads((E/'staging-receipt.json').read_text())
assert stage['only_e16'] and stage['main_git_positive_growth']<32*1024**2
for p in E.rglob('*'):
    assert not p.is_symlink(),p
    assert p.name!='__pycache__' and not p.name.startswith('._'),p
save('HYGIENE.json',dict(utc=utc(),authored_files=len(authored),python_ast_valid=True,authored_trailing_whitespace=False,
    document_links_exist=True,report_chunks=4,document_tails=tails,canonical_replay_hashes_current=True,
    preserved_empty_error_artifact='analysis-errors/empty-missing-wrapper.gz',
    raw_policy='Raw stdout, diff, traces, source snapshots, and historical fixtures are retained byte-for-byte; authored-file whitespace checks do not rewrite them.'))
lines=['# E16 complete tail receipt','','| Document | Lines | Bytes | SHA256 |','|---|---:|---:|---|']
for name,d in tails.items():lines.append(f'| {name} | {d["lines"]} | {d["bytes"]} | `{d["sha256"]}` |')
lines+=['','| Report tail, verbatim |','|---|',f'| {tails["REPORT.md"]["last_line"]} |','',
         '**E16 TAIL RECEIPT COMPLETE — all four report chunks and the final tail are present; no omitted final section.**']
(E/'TAIL-RECEIPT.md').write_text('\n'.join(lines)+'\n')
inventory=[]
for p in sorted(E.rglob('*')):
    if p.is_file() and p.name!='EVIDENCE.json':inventory.append(dict(path=str(p.relative_to(E)),bytes=p.stat().st_size,sha256=sha(p)))
save('EVIDENCE.json',dict(utc=utc(),excludes=['EVIDENCE.json'],files=inventory))
print('Authored files',len(authored),'inventory files',len(inventory),'report lines',tails['REPORT.md']['lines'])
print('# E16 HYGIENE TAIL COMPLETE')
