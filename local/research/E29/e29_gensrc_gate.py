"""E29 Mission 2 close -- the generated guest sources are UNMOVED.

The 9,454 generated sources are gitignored and live only on the SSD, so a
branch checkout or a build could in principle have disturbed them and git would
never say so. E27 committed their SHAs into this repo; E28 used those committed
values as corroboration. E29 does the same, on BOTH of E27's passes, AFTER the
branch round-trip and the build.

This is the row that proves the two permitted worktree mutations were the only
ones: MPEG.cpp changed and came back, and nothing generated moved at all.
"""
import sys
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
PASS = sys.argv[1] if len(sys.argv) > 1 else '1'

p1 = {r['path']: r for r in json.loads((E.parent / 'E27' / 'pins-pass-1.json').read_text())['rows']}
p2 = {r['path']: r for r in json.loads((E.parent / 'E27' / 'pins-pass-2.json').read_text())['rows']}

rows, bad = [], []
for path, ref in sorted(p1.items()):
    q = Path(path)
    row = dict(path=path, kind=ref['kind'], present=q.exists())
    if q.exists():
        row.update(bytes=q.stat().st_size, sha256=sha(q),
                   E27_pass1_sha256=ref['sha256'],
                   E27_pass2_sha256=p2.get(path, {}).get('sha256'))
        row['equals_E27_pass1'] = row['sha256'] == ref['sha256']
        row['equals_E27_pass2'] = row['sha256'] == row['E27_pass2_sha256']
        row['bytes_equal'] = row['bytes'] == ref['bytes']
        if not (row['equals_E27_pass1'] and row['equals_E27_pass2'] and row['bytes_equal']):
            bad.append(row)
    else:
        bad.append(row)
    rows.append(row)

green = not bad
save(f'gensrc-gate-pass-{PASS}.json', dict(
    utc=utc(), pass_id=PASS, source='E27/pins-pass-{1,2}.json (git-tracked in this repo)',
    checked=len(rows), disagreements=bad, green=green,
    after=['branch checkout', 'bypass diff', 'configure x2', 'build', 'branch commit', 'checkback'],
    rows=rows))
print(f'generated/pinned sources checked: {len(rows)}  disagreements: {len(bad)}')
for r in rows[:4]:
    print(f"  {Path(r['path']).name:<34} {r.get('bytes',0):>8,} B  {'OK' if r.get('equals_E27_pass1') else 'MOVED'}")
print('# E29 GENSRC GATE TAIL COMPLETE pass=%s green=%s' % (PASS, '1' if green else '0'))
assert green, bad
