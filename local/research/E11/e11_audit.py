#!/usr/bin/env python3
"""Final offline evidence/link/tail audit; no build, boot or mutation outside E11."""
import ast, gzip, hashlib, json, re
from pathlib import Path
E=Path(__file__).resolve().parent
checks={}
for p in E.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
checks['python_ast_files']=len(list(E.glob('*.py')))
for p in E.rglob('*.json'):json.loads(p.read_text())
checks['json_files']=len(list(E.rglob('*.json')))
for name in ['REPORT.md','NEXT-BRIEF.md','COMMANDS.md']:
    p=E/name;data=p.read_text()
    for link in re.findall(r'\]\(([^)]+)\)',data):
        if '://' not in link:assert (E/link.split('#')[0]).exists(),(name,link)
    assert data.endswith('\n') and 'TAIL COMPLETE' in data.splitlines()[-1],name
checks['report_links_and_tails']=True
retained=json.loads((E/'e11a-retained.json').read_text())
unique={}
for row in retained['files']:
    p=E/row['canonical'];data=gzip.decompress(p.read_bytes()) if row['encoding']=='gzip' else p.read_bytes()
    assert hashlib.sha256(data).hexdigest()==row['sha256'] and len(data)==row['bytes']
    unique[row['canonical']]=p.stat().st_size
checks['capture_original_files']=len(retained['files']);checks['capture_canonical_files']=len(unique)
checks['capture_retained_bytes']=sum(unique.values())
assert checks['capture_original_files']==31 and checks['capture_canonical_files']==23
for r in json.loads((E/'evidence-retention.json').read_text())['aliases']:
    p=E/r['alias'];assert p.is_symlink() and p.resolve()==(E/r['canonical']).resolve()
    data=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
    assert hashlib.sha256(data).hexdigest()==r['sha256_uncompressed']
for r in json.loads((E/'evidence-retention.json').read_text())['compressed']:
    data=gzip.decompress((E/r['canonical']).read_bytes());assert hashlib.sha256(data).hexdigest()==r['sha256']
checks['snapshot_aliases_and_compressed_logs']=True
assert not list(E.rglob('__pycache__'))
q=json.loads((E/'entry-preflight.json').read_text());assert q['query_cases']==4 and q['suite_rc']==q['binding_rc']==0
j=json.loads((E/'e11a-join.json').read_text());assert j['selected_outcome']=='ii' and j['copy_rgb_differences']==0
assert j['host_present_exact'] and j['dynamic_query_pairs']==321 and j['query_missing']==0
assert len(j['copy_pairs'])==5 and len(j['present_matches'])==4
assert all(r['mask']==r['queued']==0 for r in j['copy_pairs'])
checks['entry_request_copy_present_joins']=True
before=json.loads((E/'before/generated.json').read_text());after=json.loads((E/'after/generated.json').read_text())
b={Path(r['path']).name:r['sha256'] for r in before};a={Path(r['path']).name:r['sha256'] for r in after}
assert len(b)==9449 and len(a)==9450 and set(a)-set(b)=={'sub_002C5140_0x2c5140.cpp'}
assert set(b)-set(a)==set()
assert [n for n in b if b[n]!=a[n]]==['ps2_recompiled_functions.h','register_functions.cpp']
checks['generated_scope']=True
(E/'final-audit.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,sort_keys=True))
print('# E11 FINAL AUDIT TAIL COMPLETE')
