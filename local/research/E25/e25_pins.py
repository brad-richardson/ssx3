"""E25 mission 4 -- the OLD-vs-NEW pin table, every E23 checkpoint pin.

For each of the 575 protected paths E23 pinned in the E18 tree: old bytes/sha,
new bytes/sha, match or delta. Plus the four named binaries and the three
tree-level totals. This tool TABLES; it declares no baseline and asserts no
verdict. A path that reappears byte-identical is as interesting as one that
does not, so both are counted and both are listed.
"""
from collections import Counter
from e25_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
E23D = E.parent / 'E23'

manifest = json.loads((E23D / 'protected-build-before.json').read_text())
rows, cat = [], Counter()
size_only, sha_only, both, gone, extra_bytes = [], [], [], [], 0
for row in manifest:
    p = Path(row['path'])
    tree = '/'.join(p.parts[:3])
    if tree != '//tmp/e18-mpeg-link':
        # The other two trees are NOT rebuilt (see e25_common: one tree fits the
        # 3 GiB internal cap, and only this tree holds the runner and suite).
        cat['not_rebuilt_other_tree'] += 1
        continue
    if not p.exists():
        cat['missing_after_rebuild'] += 1
        gone.append(row['path'])
        rows.append(dict(path=row['path'], old_bytes=row['bytes'], old_sha=row['sha256'],
                         present=False, verdict='MISSING'))
        continue
    nb, ns = p.stat().st_size, sha(p)
    same_b, same_s = nb == row['bytes'], ns == row['sha256']
    verdict = ('IDENTICAL' if same_s else
               ('SAME-SIZE-DIFFERENT-SHA' if same_b else 'DIFFERENT'))
    cat[verdict] += 1
    if not same_s:
        (sha_only if same_b else size_only).append(
            dict(path=row['path'], old_bytes=row['bytes'], new_bytes=nb,
                 delta=nb - row['bytes'], old_sha=row['sha256'], new_sha=ns))
    rows.append(dict(path=row['path'], old_bytes=row['bytes'], new_bytes=nb,
                     bytes_delta=nb - row['bytes'], old_sha=row['sha256'],
                     new_sha=ns, present=True, verdict=verdict))

# Files the rebuild produced that E23's manifest did not pin (new graph edges).
pinned = {r['path'] for r in manifest if r['path'].startswith('/tmp/e18-mpeg-link')}
produced = []
for root, _dirs, files in os.walk(B0):
    for n in files:
        q = Path(root) / n
        if q.suffix in ('.o', '.a', '.pch') or q.name in ('ps2EntryRunner', 'ps2x_tests'):
            produced.append(str(q))
unpinned = sorted(set(produced) - pinned)

named = {}
for key, rel in (('runner', 'ps2xRuntime/ps2EntryRunner'), ('suite', 'ps2xTest/ps2x_tests')):
    old = json.loads((E23D / 'final-audit.json').read_text())[key]
    p = B0 / rel
    row = dict(path=str(p), old_bytes=old['bytes'], old_sha=old['sha256'], present=p.exists())
    if p.exists():
        row.update(new_bytes=p.stat().st_size, new_sha=sha(p), new_allocated=p.stat().st_blocks*512)
        row['bytes_equal'] = row['new_bytes'] == old['bytes']
        row['sha_equal'] = row['new_sha'] == old['sha256']
        row['bytes_delta'] = row['new_bytes'] - old['bytes']
    named[key] = row

out = dict(utc=utc(), tree=str(B0), pinned_in_tree=len(pinned),
           categories=dict(cat), rows=rows,
           different_sha_same_size=sha_only, different_size=size_only,
           missing_after_rebuild=gone,
           produced_not_pinned=unpinned, produced_not_pinned_count=len(unpinned),
           named_binaries=named,
           tree_allocated_now=size(B0),
           tree_bytes_pinned_old=sum(r['bytes'] for r in manifest
                                     if r['path'].startswith('/tmp/e18-mpeg-link')))
save('pins.json', out)
print('pinned in E18 tree:', len(pinned))
for k, v in sorted(cat.items()): print(f'  {k:28} {v}')
print('produced but not pinned by E23:', len(unpinned))
for k, v in named.items():
    print(f"  {k:6} present={v['present']} bytes {v.get('old_bytes')} -> {v.get('new_bytes')} "
          f"(delta {v.get('bytes_delta')}) sha_equal={v.get('sha_equal')}")
print('# E25 PINS TAIL COMPLETE')
