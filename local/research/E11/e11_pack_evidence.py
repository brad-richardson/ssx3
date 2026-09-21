#!/usr/bin/env python3
"""Deduplicate E11-owned snapshots with local aliases; compress closed logs."""
import gzip, hashlib, json, os, shutil
from pathlib import Path
E=Path(__file__).resolve().parent
assert not (E/'evidence-retention.json').exists()
aliases={
    'copy-source-arm.png':'producer-428d0abfed9a84ee0564e176319c6989536ffb7516700c020c4b45d9e76600c7.png',
    'expected-drop-generated.json':'before/generated.json',
    'after/register_functions.cpp.gz':'entry-register_functions.cpp.gz',
    'after/sub_002C5140_0x2c5140.cpp.gz':'entry-sub_002C5140_0x2c5140.cpp.gz',
    'entry-sub_00426230_0x426230.cpp.gz':'before/sub_00426230_0x426230.cpp.gz',
    'after/sub_00426230_0x426230.cpp.gz':'before/sub_00426230_0x426230.cpp.gz',
    'after/sub_004261F0_0x4261f0.cpp.gz':'before/sub_004261F0_0x4261f0.cpp.gz',
    'after/sub_002C50E0_0x2c50e0.cpp.gz':'before/sub_002C50E0_0x2c50e0.cpp.gz',
    'after/canonical.toml':'before/canonical.toml',
    'after/used.toml':'before/used.toml',
    'after/used.csv':'before/used.csv',
    'after-manifest.log':'after/manifest.json',
}
def content(p):return gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
rows=[]
for old,new in aliases.items():
    p,q=E/old,E/new
    assert p.is_file() and q.is_file() and not q.is_symlink()
    d=content(p);assert d==content(q)
    row=dict(alias=old,canonical=new,sha256_uncompressed=hashlib.sha256(d).hexdigest(),removed_bytes=p.stat().st_size)
    p.unlink();p.symlink_to(os.path.relpath(q,p.parent));assert content(p)==d
    rows.append(row)
compressed=[]
for name in ['entry-generation.log','entry-build.log','entry-binding-link.log']:
    p=E/name;d=p.read_bytes();q=E/(name+'.gz')
    with gzip.open(q,'xb',compresslevel=9) as out:out.write(d)
    assert content(q)==d
    compressed.append(dict(original=name,canonical=q.name,bytes=len(d),retained_bytes=q.stat().st_size,sha256=hashlib.sha256(d).hexdigest()))
    p.unlink()
cache=E/'__pycache__'
if cache.exists():shutil.rmtree(cache)
(E/'evidence-retention.json').write_text(json.dumps(dict(aliases=rows,compressed=compressed,python_cache_removed=True),indent=2)+'\n')
print('local aliases',len(rows),'compressed logs',len(compressed))
print('# E11 EVIDENCE RETENTION TAIL COMPLETE')
