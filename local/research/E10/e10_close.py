#!/usr/bin/env python3
"""Close E10 evidence logs and retain one canonical copy of snapshot payloads."""
import gzip,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent
def digest(data):return hashlib.sha256(data).hexdigest()
def main():
    assert not (E/'retention.json').exists()
    rows=[]
    for name in ['drop-build.log','drop-generation.log']:
        p=E/name;data=p.read_bytes();q=p.with_name(p.name+'.gz')
        assert not q.exists()
        with gzip.open(q,'wb',compresslevel=9) as f:f.write(data)
        assert gzip.decompress(q.read_bytes())==data
        rows.append(dict(original=name,canonical=q.name,encoding='gzip',raw_bytes=len(data),raw_sha256=digest(data)))
        p.unlink()
    # The failed source-glob build contains binary AppleDouble diagnostics;
    # keep the complete compressed raw, never a truncated text extraction.
    p=E/'drop-build-attempt1.log.gz';h=hashlib.sha256();n=0
    with gzip.open(p,'rb') as f:
        while block:=f.read(1024*1024):h.update(block);n+=len(block)
    rows.append(dict(original='drop-build-attempt1.log',canonical=p.name,encoding='gzip',raw_bytes=n,raw_sha256=h.hexdigest()))
    candidates=[]
    for folder in ['before','.','after']:
        for p in sorted((E/folder).iterdir()):
            if not p.is_file():continue
            if folder=='.':
                if not (p.name.startswith('drop-') and p.name.endswith(('.cpp.gz','.h.gz'))):continue
            elif p.suffix not in ['.gz','.csv','.toml']:continue
            candidates.append(p)
    seen={}
    for p in candidates:
        raw=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
        h=digest(raw);name=str(p.relative_to(E));encoding='gzip' if p.suffix=='.gz' else 'raw'
        if h in seen:
            canonical,encoding=seen[h];p.unlink()
        else:canonical=name;seen[h]=(name,encoding)
        rows.append(dict(original=name,canonical=canonical,encoding=encoding,raw_bytes=len(raw),raw_sha256=h))
    (E/'retention.json').write_text(json.dumps({'files':rows,'policy':'One canonical snapshot payload; aliases resolve to retained bytes. No generated runner source staged in the fork.'},indent=2)+'\n')
    print('retained records',len(rows),'duplicate aliases',sum(r['original']!=r['canonical'] and not r['original'].endswith('.log') for r in rows))
    print('# E10 RETENTION TAIL COMPLETE')
if __name__=='__main__':main()
