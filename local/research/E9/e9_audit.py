#!/usr/bin/env python3
"""Offline audit of E9's completed receipts; no boot or regeneration."""
import gzip, hashlib, json, tomllib
from pathlib import Path
E=Path(__file__).resolve().parent
def read(name):return json.loads((E/name).read_text())
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    checks=[]
    def check(name,condition):
        assert condition,name;checks.append(name);print(name)
    for which in ['canonical','used']:
        old=(E/'before'/f'{which}.toml').read_bytes();new=(E/f'after-{which}.toml').read_bytes()
        a=tomllib.loads(old.decode());b=tomllib.loads(new.decode())
        selector='_sceSifCmdIntrHdlr@0x00426230'
        check(f'{which}: exactly the authorized selector removed',selector in a['general']['stubs'] and selector not in b['general']['stubs'])
        a['general']['stubs'].remove(selector)
        check(f'{which}: all other config values preserved',a==b)
    before=read('before/manifest.json');generated=read('before/generated.json')
    check('active generated census pinned',len(generated)==before['generated_files']==9276)
    table=next(x for x in generated if x['path'].endswith('/register_functions.cpp'))
    raw=gzip.open(E/'before/register_functions.cpp.gz','rb').read()
    check('retained actual registry hash matches baseline',sha(raw)==table['sha256'])
    lines=[x for x in raw.decode().splitlines() if x.rstrip().endswith('// 0x426230')]
    check('baseline handler table points to guest owner',len(lines)==1 and 'sub_004261F0' in lines[0])
    check('baseline query table absent',not any(x.rstrip().endswith('// 0x2c5140') for x in raw.decode().splitlines()))
    check('all active generated sources unchanged',read('active-unchanged.json')['drift']==[])
    check('baseline actual handler normal return recorded','normal-return=1' in (E/'before-binding-test.txt').read_text())
    check('actual query fail-before recorded',read('query-fail-before.json')['rc']==1 and 'QUERY hasFunction=0 expected=1' in (E/'query-fail-before.txt').read_text())
    suite=(E/'drop-suite.txt').read_text()
    check('full suite 452/452','Total Tests: 452' in suite and 'Passed: 452' in suite and 'Failed: 0' in suite)
    rows=read('drop-partial-output.json');summary=read('drop-partial-summary.json');run=read('drop-regen.json')
    for side,key in [(False,'sources'),(True,'sidecars')]:
        group=[r for r in rows if r['sidecar']==side]
        check(f'partial {key} complete accounting',summary[key]==dict(files=len(group),bytes=sum(r['bytes'] for r in group),allocated=sum(r['allocated'] for r in group)))
    check('recorded output cap selected',run['cap_bound'] and run['rc']==-15 and sum(r['allocated'] for r in rows)>run['caps']['output_allocated'])
    check('registry never emitted',not summary['table_present'] and not any(r['name']=='register_functions.cpp' for r in rows))
    header=gzip.open(E/'drop-partial-functions.h.gz','rt').read()
    check('partial header declares guest handler but not query','void sub_00426230_0x426230(' in header and 'sub_002C5140' not in header)
    clean=read('cleanup.json')
    check('cleanup joins to complete partial manifest',clean['verified_files']==len(rows) and clean['partial_manifest_sha256']==sha((E/'drop-partial-output.json').read_bytes()))
    check('active binaries unchanged',all(x['unchanged'] for x in read('after-binaries.json')))
    close=read('closure.json')
    check('fork remote receipt matches DROP commit',close['remote']['stdout'].startswith('be0c9eeaa337d9685e9536fa4f66c5ce5029aad8'))
    check('no runner, generator or lease at closure',close['runner']['rc']==close['generator']['rc']==1 and close['lease_absent'])
    check('report tail present',(E/'REPORT.md').read_text().endswith('held, ONE next action in NEXT-BRIEF.md. Standing no-regen resumes now.\n'))
    print(f'# E9 AUDIT TAIL COMPLETE checks={len(checks)} outcome=iii boots=0')
if __name__=='__main__':main()
