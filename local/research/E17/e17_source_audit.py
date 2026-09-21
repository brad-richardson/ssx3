"""Audit only authorized CSV/generated delta and preserve the E16 checkpoint."""
import gzip,re,sys
from e17_common import *
label=sys.argv[1]
inputs=[]
for r in json.loads((E/'checkpoint.json').read_text())['inputs_sources']:
    p=Path(r['path']);n=pin(p)
    if p==R/'games/ssx3/ssx3-functions.sweep.csv':assert n['sha256']=='7c827add09aeea837e25f6048007ab91e65eb4b5f7a98f8fb4f448b606cfb9ba'
    else:assert n['sha256']==r['sha256'],str(p)
    inputs.append(n)
expected=json.loads((E/'after-generated.json').read_text())
actual=[pin(p) for p in sorted(R.joinpath('ps2xRuntime/src/runner').iterdir()) if p.suffix in ('.cpp','.h') and not p.name.startswith('._')]
assert len(actual)==9457 and {r['path']:r['sha256'] for r in actual}=={r['path']:r['sha256'] for r in expected}
protected=json.loads((E/'protected-build-before.json').read_text())
for r in protected:assert sha(r['path'])==r['sha256'],r['path']
def slots(data):return {int(pc,16):sym.decode().strip() for sym,pc in re.findall(rb'= ([^;]+); // 0x([0-9a-f]+)',data)}
a=slots(gzip.decompress((E/'sources/registry-active-base.cpp.gz').read_bytes()));b=slots((R/'ps2xRuntime/src/runner/register_functions.cpp').read_bytes())
delta=[dict(pc=hex(pc),before=a.get(pc),after=b.get(pc)) for pc in sorted(set(a)|set(b)) if a.get(pc)!=b.get(pc)]
starts={r['start'] for r in json.loads((E/'row-verification.json').read_text())['rows']}
assert {r['pc'] for r in delta if r['before'] is None}==starts,delta
interior=[r for r in delta if r['before'] is not None]
assert {r['pc'] for r in interior}=={'0x14f2c8','0x14f31c'}
assert all(r['before']=='sub_0014F250_0x14f250' and r['after']=='sub_0014F2A8_0x14f2a8' for r in interior)
receipt=json.loads((E/'i12-interior-slot-receipt.json').read_text())
assert all(any(row['text'].endswith('// '+r['pc']) and r['after'] in row['text'] for row in receipt['rows']) for r in interior)
record=dict(utc=utc(),generated_names=9457,all_generated_hashes_match=True,protected_build_files=len(protected),protected_build_unchanged=True,inputs_sources=inputs,registry_active_delta=delta,all_five_new_exact_slots=True,interior_aliases_match_I12=True,resources=sample())
save(label+'-source-audit.json',record)
print('Generated9457; protected554 unchanged; five formerly empty slots plus two I12-matched interior aliases.')
print('# E17 SOURCE AUDIT TAIL COMPLETE '+label)
