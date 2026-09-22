"""The THREE intentional changes on top of the pure hex-safe rename.

Each exists because a PROTECTED build tree was wiped by the host restart and a
gate that E23 asserted can no longer run. None of them weakens an assertion
that is still measurable; each records BLOCKED with its receipt instead of
skipping silently or re-pointing at a different build. Diffs in tooling-diff.md.
"""
import json
from pathlib import Path

CHANGES = [
    ('e24_validate.py', """def suite(label):
    scratch=E/('.suite-'+label);scratch.mkdir(exist_ok=False)""",
     '''def suite(label):
    # E24 CHANGE 1: the suite binary lives in a PROTECTED build tree that the
    # host restart wiped (`env-audit.json`). A missing suite is a BLOCKED gate
    # with its receipt, never a silent skip and never a re-point at another
    # build -- the 458 counts and the E18 R1-R6 text are properties of THAT
    # binary. Callers record the returned row and stop.
    binary=B/'ps2xTest/ps2x_tests'
    if not binary.exists():
        row=dict(label=label,status='BLOCKED',binary=str(binary),present=False,
                 reason='protected build tree absent after host restart')
        save(label+'-suite.json',row)
        print('SUITE',label,'BLOCKED (binary absent)')
        return None,'',row
    scratch=E/('.suite-'+label);scratch.mkdir(exist_ok=False)'''),

    ('e24_baseline.py', "suite('checkpoint')\n",
     """suite_rc,suite_txt,suite_row=suite('checkpoint')
# E24 CHANGE 2: the 458-test suite is BLOCKED (binary wiped with the protected
# build tree). The fixture half below still runs on the SSD-resident, sha-equal
# `binding-test`, so the behavior checkpoint is reported as what it IS:
# fixture gates VERIFIED, suite gate BLOCKED.
"""),
    ('e24_baseline.py', "save('checkpoint-complete.json',dict(utc=utc(),suite=458,closure_cases=6",
     "save('checkpoint-complete.json',dict(utc=utc(),suite=None,suite_status=suite_row.get('status','BLOCKED'),suite_receipt=suite_row,closure_cases=6"),

    ('e24_observer_regression.py', "rows=[]\nfor directory in [E/'.suite-observer/parser-observer',",
     """rows=[]
# E24 CHANGE 3: the suite's own observer dir is BLOCKED with the suite binary.
# In E23 the suite was the ONLY loaded run that reached the parser, so the
# parser-reach receipt moves to the surviving E23 cadence fixture, which drives
# the R3 payload through the actual title wrappers (`e24_cadence.py`). The
# fixture closures below still carry real `# E21 PARSER CLOSURE` footers.
for directory in ["""),
    ('e24_observer_regression.py', "assert rows[0]['footer']['parseCalls']>0\n",
     "assert all(r['footer']['bindingChecks']==4 for r in rows),'loaded bindings not 4/4'\n"),
    ('e24_observer_regression.py', "save('observer-regression.json',dict(utc=utc(),suite=458,",
     "save('observer-regression.json',dict(utc=utc(),suite=None,suite_status='BLOCKED',parser_reach_moved_to='e24_cadence.py',"),
]


def main():
    applied = []
    for name, old, new in CHANGES:
        p = Path(name)
        t = p.read_text()
        assert t.count(old) == 1, (name, old[:60], t.count(old))
        p.write_text(t.replace(old, new))
        applied.append(dict(file=name, removed=old, added=new))
    Path('tooling-changes.json').write_text(json.dumps(dict(
        note='intentional changes on top of the pure hex-safe rename',
        count=len(applied), changes=applied), indent=2) + '\n')
    print(f'applied {len(applied)} intentional changes')
    print('# E24 PATCH TAIL COMPLETE')


if __name__ == '__main__':
    main()
