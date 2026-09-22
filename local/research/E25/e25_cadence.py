"""Complete-feed demand-cadence reference: sweep authored prefixes on the actual wrappers."""
from e25_common import *
from e25_validate import validate, logged
from e25_parser_receipt import receipt
from e25_mine import fixture_cadence, parse_table
assert os.environ.get('COPYFILE_DISABLE')=='1'
proven=json.loads((E.parent/'E21/parser-build.json').read_text())['observer']
assert sha(E/'parser/e21-parser-observer.dylib')==proven['sha256'],'reused instrument re-sha missed'
admission(sample())
binary=P/'e23-fixtures/complete/binding-test'
os.environ['E25_OBSERVER_DYLIB']=str(E/'parser/e21-parser-observer.dylib')

# Control 1: the NEW binary must reproduce every carried fixture receipt, so the
# only behavioural difference from the checkpoint binary is the added mode.
validate('newbin-bindings',binary,['prior','no-input','input'])
validate('newbin-closure',binary,['quiescent','idempotent','window-complete','disabled','unopened','fallback-error'])

rows=[]
for bytes_fed in (60,120,180,240):
    dest=P/'e25-fixtures/cadence'/str(bytes_fed);dest.mkdir(parents=True,exist_ok=False)
    env={k:v for k,v in os.environ.items() if not k.startswith(('PS2X_','DYLD_'))}
    env.update(PS2X_E15_TRACE='1',PS2X_E7_DIR=str(dest),
               DYLD_INSERT_LIBRARIES=str(E/'parser/e21-parser-observer.dylib'),
               PS2X_E21_PARSER_DIR=str(dest/'parser-observer'))
    (dest/'parser-observer').mkdir(exist_ok=False)
    rc,txt,rec=logged([str(binary),'complete',str(bytes_fed)],env,dest,E/f'cadence-{bytes_fed}.txt')
    assert rc==0 and '# E23 COMPLETE FEED FIXTURE TAIL COMPLETE' in txt,(bytes_fed,rc)
    tapfile=dest/'e7-events.txt'
    (E/f'cadence-{bytes_fed}-events.txt').write_text(tapfile.read_text())
    cadence=fixture_cadence(tapfile)
    parser=parse_table(dest/'parser-observer')
    line=next(l for l in txt.splitlines() if l.startswith('CADENCE '))
    fields={k:(int(v,0) if v.lstrip('-').replace('0x','').isalnum() and not v.isalpha() else v)
            for k,v in (x.split('=',1) for x in line.split() if '=' in x)}
    outcome='SERVED' if 'outcome=SERVED' in txt else 'STALLED'
    rows.append(dict(feedBytes=bytes_fed,rc=rc,outcome=outcome,stdout=fields,
                     cadence={k:v for k,v in cadence.items() if k!='sequence'},
                     sequence=cadence['sequence'],parser=parser,run=rec))
    save('cadence.json',dict(utc=utc(),binary=pin(binary),observer=pin(E/'parser/e21-parser-observer.dylib'),rows=rows))
    print(f"FEED {bytes_fed:>3} -> {outcome:8} producerFirings={cadence['producerFirings']} addBs={cadence['addBs']} "
          f"completions={cadence['completions']} matched={cadence['completionsMatched']} parks={cadence['parks']} "
          f"parseCalls={parser['footer']['parseCalls']} packets={parser['footer']['packets']} frames={parser['footer']['frames']}",flush=True)
save('cadence-complete.json',dict(utc=utc(),cases=len(rows),boot=0,resources=sample()))
print('# E25 CADENCE TAIL COMPLETE')
