import gzip, json, os, subprocess, sys
from pathlib import Path
from e16_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
label = sys.argv[1]
record = dict(utc=utc(), label=label, admission=sample())
save(label+'-admission.json', record)
admission(record['admission'])
commands = []
for args in [['rev-parse','HEAD','refs/remotes/fork/ssx3'], ['ls-remote','fork','refs/heads/ssx3'], ['status','--short']]:
    argv = ['git','-C',str(R)]+args
    p = subprocess.run(argv, capture_output=True, text=True)
    commands.append(dict(argv=argv, rc=p.returncode, stdout=p.stdout, stderr=p.stderr))
    assert p.returncode == 0, commands[-1]
save(label+'-fork.json', commands)
if label == 'before':
    assert commands[0]['stdout'].splitlines() == [BASE_SHA, BASE_SHA]
    assert commands[1]['stdout'].split()[0] == BASE_SHA
prior = E/'expected'
expected = json.loads((prior/'generated.json').read_text())
paths = list((R/'ps2xRuntime/src/runner').glob('*.cpp')) + list((R/'ps2xRuntime/src/runner').glob('ps2_recompiled_*.h')) + list((R/'ps2xRuntime/include').glob('ps2_recompiled_*.h'))
paths = sorted(p for p in paths if not p.name.startswith('._'))
actual = [pin(p) for p in paths]
save(label+'-generated.json', actual)
old = {x['path']:x['sha256'] for x in expected}; new = {x['path']:x['sha256'] for x in actual}
record['generated'] = dict(count=len(actual), names_equal=old.keys()==new.keys(), changed=[p for p in old if new.get(p)!=old[p]])
assert len(actual)==9452 and old==new, record['generated']
record['inputs'] = []
for x in json.loads((prior/'manifest.json').read_text())['inputs']:
    y = pin(x['path']); y['unchanged'] = y['sha256']==x['sha256']; record['inputs'].append(y); assert y['unchanged']
record['sources'] = []
for x in json.loads((prior/'source-audit.json').read_text())['sources']:
    p = Path(x['path']); p = p if p.is_absolute() else R/p
    y = pin(p); y['same_as_e15'] = y['sha256']==x['sha256']; record['sources'].append(y)
    if label=='before' or p.name!='ps2_runtime.cpp': assert y['same_as_e15'], y
record['main'] = pin(R/'ps2xRuntime/src/main.cpp')
assert record['main']['sha256']==__import__('hashlib').sha256(gzip.decompress((E/'sources/main.cpp.gz').read_bytes())).hexdigest()
record['fixture'] = pin(P/'e15-binding-tests/entry/binding-test')
assert record['fixture']['sha256']=='b0aefc016c69a0dd693093828bda828a1c7f9eaf36c17a38bb757763642321f2'
record['build_exists'] = B.exists()
record['source_sidecars'] = [str(p) for p in R.rglob('._*') if '.git' not in p.parts and p.suffix in ('.cpp','.c','.h','.hpp','.mm')]
record['globbed_sidecars'] = [p for p in record['source_sidecars'] if '/src/runner/' in p or '/src/lib/Kernel/' in p]
record['sidecar_policy'] = 'Existing sidecars retained; only runner and Kernel source globs are executable inputs. Verify compile_commands after configure.'
save(label+'-checkpoint.json', record)
assert not record['globbed_sidecars'], record['globbed_sidecars']
print(json.dumps({k:v for k,v in record.items() if k not in ('sources','inputs')},indent=2))
print('# E16 CHECKPOINT AUDIT TAIL COMPLETE')
