#!/usr/bin/env python3
"""Read-only reproduction from retained captures; never runs the guest."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parent
assert os.environ.get('COPYFILE_DISABLE')=='1'
names=['e12a-summary.json','e12a-card.json','e12a-progress.json','e12a-frame.json',
       'e12a-join.json','e12a-copy-content-join.json','e12a-residual-join.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={name:sha(E/name) for name in names}
steps=[]
for script,args in [('e12_mine.py',['a']),('e12_card.py',['a']),('e12_progress.py',['a']),
                    ('e12_frame.py',['a']),('e12_join.py',[]),('e12_residual.py',[])]:
    argv=[sys.executable,'-B',str(E/script),*args]
    p=subprocess.run(argv,capture_output=True,text=True)
    (E/('rerun-'+script.removesuffix('.py')+'.txt')).write_text(p.stdout+p.stderr)
    steps.append(dict(argv=argv,rc=p.returncode,tail=p.stdout.splitlines()[-1:]));assert p.returncode==0,(script,p.stderr)
after={name:sha(E/name) for name in names}
assert before==after,(before,after)
(E/'reproduction.json').write_text(json.dumps(dict(steps=steps,before=before,after=after,all_identical=True),indent=2)+'\n')
print('6 miners rerun from retained captures; all7 joined outputs byte-identical')
print('# E12 REPRODUCTION TAIL COMPLETE')
