"""Reverify the E17 checkpoint and protect both retained builds before edits."""
import gzip
from e18_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
prior = E.parent/'E17'
expected = json.loads((prior/'after-generated.json').read_text())
actual = [pin(p) for p in sorted((R/'ps2xRuntime/src/runner').iterdir())
          if p.suffix in ('.cpp','.h') and not p.name.startswith('._')]
assert len(actual) == 9457
assert {r['path']:r['sha256'] for r in actual} == {r['path']:r['sha256'] for r in expected}
save('before-generated.json', actual)
sources = []
for item in json.loads((prior/'final-source-audit.json').read_text())['inputs_sources']:
    row = pin(item['path']); assert row['sha256'] == item['sha256'], row
    sources.append(row)
for name in ['ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp',
             'ps2xRuntime/src/lib/Kernel/Stubs/MPEG.h',
             'ps2xRuntime/src/lib/Kernel/EeScheduler.cpp',
             'ps2xRuntime/include/runtime/ee_scheduler.h',
             'ps2xTest/src/ps2_runtime_expansion_tests.cpp']:
    path = R/name
    if not any(row['path'] == str(path) for row in sources): sources.append(pin(path))
(E/'sources').mkdir()
for row in sources:
    path = Path(row['path'])
    with gzip.open(E/'sources'/('before-'+path.name+'.gz'), 'wb') as f: f.write(path.read_bytes())
protected = []
for build in [Path('/tmp/p1-link/runtime'), B0]:
    assert build.is_dir()
    for path in sorted(build.rglob('*')):
        if path.is_file() and (path.suffix in ('.o','.a','.pch') or path.name in ('ps2EntryRunner','ps2x_tests')):
            protected.append(pin(path))
save('protected-build-before.json', protected)
expected_bins = json.loads((prior/'built-binaries.json').read_text())
bins = [pin(B0/'ps2xRuntime/ps2EntryRunner'),pin(B0/'ps2xTest/ps2x_tests')]
# E17's standalone final audit pins the exact protected runner and suite.
end = json.loads((prior/'final-audit.json').read_text())
assert bins[0]['sha256'] == end['runner']['sha256']
assert bins[1]['sha256'] == end['suite']['sha256']
fixture = pin(P/'e17-fixtures/after/binding-test')
assert fixture['sha256'] == end['fixture']['sha256']
allocated = {}
for root in [R/'.git',R/'ps2xRuntime/src/lib/Kernel/Stubs',R/'ps2xTest/src']:
    for path in [root,*root.rglob('*')]:
        try: allocated[str(path)] = path.lstat().st_blocks*512
        except FileNotFoundError: pass
save('fork-allocation-before.json',dict(utc=utc(),allocated=allocated))
resources = sample(); admission(resources)
save('checkpoint.json',dict(utc=utc(),fork=BASE_SHA,generated_names=9457,
    all_generated_hashes_match=True,inputs_sources=sources,protected_build_files=len(protected),
    binaries=bins,fixture=fixture,fixture_reused=True,resources=resources))
print('Checkpoint9457 names/hashes; protected build files',len(protected),'; E17 runner/suite/fixture hashes match.')
print('# E18 CHECKPOINT TAIL COMPLETE')
