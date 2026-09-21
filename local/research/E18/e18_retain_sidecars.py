import subprocess
from e18_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
a=json.loads((E/'sidecar-audit.json').read_text());owned=[x for x in a['sidecars'] if x['before_allocation'] is None]
expected={str(R/'ps2xRuntime/src/lib/Kernel/Stubs/._MPEG.cpp'),str(R/'ps2xTest/src/._ps2_runtime_expansion_tests.cpp')}
assert {x['path'] for x in owned}==expected
assert all(not x['tracked'] and x['magic']=='00051607' for x in owned)
admission(sample());dest=P/'e18-sidecars';dest.mkdir(exist_ok=False)
rows=[]
for x in owned:
 p=Path(x['path']);assert sha(p)==x['sha256']
 q=dest/(p.name[2:]+'.appledouble');assert not q.exists();p.rename(q)
 assert sha(q)==x['sha256'];rows.append(dict(original=str(p),retained=pin(q)))
save('sidecars-retained.json',dict(utc=utc(),ownership='Absent in pre-edit allocation manifest; birth times match E18 source edits; AppleDouble magic; untracked',rows=rows,deleted_bytes=0,preexisting_sidecars_untouched=True))
cc=json.loads((B/'compile_commands.json').read_text());assert all(not Path(x['file']).exists() for x in cc if '/._' in x['file'])
print('2 E18-created AppleDouble files retained by rename; 0 deletion; source bytes unchanged')
