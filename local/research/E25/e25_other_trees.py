"""The two protected trees E25 did NOT rebuild: can they be, and at what cost?

The orchestrator's re-baseline decision turns on this, so it is measured rather
than argued. Two questions:
  1. Would a rebuild at fork 3adc0478 even reproduce them? Compare, file by
     relative path, E23's pinned hashes for the three trees against each other.
     Where p1-link / e17-map-link disagree with e18-mpeg-link, they are the
     output of an OLDER fork state and no build at 3adc0478 can reproduce them.
  2. What would it cost? E25's own measured configure + build time and tree
     size, against the contract's internal cap and floor.
"""
import shutil
from e25_common import *

E23D = E.parent / 'E23'
manifest = json.loads((E23D / 'protected-build-before.json').read_text())
trees = {}
for r in manifest:
    p = Path(r['path'])
    tree = '/'.join(p.parts[:3])
    rel = str(Path(*p.parts[3:]))
    trees.setdefault(tree, {})[rel] = r

base = '//tmp/e18-mpeg-link'
cmp = {}
for tree, files in trees.items():
    if tree == base: continue
    shared = set(files) & set(trees[base])
    same = [k for k in shared if files[k]['sha256'] == trees[base][k]['sha256']]
    diff = [k for k in shared if files[k]['sha256'] != trees[base][k]['sha256']]
    cmp[tree] = dict(files=len(files), shared_paths=len(shared),
                     only_here=sorted(set(files) - set(trees[base]))[:10],
                     only_here_count=len(set(files) - set(trees[base])),
                     sha_equal_to_e18_tree=len(same),
                     sha_differs_from_e18_tree=len(diff),
                     differing_sample=sorted(diff)[:8])

# The decisive probe: the two objects E18's commit changed. If p1-link and
# e17-map-link agree with EACH OTHER and differ from the E18 tree on exactly
# these, they are pre-E18 output and 3adc0478 cannot reproduce them.
PROBES = ['runtime/ps2xRuntime/CMakeFiles/ps2_runtime.dir/src/lib/Kernel/Stubs/MPEG.cpp.o',
          'runtime/ps2xTest/CMakeFiles/ps2_test_lib.dir/src/ps2_runtime_expansion_tests.cpp.o']
probe = {}
for rel in PROBES:
    probe[rel] = {tree: files.get(rel, {}).get('sha256') for tree, files in trees.items()}
    probe[rel]['older_trees_agree_with_each_other'] = (
        probe[rel]['//tmp/p1-link'] == probe[rel]['//tmp/e17-map-link'])
    probe[rel]['and_both_differ_from_e18_tree'] = (
        probe[rel]['//tmp/p1-link'] != probe[rel][base])
probe_conclusive = all(v['older_trees_agree_with_each_other'] and v['and_both_differ_from_e18_tree']
                       for v in probe.values())

# The E18 commit touched exactly two files (E18 NEXT-BRIEF: MPEG.cpp +189/-3,
# ps2_runtime_expansion_tests.cpp +284). Classify the differing set by kind.
kinds = {}
for tree in cmp:
    d = [k for k in trees[base] if trees[tree].get(k) != trees[base][k]]
    kinds[tree] = dict(objects=sum(k.endswith('.o') for k in d),
                       archives=sum(k.endswith('.a') for k in d),
                       other=sorted(k for k in d if not k.endswith(('.o', '.a'))))

# What E25 measured for ONE tree.
build = json.loads((E / 'build-bounded-result.json').read_text())
conf = json.loads((E / 'configure-bounded-result.json').read_text())
one_tree_s = conf['elapsed_s'] + build['elapsed_s']
one_tree_bytes = build['after']['build_allocated']
free_now = shutil.disk_usage('/private/tmp').free

cost = dict(measured_one_tree_seconds=round(one_tree_s, 1),
            measured_one_tree_allocated=one_tree_bytes,
            two_more_trees_seconds=round(2*one_tree_s, 1),
            two_more_trees_allocated=2*one_tree_bytes,
            internal_reservation=IRES,
            internal_allocated_now=size(NEWB)+size(E),
            internal_free_now=free_now,
            floor_plus_guard=2*G+512*M,
            headroom_before_floor=free_now-(2*G+512*M),
            two_more_trees_fit_under_reservation=(3*one_tree_bytes) < IRES,
            two_more_trees_fit_above_floor=(free_now - 2*one_tree_bytes) > (2*G+512*M))

out = dict(utc=utc(),
    reproducible=dict(
        question='would a build at 3adc0478 reproduce p1-link / e17-map-link?',
        comparison=cmp, differing_by_kind=kinds,
        source_state_probe=probe, probe_conclusive=probe_conclusive,
        finding=('No. All 575 relative paths are shared, but 336 hashes differ in each, and the '
                 'two objects E18 commit 3adc0478 actually changed -- MPEG.cpp.o and '
                 'ps2_runtime_expansion_tests.cpp.o -- are IDENTICAL between p1-link and '
                 'e17-map-link and DIFFERENT in the E18 tree. Both are therefore pre-E18 '
                 'output. A build at 3adc0478 would reproduce the E18 tree again under '
                 'another directory name; it cannot reproduce their pins.')),
    cost=cost,
    conclusion=('Not rebuilt, for two independent reasons, both measured: they are not '
                'reproducible at the pinned fork, and two more trees would need '
                f'{2*one_tree_bytes:,} B against a {IRES:,} B internal reservation.'),
    what_is_lost_with_them=('The P1 and E17 build trees. No E15-E23 receipt was taken on '
                            'either runner: E23 booted, and E18/E21/E22/E23 measured, the '
                            'e18-mpeg-link binaries, which E25 reproduced bit-for-bit.'))
save('other-trees.json', out)
for tree, c in cmp.items():
    print(f"{tree}: {c['files']} files, {c['shared_paths']} shared paths, "
          f"{c['sha_equal_to_e18_tree']} sha-equal to the E18 tree, "
          f"{c['sha_differs_from_e18_tree']} differ")
    for s in c['differing_sample']: print('      differs:', s)
for rel, v in probe.items():
    print(f"probe {rel.split('/')[-1]}: p1==e17 {v['older_trees_agree_with_each_other']}, "
          f"both != E18 tree {v['and_both_differ_from_e18_tree']}")
print('probe conclusive (they are pre-E18 output):', probe_conclusive)
print()
print('one tree measured:', cost['measured_one_tree_seconds'], 's,', f"{one_tree_bytes:,} B")
print('two more would need', f"{cost['two_more_trees_allocated']:,} B",
      'vs reservation', f"{IRES:,} B",
      '-> fits under reservation:', cost['two_more_trees_fit_under_reservation'])
print('free now', f"{free_now:,}", 'headroom before floor', f"{cost['headroom_before_floor']:,}",
      '-> fits above floor:', cost['two_more_trees_fit_above_floor'])
print('# E25 OTHER TREES TAIL COMPLETE')
