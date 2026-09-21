#!/usr/bin/env python3
"""Read-only reproduction from retained captures; never runs the guest."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parent
assert os.environ.get('COPYFILE_DISABLE')=='1'
names=['e13a-summary.json','e13a-card.json','e13a-progress.json','e13a-frame.json',
       'e13a-join.json','e13a-copy-content-join.json','e13a-residual-join.json','e13a-observation-closure.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={name:sha(E/name) for name in names}
steps=[]
for script,args in [('e13_observation_audit.py',[]),('e13_mine.py',['a']),('e13_card.py',['a']),('e13_progress.py',['a']),
                    ('e13_frame.py',['a']),('e13_join.py',[]),('e13_residual.py',[])]:
    argv=[sys.executable,'-B',str(E/script),*args]
    p=subprocess.run(argv,capture_output=True,text=True)
    (E/('rerun-'+script.removesuffix('.py')+'.txt')).write_text(p.stdout+p.stderr)
    steps.append(dict(argv=argv,rc=p.returncode,tail=p.stdout.splitlines()[-1:]));assert p.returncode==0,(script,p.stderr)
after={name:sha(E/name) for name in names}
assert before==after,(before,after)
(E/'reproduction.json').write_text(json.dumps(dict(steps=steps,before=before,after=after,all_identical=True),indent=2)+'\n')
print('7 miners rerun from retained captures; all8 joined outputs byte-identical')
print('# E13 REPRODUCTION TAIL COMPLETE')
