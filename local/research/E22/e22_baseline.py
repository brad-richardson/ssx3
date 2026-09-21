"""Baseline suite and actual-linked fixtures; no ELF/title boot."""
from e22_common import *
from e22_validate import suite, validate, logged
assert os.environ.get('COPYFILE_DISABLE')=='1'
admission(sample())
binary=P/'e18-fixtures/after/binding-test'
suite('checkpoint')
validate('checkpoint-bindings',binary,['prior','no-input','input'])
validate('checkpoint-closure',binary,['quiescent','idempotent','window-complete','disabled','unopened','fallback-error'])
rows=[]
cases=[('presence-'+hex(pc),['check-present',hex(pc)]) for pc in (0x14f2a8,0x156750,0x243a80,0x395730,0x3a0158)]
cases += [(x,[x]) for x in ('ownership-queued-ready','ownership-queued-park','ownership-current')]
for name,args in cases:
    cwd=P/'e22-fixtures/checkpoint-extra'/name;cwd.mkdir(parents=True,exist_ok=False)
    env={k:v for k,v in os.environ.items() if not k.startswith('PS2X_')}
    rc,txt,rec=logged([str(binary),*args],env,cwd,E/f'checkpoint-{name}.txt')
    rec.update(mode=name,rc=rc);rows.append(rec);save('checkpoint-extra-validation.json',dict(binary=pin(binary),cases=rows))
    assert rc==0 and ('E17 PRESENCE CHECK TAIL COMPLETE success=1' if name.startswith('presence') else '# E18 OWNERSHIP FIXTURE TAIL COMPLETE boot=0') in txt
save('checkpoint-complete.json',dict(utc=utc(),suite=458,closure_cases=6,prior=[24,3,14,4,'DROP'],e15_rc=[0,0],extra_cases=8,boot=0,resources=sample()))
print('# E22 CHECKPOINT REGRESSION TAIL COMPLETE')
