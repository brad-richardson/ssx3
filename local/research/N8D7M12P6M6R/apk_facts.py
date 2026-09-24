#!/usr/bin/env python3
"""N8D7M12P6M6R WSL package facts (read-only): same reads as apk_gate.py but
records string/cache/flag facts without asserting, so one missing string
cannot hide the remaining values. Outputs to root top level only."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

root = Path('/home/brad/n8d7m12p6m6')
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
n8d7m1_runner_build_id = '73291620f0c62fdc01ac0b603e9e5cca3114d0a5'
n8d7m1_runner_sha = 'f3de999acc9227b82a9d9fab6a4a0b5b7fb279e6205991c1b3022da781e3c1bf'
p3_runner_build_id = '65ce162abca08d664223a362824b70c86aea6f4f'
p3_runner_sha = '329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d'
p3_apk_sha = 'caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512'
off_flags = ('PS2X_BUILD_TEST', 'PS2X_ENABLE_DIAG_TAPS', 'PS2X_ENABLE_RUNTIME_LOGS',
             'PS2X_ENABLE_AGRESSIVE_LOGS', 'PS2X_ENABLE_IOP_RPC_TRACE',
             'PS2X_ENABLE_DEBUG_UI')
strings = (
    'PS2X_GS_REPLAY_ONDEVICE', 'PS2X_GS_REPLAY_CAPTURE', 'PS2XGSC1',
    'GB4_REPLAY_SUMMARY',
    'PS2X_N8D7F_SELECTED_CAPTURE', 'PS2X_N8D7L_ORACLE', '[n8d7f]', '[n8d7l]',
    'vram_sha256=', 'input_sha256=', 'circuit_sha256=', 'input_circuit_equal=',
    'circuit_stage_equal=', 'PS2X_N8D5_TILE_CAPTURE', 'circuit1',
    'pre_deinterlace_merged', 'stage=final', 'control=', 'sampled_summary',
    'raw_summary', 'PNG write failed path=', 'oracle_controls=',
    'oracle_input_equal=',
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
       'members': {}, 'caches': [], 'checks': {}}
out['checks']['apk_pair_equal'] = out['apk'][0] == out['apk'][1]
out['apk_new_vs_p3'] = out['apk'][0] != p3_apk_sha
with zipfile.ZipFile(apk) as z:
    found = sorted(n for n in z.namelist() if n.startswith('lib/') and not n.endswith('/'))
    out['found_members'] = found
    out['checks']['member_set_exact'] = set(found) == members
    for name in sorted(members):
        reads = [sha_member(name), sha_member(name)]
        entry = {'sha': reads, 'size': z.getinfo(name).file_size,
                 'pair_equal': reads[0] == reads[1]}
        if name in pins:
            entry['pin_equal'] = reads[0] == pins[name]
        out['members'][name] = entry
    runner = root / 'runner-extracted.so'
    with z.open('lib/arm64-v8a/libps2EntryRunner.so') as src, runner.open('wb') as dest:
        for chunk in iter(lambda: src.read(1024 * 1024), b''):
            dest.write(chunk)
out['checks']['extracted_equal_member'] = (
    [sha_file(runner), sha_file(runner)]
    == out['members']['lib/arm64-v8a/libps2EntryRunner.so']['sha'])
rsha = out['members']['lib/arm64-v8a/libps2EntryRunner.so']['sha'][0]
out['runner_new_vs_n8d7m1'] = rsha != n8d7m1_runner_sha
out['runner_new_vs_p3'] = rsha != p3_runner_sha

readelf = '/home/brad/n2/toolchain/android-sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readelf'
notes = subprocess.check_output([readelf, '-n', str(runner)], text=True)
match = re.search(r'Build ID: ([0-9a-f]+)', notes)
out['runner_build_id'] = match.group(1) if match else None
out['runner_build_id_new_vs_n8d7m1'] = out['runner_build_id'] != n8d7m1_runner_build_id
out['runner_build_id_new_vs_p3'] = out['runner_build_id'] != p3_runner_build_id
data = runner.read_bytes()
out['strings'] = {s: s.encode() in data for s in strings}
out['strings_missing'] = [s for s, v in out['strings'].items() if not v]
out['checks']['strings_all_present'] = not out['strings_missing']

caches = list((root / 'PS2Recomp/android/app/.cxx/RelWithDebInfo').glob('*/arm64-v8a/CMakeCache.txt'))
out['checks']['sole_arm64_cache'] = len(caches) == 1
for cache in caches:
    cache_text = cache.read_text(errors='replace')
    vals = {}
    for flag in off_flags:
        m = re.search(rf'^{flag}:BOOL=(\w+)$', cache_text, re.M)
        vals[flag] = m.group(1) if m else 'absent'
    for key in ('PS2X_GS_SHADOW_PARALLEL', 'PS2X_PARALLEL_GS_SOURCE_DIR',
                'PS2X_GAME_CODEGEN_DIR', 'CMAKE_BUILD_TYPE'):
        m = re.search(rf'^{key}:[^=]+=(.*)$', cache_text, re.M)
        vals[key] = m.group(1) if m else 'absent'
    out['caches'].append({'path': str(cache), 'values': vals})
out['checks']['off_flags_all_off'] = all(
    c['values'].get(f) == 'OFF' for c in out['caches'] for f in off_flags)
out['checks']['shadow_on'] = all(
    c['values'].get('PS2X_GS_SHADOW_PARALLEL') == 'ON' for c in out['caches'])
out['checks']['parallel_dir_is_new_root'] = all(
    c['values'].get('PS2X_PARALLEL_GS_SOURCE_DIR') == str(root / 'parallel-gs')
    for c in out['caches'])
out['checks']['codegen_dir_is_new_root'] = all(
    c['values'].get('PS2X_GAME_CODEGEN_DIR') == str(root / 'codegen-ssx3')
    for c in out['caches'])
out['root_size_bytes'] = int(subprocess.check_output(['du', '-sb', str(root)], text=True).split()[0])
out['checks']['root_under_10gib'] = out['root_size_bytes'] < 10 * 1024 ** 3
out['status'] = 'pass' if all(out['checks'].values()) else 'mismatch'
(root / 'apk-facts.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
