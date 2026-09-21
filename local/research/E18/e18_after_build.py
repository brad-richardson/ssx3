from e18_common import *
import subprocess,sys
assert os.environ.get('COPYFILE_DISABLE')=='1'
r=json.loads((E/'build-source-only-bounded-result.json').read_text());assert r['rc']==0 and r['bound'] is None and not r['stdout_truncated']
source_records=json.loads((E/'before-generated.json').read_text());root=R/'ps2xRuntime/src/runner'
current={str(p) for p in root.iterdir() if p.suffix in ('.cpp','.h') and not p.name.startswith('._')}
assert current=={p['path'] for p in source_records}
for p in source_records:assert sha(p['path'])==p['sha256'],p['path']
save('after-generated-audit.json',dict(utc=utc(),count=len(current),all_hashes_match=True,before_manifest=pin(E/'before-generated.json'),codegen_invocations=0))
protected=json.loads((E/'protected-build-before.json').read_text())
for p in protected:assert sha(p['path'])==p['sha256'],p['path']
save('after-protected-audit.json',dict(utc=utc(),count=len(protected),all_hashes_match=True))
cc=json.loads((B/'compile_commands.json').read_text());sidecars=[c['file'] for c in cc if '/._' in c['file']];assert sidecars==[]
save('built-binaries.json',dict(utc=utc(),runner=pin(B/'ps2xRuntime/ps2EntryRunner'),suite=pin(B/'ps2xTest/ps2x_tests'),compiler_sidecar_inputs=sidecars,allocation=sample()))
subprocess.run([sys.executable,str(E/'e18_scope.py'),'after-build'],check=True)
print('BUILD AUDIT TAIL COMPLETE: generated9457 unchanged; protected build objects unchanged; no AppleDouble compiler inputs')
