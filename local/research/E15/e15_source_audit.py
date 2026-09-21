#!/usr/bin/env python3
"""Pin unchanged MPEG/generated inputs and the observation-only fork diff."""
import gzip,hashlib,json,os,subprocess
from pathlib import Path
E=Path(__file__).resolve().parent;R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
FILES=['ps2xRuntime/include/ps2_e4.h','ps2xRuntime/include/ps2_e7.h','ps2xRuntime/include/ps2_e15.h','ps2xRuntime/src/lib/ps2_runtime.cpp','ps2xRuntime/src/lib/Kernel/EeScheduler.cpp']
BASE='83fb4d60904abb016522c477cce704c52118f95f'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    out=E/'sources';out.mkdir(exist_ok=True);rows=[]
    previous=json.loads((E/'prior-residual-source-manifest.json').read_text())
    for row in previous:
        p=Path(row['path'])
        if str(p.relative_to(R)) in FILES:continue
        assert sha(p)==row['sha256'],row
        dest=out/(p.name+'.gz');dest.write_bytes(gzip.compress(p.read_bytes(),mtime=0))
        rows.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,retained=str(dest.relative_to(E)),same_as_E13=True))
    for rel in FILES:
        p=R/rel;dest=out/(p.name+'.gz');dest.write_bytes(gzip.compress(p.read_bytes(),mtime=0))
        rows.append(dict(path=rel,sha256=sha(p),bytes=p.stat().st_size,retained=str(dest.relative_to(E)),observation=True))
    diff=subprocess.check_output(['git','-C',str(R),'diff',BASE,'--',*FILES],text=True)
    (E/'observation-tracked.diff').write_text(diff)
    # The new header is retained in full; git diff excludes it until staged.
    header=(R/FILES[2]).read_text()
    assert 'SET_GPR' not in header and 'const uint8_t *ram' in header and 'const R5900Context *ctx' in header
    before=json.loads((E/'before/generated.json').read_text());changed=[]
    for row in before:
        p=Path(row['path'])
        if not p.exists() or sha(p)!=row['sha256']:changed.append(str(p))
    expected={row['path'] for row in before}
    current=set()
    for folder,pattern in [(R/'ps2xRuntime/src/runner','*.cpp'),(R/'ps2xRuntime/src/runner','ps2_recompiled_*.h'),(R/'ps2xRuntime/include','ps2_recompiled_*.h')]:
        current.update(str(p) for p in folder.glob(pattern) if not p.name.startswith('._'))
    assert not changed and expected==current
    m=json.loads((E/'before/manifest.json').read_text());inputs=[]
    for row in m['inputs']:
        p=Path(row['path']);inputs.append(dict(path=str(p),sha256=sha(p),unchanged=sha(p)==row['sha256']))
    assert all(x['unchanged'] for x in inputs)
    result=dict(baseline=BASE,named_observation_files=FILES,generated_count=len(before),generated_changed=changed,generated_names_equal=expected==current,inputs=inputs,sources=rows,
                read_only_review='E15 header takes const guest pointers, copies argument/field values into diagnostic state and emits bounded files; runtime/scheduler changes add only gated calls, local Trace scopes, and four bounded Present keeps. E4/E7 changes affect only diagnostic capture state and closure.')
    (E/'source-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print('generated',len(before),'unchanged; config unchanged; MPEG/source receipts unchanged; named observation files',len(FILES))
    print('# E15 SOURCE AUDIT TAIL COMPLETE')
if __name__=='__main__':main()
