#!/usr/bin/env python3
"""Compress/move only closed E12-owned captures, verify hashes, retain one copy."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil

EVIDENCE=Path(__file__).resolve().parent
RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')


def digest(path,compressed=False):
    op=gzip.open if compressed else open
    with op(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['a','b','c','d']);args=ap.parse_args()
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    label='e12'+args.phase
    result=json.loads((EVIDENCE/f'{label}-result.json').read_text())
    assert result.get('release_utc') and not result.get('lease_ownership_error')
    manifest=EVIDENCE/f'{label}-retained.json'
    assert not manifest.exists(), 'retention is already complete'
    (EVIDENCE/'raw').mkdir(exist_ok=True)
    rows=[]
    canonical={}
    for old in sorted(EVIDENCE.glob('e12*-retained.json')):
        for row in json.loads(old.read_text())['files']:
            canonical[(row['sha256'],row['encoding'])]=EVIDENCE/row['canonical']
    def keep(src,dest,compress=False):
        size=src.stat().st_size;sha=digest(src)
        encoding='gzip' if compress else 'identity'
        key=(sha,encoding)
        if key in canonical:dest=canonical[key]
        elif src.suffix in ['.png','.bin'] and not compress:
            dest=EVIDENCE/'raw'/f'{sha}{src.suffix}'
        dest.parent.mkdir(exist_ok=True,parents=True)
        if not dest.exists():
            if compress:
                with src.open('rb') as a,gzip.open(dest,'xb',compresslevel=6) as b:shutil.copyfileobj(a,b,1024*1024)
            else:shutil.copyfile(src,dest)
        assert digest(dest,compress)==sha,(src,dest)
        rows.append(dict(original=str(src),canonical=os.path.relpath(dest,EVIDENCE),bytes=size,sha256=sha,
                         retained_bytes=dest.stat().st_size,encoding=encoding))
        canonical[key]=dest
        src.unlink()
    for name in [f'boot-{label}-1.log',f'syscalls-{label}-on.txt',f'ps2_log-{label}-1.txt']:
        keep(RUN/name,EVIDENCE/'raw'/(name+'.gz'),True)
    for src in sorted((RUN/f'{label}-1').iterdir()):
        if src.name.startswith('._'):continue
        if src.suffix=='.bin':
            sha=digest(src)
            dest=EVIDENCE/'raw'/f'vram-{sha}.bin.gz'
            keep(src,dest,True)
        else:keep(src,EVIDENCE/(label+'-'+src.name.removeprefix('e4-')))
    join=RUN/f'{label}-join'
    if join.exists():
        for src in sorted(join.iterdir()):
            if src.name.startswith('._'):continue
            dest=EVIDENCE/f'{label}-events.txt' if src.name=='e7-events.txt' else EVIDENCE/f'{label}-packets'/src.name
            keep(src,dest)
    for prefix in ['frames','park']:
        folder=RUN/f'{prefix}-{label}-1'
        if folder.exists():
            for src in sorted(folder.iterdir()):
                if src.name.startswith('._') or not src.is_file():continue
                keep(src,EVIDENCE/(label+'-'+('park-' if prefix=='park' else '')+src.name))
    manifest.write_text(json.dumps(dict(label=label,release_utc=result['release_utc'],files=rows),indent=2)+'\n')
    # Remove only metadata sidecars and empty directories belonging to this capture.
    for folder in [RUN/f'{label}-1',RUN/f'{label}-join',RUN/f'frames-{label}-1',RUN/f'park-{label}-1']:
        if folder.exists():
            for p in folder.iterdir():
                if p.is_file() and p.name.startswith('._'):p.unlink()
            folder.rmdir()
    print(label,'files',len(rows),'original_bytes',sum(r['bytes'] for r in rows),'manifest',manifest)
    print('# E12 RETENTION TAIL COMPLETE; every removed raw verified against its canonical content hash')


if __name__=='__main__':main()
