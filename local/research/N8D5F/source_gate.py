#!/usr/bin/env python3
"""Check N8D5F source isolation and the exact pinned PNG writer hunk."""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path('/home/brad/n8d5f')
base = Path('/home/brad/n8b1')
pins = {
    'backend': (root/'PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp',
                '4e3efc51d8d104ab5d3c537076e85c6cfcd8344c8e6c147de02f5a5015c8f1e5'),
    'header': (root/'parallel-gs/gs/n8d5_tile_spirv.hpp',
               '19b9ba5fc747d8fcb70d712b86bd5738c64424ceb15c24d4b5ed58219f71bac9'),
    'writer': (root/'PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp',
               '358d726bf39e319b906e7e15407e1bf361cd2cdbdd8e79d4a96b25a9588c3f96'),
    'codegen': (base/'codegen-ssx3/register_functions.cpp',
                '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'),
}

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024*1024), b''):
            h.update(part)
    return h.hexdigest()

out = {'files': {}, 'source_diff': {}}
for name, (path, expected) in pins.items():
    reads = [sha(path), sha(path)]
    assert reads == [expected, expected], f'{name} SHA mismatch {reads}'
    out['files'][name] = {'path': str(path), 'sha': reads, 'bytes': path.stat().st_size}

for name, left, right, wanted in [
    ('fork', base/'PS2Recomp', root/'PS2Recomp',
     ['ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp',
      'ps2xRuntime/src/lib/ps2_runtime.cpp']),
    ('parallel', base/'parallel-gs', root/'parallel-gs', ['gs/n8d5_tile_spirv.hpp']),
    ('jni', Path('/home/brad/n8d5d/jniLibs'), root/'jniLibs', []),
]:
    cmd = ['diff', '-rq', '--exclude=.cxx', '--exclude=build', '--exclude=.gradle']
    if name == 'fork':
        cmd.append('--exclude=runner')
    proc = subprocess.run(cmd + [str(left), str(right)], text=True, capture_output=True)
    assert proc.returncode in (0, 1), f'{name} diff error {proc.stderr}'
    lines = sorted(proc.stdout.splitlines())
    expected = sorted(
        (f'Only in {(right/p).parent}: {(right/p).name}' if name == 'parallel' else
         f'Files {left/p} and {right/p} differ') for p in wanted
    )
    assert lines == expected, f'{name} differs: actual {lines}; expected {expected}'
    out['source_diff'][name] = lines

left = base/'PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp'
right = pins['writer'][0]
proc = subprocess.run(['diff', '-U3', str(left), str(right)], text=True, capture_output=True)
assert proc.returncode == 1 and not proc.stderr, f'writer diff failed: {proc.stderr}'
hunk = '\n'.join(proc.stdout.splitlines()[2:]) + '\n'
hunk_sha = hashlib.sha256(hunk.encode()).hexdigest()
assert hunk.count('@@ ') == 1, 'writer has more than one diff hunk'
assert hunk_sha == '64b584851662ae0ddbdf003cca89057b07ac0f0640bcf22d60497865f44fa4ff', f'writer hunk SHA {hunk_sha}'
out['writer_hunk_sha'] = hunk_sha
out['writer_diff'] = proc.stdout
out['size_bytes'] = int(subprocess.check_output(['du', '-sb', str(root)], text=True).split()[0])
assert out['size_bytes'] < 10*1024**3, 'WSL scratch exceeds 10 GiB'
out['status'] = 'pass'
print(json.dumps(out, indent=2))
