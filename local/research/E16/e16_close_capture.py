#!/usr/bin/env python3
"""Measure closed capture sizes (including shutdown flush) before retention."""
import datetime, hashlib, json, os, subprocess
from pathlib import Path
from e16_capture import size

E=Path(__file__).resolve().parent
assert os.environ.get('COPYFILE_DISABLE')=='1'
c=json.loads((E/'e16a-config.json').read_text())
paths={k:Path(v) for k,v in c['paths'].items()}
paths['function_log']=paths['function_log'].with_name('ps2_log-e16a-1.txt')
assert not Path('/tmp/ssx3-p-lane-lease').exists()
p=subprocess.run(['pgrep','-x','ps2EntryRunner'],text=True,capture_output=True)
assert p.returncode==1, (p.returncode,p.stdout,p.stderr)
rows=[]
for k,path in paths.items():
    n=size(path);a=size(path,True)
    assert n<c['caps'][k] and a<c['allocated_caps'][k]
    rows.append(dict(group=k,path=str(path),logical=n,allocated=a,logical_cap=c['caps'][k],allocated_cap=c['allocated_caps'][k]))
n=sum(r['logical'] for r in rows);a=sum(r['allocated'] for r in rows)
assert n<c['caps']['aggregate'] and a<c['allocated_caps']['aggregate']
with paths['trace'].open('rb') as f:lines=sum(1 for _ in f)
assert lines<c['caps']['progress_lines']
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),lease_absent=True,pgrep_rc=p.returncode,
       groups=rows,logical_aggregate=n,allocated_aggregate=a,trace_lines=lines,all_caps_pass=True)
(E/'e16a-closed-caps.json').write_text(json.dumps(r,indent=2)+'\n')
with (E/'e16a-raw-tails.txt').open('w') as out:
    for k in ['boot_log','trace','function_log']:
        with paths[k].open('rb') as f:
            f.seek(max(0,paths[k].stat().st_size-8192));data=f.read()
        out.write(f'## {k}; complete newline={data.endswith(bytes([10]))}\n')
        out.write('\n'.join(data.decode(errors='replace').splitlines()[-8:])+'\n')
    out.write('# E16 RAW TAILS COMPLETE\n')
print('closed logical',n,'allocated',a,'trace lines',lines)
print('# E16 CLOSED CAPS TAIL COMPLETE')
