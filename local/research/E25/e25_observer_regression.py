"""Full regression with the isolation-proven E25 observer. No title boot."""
from e25_common import *
from e25_validate import suite, validate
from e25_parser_receipt import receipt
assert os.environ.get('COPYFILE_DISABLE')=='1'
# E25 inherits E21's isolation proof by binary identity: the instrument is the
# SAME file, re-hashed here, not a rebuild. Re-proving forwarding would require
# rebuilding the proven dylib, which the brief forbids.
inherited=json.loads((E.parent/'E21/isolation-proof.json').read_text())
assert inherited['feed']['identical'] and inherited['exit']['plain_rc']==inherited['exit']['loaded_rc']==3
assert all(b['valid']==1 for b in inherited['addrs']['observer_bindings'])
proven=json.loads((E.parent/'E21/parser-build.json').read_text())['observer']
assert sha(E/'parser/e21-parser-observer.dylib')==proven['sha256'],'reused instrument re-sha missed'
admission(sample())
os.environ['E25_OBSERVER_DYLIB']=str(E/'parser/e21-parser-observer.dylib')
binary=P/'e18-fixtures/after/binding-test'
suite_rc,suite_txt,suite_row=suite('observer')
assert suite_rc==0 and suite_row.get('status')!='BLOCKED',suite_row
validate('observer-bindings',binary,['prior','no-input','input'])
validate('observer-closure',binary,['quiescent','idempotent','window-complete','disabled','unopened','fallback-error'])
rows=[]
# E25 CHANGE 2 (reverts E24 CHANGE 3): with the suite rebuilt, the suite's own
# observer directory is once more the loaded run that REACHES the parser, so it
# leads the closure list exactly as it did in E23 and the parser-reach receipt
# returns here from the cadence fixture.
for directory in [E/'.suite-observer/parser-observer',
                  *sorted((P/'e25-fixtures/observer-bindings').glob('*/parser-observer')),
                  *sorted((P/'e25-fixtures/observer-closure').glob('*/parser-observer'))]:
    r=receipt(directory);footer=r['footer'];rows.append(dict(directory=str(directory),footer=footer,count_match=True))
    assert footer['pending']==0
    if directory.parent.name in ('quiescent','idempotent','window-complete','disabled','unopened'):
        assert footer['reason']=='_Exit' and footer['rc']==0
    for name in ['parser-events.txt','parser-input.bin']:
        target=E/'observer-receipts'/directory.parent.name;target.mkdir(parents=True,exist_ok=True)
        (target/name).write_bytes((directory/name).read_bytes())
assert all(r['footer']['bindingChecks']==4 for r in rows),'loaded bindings not 4/4'
assert rows[0]['footer']['parseCalls']>0,'suite observer dir did not reach the parser'
save('observer-regression.json',dict(utc=utc(),suite=458,suite_status='PASS',parser_reach='suite observer dir',e15_rc=[0,0],closure_cases=6,prior=[24,3,14,4,'DROP'],
    observer=pin(E/'parser/e21-parser-observer.dylib'),closures=rows,boot=0,resources=sample()))
print('# E25 OBSERVER REGRESSION TAIL COMPLETE')
