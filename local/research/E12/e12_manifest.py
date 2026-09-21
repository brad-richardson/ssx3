#!/usr/bin/env python3
"""Pin E12 configs, active generated sources/bindings and executable identity."""
import gzip, hashlib, json, os, re, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
W=Path('/Volumes/Extreme SSD/ps2recomp-spike'); R=W/'PS2Recomp'
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def pin(p):
    s=p.stat(); return dict(path=str(p),bytes=s.st_size,allocated=s.st_blocks*512,sha256=sha(p))
def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    label=sys.argv[1]; out=HERE/label; out.mkdir(exist_ok=False)
    sources=list((R/'ps2xRuntime/src/runner').glob('*.cpp'))+list((R/'ps2xRuntime/src/runner').glob('ps2_recompiled_*.h'))+list((R/'ps2xRuntime/include').glob('ps2_recompiled_*.h'))
    sources=[p for p in sources if not p.name.startswith('._')]
    rows=[pin(p) for p in sorted(sources)]
    (out/'generated.json').write_text(json.dumps(rows,indent=2)+'\n')
    table=R/'ps2xRuntime/src/runner/register_functions.cpp'
    text=table.read_text(); matches=re.findall(r'\[(\d+)\]\s*=\s*([^,\n]+)',text)
    # Preserve the exact full table as well as the parsed representation.
    with gzip.open(out/'register_functions.cpp.gz','wb',compresslevel=9) as f:f.write(table.read_bytes())
    bindings=[]
    for line in text.splitlines():
        if ('0x' in line and ('sub_' in line or 'ps2_stubs' in line or 'ps2_syscalls' in line)):
            bindings.append(line)
    selected={hex(pc):[line for line in bindings if line.rstrip().endswith(f'// 0x{pc:x}')]
              for pc in [0x2c50e0,0x2c5140,0x2c52d8,0x2c5300,0x2c5358,0x426230]}
    (out/'binding-targets.json').write_text(json.dumps(dict(registry_sha256=sha(table),targets=selected),indent=2)+'\n')
    paths={'canonical.toml':R/'games/ssx3/ssx3.toml','used.toml':W/'P1/ssx3.toml',
           'canonical.csv':R/'games/ssx3/ssx3-functions.sweep.csv','used.csv':W/'P1/ssx3-functions.sweep.csv'}
    inputs=[]
    for name,p in paths.items():
        inputs.append(pin(p)); (out/name).write_bytes(p.read_bytes())
    for p in sources:
        if any(s in p.name for s in ['002C50E0','002C5140','002C52D8','002C5300','002C5338','004261F0','00426230']):
            with gzip.open(out/(p.name+'.gz'),'wb',compresslevel=9) as f:f.write(p.read_bytes())
    executables=[]
    for p in [Path('/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner'),Path('/tmp/p1-link/runtime/ps2xTest/ps2x_tests'),W/'P1/SLUS_207.72']:
        executables.append(pin(p))
    record=dict(label=label,inputs=inputs,executables=executables,generated_files=len(rows),
                generated_bytes=sum(x['bytes'] for x in rows),generated_allocated=sum(x['allocated'] for x in rows),
                git_head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),
                git_status=subprocess.check_output(['git','-C',str(R),'status','--short'],text=True))
    (out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n'); print(json.dumps(record,indent=2))
if __name__=='__main__':main()
