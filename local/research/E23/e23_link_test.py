"""Compile the E23 complete-feed fixture and relink the current, unmodified runner object set."""
import shlex, subprocess, sys
from e23_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
label=sys.argv[1];dest=P/'e23-fixtures'/label;dest.mkdir(parents=True,exist_ok=False)
sources=['e23_complete_test.cpp','e23_payload.inc','e21_binding_test.cpp','e18_binding_test.cpp',
         'e17_binding_test.cpp','e16_binding_test.cpp','e15_binding_test.cpp','prior_binding_test.cpp',
         'e21_parser_observer.h']
source_record=[pin(E/name) for name in sources]
cc=json.loads((B/'compile_commands.json').read_text())
sample=next(c for c in cc if 'ps2EntryRunner.dir' in c['command'] and c['file'].endswith('cxx.cxx'))
args=shlex.split(sample['command']);out=[];skip=False
for a in args:
    if skip:skip=False;continue
    if a=='-o':skip=True;continue
    if a in ('-c',sample['file']):continue
    out.append(a)
out+=['-c',str(E/'e23_complete_test.cpp'),'-o',str(dest/'test.o')]
raw=subprocess.check_output(['ninja','-C',str(B),'-t','commands','ps2EntryRunner'],text=True).splitlines()[-1]
parts=shlex.split(raw);start=parts.index('&&')+1 if parts[0]==':' else 0
end=parts.index('&&',start) if '&&' in parts[start:] else len(parts)
link=parts[start:end];link[link.index('-o')+1]=str(dest/'binding-test')
link+=[str(dest/'test.o'),'-Wl,-e,_e23_binding_main','-Wl,-export_dynamic']
save(label+'-fixture-link.json',dict(compile=out,link=link,cwd=str(B),original_link=raw,fixture_sources=source_record))
for cmd in (out,link):subprocess.run(cmd,cwd=B,check=True)
save(label+'-fixture-binary.json',pin(dest/'binding-test'))
print(dest/'binding-test');print('# E23 ACTUAL OBJECT LINK TAIL COMPLETE')
