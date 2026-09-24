#!/usr/bin/env python3
"""Check the two transferred source files and private snapshot isolation."""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path('/home/brad/n8d5d')
base = Path('/home/brad/n8b1')
files = {
    'backend': (root/'PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp',
                '4e3efc51d8d104ab5d3c537076e85c6cfcd8344c8e6c147de02f5a5015c8f1e5'),
    'header': (root/'parallel-gs/gs/n8d5_tile_spirv.hpp',
               '19b9ba5fc747d8fcb70d712b86bd5738c64424ceb15c24d4b5ed58219f71bac9'),
}

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

out = {'files': {}, 'source_diff': {}, 'size_bytes': 0}
for name, (path, expected) in files.items():
    reads = [sha(path), sha(path)]
    assert reads == [expected, expected], f'{name} SHA mismatch {reads}'
    out['files'][name] = {'path': str(path), 'sha': reads, 'bytes': path.stat().st_size}

for name, left, right, allowed in [
    ('fork', base/'PS2Recomp', root/'PS2Recomp',
     'ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp'),
    ('parallel', base/'parallel-gs', root/'parallel-gs',
     'gs/n8d5_tile_spirv.hpp'),
    ('jni', Path('/home/brad/n8d3/jniLibs'), root/'jniLibs', None),
]:
    cmd = ['diff', '-rq', '--exclude=.cxx', '--exclude=build', '--exclude=.gradle']
    if name == 'fork':
        cmd.append('--exclude=runner')
    proc = subprocess.run(cmd + [str(left), str(right)], text=True, capture_output=True)
    assert proc.returncode in (0, 1), f'{name} diff error {proc.stderr}'
    lines = proc.stdout.splitlines()
    if allowed is None:
        assert not lines, f'{name} differs: {lines}'
    else:
        assert len(lines) == 1 and allowed.split('/')[-1] in lines[0], f'{name} differs: {lines}'
        if name == 'parallel':
            assert lines[0] == f'Only in {(right/allowed).parent}: {(right/allowed).name}', f'{name} wrong file: {lines}'
        else:
            assert str(right/allowed) in lines[0], f'{name} wrong file: {lines}'
    out['source_diff'][name] = lines

du = subprocess.check_output(['du', '-sb', str(root)], text=True)
out['size_bytes'] = int(du.split()[0])
assert out['size_bytes'] < 10 * 1024**3, f'WSL scratch over cap: {out["size_bytes"]}'
out['status'] = 'pass'
print(json.dumps(out, indent=2))
