#!/usr/bin/env python3
"""N8D3 package gate; reads each archive/member twice."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

root = Path('/home/brad/n8d3')
apk = root / 'PS2Recomp/android/app/build/outputs/apk/release/app-release.apk'
members = {
    'lib/arm64-v8a/libps2EntryRunner.so',
    'lib/arm64-v8a/libvulkan_freedreno.so',
    'lib/arm64-v8a/libhardware.so',
}
pins = {
    'lib/arm64-v8a/libvulkan_freedreno.so': '717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d',
}
flags = ('PS2X_ENABLE_DIAG_TAPS', 'PS2X_ENABLE_RUNTIME_LOGS',
         'PS2X_ENABLE_AGRESSIVE_LOGS', 'PS2X_ENABLE_IOP_RPC_TRACE',
         'PS2X_ENABLE_DEBUG_UI')

def sha_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def sha_member(name):
    h = hashlib.sha256()
    with zipfile.ZipFile(apk) as z, z.open(name) as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

out = {'apk': [sha_file(apk), sha_file(apk)], 'members': {}, 'caches': []}
assert out['apk'][0] == out['apk'][1], 'APK SHA pair mismatch'
with zipfile.ZipFile(apk) as z:
    found = {n for n in z.namelist() if n.startswith('lib/') and not n.endswith('/')}
    assert found == members, f'APK members {found}'
    for name in sorted(members):
        reads = [sha_member(name), sha_member(name)]
        assert reads[0] == reads[1], f'{name} SHA pair mismatch'
        if name in pins:
            assert reads[0] == pins[name], f'{name} pinned SHA mismatch'
        out['members'][name] = {'sha': reads, 'size': z.getinfo(name).file_size}
    runner = root / 'runner-extracted.so'
    with z.open('lib/arm64-v8a/libps2EntryRunner.so') as src, runner.open('wb') as dest:
        for chunk in iter(lambda: src.read(1024 * 1024), b''):
            dest.write(chunk)
    assert [sha_file(runner), sha_file(runner)] == out['members']['lib/arm64-v8a/libps2EntryRunner.so']['sha']

readelf = '/home/brad/n2/toolchain/android-sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readelf'
notes = subprocess.check_output([readelf, '-n', str(runner)], text=True)
match = re.search(r'Build ID: ([0-9a-f]+)', notes)
assert match, 'runner Build ID absent'
out['runner_build_id'] = match.group(1)
caches = list((root / 'PS2Recomp/android/app/.cxx/RelWithDebInfo').glob('*/arm64-v8a/CMakeCache.txt'))
assert caches, 'CMake cache absent'
for cache in caches:
    text = cache.read_text(errors='replace')
    vals = {}
    for flag in flags:
        match = re.search(rf'^{flag}:BOOL=(\w+)$', text, re.M)
        assert match and match.group(1) == 'OFF', f'{cache} {flag}={match.group(1) if match else "absent"}'
        vals[flag] = match.group(1)
    out['caches'].append({'path': str(cache), 'flags': vals})
out['status'] = 'pass'
(root / 'apk-gate.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
