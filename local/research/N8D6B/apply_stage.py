#!/usr/bin/env python3
"""Apply the pinned G43 patch only if all three N8D5F contexts match."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

root = Path('/home/brad/n8d6b')
tree = root / 'parallel-gs'
names = ('gs/gs_interface.hpp', 'gs/gs_renderer.hpp', 'gs/gs_renderer.cpp')
patch_bytes = (root / 'g43-stage.patch').read_bytes()
patch_sha = hashlib.sha256(patch_bytes).hexdigest()
assert patch_sha == '013b23508b678d2852f61fad066c4f498762e42aa6226aa1c7ea8cb4af0390a4'
original = patch_bytes.decode()
normalized = original.replace('--- N8D5B/', '--- a/').replace('+++ N8D6A/', '+++ b/')
assert normalized != original
assert normalized.count('--- a/') == normalized.count('+++ b/') == 3
assert all(f'--- a/{name}\n+++ b/{name}\n' in normalized for name in names)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

result = {'patch_sha': patch_sha, 'paths': {}, 'status': 'pending'}
for name in names:
    result['paths'][name] = {'before': [sha(tree/name), sha(tree/name)], 'after': 'not found'}

dry = subprocess.run(['patch', '--dry-run', '-p1', '--fuzz=0', '--batch'], input=normalized,
                     cwd=tree, text=True, capture_output=True)
result['dry_run'] = {'exit': dry.returncode, 'stdout': dry.stdout, 'stderr': dry.stderr}
if dry.returncode:
    result['status'] = 'patch-context-mismatch'
    print(json.dumps(result, indent=2))
    sys.exit(2)

applied = subprocess.run(['patch', '-p1', '--fuzz=0', '--batch'], input=normalized,
                         cwd=tree, text=True, capture_output=True)
result['apply'] = {'exit': applied.returncode, 'stdout': applied.stdout, 'stderr': applied.stderr}
if applied.returncode:
    result['status'] = 'patch-apply-failed'
    print(json.dumps(result, indent=2))
    sys.exit(2)
for name in names:
    result['paths'][name]['after'] = [sha(tree/name), sha(tree/name)]
result['status'] = 'pass'
print(json.dumps(result, indent=2))
