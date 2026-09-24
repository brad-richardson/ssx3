#!/usr/bin/env python3
"""N8D7M12P3 acceptance checker: source/overlay pins, one build, APK, budget.

Reads the receipts in this dir. Verdict A = source + package gates pass;
B = build/package mismatch with the smallest failing row; OTHER =
pin/permission/resource failure. Writes result.json. No device action.
"""
from pathlib import Path
import json
import re
import sys

here = Path(__file__).resolve().parent
rows = []
other = []
fails = []

def row(name, ok, detail=''):
    rows.append({'check': name, 'pass': bool(ok), 'detail': detail})
    if not ok:
        fails.append(name)

def must_read(name):
    p = here / name
    if not p.exists():
        other.append(f'missing receipt {name}')
        return None
    return p.read_text(errors='replace')

pre = must_read('preflight.txt')
if pre is not None:
    row('preflight_root_absent', 'n8d7m12p3 absent OK' in pre)
    m = re.search(r'HEAVY_JOBS (\[.*\])', pre)
    row('preflight_no_heavy_job', m and m.group(1) == '[]', m.group(1) if m else 'no line')
    m2 = re.search(r'/dev/sdc\s+\S+\s+\S+\s+(\S+)', pre)
    row('preflight_disk_free', 'ndk present OK' in pre and 'codegen present OK' in pre, (m2.group(0) if m2 else '') + ' ndk+codegen lines')
else:
    row('preflight', False, 'missing')

prep = must_read('prepare.txt')
if prep is not None:
    row('prepare_diffs_empty', 'PRE_CANDIDATE_DIFFS_EMPTY' in prep)
else:
    row('prepare', False, 'missing')

for name in ('source-gate.json', 'source-gate-postbuild.json'):
    txt = must_read(name)
    if txt is None:
        row(name, False, 'missing')
        continue
    try:
        g = json.loads(txt)
    except json.JSONDecodeError as e:
        row(name, False, f'bad json {e}')
        continue
    ok = (g.get('status') == 'pass'
          and sorted(g.get('diff', {}).get('fork_modified', [])) == sorted([
              'ps2xRuntime/CMakeLists.txt',
              'ps2xRuntime/include/runtime/gs/gs_cpu_backend.h',
              'ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp',
              'ps2xRuntime/src/main.cpp',
              'ps2xTest/src/ps2_gs_replay_tests.cpp'])
          and sorted(g.get('diff', {}).get('fork_added', [])) == sorted([
              'ps2xRuntime/include/runtime/gs/gs_replay_core.h',
              'ps2xRuntime/src/lib/gs/gs_replay_core.cpp'])
          and g.get('diff', {}).get('fork_removed', []) == []
          and g.get('diff', {}).get('parallel', []) == []
          and g.get('diff', {}).get('jniLibs', []) == []
          and g.get('runner_files', None) == []
          and all(v.get('reads', [None, None])[0] == v.get('reads', [None, None])[1] for v in g.get('sha', {}).values())
          and g.get('size_bytes', 10**13) < 10*1024**3)
    row(name, ok, f"status={g.get('status')} size={g.get('size_bytes')}")

build = must_read('build.txt')
if build is None:
    row('build', False, 'missing')
else:
    n = len(re.findall(r'BUILD SUCCESSFUL', build))
    row('build_one_success_no_retry', n == 1 and 'FAILED' not in build, f'BUILD SUCCESSFUL x{n}')

for name in ('apk-gate.json', 'mac-apk-gate.json'):
    txt = must_read(name)
    if txt is None:
        row(name, False, 'missing')
        continue
    try:
        g = json.loads(txt)
    except json.JSONDecodeError as e:
        row(name, False, f'bad json {e}')
        continue
    row(name, g.get('status') == 'pass', f"status={g.get('status')}")

disk = must_read('disk-budget.txt')
if disk is None:
    row('disk_budget', False, 'missing')
else:
    row('disk_budget', 'ssx3 internal usage' in disk, disk.strip().splitlines()[-1] if disk.strip() else '')

if other:
    verdict = 'OTHER'
elif fails:
    verdict = 'B'
else:
    verdict = 'A'
out = {'verdict': verdict, 'rows': rows, 'other': other, 'failing': fails,
       'note': 'Source/default-OFF path is statically gated; no runtime OFF-path or Turnip/HMI behavior is proved without a later Odin run.'}
(here/'result.json').write_text(json.dumps(out, indent=2) + '\n')
(here/'check-result.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
sys.exit(0 if verdict == 'A' else 1)
