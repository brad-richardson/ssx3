#!/usr/bin/env python3
"""Compare the N8D6B snapshot with N8D5F, excluding generated caches."""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path('/home/brad/n8d6b')
base = Path('/home/brad/n8d5f')
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
    'backend': (root/'PS2Recomp'/backend, 'e730b9f05994c9887f9c5605f9a34b2fe6f4ac1c239bb964f17cdfc515b1fb5c'),
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

patch = (root/'g43-stage.patch').read_text()
normalized = patch.replace('--- N8D5B/', '--- a/').replace('+++ N8D6A/', '+++ b/')
reverse = subprocess.run(['patch', '--dry-run', '-R', '-p1', '--fuzz=0', '--batch'],
                         input=normalized, cwd=root/'parallel-gs', text=True, capture_output=True)
assert reverse.returncode == 0, f'G43 reverse patch mismatch: {reverse.stdout} {reverse.stderr}'
out['reverse_patch'] = reverse.stdout.strip().splitlines()
out['size_bytes'] = int(subprocess.check_output(['du', '-sb', str(root)], text=True).split()[0])
assert out['size_bytes'] < 10*1024**3
out['status'] = 'pass'
print(json.dumps(out, indent=2))
