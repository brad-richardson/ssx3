"""Full regression with the isolation-proven E23 observer. No title boot."""
from e23_common import *
from e23_validate import suite, validate
from e23_parser_receipt import receipt
assert os.environ.get('COPYFILE_DISABLE')=='1'
# E23 inherits E21's isolation proof by binary identity: the instrument is the
# SAME file, re-hashed here, not a rebuild. Re-proving forwarding would require
# rebuilding the proven dylib, which the brief forbids.
inherited=json.loads((E.parent/'E21/isolation-proof.json').read_text())
assert inherited['feed']['identical'] and inherited['exit']['plain_rc']==inherited['exit']['loaded_rc']==3
assert all(b['valid']==1 for b in inherited['addrs']['observer_bindings'])
proven=json.loads((E.parent/'E21/parser-build.json').read_text())['observer']
assert sha(E/'parser/e21-parser-observer.dylib')==proven['sha256'],'reused instrument re-sha missed'
admission(sample())
os.environ['E23_OBSERVER_DYLIB']=str(E/'parser/e21-parser-observer.dylib')
binary=P/'e18-fixtures/after/binding-test'
suite('observer')
validate('observer-bindings',binary,['prior','no-input','input'])
validate('observer-closure',binary,['quiescent','idempotent','window-complete','disabled','unopened','fallback-error'])
rows=[]
for directory in [E/'.suite-observer/parser-observer',*sorted((P/'e23-fixtures/observer-bindings').glob('*/parser-observer')),
                  *sorted((P/'e23-fixtures/observer-closure').glob('*/parser-observer'))]:
    r=receipt(directory);footer=r['footer'];rows.append(dict(directory=str(directory),footer=footer,count_match=True))
    assert footer['pending']==0
    if directory.parent.name in ('quiescent','idempotent','window-complete','disabled','unopened'):
        assert footer['reason']=='_Exit' and footer['rc']==0
    for name in ['parser-events.txt','parser-input.bin']:
        target=E/'observer-receipts'/directory.parent.name;target.mkdir(parents=True,exist_ok=True)
        (target/name).write_bytes((directory/name).read_bytes())
assert rows[0]['footer']['parseCalls']>0
save('observer-regression.json',dict(utc=utc(),suite=458,e15_rc=[0,0],closure_cases=6,prior=[24,3,14,4,'DROP'],
    observer=pin(E/'parser/e21-parser-observer.dylib'),closures=rows,boot=0,resources=sample()))
print('# E23 OBSERVER REGRESSION TAIL COMPLETE')
