#!/usr/bin/env python3
"""Retrieve N8D1's third selected host image without another launch."""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path('/Users/brad/dev/ssx3-work/N8D1')
serial = '622c49b1'
dump = '/storage/emulated/0/Android/data/com.ps2x.runner/files/n8d1-frames'
lease_path = '/data/local/tmp/mg/LEASE'
claim = 'N8D1 receipt-pull'

def adb(*args):
    p = subprocess.run(['adb', '-s', serial, *args], text=True, capture_output=True, check=True)
    return p.stdout.strip()

def sh(command):
    return adb('shell', command)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

lease = sh(f'cat {lease_path}')
assert lease.startswith('LEASE_FREE'), f'Odin lease busy: {lease}'
sh(f"echo '{claim}' > {lease_path}")
try:
    assert sh(f'cat {lease_path}') == claim
    assert not sh('pidof com.ps2x.runner 2>/dev/null || true'), 'app unexpectedly running'
    receipt = json.loads((root / 'result.json').read_text())
    entry = {'kind': 'upload', 'png': 'upload-latest.png', 'txt': 'upload-latest.txt'}
    for name in (entry['png'], entry['txt']):
        remote = f'{dump}/{name}'
        remote_shas = [sh(f'sha256sum {remote}').split()[0] for _ in range(2)]
        local = root / name
        adb('pull', remote, str(local))
        local_shas = [sha(local), sha(local)]
        assert len(set(remote_shas + local_shas)) == 1, f'{name} hash mismatch'
        entry[name + '_sha'] = remote_shas + local_shas
        entry[name + '_bytes'] = local.stat().st_size
    entry['metadata'] = (root / entry['txt']).read_text().strip()
    assert 'seq=2 tick=840 ' in entry['metadata'], entry['metadata']
    assert len(receipt['images']) == 2
    receipt['images'].append(entry)
    event = f'RECEIPT_PULL upload-latest.png {entry["metadata"]} sha={entry[entry["png"] + "_sha"][0]}'
    receipt['events'].append(event)
    (root / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')
    with (root / 'driver.log').open('a') as out:
        out.write(event + '\n')
    print(event)
finally:
    sh("echo 'LEASE_FREE N8D1 done' > /data/local/tmp/mg/LEASE")
    print('RECEIPT_PULL cleanup pid=' + (sh('pidof com.ps2x.runner 2>/dev/null || true') or 'none') +
          ' lease=' + sh(f'cat {lease_path}'))
