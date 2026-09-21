"""Compile non-title fixture and relink the current, unmodified runner object set."""
import shlex, subprocess, sys
from e17_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
label=sys.argv[1];dest=P/'e17-fixtures'/label;dest.mkdir(parents=True,exist_ok=False)
source_record=[pin(E/name) for name in ['e17_binding_test.cpp','e16_binding_test.cpp','e15_binding_test.cpp','prior_binding_test.cpp']]
assert all(sha(p['path'])==p['sha256'] for p in source_record), 'fixture source drift from before/after proof'
cc=json.loads((B/'compile_commands.json').read_text())
sample=next(c for c in cc if 'ps2EntryRunner.dir' in c['command'] and c['file'].endswith('cxx.cxx'))
args=shlex.split(sample['command']);out=[];skip=False
for a in args:
    if skip:skip=False;continue
    if a=='-o':skip=True;continue
    if a in ('-c',sample['file']):continue
    out.append(a)
out+=['-c',str(E/'e17_binding_test.cpp'),'-o',str(dest/'test.o')]
raw=subprocess.check_output(['ninja','-C',str(B),'-t','commands','ps2EntryRunner'],text=True).splitlines()[-1]
parts=shlex.split(raw);start=parts.index('&&')+1 if parts[0]==':' else 0;end=parts.index('&&',start) if '&&' in parts[start:] else len(parts)
link=parts[start:end];link[link.index('-o')+1]=str(dest/'binding-test')
link+=[str(dest/'test.o'),'-Wl,-e,_e17_binding_main','-Wl,-export_dynamic']
save(label+'-fixture-link.json',dict(compile=out,link=link,cwd=str(B),original_link=raw,fixture_sources=source_record))
for cmd in (out,link):subprocess.run(cmd,cwd=B,check=True)
save(label+'-fixture-binary.json',pin(dest/'binding-test'))
print(dest/'binding-test');print('# E17 ACTUAL OBJECT LINK TAIL COMPLETE')
