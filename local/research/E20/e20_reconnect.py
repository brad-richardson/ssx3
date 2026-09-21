"""Re-admit the returned SSD and reverify the checkpoint before execution."""
import subprocess
from e20_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
record=dict(utc=utc(),before=sample(),commands=[]);admission(record['before'])
for command in [['git','-C',str(R),'rev-parse','HEAD','refs/remotes/fork/ssx3'],
                ['git','-C',str(R),'ls-remote','fork','refs/heads/ssx3'],
                ['git','-C',str(R),'status','--short']]:
    p=subprocess.run(command,text=True,capture_output=True,check=True)
    record['commands'].append(dict(argv=command,rc=p.returncode,stdout=p.stdout,stderr=p.stderr))
assert record['commands'][0]['stdout'].splitlines()==[BASE_SHA,BASE_SHA]
assert record['commands'][1]['stdout'].split()[0]==BASE_SHA
assert record['commands'][2]['stdout']=='?? ps2_log.txt\n'
checkpoint=json.loads((E/'checkpoint.json').read_text())
for item in checkpoint['inputs_sources']+[checkpoint[k] for k in ('runner','suite','fixture')]:
    assert sha(item['path'])==item['sha256'],item['path']
expected=json.loads((E/'before-generated.json').read_text())
actual=[pin(p) for p in sorted((R/'ps2xRuntime/src/runner').iterdir()) if p.suffix in ('.cpp','.h') and not p.name.startswith('._')]
assert len(actual)==9457 and {x['path']:x['sha256'] for x in actual}=={x['path']:x['sha256'] for x in expected}
for item in json.loads((E/'protected-build-before.json').read_text()):assert sha(item['path'])==item['sha256'],item['path']
record.update(completed_utc=utc(),generated_names=9457,protected_files=1725,hashes_equal=True,after=sample(),baseline_previously_launched=False)
save('reconnection.json',record)
print('Returned SSD re-admitted; fork3adc0478,9457 generated,1725 protected hashes equal.')
print('# E20 RECONNECTION TAIL COMPLETE')
