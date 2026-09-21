#!/usr/bin/env python3
"""Record E15 resource bounds and clean only duplicated E15 fixture receipts."""
import datetime,hashlib,json,os,shutil,subprocess
from pathlib import Path
from e15_bounded import sample
E=Path(__file__).resolve().parent;W=Path('/Volumes/Extreme SSD/ps2recomp-spike');R=W/'PS2Recomp'
assert os.environ.get('COPYFILE_DISABLE')=='1'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
removed=[]
for phase in ['actual','final']:
    for mode in ['input','no-input']:
        folder=W/'P1/e15-binding-tests'/phase/mode
        original=folder/'e7-events.txt';canonical=E/f'{phase}-{mode}-events.txt'
        assert original.exists() and sha(original)==sha(canonical)
        removed.append(dict(original=str(original),canonical=str(canonical.relative_to(E)),sha256=sha(canonical)))
        original.unlink()
        for p in folder.iterdir():
            assert p.is_file() and p.name=='._e7-events.txt';p.unlink()
        folder.rmdir()
    parent=W/'P1/e15-binding-tests'/phase
    for p in parent.iterdir():
        assert p.is_file() and p.name in ['._input','._no-input'];p.unlink()
    parent.rmdir()
tmp=W/'P1/e15-tooltmp';assert not list(tmp.iterdir());tmp.rmdir()
rows=[]
def add(source,r):
    if isinstance(r,dict) and 'internal_free' in r:rows.append(dict(source=source,**r))
for p in E.glob('*-bounded-result.json'):
    d=json.loads(p.read_text())
    for k in ['before','bound','after']:add(p.name+':'+k,d.get(k))
for p in E.glob('*-liveness.jsonl'):
    for i,l in enumerate(p.read_text().splitlines(),1):
        d=json.loads(l);add(p.name+':'+str(i),d.get('resources',d))
boot=json.loads((E/'e15a-result.json').read_text());bind=boot['bind']
# During the boot this shared filename was covered by the boot's own caps,
# but excluded from the broad e15-* path glob. Reconstruct its exact binding
# sample contribution explicitly rather than rewrite the original sample.
joined=bind['resources']['ssd_allocated']+bind['allocated']['function_log']
pgrep=subprocess.run(['pgrep','-x','ps2EntryRunner'],text=True,capture_output=True)
assert pgrep.returncode==1 and not Path('/tmp/ssx3-p-lane-lease').exists()
now=sample();add('final',now)
peaks={k:max(rows,key=lambda r:r.get(k,0)) for k in ['internal_growth','ssd_allocated','tmp_allocated','fixture_allocated','log_bytes']}
low=min(rows,key=lambda r:r['internal_free'])
files=[]
for p in [Path('/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner'),Path('/tmp/p1-link/runtime/ps2xTest/ps2x_tests'),W/'P1/e15-binding-tests/entry/binding-test']:
    files.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
fork=subprocess.run(['git','-C',str(R),'status','--short'],text=True,capture_output=True)
head=subprocess.run(['git','-C',str(R),'rev-parse','HEAD'],text=True,capture_output=True)
(E/'e15-waits.log').write_bytes((W/'P1/run/e15-waits.log').read_bytes())
out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),removed_duplicate_receipts=removed,
    sampled_peaks=peaks,sampled_internal_floor=low,final_resources=now,
    broad_ssd_boot_sample_omission='Shared ps2_log.txt excluded from e15-* glob; boot-specific logical/allocated cap counted it throughout',
    corrected_binding_ssd_allocated=joined,
    conservative_whole_boot_ssd_bound=json.loads((E/'e15a-preflight.json').read_text())['resource_admission']['ssd_allocated']+1610612736+8*1024**2,
    tool_log_cap_failure=dict(cap=16777216,closed_raw=192334611,overshoot=192334611-16777216,canonical='build.log.gz',
        evidence_component_reservation=134217728,component_also_exceeded=True,
        total_internal_growth_after_failure=193581056,total_internal_reservation=536870912,
        repair='Hard bounded stdout pipe, same budgets; own AppleDouble compiler input removed with ownership receipt'),
    no_reclamation=True,no_generated_rebuild=True,boot_count=1,lease_absent=True,pgrep_rc=pgrep.returncode,
    fork_head=head.stdout.strip(),fork_status=fork.stdout,files=files,
    df=subprocess.check_output(['df','-h',str(W),'/private/tmp'],text=True))
(E/'final-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print('final fork',head.stdout.strip(),'boot_count=1 lease absent; pgrep=1')
print('internal growth',now['internal_growth'],'SSD allocation',now['ssd_allocated'],'minimum sampled internal free',low['internal_free'])
print('tool-log cap overrun retained explicitly; boot cap checks pass; source shutdown closure missing')
print('# E15 FINAL AUDIT TAIL COMPLETE')
