#!/usr/bin/env python3
"""N9 Part 2 WSL package gate: double-read archive and members.

Adapted from N8D7M12P6M6R/apk_gate.py (root n9). Requires exactly the arm64
runner/Turnip/HAL members, unchanged Turnip/HAL pins, a runner Build ID NEW
vs P6M6, every Turnip/HMI/HAL product string (all present in staged fb11e18
sources), NONE of the replay/diagnostic strings (all verified absent from
staged sources, incl. PS2X_PGS_HIER: this build carries only the clean N8X1
diff), and the sole arm64 CMake cache pointing at the new root with the six
flags OFF and shadow-parallel ON. All outputs go to the WSL root top level
(outside the four staged source roots).
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

root = Path('/home/brad/n9')
apk = root / 'PS2Recomp/android/app/build/outputs/apk/release/app-release.apk'
members = {
    'lib/arm64-v8a/libps2EntryRunner.so',
    'lib/arm64-v8a/libvulkan_freedreno.so',
    'lib/arm64-v8a/libhardware.so',
}
pins = {
    'lib/arm64-v8a/libvulkan_freedreno.so': '717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d',
    'lib/arm64-v8a/libhardware.so': '1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387',
}
p6m6_runner_build_id = '4c9c9d149900cdc3494201c38124d11bfb616fa3'
p6m6_runner_sha = 'e5a3302c6bef489b04a4a143c47b01e616735f8db0acdbda663710a326c11af1'
p6m6_apk_sha = 'da9a41a8e808fe31d509489c60b3927587c367866c6c2c6582009c35de6ef262'
off_flags = ('PS2X_BUILD_TEST', 'PS2X_ENABLE_DIAG_TAPS', 'PS2X_ENABLE_RUNTIME_LOGS',
             'PS2X_ENABLE_AGRESSIVE_LOGS', 'PS2X_ENABLE_IOP_RPC_TRACE',
             'PS2X_ENABLE_DEBUG_UI')
present_strings = (
    # In-process Turnip path (fb11e18 backend sources)
    'PS2X_GS_TURNIP', 'libvulkan_freedreno.so',
    'Turnip requested via PS2X_GS_TURNIP=1', 'Turnip HMI mapped base=',
    'Turnip HAL open rc=', 'vulkan0', 'Turnip dlopen failed: ',
)
absent_strings = (
    # No replay core, no snapshot diagnostics, no N8X1 knob (clean diff only)
    'PS2X_GS_REPLAY_ONDEVICE', 'PS2X_GS_REPLAY_CAPTURE', 'GB4_REPLAY_SUMMARY',
    'PS2X_N8D7F_SELECTED_CAPTURE', 'PS2X_N8D7L_ORACLE', '[n8d7f]', '[n8d7l]',
    'vram_sha256=', 'PS2X_N8D5_TILE_CAPTURE', 'pre_deinterlace_merged',
    'n8d5_tile', 'PGS_G40_WALL', 'PGS_G41_CANARY',
    'PGS_SKIP_SAMPLER_FEEDBACK', 'PS2X_PGS_HIER', 'oracle_input_equal=',
)

def sha_stream(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(chunk)
    return h.hexdigest()

def sha_file(path):
    with path.open('rb') as f:
        return sha_stream(f)

def sha_member(name):
    with zipfile.ZipFile(apk) as z, z.open(name) as f:
        return sha_stream(f)

out = {'apk': [sha_file(apk), sha_file(apk)], 'apk_size': apk.stat().st_size,
       'members': {}, 'caches': []}
assert out['apk'][0] == out['apk'][1], 'APK SHA pair mismatch'
assert out['apk'][0] != p6m6_apk_sha, 'APK SHA unchanged from P6M6'
with zipfile.ZipFile(apk) as z:
    found = {n for n in z.namelist() if n.startswith('lib/') and not n.endswith('/')}
    assert found == members, f'APK members {found}'
    for name in sorted(members):
        reads = [sha_member(name), sha_member(name)]
        assert reads[0] == reads[1], f'{name} SHA pair mismatch'
        if name in pins:
            assert reads[0] == pins[name], f'{name} pin mismatch: actual {reads[0]}, expected {pins[name]}'
        out['members'][name] = {'sha': reads, 'size': z.getinfo(name).file_size}
    runner = root / 'runner-extracted.so'
    with z.open('lib/arm64-v8a/libps2EntryRunner.so') as src, runner.open('wb') as dest:
        for chunk in iter(lambda: src.read(1024 * 1024), b''):
            dest.write(chunk)
assert [sha_file(runner), sha_file(runner)] == out['members']['lib/arm64-v8a/libps2EntryRunner.so']['sha']
assert out['members']['lib/arm64-v8a/libps2EntryRunner.so']['sha'][0] != p6m6_runner_sha, 'runner SHA unchanged from P6M6'
out['runner_new_vs_p6m6'] = True

readelf = '/home/brad/n2/toolchain/android-sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readelf'
notes = subprocess.check_output([readelf, '-n', str(runner)], text=True)
match = re.search(r'Build ID: ([0-9a-f]+)', notes)
assert match, 'runner Build ID absent'
out['runner_build_id'] = match.group(1)
assert out['runner_build_id'] != p6m6_runner_build_id, 'runner Build ID unchanged from P6M6'
data = runner.read_bytes()
out['present'] = {s: s.encode() in data for s in present_strings}
assert all(out['present'].values()), f'product strings absent: {out["present"]}'
out['absent'] = {s: s.encode() in data for s in absent_strings}
assert not any(out['absent'].values()), f'diagnostic strings present: {[s for s, v in out["absent"].items() if v]}'

caches = list((root / 'PS2Recomp/android/app/.cxx/RelWithDebInfo').glob('*/arm64-v8a/CMakeCache.txt'))
assert len(caches) == 1, f'expected one arm64 cache, found {caches}'
for cache in caches:
    cache_text = cache.read_text(errors='replace')
    vals = {}
    for flag in off_flags:
        match = re.search(rf'^{flag}:BOOL=(\w+)$', cache_text, re.M)
        assert match and match.group(1) == 'OFF', f'{cache} {flag}={match.group(1) if match else "absent"}'
        vals[flag] = match.group(1)
    for key, expected in {
        'PS2X_GS_SHADOW_PARALLEL': 'ON',
        'PS2X_PARALLEL_GS_SOURCE_DIR': str(root / 'parallel-gs'),
        'PS2X_GAME_CODEGEN_DIR': str(root / 'codegen-ssx3'),
    }.items():
        match = re.search(rf'^{key}:[^=]+=(.*)$', cache_text, re.M)
        assert match and match.group(1) == expected, f'{cache} {key}={match.group(1) if match else "absent"}'
        vals[key] = match.group(1)
    out['caches'].append({'path': str(cache), 'values': vals})
out['status'] = 'pass'
(root / 'apk-gate.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
