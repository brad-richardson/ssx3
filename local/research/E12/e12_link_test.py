#!/usr/bin/env python3
"""Relink current runner objects with a separate test entry; registry is unchanged."""
import json, os, shlex, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
B=Path('/tmp/p1-link/runtime')
def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    label=sys.argv[1]; dest=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/e12-binding-tests')/label; dest.mkdir(exist_ok=True,parents=True)
    cc=json.loads((B/'compile_commands.json').read_text())
    sample=next(c for c in cc if 'ps2EntryRunner.dir' in c['command'] and c['file'].endswith('cxx.cxx'))
    args=shlex.split(sample['command']); out=[];skip=False
    for n,a in enumerate(args):
        if skip: skip=False;continue
        if a == '-o':skip=True;continue
        if a in ['-c',sample['file']]:continue
        out.append(a)
    out+=['-c',str(HERE/'e12_binding_test.cpp'),'-o',str(dest/'test.o')]
    raw=subprocess.check_output(['ninja','-C',str(B),'-t','commands','ps2EntryRunner'],text=True).splitlines()[-1]
    parts=shlex.split(raw); start=parts.index('&&')+1 if parts[0]==':' else 0
    end=parts.index('&&',start) if '&&' in parts[start:] else len(parts)
    link=parts[start:end]; link[link.index('-o')+1]=str(dest/'binding-test')
    link += [str(dest/'test.o'),'-Wl,-e,_e12_binding_main','-Wl,-export_dynamic']
    record=dict(compile=out,link=link,cwd=str(B),original_link=raw)
    (HERE/f'{label}-binding-link.json').write_text(json.dumps(record,indent=2)+'\n')
    for cmd in [out,link]: subprocess.run(cmd,cwd=B,check=True)
    print(dest/'binding-test')
if __name__=='__main__':main()
