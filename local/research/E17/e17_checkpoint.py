"""Reverify the protected E16 checkpoint without rebuilding or mutating it."""
import subprocess
from e17_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
old=json.loads((E/'expected/checkpoint.json').read_text())
paths=sorted([p for pattern in ['*.cpp','ps2_recompiled_*.h'] for p in (R/'ps2xRuntime/src/runner').glob(pattern) if not p.name.startswith('._')]+list((R/'ps2xRuntime/include').glob('ps2_recompiled_*.h')))
actual=[pin(p) for p in paths];expected=json.loads((E/'expected/generated.json').read_text())
assert len(actual)==9452 and {x['path']:x['sha256'] for x in actual}=={x['path']:x['sha256'] for x in expected}
save('before-generated.json',actual)
checks=[]
for r in old['inputs']+old['sources']+[old['main']]:
    n=pin(r['path']);n['unchanged']=n['sha256']==r['sha256'];checks.append(n);assert n['unchanged'],n
objects=json.loads((E/'expected/objects.json').read_text())
protected=[]
for p in sorted(B0.rglob('*')):
    if p.is_file() and (p.suffix=='.o' or p.name in ('ps2EntryRunner','ps2x_tests')):protected.append(pin(p))
save('protected-build-before.json',protected)
fixture=pin(P/'e16-fixtures/after/binding-test')
assert fixture['sha256']=='2089be52f52e1a6001cae902f78cc177b32669a46d8f96b70ff67d95bc45c94f'
assert pin(B0/'ps2xRuntime/ps2EntryRunner')['sha256']=='d9eb59012898545b84981a810c0b20ff78a6e4f60664774f660cecc2cadeed8d'
assert pin(B0/'ps2xTest/ps2x_tests')['sha256']=='8ba90048da7804a3dd278f172efbeb92d968ca89fd4ac9209b243e3d15c5a2eb'
for name in ['ssx3.toml','ssx3-functions.sweep.csv']:(E/('before-'+name)).write_bytes((R/'games/ssx3'/name).read_bytes())
save('checkpoint.json',dict(utc=utc(),generated_names=9452,all_hashes_equal=True,inputs_sources=checks,fixture=fixture,protected_build_files=len(protected),resources=sample()))
print('Checkpoint: 9452 names/hashes; all pinned inputs/source/binaries match; protected files',len(protected))
print('# E17 CHECKPOINT TAIL COMPLETE')
