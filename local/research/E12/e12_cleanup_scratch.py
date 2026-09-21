#!/usr/bin/env python3
"""Remove owned completed scratch only after every emitted byte is installed."""
import datetime,hashlib,json,os,shutil,subprocess
from pathlib import Path
E=Path(__file__).resolve().parent;OUT=Path('/tmp/ssx3-e12-predicate-codegen')
R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp');DEST=R/'ps2xRuntime/src/runner'
assert os.environ.get('COPYFILE_DISABLE')=='1'
owner=json.loads((OUT/'E12-owner.json').read_text());assert owner['evidence']==str(E)
assert json.loads((E/'entry-generation.json').read_text())['rc']==0
assert (E/'entry-installation.json').exists()
kept=[]
for row in json.loads((E/'entry-output.json').read_text()):
    if not row['name'].endswith(('.cpp','.h')):continue
    p=DEST/row['name']
    with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    assert sha==row['sha256'],row['name']
    kept.append(dict(path=str(p),sha256=sha,bytes=p.stat().st_size))
def df():return subprocess.run(['df','-k',str(R),'/private/tmp'],text=True,capture_output=True).stdout
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),marker=owner,retained_installed=kept,
       free_before=shutil.disk_usage('/private/tmp').free,df_before=df(),
       logical_removed=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file()),
       allocated_removed=sum(p.stat().st_blocks*512 for p in OUT.iterdir() if p.is_file()))
shutil.rmtree(OUT)
r.update(scratch_absent=not OUT.exists(),free_after=shutil.disk_usage('/private/tmp').free,df_after=df())
(E/'scratch-cleanup.json').write_text(json.dumps(r,indent=2)+'\n')
print('installed hashes',len(kept),'scratch absent',r['scratch_absent'],'internal free',r['free_after'])
print('# E12 SCRATCH CLEANUP TAIL COMPLETE')
