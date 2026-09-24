#!/usr/bin/env python3
"""N8D7M12P3 WSL source gate: new root vs N8D7M1, plus double-read pins.

Expected: fork differs in exactly the seven a608ed1 overlay paths
(d1ba1d4..a608ed1 file list; gs_replay_core.* are new files, the other
five are modifications); parallel-gs and jniLibs have zero differences;
no runner files in the new root. Overlay pins must equal the Mac a608ed1
double-reads; preserved pins (oracle backend, header, G43, writer, shader,
codegen, Turnip, shim source) must equal the N8D7M1 pins.
"""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path('/home/brad/n8d7m12p3')
base = Path('/home/brad/n8d7m1')
OVERLAY = [
    'ps2xRuntime/CMakeLists.txt',
    'ps2xRuntime/include/runtime/gs/gs_cpu_backend.h',
    'ps2xRuntime/include/runtime/gs/gs_replay_core.h',
    'ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp',
    'ps2xRuntime/src/lib/gs/gs_replay_core.cpp',
    'ps2xRuntime/src/main.cpp',
    'ps2xTest/src/ps2_gs_replay_tests.cpp',
]
NEW_FILES = {
    'ps2xRuntime/include/runtime/gs/gs_replay_core.h',
    'ps2xRuntime/src/lib/gs/gs_replay_core.cpp',
}

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024*1024), b''):
            h.update(part)
    return h.hexdigest()

def files(path, exclude_runner):
    out = set()
    for p in path.rglob('*'):
        if not p.is_file():
            continue
        rel = p.relative_to(path)
        if any(x in {'.cxx', 'build', '.gradle'} for x in rel.parts):
            continue
        if exclude_runner and 'runner' in rel.parts:
            continue
        out.add(str(rel))
    return out

def tree_diff(left, right):
    la, rb = files(left, True), files(right, True)
    added = sorted(rb - la)
    removed = sorted(la - rb)
    modified = sorted(p for p in la & rb if sha(left/p) != sha(right/p))
    return added, removed, modified

def exact_tree_diff(left, right):
    excluded = {'.cxx', 'build', '.gradle'}
    def flist(path):
        return {str(p.relative_to(path)) for p in path.rglob('*')
                if p.is_file() and not any(x in excluded for x in p.relative_to(path).parts)}
    la, rb = flist(left), flist(right)
    assert la == rb, f'file set mismatch added={sorted(rb-la)} removed={sorted(la-rb)}'
    return sorted(p for p in la if sha(left/p) != sha(right/p))

out = {'diff': {}, 'sha': {}, 'status': 'pending'}
added, removed, modified = tree_diff(base/'PS2Recomp', root/'PS2Recomp')
out['diff']['fork_added'] = added
out['diff']['fork_removed'] = removed
out['diff']['fork_modified'] = modified
assert added == sorted(NEW_FILES), f'added {added}'
assert removed == [], f'removed {removed}'
assert modified == sorted(set(OVERLAY) - NEW_FILES), f'modified {modified}'
out['diff']['parallel'] = exact_tree_diff(base/'parallel-gs', root/'parallel-gs')
assert out['diff']['parallel'] == [], out['diff']['parallel']
out['diff']['jniLibs'] = exact_tree_diff(base/'jniLibs', root/'jniLibs')
assert out['diff']['jniLibs'] == [], out['diff']['jniLibs']
runner_dir = root/'PS2Recomp/ps2xRuntime/src/runner'
runner_hits = [str(p.relative_to(root/'PS2Recomp')) for p in runner_dir.rglob('*')] if runner_dir.exists() else []
assert runner_hits == [], f'generated runner files present: {runner_hits[:5]}'
out['runner_files'] = []

pins = {
    # seven overlay files: Mac a608ed1 double-reads
    'ov_cmakelists': (root/'PS2Recomp/ps2xRuntime/CMakeLists.txt', 'b229b7ace623e7494bca6b6ddb50eeb5be54c8d060950a93b4534f40e86fddcf'),
    'ov_cpu_backend_h': (root/'PS2Recomp/ps2xRuntime/include/runtime/gs/gs_cpu_backend.h', '0d0377edd8ae46e19e161562ff1862cb0686cd939736ddcbde4b8ddc1e2e3a46'),
    'ov_replay_core_h': (root/'PS2Recomp/ps2xRuntime/include/runtime/gs/gs_replay_core.h', 'd80f9af2d2761264e4e3548643d4a8a999b568e093e37a28b2a1c8eab69f9964'),
    'ov_cpu_backend_cpp': (root/'PS2Recomp/ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp', 'c762efd61886221b01aecc72301c7bda7fc333bc2b58ea85520cd5a0a50ec57f'),
    'ov_replay_core_cpp': (root/'PS2Recomp/ps2xRuntime/src/lib/gs/gs_replay_core.cpp', 'c5fdaf64ee065ba43e054eff821887aa9db980abf2367e7e6a227ccdbfda396c'),
    'ov_main': (root/'PS2Recomp/ps2xRuntime/src/main.cpp', '7ab53178547e360e115478a26d3d4bb36413efb6407fe2142f07afcfeb4c17bf'),
    'ov_replay_tests': (root/'PS2Recomp/ps2xTest/src/ps2_gs_replay_tests.cpp', 'db2e9c7c92b97320d224d8f2357cb523e988da0a90b24250576495a6849611ae'),
    # preserved N8D7M1 pins
    'backend': (root/'PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp', '84a13a80686be8d4ed17750a9399d298ea6b998b98f48d3720b6b5bc839a4645'),
    'header': (root/'PS2Recomp/ps2xRuntime/include/runtime/gs/ps2_gs_psmct32.h', '9635a40e11bae56189b64d1d9660fb68d0375444d355db43246973adb95e71f7'),
    'header_base': (base/'PS2Recomp/ps2xRuntime/include/runtime/gs/ps2_gs_psmct32.h', '9635a40e11bae56189b64d1d9660fb68d0375444d355db43246973adb95e71f7'),
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
