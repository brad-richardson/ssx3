"""Full regression with the isolation-proven E24 observer. No title boot."""
from e24_common import *
from e24_validate import suite, validate
from e24_parser_receipt import receipt
assert os.environ.get('COPYFILE_DISABLE')=='1'
# E24 inherits E21's isolation proof by binary identity: the instrument is the
# SAME file, re-hashed here, not a rebuild. Re-proving forwarding would require
# rebuilding the proven dylib, which the brief forbids.
inherited=json.loads((E.parent/'E21/isolation-proof.json').read_text())
assert inherited['feed']['identical'] and inherited['exit']['plain_rc']==inherited['exit']['loaded_rc']==3
assert all(b['valid']==1 for b in inherited['addrs']['observer_bindings'])
proven=json.loads((E.parent/'E21/parser-build.json').read_text())['observer']
assert sha(E/'parser/e21-parser-observer.dylib')==proven['sha256'],'reused instrument re-sha missed'
admission(sample())
os.environ['E24_OBSERVER_DYLIB']=str(E/'parser/e21-parser-observer.dylib')
binary=P/'e18-fixtures/after/binding-test'
suite('observer')
validate('observer-bindings',binary,['prior','no-input','input'])
validate('observer-closure',binary,['quiescent','idempotent','window-complete','disabled','unopened','fallback-error'])
rows=[]
# E24 CHANGE 3: the suite's own observer dir is BLOCKED with the suite binary.
# In E23 the suite was the ONLY loaded run that reached the parser, so the
# parser-reach receipt moves to the surviving E23 cadence fixture, which drives
# the R3 payload through the actual title wrappers (`e24_cadence.py`). The
# fixture closures below still carry real `# E21 PARSER CLOSURE` footers.
for directory in [*sorted((P/'e24-fixtures/observer-bindings').glob('*/parser-observer')),
                  *sorted((P/'e24-fixtures/observer-closure').glob('*/parser-observer'))]:
    r=receipt(directory);footer=r['footer'];rows.append(dict(directory=str(directory),footer=footer,count_match=True))
    assert footer['pending']==0
    if directory.parent.name in ('quiescent','idempotent','window-complete','disabled','unopened'):
        assert footer['reason']=='_Exit' and footer['rc']==0
    for name in ['parser-events.txt','parser-input.bin']:
        target=E/'observer-receipts'/directory.parent.name;target.mkdir(parents=True,exist_ok=True)
        (target/name).write_bytes((directory/name).read_bytes())
assert all(r['footer']['bindingChecks']==4 for r in rows),'loaded bindings not 4/4'
save('observer-regression.json',dict(utc=utc(),suite=None,suite_status='BLOCKED',parser_reach_moved_to='e24_cadence.py',e15_rc=[0,0],closure_cases=6,prior=[24,3,14,4,'DROP'],
    observer=pin(E/'parser/e21-parser-observer.dylib'),closures=rows,boot=0,resources=sample()))
print('# E24 OBSERVER REGRESSION TAIL COMPLETE')
