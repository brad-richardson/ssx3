#!/usr/bin/env python3
"""Compare the N8D7H snapshot with N8D6B, excluding generated caches.

Expected: exactly one fork backend plus the three overlaid G43 files differ;
jniLibs identical. Double-read each overlay SHA and every canonical pin.
"""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path('/home/brad/n8d7h')
base = Path('/home/brad/n8d6b')
backend = 'ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp'
stages = {'gs/gs_interface.hpp', 'gs/gs_renderer.hpp', 'gs/gs_renderer.cpp'}

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024*1024), b''):
            h.update(part)
    return h.hexdigest()

def tree_diff(left, right, fork=False):
    excluded = {'.cxx', 'build', '.gradle'}
    if fork:
        excluded.add('runner')
    def files(path):
        return {str(p.relative_to(path)) for p in path.rglob('*')
                if p.is_file() and not any(x in excluded for x in p.relative_to(path).parts)}
    la, rb = files(left), files(right)
    assert la == rb, f'file set mismatch added={sorted(rb-la)} removed={sorted(la-rb)}'
    return sorted(p for p in la if sha(left/p) != sha(right/p))

out = {'diff': {}, 'sha': {}, 'status': 'pending'}
out['diff']['fork'] = tree_diff(base/'PS2Recomp', root/'PS2Recomp', True)
out['diff']['parallel'] = tree_diff(base/'parallel-gs', root/'parallel-gs')
out['diff']['jniLibs'] = tree_diff(base/'jniLibs', root/'jniLibs')
assert out['diff'] == {'fork': [backend], 'parallel': sorted(stages), 'jniLibs': []}, out['diff']

pins = {
    'backend': (root/'PS2Recomp'/backend, 'c6135b3ce986504ada7826a56f7a3d411a76690f9ca7dd80d918a3666d4fb41f'),
    'g43_interface': (root/'parallel-gs/gs/gs_interface.hpp', '3a1751b4a708a56827af3e97ef32034349311d0c7fa2f59e4691700f05954d9d'),
    'g43_renderer_hpp': (root/'parallel-gs/gs/gs_renderer.hpp', 'fae3261aebb243214e08db51ac60df9d527e56cbcd0378c8603003e0a93a401a'),
    'g43_renderer_cpp': (root/'parallel-gs/gs/gs_renderer.cpp', '85c29cb01b04c8fefdf4fffba8dbbd953293c9de682d0443437e0b91de3de77e'),
    'writer': (root/'PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp', '358d726bf39e319b906e7e15407e1bf361cd2cdbdd8e79d4a96b25a9588c3f96'),
    'shader_header': (root/'parallel-gs/gs/n8d5_tile_spirv.hpp', '19b9ba5fc747d8fcb70d712b86bd5738c64424ceb15c24d4b5ed58219f71bac9'),
    'codegen': (Path('/home/brad/n8b1/codegen-ssx3/register_functions.cpp'), '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'),
    'turnip': (root/'jniLibs/arm64-v8a/libvulkan_freedreno.so', '717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d'),
    'shim_source': (root/'jniLibs/arm64-v8a/libhardware.so', 'd7add7e8e2e31f3c49b83941c6686fa66ab3d844c650e8d70c93b026f90cafa0'),
}
for label, (path, expected) in pins.items():
    reads = [sha(path), sha(path)]
    assert reads == [expected, expected], f'{label}: {reads}'
    out['sha'][label] = {'path': str(path), 'reads': reads}

out['size_bytes'] = int(subprocess.check_output(['du', '-sb', str(root)], text=True).split()[0])
assert out['size_bytes'] < 10*1024**3
out['status'] = 'pass'
print(json.dumps(out, indent=2))
