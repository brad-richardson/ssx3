#!/usr/bin/env python3
"""Pin the tested new binary and fork state for guarded pre-claim verification."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
E=Path(__file__).resolve().parent
R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert not (E/'e13a-build.json').exists()
gate=json.loads((E/'entry-preflight.json').read_text())
assert gate['binding_rc']==gate['suite_rc']==0
commit=json.loads((E/'fork-commit.json').read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def git(*args):
    p=subprocess.run(['git','-C',str(R),*args],capture_output=True,text=True);assert p.returncode==0
    return p.stdout
record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),fork_head=git('rev-parse','HEAD').strip(),
            fork_status=git('status','--short'),test_count=452)
assert record['fork_head']==commit['head']
for key,path in [('bin','ps2xRuntime/ps2EntryRunner'),('test','ps2xTest/ps2x_tests')]:
    p=Path('/tmp/p1-link/runtime')/path;record[key+'_size']=p.stat().st_size;record[key+'_sha']=sha(p)
(E/'e13a-build.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
print('# E13 BUILD IDENTITY TAIL COMPLETE')
