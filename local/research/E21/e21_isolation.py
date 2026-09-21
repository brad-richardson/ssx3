"""Isolation proof: 1:1 forwarding + byte-identical results + _Exit closure + address mechanism. No suite/title."""
import shutil
from e21_common import *
from e21_validate import logged
from e21_parser_receipt import receipt, fnv
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert (E/'parser-build.json').exists()
admission(sample())
harness=E/'parser/e21-isolation-test';dylib=E/'parser/e21-parser-observer.dylib'
incoming=E/'parser/authored-black.m2v'
assert harness.is_file() and dylib.is_file() and incoming.is_file()

def base_env():
    return {k:v for k,v in os.environ.items() if not k.startswith(('PS2X_','DYLD_'))}

ATTEMPT='a2'
def run_isolated(name, argv, *, loaded, proof=False):
    dest=P/'e21-fixtures/isolation'/ATTEMPT/name;dest.mkdir(parents=True,exist_ok=False)
    env=base_env()
    obsdir=None
    if loaded:
        obsdir=dest/'parser-observer';obsdir.mkdir(exist_ok=False)
        env.update(DYLD_INSERT_LIBRARIES=str(dylib),PS2X_E21_PARSER_DIR=str(obsdir))
        if proof:env['PS2X_E21_PROOF']='1'
    rc,txt,rec=logged(argv,env,dest,E/f'isolation-{name}.txt',120)
    rec.update(name=name,rc=rc,loaded=loaded,proof=proof)
    return dest,obsdir,rc,txt,rec

# A. feed determinism: uninstrumented vs observed, identical input.
plain,_po,rc0,_,rec0=run_isolated('feed-plain',[str(harness),'feed',str(incoming),str(P/'e21-fixtures/isolation'/ATTEMPT/'feed-plain/result.txt')],loaded=False)
assert rc0==0
assert 'FEED TAIL COMPLETE' in (plain/'result.txt').read_text()
fed,obs,rc1,_,rec1=run_isolated('feed-loaded',[str(harness),'feed',str(incoming),str(P/'e21-fixtures/isolation'/ATTEMPT/'feed-loaded/result.txt')],loaded=True,proof=True)
assert rc1==0
a=(plain/'result.txt').read_bytes();b=(fed/'result.txt').read_bytes()
assert a==b,(len(a),len(b))
r=receipt(obs,expect_proof=1,expect_exit=('destructor',0))
assert r['footer']['parseCalls']>0 and r['footer']['packets']>0 and r['footer']['receiveCalls']>0 and r['footer']['frames']>0
assert r['footer']['errors']==0
(E/'isolation-feed-record.txt').write_bytes(a)
shutil.copyfile(obs/'parser-events.txt',E/'isolation-feed-events.txt')
shutil.copyfile(obs/'parser-input.bin',E/'isolation-feed-input.bin')

# B. _Exit closure: same status both ways; loaded run closes with _Exit footer.
_,_,rc2,_,rec2=run_isolated('exit-plain',[str(harness),'exitcode','3'],loaded=False)
assert rc2==3
_,obs3,rc3,_,rec3=run_isolated('exit-loaded',[str(harness),'exitcode','3'],loaded=True)
assert rc3==3
rx=receipt(obs3,expect_proof=0,expect_exit=('_Exit',3))
assert rx['footer']['parseCalls']>=1
shutil.copyfile(obs3/'parser-events.txt',E/'isolation-exit-events.txt')

# C. address mechanism, both worlds.
_,_,rc4,txt4,rec4=run_isolated('addrs-plain',[str(harness),'addrs'],loaded=False)
assert rc4==0 and 'ADDRS TAIL COMPLETE' in txt4
_,obs5,rc5,txt5,rec5=run_isolated('addrs-loaded',[str(harness),'addrs'],loaded=True)
assert rc5==0 and 'ADDRS TAIL COMPLETE' in txt5
ra=receipt(obs5,expect_proof=0,expect_exit=('destructor',0))
bindings=[{k:r2[k] for k in ('api','nextIsReplacement','explicitIsReplacement','valid','image','symbol')} for r2 in ra['rows'] if r2['kind']=='binding']

save('isolation-proof.json',dict(utc=utc(),harness=pin(harness),observer=pin(dylib),incoming=pin(incoming),
    feed=dict(plain_bytes=len(a),loaded_bytes=len(b),identical=True,fnv64=hex(fnv(a)),footer=r['footer']),
    exit=dict(plain_rc=rc2,loaded_rc=rc3,footer=rx['footer']),
    addrs=dict(plain=txt4,loaded=txt5,observer_bindings=bindings),
    runs=[rec0,rec1,rec2,rec3,rec4,rec5],boot=0,resources=sample()))
print('feed identical bytes',len(a),'fnv',hex(fnv(a)),'footer',r['footer'])
print('exit rc',rc2,rc3,'footer',rx['footer'])
print('bindings',bindings)
print('# E21 ISOLATION PROOF TAIL COMPLETE')
