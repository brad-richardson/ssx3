"""Closed E16 resource/source/retention receipts; no mutation outside evidence."""
import gzip, subprocess
from e16_common import *

assert os.environ.get('COPYFILE_DISABLE')=='1'
base=json.loads((E/'fork-allocation-before.json').read_text())
old={**base['files'],**base.get('directories',{})}
fork_growth=[]
for p in (R/'.git').rglob('*'):
    try:
        n=p.stat().st_blocks*512;delta=max(0,n-old.get(str(p),0))
        if delta:fork_growth.append(dict(path=str(p),allocated=n,positive_growth=delta))
    except FileNotFoundError:pass
resources=sample();resources['fork_positive_growth']=sum(r['positive_growth'] for r in fork_growth)
resources['ssd_total_with_fork_growth']=resources['ssd_owned_paths_allocated']+resources['fork_positive_growth']
assert resources['ssd_total_with_fork_growth']<12*G and resources['internal_allocated']<5*G
assert not bound(resources)
record=dict(utc=utc(),resources=resources,fork_growth=fork_growth,runner=pin(B/'ps2xRuntime/ps2EntryRunner'),suite=pin(B/'ps2xTest/ps2x_tests'),fixture=pin(P/'e16-fixtures/after/binding-test'))
audit=json.loads((E/'final-checkpoint.json').read_text())
assert audit['generated']['count']==9452 and audit['generated']['names_equal'] and not audit['generated']['changed']
assert all(r['unchanged'] for r in audit['inputs'])
assert all(r['same_as_e15'] for r in audit['sources'] if not r['path'].endswith('/ps2_runtime.cpp'))
record['generated_count']=9452;record['config_unchanged']=True;record['mpeg_unchanged']=True;record['main_unchanged']=True
record['boot_attempts']=int((E/'boot-attempt.json').exists())
record['lease_absent']=not Path('/tmp/ssx3-p-lane-lease').exists()
p=subprocess.run(['pgrep','-x','ps2EntryRunner'],capture_output=True,text=True)
record['pgrep']=dict(rc=p.returncode,stdout=p.stdout,stderr=p.stderr)
assert record['lease_absent'] and p.returncode==1
canonical=[]
manifest=E/'e16a-retained.json'
if manifest.exists():
    rows=json.loads(manifest.read_text())['files']
    for r in rows:
        q=E/r['canonical'];op=gzip.open if r['encoding']=='gzip' else open
        with op(q,'rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
        assert digest==r['sha256'],r
        canonical.append(r['canonical'])
    record['retention']=dict(original_files=len(rows),canonical_files=len(set(canonical)),canonical_bytes=sum((E/p).stat().st_size for p in set(canonical)),all_hashes_verified=True,ssd_originals_preserved=True)
    from e16_closed_events import tap,fields
    events,tail=tap(P/'run/e16a-join/e7-events.txt')
    record['source_shutdown']=dict(events=len(events),shutdown=fields(tail),complete=True)
    record['boot_result']=json.loads((E/'e16a-result.json').read_text())
record['bounded_tools']=[dict(label=(d:=json.loads(p.read_text()))['label'],rc=d['rc'],bound=d['bound'],stdout_truncated=d['stdout_truncated'],elapsed_s=d['elapsed_s']) for p in sorted(E.glob('*-bounded-result.json'))]
assert all(d['bound'] is None and not d['stdout_truncated'] for d in record['bounded_tools'])
save('final-audit.json',record)
print(json.dumps({k:v for k,v in record.items() if k not in ('fork_growth','bounded_tools','boot_result')},indent=2))
print('# E16 FINAL AUDIT TAIL COMPLETE')
