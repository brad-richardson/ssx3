"""Verify standalone E18 canonical captures without reading SSD originals."""
import gzip,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent
manifest=json.loads((E/'e18a-retained.json').read_text());unique={};logical=0
for row in manifest['files']:
    path=E/row['canonical'];op=gzip.open if row['encoding']=='gzip' else open
    with op(path,'rb') as f:
        h=hashlib.sha256();n=0
        while b:=f.read(1024*1024):h.update(b);n+=len(b)
    assert n==row['bytes'] and h.hexdigest()==row['sha256'],row
    logical+=n;unique[str(path)]=path.stat().st_blocks*512
record=dict(files=len(manifest['files']),canonical_files=len(unique),logical_bytes=logical,canonical_allocated=sum(unique.values()),all_hashes_match=True,ssd_original_reads=0)
(E/'standalone-retention-verification.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record));print('# E18 STANDALONE CAPTURE VERIFICATION TAIL COMPLETE')
