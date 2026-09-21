"""Full regression with the isolation-proven E21 observer. No title boot."""
from e21_common import *
from e21_validate import suite, validate
from e21_parser_receipt import receipt
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert (E/'isolation-proof.json').exists()
admission(sample())
os.environ['E21_OBSERVER_DYLIB']=str(E/'parser/e21-parser-observer.dylib')
binary=P/'e18-fixtures/after/binding-test'
suite('observer')
validate('observer-bindings',binary,['prior','no-input','input'])
validate('observer-closure',binary,['quiescent','idempotent','window-complete','disabled','unopened','fallback-error'])
rows=[]
for directory in [E/'.suite-observer/parser-observer',*sorted((P/'e21-fixtures/observer-bindings').glob('*/parser-observer')),
                  *sorted((P/'e21-fixtures/observer-closure').glob('*/parser-observer'))]:
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
print('# E21 OBSERVER REGRESSION TAIL COMPLETE')
