"""E25 intentional tooling changes, applied idempotently and recorded as data.

The renames from E24 are byte-pure (`rename-proof-hexsafe.json`). E24's tools
encode a BLOCKED suite, because in E24 the suite binary did not exist. E25
rebuilt it, so three E24 CHANGE comments are reverted to the E23 shape they
describe -- the suite runs again, and the suite's own observer directory is
once more the loaded run that reaches the parser. Every edit is a literal
before/after pair; an edit whose `before` is absent is reported, never forced.
"""
import difflib
from e25_common import *

EDITS = [
    ('e25_baseline.py',
     "suite_rc,suite_txt,suite_row=suite('checkpoint')\n"
     "# E25 CHANGE 2: the 458-test suite is BLOCKED (binary wiped with the protected\n"
     "# build tree). The fixture half below still runs on the SSD-resident, sha-equal\n"
     "# `binding-test`, so the behavior checkpoint is reported as what it IS:\n"
     "# fixture gates VERIFIED, suite gate BLOCKED.\n",
     "# E25 CHANGE 1 (reverts E24 CHANGE 2): the suite binary was REBUILT by this\n"
     "# lane, so the 458-test gate runs again instead of reporting BLOCKED. The\n"
     "# presence short-circuit in e25_validate.suite() is kept -- it is the gate\n"
     "# that would catch a failed rebuild -- but it is no longer expected to fire.\n"
     "suite_rc,suite_txt,suite_row=suite('checkpoint')\n"
     "assert suite_rc==0 and suite_row.get('status')!='BLOCKED',suite_row\n",
     'restore the 458-test unloaded suite gate'),

    ('e25_baseline.py',
     "save('checkpoint-complete.json',dict(utc=utc(),suite=None,suite_status=suite_row.get('status','BLOCKED'),suite_receipt=suite_row,",
     "save('checkpoint-complete.json',dict(utc=utc(),suite=458,suite_status='PASS',suite_receipt=suite_row,",
     'record the restored suite count in the checkpoint receipt'),

    ('e25_observer_regression.py',
     "suite('observer')\n",
     "suite_rc,suite_txt,suite_row=suite('observer')\n"
     "assert suite_rc==0 and suite_row.get('status')!='BLOCKED',suite_row\n",
     'assert the observer-LOADED suite ran rather than short-circuiting'),

    ('e25_observer_regression.py',
     "# E25 CHANGE 3: the suite's own observer dir is BLOCKED with the suite binary.\n"
     "# In E23 the suite was the ONLY loaded run that reached the parser, so the\n"
     "# parser-reach receipt moves to the surviving E23 cadence fixture, which drives\n"
     "# the R3 payload through the actual title wrappers (`e25_cadence.py`). The\n"
     "# fixture closures below still carry real `# E21 PARSER CLOSURE` footers.\n"
     "for directory in [*sorted((P/'e25-fixtures/observer-bindings').glob('*/parser-observer')),\n",
     "# E25 CHANGE 2 (reverts E24 CHANGE 3): with the suite rebuilt, the suite's own\n"
     "# observer directory is once more the loaded run that REACHES the parser, so it\n"
     "# leads the closure list exactly as it did in E23 and the parser-reach receipt\n"
     "# returns here from the cadence fixture.\n"
     "for directory in [E/'.suite-observer/parser-observer',\n"
     "                  *sorted((P/'e25-fixtures/observer-bindings').glob('*/parser-observer')),\n",
     "restore the suite's own observer directory as the parser-reach receipt"),

    ('e25_observer_regression.py',
     "assert all(r['footer']['bindingChecks']==4 for r in rows),'loaded bindings not 4/4'\n"
     "save('observer-regression.json',dict(utc=utc(),suite=None,suite_status='BLOCKED',parser_reach_moved_to='e25_cadence.py',",
     "assert all(r['footer']['bindingChecks']==4 for r in rows),'loaded bindings not 4/4'\n"
     "assert rows[0]['footer']['parseCalls']>0,'suite observer dir did not reach the parser'\n"
     "save('observer-regression.json',dict(utc=utc(),suite=458,suite_status='PASS',parser_reach='suite observer dir',",
     'restore E23 parser-reach assertion and the loaded suite count'),
]

rows = []
for name, before, after, why in EDITS:
    p = E / name
    text = p.read_text()
    if after in text:
        rows.append(dict(file=name, why=why, status='ALREADY-APPLIED', applied=False)); continue
    if before not in text:
        rows.append(dict(file=name, why=why, status='ANCHOR-ABSENT', applied=False)); continue
    assert text.count(before) == 1, (name, text.count(before))
    new = text.replace(before, after)
    p.write_text(new)
    rows.append(dict(file=name, why=why, status='APPLIED', applied=True,
                     before_bytes=len(text.encode()), after_bytes=len(new.encode()),
                     diff='\n'.join(difflib.unified_diff(
                         before.splitlines(), after.splitlines(),
                         f'{name} (E24 shape)', f'{name} (E25)', lineterm='', n=0))))

save('tooling-changes.json', dict(utc=utc(), source_lane='E24',
                                  pure_renames='rename-proof-hexsafe.json (9 files, all proofs empty)',
                                  intentional_changes=rows,
                                  applied=sum(r['applied'] for r in rows),
                                  anchors_absent=[r['file'] for r in rows if r['status'] == 'ANCHOR-ABSENT']))
(E / 'tooling-diff.md').write_text(
    '# E25 intentional tooling changes\n\n'
    'Nine tools are byte-pure renames from E24 (`rename-proof-hexsafe.json`).\n'
    '`e25_common.py` is written fresh (internal reservation 3 GiB, declared in\n'
    '`CONTRACT.md`; rebuild target `NEWB = B0`, the E18 path). The edits below\n'
    'revert the three E24 CHANGE comments that exist only because E24 had no\n'
    'suite binary.\n\n' +
    '\n\n'.join(f"## {r['file']} — {r['why']} ({r['status']})\n\n```diff\n{r.get('diff','(no diff: '+r['status']+')')}\n```"
                for r in rows) + '\n\n# E25 TOOLING DIFF TAIL COMPLETE\n')
for r in rows: print(f"{r['status']:<16} {r['file']:<28} {r['why']}")
print('# E25 PATCH TAIL COMPLETE')
