#!/usr/bin/env python3
"""Compress closed tool logs and alias identical local snapshots inside E13."""
import gzip,hashlib,json,os
from pathlib import Path
E=Path(__file__).resolve().parent
assert (E/'reproduction.json').exists()
assert not (E/'evidence-retention.json').exists()
rows=[]
def sha(data):return hashlib.sha256(data).hexdigest()
for name in ['baseline-link.log','entry-generation.log','entry-build.log','entry-link.log']:
    p=E/name;data=p.read_bytes();dest=p.with_name(p.name+'.gz')
    assert not dest.exists();dest.write_bytes(gzip.compress(data,mtime=0))
    assert gzip.decompress(dest.read_bytes())==data
    rows.append(dict(original=name,canonical=dest.name,encoding='gzip',bytes=len(data),sha256=sha(data)))
    p.unlink()
# Keep one local copy of identical snapshots. Never alias outside the evidence tree.
canonical={}
for p in sorted(E.rglob('*')):
    if p.is_symlink() or not p.is_file():continue
    if not (p.name.endswith(('.cpp.gz','.h.gz','.csv','.toml','.png'))):continue
    data=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
    key=(p.suffix,sha(data))
    if key not in canonical:canonical[key]=p;continue
    dest=canonical[key];relative=os.path.relpath(dest,p.parent)
    rows.append(dict(original=str(p.relative_to(E)),canonical=str(dest.relative_to(E)),encoding='local-relative-alias',bytes=len(data),sha256=key[1]))
    p.unlink();p.symlink_to(relative)
    assert p.resolve().is_relative_to(E.resolve())
    check=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
    assert check==data
(E/'evidence-retention.json').write_text(json.dumps(dict(files=rows,all_verified=True),indent=2)+'\n')
print('closed logs and duplicate snapshots retained:',len(rows),'verified dispositions')
print('# E13 EVIDENCE RETENTION TAIL COMPLETE')
