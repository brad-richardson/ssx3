"""E24 checkpoint: read-only. Every gate E23 ran, each recorded as VERIFIED or
BLOCKED against its exact receipt. No title launch, no fork mutation, no build.

Changed vs E23: the three protected build trees were wiped by the host restart
(`env-audit.json`), so the 1,725-hash re-verify and the 458-test suite cannot
run. Those gates are recorded BLOCKED with the manifest that proves the loss,
rather than asserted away or silently re-pointed at another build.
"""
import gzip, subprocess
from e24_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
prior = E.parent/'E18'
gates = []

def gate(name, status, **detail):
    gates.append(dict(gate=name, status=status, **detail))
    print(f'[{status}] {name}', json.dumps(detail)[:180])

# --- fork identity: triple agreement, unchanged ---------------------------
commands = [['git','-C',str(R),'rev-parse','HEAD','refs/remotes/fork/ssx3'],
            ['git','-C',str(R),'ls-remote','fork','refs/heads/ssx3'],
            ['git','-C',str(R),'status','--short']]
receipts=[]
for command in commands:
    p=subprocess.run(command,text=True,capture_output=True,check=True)
    receipts.append(dict(argv=command,stdout=p.stdout,stderr=p.stderr,rc=p.returncode))
assert receipts[0]['stdout'].splitlines()==[BASE_SHA,BASE_SHA]
assert receipts[1]['stdout'].split()[0]==BASE_SHA
assert receipts[2]['stdout']=='?? ps2_log.txt\n'
save('fork-before.json',dict(utc=utc(),commands=receipts))
gate('fork triple-agree', 'VERIFIED', sha=BASE_SHA, head=True, remote_ref=True, ls_remote=True)

# --- 9,457 generated names/hashes, unchanged ------------------------------
expected=json.loads((prior/'before-generated.json').read_text())
actual=[pin(p) for p in sorted((R/'ps2xRuntime/src/runner').iterdir())
        if p.suffix in ('.cpp','.h') and not p.name.startswith('._')]
assert len(actual)==9457
assert {p['path']:p['sha256'] for p in actual}=={p['path']:p['sha256'] for p in expected}
save('before-generated.json',actual)
gate('9,457 generated names/hashes', 'VERIFIED', count=len(actual), all_hashes_match=True)

# --- E18 input/behavior source hashes -------------------------------------
end=json.loads((prior/'final-audit.json').read_text())
sources=[]
(E/'sources').mkdir(exist_ok=False)
for item in end['inputs_sources']+end['behavior_sources']:
    p=pin(item['path']);assert p['sha256']==item['sha256'],p
    sources.append(p)
    with gzip.open(E/'sources'/('before-'+Path(p['path']).name+'.gz'),'wb') as f:
        f.write(Path(p['path']).read_bytes())
gate('E18 input/behavior source hashes', 'VERIFIED', files=len(sources))

# --- protected builds: BLOCKED (wiped by the host restart) ----------------
env_audit=json.loads((E/'env-audit.json').read_text())
gate('1,725 protected build hashes', 'BLOCKED',
     reason='all three protected build trees absent after host restart',
     manifest=env_audit['protected_files_manifest'],
     present=env_audit['protected_files_present'],
     missing=env_audit['protected_files_missing'],
     missing_bytes=env_audit['protected_missing_bytes'],
     trees=env_audit['protected_build_trees'],
     local_snapshots_available=False, recoverable_copy_found=False)
gate('runner binary', 'BLOCKED', **env_audit['key_binaries']['runner'])
gate('suite binary (458 tests, E18 R1-R6 text)', 'BLOCKED', **env_audit['key_binaries']['suite'])

# --- fixtures + instrument: survived on the SSD ---------------------------
for key in ('fixture','cadence_fixture'):
    row=env_audit['key_binaries'][key]
    assert row['present'] and row['sha_equal'],row
    gate(f'{key} binary', 'VERIFIED', path=row['path'], bytes=row['actual_bytes'], sha_equal=True)
inst=env_audit['instrument']
assert inst['present'] and inst['sha_equal'],inst
gate('reused observer dylib (re-sha, never rebuilt)', 'VERIFIED',
     sha256=inst['actual_sha'], bytes=inst['actual_bytes'])

# --- fork allocation baseline for the storage ledger ----------------------
allocated={}
for root in [R/'.git',R/'ps2xRuntime/src/lib/Kernel/Stubs',R/'ps2xTest/src']:
    for p in [root,*root.rglob('*')]:
        try:allocated[str(p)]=p.lstat().st_blocks*512
        except FileNotFoundError:pass
save('fork-allocation-before.json',dict(utc=utc(),allocated=allocated))

s=sample();admission(s)
blocked=[g for g in gates if g['status']=='BLOCKED']
save('checkpoint.json',dict(utc=utc(),fork=BASE_SHA,generated_names=9457,
    all_generated_hashes_match=True,inputs_sources=sources,
    gates=gates,gates_verified=len(gates)-len(blocked),gates_blocked=len(blocked),
    red=bool(blocked),red_gates=[g['gate'] for g in blocked],
    protected_build_files=0,protected_build_files_expected=1725,
    runner=env_audit['key_binaries']['runner'],suite=env_audit['key_binaries']['suite'],
    fixture=env_audit['key_binaries']['fixture'],fixture_reused=True,resources=s))
print()
print(f'gates: {len(gates)-len(blocked)} VERIFIED / {len(blocked)} BLOCKED')
print('RED:', [g['gate'] for g in blocked])
print('# E24 CHECKPOINT TAIL COMPLETE')
