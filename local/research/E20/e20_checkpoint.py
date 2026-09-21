"""Read-only E18 checkpoint audit; no title launch or fork mutation."""
import gzip, subprocess
from e20_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
prior = E.parent/'E18'
commands = [['git','-C',str(R),'rev-parse','HEAD','refs/remotes/fork/ssx3'],
            ['git','-C',str(R),'ls-remote','fork','refs/heads/ssx3'],
            ['git','-C',str(R),'status','--short']]
receipts=[]
for command in commands:
    p=subprocess.run(command,text=True,capture_output=True,check=True)
    receipts.append(dict(argv=command,stdout=p.stdout,stderr=p.stderr,rc=p.returncode))
assert receipts[0]['stdout'].splitlines()==[BASE_SHA,BASE_SHA]
assert receipts[1]['stdout'].split()[0]==BASE_SHA
assert receipts[2]['stdout']=='?? ps2_log.txt\n'
save('fork-before.json',dict(utc=utc(),commands=receipts))
expected=json.loads((prior/'before-generated.json').read_text())
actual=[pin(p) for p in sorted((R/'ps2xRuntime/src/runner').iterdir())
        if p.suffix in ('.cpp','.h') and not p.name.startswith('._')]
assert len(actual)==9457
assert {p['path']:p['sha256'] for p in actual}=={p['path']:p['sha256'] for p in expected}
save('before-generated.json',actual)
end=json.loads((prior/'final-audit.json').read_text())
sources=[]
(E/'sources').mkdir(exist_ok=False)
for item in end['inputs_sources']+end['behavior_sources']:
    p=pin(item['path']);assert p['sha256']==item['sha256'],p
    sources.append(p)
    with gzip.open(E/'sources'/('before-'+Path(p['path']).name+'.gz'),'wb') as f:
        f.write(Path(p['path']).read_bytes())
protected=[]
for build in [Path('/tmp/p1-link/runtime'),Path('/tmp/e17-map-link/runtime'),B]:
    assert build.is_dir()
    for p in sorted(build.rglob('*')):
        if p.is_file() and (p.suffix in ('.o','.a','.pch') or p.name in ('ps2EntryRunner','ps2x_tests')):
            protected.append(pin(p))
save('protected-build-before.json',protected)
for key in ['runner','suite','fixture']:
    assert pin(end[key]['path'])['sha256']==end[key]['sha256'],key
allocated={}
for root in [R/'.git',R/'ps2xRuntime/src/lib/Kernel/Stubs',R/'ps2xTest/src']:
    for p in [root,*root.rglob('*')]:
        try:allocated[str(p)]=p.lstat().st_blocks*512
        except FileNotFoundError:pass
save('fork-allocation-before.json',dict(utc=utc(),allocated=allocated))
s=sample();admission(s)
save('checkpoint.json',dict(utc=utc(),fork=BASE_SHA,generated_names=9457,all_generated_hashes_match=True,
    inputs_sources=sources,protected_build_files=len(protected),runner=end['runner'],suite=end['suite'],
    fixture=end['fixture'],fixture_reused=True,resources=s))
print('9457 generated hashes; protected files',len(protected),'; E18 binaries and source hashes agree.')
print('# E20 CHECKPOINT TAIL COMPLETE')
