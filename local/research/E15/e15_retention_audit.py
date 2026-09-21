#!/usr/bin/env python3
"""Validate completed retention after the monitor's list/stat cleanup race."""
import datetime,gzip,hashlib,json,os,shutil
from pathlib import Path
from e15_bounded import sample
E=Path(__file__).resolve().parent
assert os.environ.get('COPYFILE_DISABLE')=='1'
m=json.loads((E/'e15a-retained.json').read_text());unique={};rows=[]
for r in m['files']:
    p=E/r['canonical'];op=gzip.open if r['encoding']=='gzip' else open
    with op(p,'rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
    assert actual==r['sha256'] and not Path(r['original']).exists()
    unique[str(p)]=p.stat().st_size;rows.append(dict(original=r['original'],canonical=r['canonical'],sha256=actual))
assert not (E/'e15a-retaining.json').exists()
tmp=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/e15-tooltmp/retention')
owner=json.loads((tmp/'E15-owner.json').read_text())
assert owner['label']=='retention' and owner['evidence']==str(E)
assert {p.name for p in tmp.iterdir()}<={'E15-owner.json','._E15-owner.json'}
before=sample();shutil.rmtree(tmp)
out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    monitor_failure='FileNotFoundError: capture directory was removed between glob and stat after retention manifest completed. No retention rerun.',
    child_return_code='not captured by failed monitor; not invented',
    proof='Every manifest content hash round-tripped; all original paths absent; no pending retention journal.',
    files=len(rows),unique_canonical_files=len(unique),original_logical_bytes=sum(r['bytes'] for r in m['files']),
    unique_retained_logical_bytes=sum(unique.values()),rows=rows,temporary_owner=owner,temporary_cleaned=not tmp.exists(),
    before=before,after=sample())
(E/'retention-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print('retained',len(rows),'files;',len(unique),'canonical;',sum(unique.values()),'bytes; hash round-trip complete; owned temporary cleaned')
print('# E15 RETENTION AUDIT TAIL COMPLETE')
