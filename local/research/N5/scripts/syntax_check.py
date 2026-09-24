#!/usr/bin/env python3
"""N5: -fsyntax-only over the runtime TUs (+2 guest unity TUs) with taps OFF, and one TU with taps ON."""
import json, shlex, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
cc = json.load(open(sys.argv[1]))
cc = [e for e in cc if '-emit-pch' not in e['command']]
rt = [e for e in cc if 'ps2_game_objects.dir' not in e['file'] and 'ps2_game_objects.dir' not in e['command']]
game = [e for e in cc if 'ps2_game_objects.dir/Unity/unity_' in e['file']][:2]
def cmd(e, taps):
    a = shlex.split(e['command'])
    out, skip, i = [], False, 0
    while i < len(a):
        x = a[i]
        if x == '-o': i += 2; continue
        if x == '-Xclang' and i + 3 < len(a) and a[i + 1] == '-include-pch': i += 4; continue
        out.append(x); i += 1
    return out + ['-fsyntax-only', f'-DPS2X_ENABLE_DIAG_TAPS={taps}', '-Wno-macro-redefined']
jobs = [(e, 0) for e in rt + game] + [(game[0], 1)]
def run(j):
    e, t = j
    r = subprocess.run(cmd(e, t), cwd=e['directory'], capture_output=True, text=True, errors='replace')
    errs = [l for l in r.stderr.splitlines() if ' error: ' in l]
    return (os.path.basename(e['file']), t, r.returncode, errs[:3])
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(run, jobs))
bad = [r for r in res if r[2] != 0]
print(f'runtime={len(rt)} game={len(game)} TUs={len(res)} ok={len(res)-len(bad)} fail={len(bad)}')
for r in bad: print('FAIL', r)
