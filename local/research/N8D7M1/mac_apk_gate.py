#!/usr/bin/env python3
"""Double-read transferred APK and arm64 members against the WSL gate."""
from pathlib import Path
import hashlib
import json
import zipfile

here = Path(__file__).resolve().parent
apk = Path('/Users/brad/dev/ssx3-work/N8D7M1/app-release.apk')
wsl = json.loads((here/'apk-gate.json').read_text())

def digest(stream):
    h = hashlib.sha256()
    for part in iter(lambda: stream.read(1024*1024), b''):
        h.update(part)
    return h.hexdigest()

def apk_sha():
    with apk.open('rb') as stream:
        return digest(stream)

out = {'apk': [apk_sha(), apk_sha()], 'members': {}, 'size': apk.stat().st_size}
assert out['apk'] == wsl['apk'], 'transferred APK SHA mismatch'
assert out['size'] == wsl['apk_size'], 'transferred APK size mismatch'
assert out['size'] < 500 * 1024 * 1024, 'APK copy exceeds 500 MiB'
with zipfile.ZipFile(apk) as z:
    names = {n for n in z.namelist() if n.startswith('lib/') and not n.endswith('/')}
    assert names == set(wsl['members']), f'unexpected native members: {names}'
    for name in sorted(names):
        reads = []
        for _ in range(2):
            with z.open(name) as stream:
                reads.append(digest(stream))
        assert reads == wsl['members'][name]['sha'], f'{name} differs from WSL'
        out['members'][name] = reads
out['status'] = 'pass'
(here/'mac-apk-gate.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
