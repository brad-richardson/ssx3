#!/usr/bin/env python3
"""Read-only E13 final identity, process, ownership and retention receipt."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

E = Path(__file__).resolve().parent
W = Path('/Volumes/Extreme SSD/ps2recomp-spike')
R = W / 'PS2Recomp'
assert os.environ.get('COPYFILE_DISABLE') == '1'

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def command(argv):
    r = subprocess.run(argv, capture_output=True, text=True)
    return dict(argv=argv, rc=r.returncode, stdout=r.stdout, stderr=r.stderr)

expected = json.loads((E / 'after/manifest.json').read_text())
generated = json.loads((E / 'after/generated.json').read_text())
rows = []
for old in generated + expected['inputs'] + expected['executables']:
    p = Path(old['path'])
    row = dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p))
    row['matches'] = row['bytes'] == old['bytes'] and row['sha256'] == old['sha256']
    rows.append(row)
assert all(x['matches'] for x in rows)
current = list((R / 'ps2xRuntime/src/runner').glob('*.cpp'))
current += list((R / 'ps2xRuntime/src/runner').glob('ps2_recompiled_*.h'))
current += list((R / 'ps2xRuntime/include').glob('ps2_recompiled_*.h'))
names = {str(p) for p in current if not p.name.startswith('._')}
assert names == {x['path'] for x in generated}
commands = {key: command(argv) for key, argv in {
    'pgrep': ['pgrep', '-x', 'ps2EntryRunner'],
    'df': ['df', '-k', str(W), '/private/tmp'],
    'fork_head': ['git', '-C', str(R), 'rev-parse', 'HEAD'],
    'fork_status': ['git', '-C', str(R), 'status', '--short'],
    'fork_staged': ['git', '-C', str(R), 'diff', '--cached', '--name-only'],
    'main_head': ['git', 'rev-parse', 'HEAD'],
    'main_status': ['git', 'status', '--short'],
}.items()}
assert commands['pgrep']['rc'] == 1
assert all(v['rc'] == 0 for k, v in commands.items() if k != 'pgrep')
assert commands['fork_head']['stdout'].strip() == '83fb4d60904abb016522c477cce704c52118f95f'
assert not commands['fork_staged']['stdout'].strip()
waits = W / 'P1/run/e13-waits.log'
(E / 'e13-waits.log').write_bytes(waits.read_bytes())
record = dict(
    utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    lease_absent=not Path('/tmp/ssx3-p-lane-lease').exists(),
    scratch_absent=not Path('/tmp/ssx3-e13-leaf-codegen').exists(),
    generated_count=len(generated), generated_names_match=True,
    identity_rows=rows[-len(expected['inputs'] + expected['executables']):],
    all_generated_hashes_match=True,
    generated_manifest_sha256=sha(E / 'after/generated.json'),
    protected_checkpoint_present=Path('/tmp/p1-link/runtime').is_dir(),
    owned_tooltmp_remaining=[str(p) for p in (W / 'P1/e13-tooltmp').iterdir()]
        if (W / 'P1/e13-tooltmp').exists() else [],
    commands=commands, boot_count=1, no_ssx3_push=True,
    fork_remote_receipt='fork-commit.json',
)
assert record['lease_absent'] and record['scratch_absent']
assert record['protected_checkpoint_present'] and not record['owned_tooltmp_remaining']
(E / 'closeout.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({k: v for k, v in record.items() if k not in ('commands', 'identity_rows')}, indent=2))
print('# E13 CLOSEOUT TAIL COMPLETE — no execution, rebuild, regeneration or lease mutation')
