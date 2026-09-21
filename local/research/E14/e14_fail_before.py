#!/usr/bin/env python3
"""Record all five baseline absence/presence expectations on actual bindings."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
from e14_rows import SPECS
E=Path(__file__).resolve().parent;R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
B=R.parent/'P1/e14-binding-tests/baseline/binding-test'
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert json.loads((E/'baseline-link-bounded-result.json').read_text())['rc']==0
gate=json.loads((E/'checkpoint.json').read_text());assert 'fail_before_utc' not in gate
rows=[]
for pc,*_ in SPECS:
    row=dict(pc=hex(pc))
    for mode,want in [('check-absent',0),('check-present',1)]:
        args=[str(B),mode,hex(pc)]
        p=subprocess.run(args,cwd=R,capture_output=True,text=True)
        out=p.stdout+p.stderr;(E/f'baseline-{pc:x}-{mode}.txt').write_text(out)
        row[mode]=dict(argv=args,rc=p.returncode)
        assert p.returncode==want and f'pc={pc:#x} hasFunction=0' in out,(pc,mode,p.returncode,out)
    rows.append(row)
gate.update(binding_absent_rc=0,binding_present_rc=1,fail_before_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),fail_befores=rows,baseline_binding_sha256=hashlib.sha256(B.read_bytes()).hexdigest())
(E/'checkpoint.json').write_text(json.dumps(gate,indent=2)+'\n')
(E/'baseline-binding-results.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2));print('# E14 FIVE FAIL-BEFORES TAIL COMPLETE — no CSV mutation')
