#!/usr/bin/env python3
"""Replay E10's retained evidence joins only; no SSD access, build or boot."""
import ast,gzip,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    kept=json.loads((E/'retention.json').read_text())['files'];aliases={r['original']:r for r in kept}
    def read(name):
        if name in aliases:
            r=aliases[name];p=E/r['canonical'];data=gzip.decompress(p.read_bytes()) if r['encoding']=='gzip' else p.read_bytes()
            assert len(data)==r['raw_bytes'] and sha(data)==r['raw_sha256'];return data
        return (E/name).read_bytes()
    def obj(name):return json.loads(read(name))
    for row in kept:read(row['original'])
    before=obj('before/generated.json');after=obj('after/generated.json');output=obj('drop-output.json')
    b={Path(r['path']).name:r['sha256'] for r in before};a={Path(r['path']).name:r['sha256'] for r in after}
    g={r['name']:r['sha256'] for r in output if r['name'].endswith(('.cpp','.h'))}
    assert len(b)==9278 and len(a)==9449 and a==g
    assert len(a.keys()-b.keys())==172 and len(b.keys()-a.keys())==1
    assert len([n for n in a.keys()&b.keys() if a[n]!=b[n]])==2
    gen=obj('drop-generation.json');assert gen['rc']==0 and not gen.get('bound')
    assert len(output)==gen['files']==9450
    assert sum(r['bytes'] for r in output)==gen['logical']==266708892
    assert sum(r['allocated'] for r in output)==gen['allocated']==286580736
    caps=gen['caps'];assert gen['logical']<caps['logical']-caps['output_guard'] and gen['allocated']<caps['allocated']-caps['output_guard']
    assert gen['free_before']>=caps['logical']+caps['free_floor']+caps['free_guard']
    assert gen['free_after']>caps['free_floor']+caps['free_guard']
    registry=read('drop-register_functions.cpp.gz');assert sha(registry)==a['register_functions.cpp']
    text=registry.decode();line=[s for s in text.splitlines() if s.endswith('// 0x426230')]
    assert len(line)==1 and 'sub_00426230_0x426230' in line[0]
    assert not any(s.endswith('// 0x2c5140') for s in text.splitlines())
    body=read('drop-sub_00426230_0x426230.cpp.gz');assert sha(body)==a['sub_00426230_0x426230.cpp']
    assert b'TODO' not in body and b'ps2_stubs::sceSifCmdIntrHdlr' not in body
    for name in ['canonical.csv','canonical.toml','used.csv','used.toml']:assert read('before/'+name)==read('after/'+name)
    assert b'sub_002C5140,' not in read('after/canonical.csv')
    for name in ['canonical.toml','used.toml']:assert b'_sceSifCmdIntrHdlr@0x00426230' not in read('after/'+name)
    suite=read('drop-suite.txt').decode();assert 'Total Tests: 452' in suite and 'Passed: 452' in suite and 'Failed: 0' in suite
    checks=obj('drop-binding-results.json')['runs'];assert [r['rc'] for r in checks]==[0,1]
    assert checks[0]['output']==read('drop-binding-absent.txt').decode() and checks[1]['output']==read('drop-binding-present.txt').decode()
    assert 'sub_00426230_0x426230' in checks[0]['output'] and 'pc=0xf00000 sp=0x100000 v0=0 s0-preserved=1 normal-return=1' in checks[0]['output']
    assert 'QUERY hasFunction=0 expected=0' in checks[0]['output'] and 'QUERY hasFunction=0 expected=1' in checks[1]['output']
    failure=obj('entry-admission-failure.json');assert failure['required']==caps['logical']+caps['free_floor']+caps['free_guard']==3489660928
    assert failure['free_before']==3240579072 and failure['required']-failure['free_before']==failure['shortfall']==249081856
    assert not failure['generator_started'] and failure['boots']==0 and not failure['entry_generated']
    assert not any(E.glob('e10?-result.json')) and not (E/'entry-generation.json').exists()
    closure=obj('closure-restoration.json');assert closure['scratch_absent'] and closure['lease_absent'] and closure['runner_process_check']==1
    assert closure['csv_restored_sha256']==sha(read('before/canonical.csv'))
    manifest=obj('after/manifest.json');assert manifest['executables'][0]['sha256']==closure['runner_restored']['sha256']==obj('drop-build.json')['runner']['sha256']
    assert manifest['git_head']=='be0c9eeaa337d9685e9536fa4f66c5ce5029aad8'
    assert manifest['git_status']==' M ps2xRuntime/src/runner/register_functions.cpp\n'
    for p in E.glob('*.py'):ast.parse(p.read_text(),filename=p.name)
    report=read('REPORT.md').decode();assert report.rstrip().endswith('restored; APFS scratch and lease absent; no ssx3 push; standing no-regen resumed.')
    result=dict(outcome='iii',drop_complete=True,mirror_files=len(a),new_bodies=172,suite_passed=452,suite_failed=0,actual_handler='sub_00426230_0x426230',query_absent=True,entry_admission_shortfall=failure['shortfall'],boots=0,scratch_absent=True,lease_absent=True,retention_records=len(kept))
    (E/'replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));print('# E10 REPLAY TAIL COMPLETE: all retained joins match; no boot/build/regen')
if __name__=='__main__':main()
