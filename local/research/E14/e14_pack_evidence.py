#!/usr/bin/env python3
"""Compress the closed link raw and alias identical local retained snapshots."""
import gzip,hashlib,json,os
from pathlib import Path
E=Path(__file__).resolve().parent
assert (E/'stop.json').exists() and not (E/'evidence-retention.json').exists()
rows=[]
p=E/'baseline-link.log';raw=p.read_bytes();target=E/'baseline-link.log.gz'
target.write_bytes(gzip.compress(raw,mtime=0));assert gzip.decompress(target.read_bytes())==raw
rows.append(dict(original=p.name,canonical=target.name,encoding='gzip',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()));p.unlink()
canonical={}
for p in sorted(E.rglob('*')):
    if p.is_symlink() or not p.is_file() or not p.name.endswith(('.cpp.gz','.h.gz','.csv','.toml','.json')):continue
    raw=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
    key=(p.suffix,hashlib.sha256(raw).hexdigest())
    if key not in canonical:canonical[key]=p;continue
    target=canonical[key]
    rows.append(dict(original=str(p.relative_to(E)),canonical=str(target.relative_to(E)),encoding='local-relative-alias',bytes=len(raw),sha256=key[1]))
    relative=os.path.relpath(target,p.parent);p.unlink();p.symlink_to(relative)
    assert p.resolve().is_relative_to(E.resolve())
    check=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes();assert check==raw
(E/'evidence-retention.json').write_text(json.dumps(dict(rows=rows,all_verified=True),indent=2)+'\n')
print('Verified retention dispositions:',len(rows))
print('# E14 RETENTION TAIL COMPLETE')
