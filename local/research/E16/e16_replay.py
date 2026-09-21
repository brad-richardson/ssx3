"""Replay every boot join from retained canonical inputs, without SSD captures."""
import os, subprocess, sys
from e16_common import E, save, sha, utc

assert os.environ.get('E16_CANONICAL_ONLY')=='1'
outputs=['e16a-mpeg.json','e16a-graphics.json','e16a-observation-closure.json',
         'e16a-card.json','e16a-card-events.json','e16a-lifetime.json',
         'e16a-progress.json','e16a-function-census.json','function-owner-alias-audit.json']
before={name:sha(E/name) for name in outputs}
commands=[]
for script,args in [('e16_mine.py',[]),('e16_card.py',['a']),('e16_lifetime.py',[]),
                    ('e16_progress.py',['a']),('e16_alias_audit.py',[])]:
    argv=[sys.executable,'-B',str(E/script)]+args
    log=E/('replay-'+script.removesuffix('.py')+'.txt')
    with log.open('w') as out:
        p=subprocess.run(argv,stdout=out,stderr=subprocess.STDOUT,timeout=120)
    commands.append(dict(argv=argv,rc=p.returncode,stdout=log.name,stdout_bytes=log.stat().st_size))
    assert p.returncode==0 and log.stat().st_size<1024**2,commands[-1]
after={name:sha(E/name) for name in outputs}
assert before==after,[(k,before[k],after[k]) for k in before if before[k]!=after[k]]
save('canonical-replay.json',dict(utc=utc(),canonical_only=True,commands=commands,
     outputs=[dict(path=name,sha256=before[name],identical=True) for name in outputs]))
print('Five canonical-only miners returned 0; all nine analysis outputs are byte-identical.')
print('# E16 CANONICAL REPLAY TAIL COMPLETE')
