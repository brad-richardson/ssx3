"""Audit the mechanical carry for RENAME-INDUCED DANGLING PATHS.

Errata E23-E1 protected hex digests from the lane rename. This audit covers the
neighbouring hazard: a REAL PATH whose spelling happens to contain the source
lane's token. `e26_restore_gate.py` reads E25's readiness receipt, and E25 named
that file `e26-readiness.json` -- so the e26->e29 carry rewrote it to a path
that does not exist. The rename proof was blind to it, because the normalized
diff maps both tokens to one placeholder and the file is *supposed* to change
there.

This tool resolves EVERY cross-lane `E.parent / 'EXX/...'` literal in every
carried tool and requires the file to exist. It is the check that catches the
class, not the instance.
"""
import re
from e29_common import *

LANE_REF = re.compile(r"E\.parent\s*/\s*f?'(E\d\d)/([^']*)'")
FSTR = re.compile(r"\{[^}]*\}")
rows = []
for tool in sorted(E.glob('e29_*.py')):
    text = tool.read_text()
    for lane, rel in LANE_REF.findall(text):
        target = E.parent / lane / rel
        templated = bool(FSTR.search(rel))
        exists = any(E.parent.joinpath(lane).glob(FSTR.sub('*', rel))) if templated else target.exists()
        rows.append(dict(tool=tool.name, lane=lane, rel=rel, path=str(target),
                         templated=templated, exists=exists,
                         carries_e29_token=('e29' in rel or 'E29' in rel)))
dangling = [r for r in rows if not r['exists']]
save('carry-audit.json', dict(utc=utc(),
     what='every cross-lane path literal in every carried E29 tool, resolved',
     rule='a real path that contains the source lane token must be PROTECTED, not renamed',
     references=len(rows), dangling=dangling, green=not dangling, rows=rows))
for r in rows:
    print(f"{'OK  ' if r['exists'] else 'DANGLING'}  {r['tool']:<24} {r['lane']}/{r['rel']}")
print('references', len(rows), 'dangling', len(dangling))
print('# E29 CARRY AUDIT TAIL COMPLETE green=' + ('1' if not dangling else '0'))
assert not dangling, dangling
