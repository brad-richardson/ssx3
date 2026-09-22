"""E29 open: fork allocation baseline + initial admission against the contract.

E29 CHANGE 4, declared: unlike E22-E28, this lane DOES mutate the fork worktree
-- exactly twice, as the brief permits (the `e29-movie-bypass` checkout and the
Mission-1 bypass diff) -- and DOES build, into a NEW dir on the SSD. So the
baseline is not here to prove "fork growth 0"; it is here to MEASURE the growth
the two permitted mutations cause, and to prove at close that nothing else did.
"""
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'

allocated = {}
for root in [R/'.git', R/'ps2xRuntime/src/lib/Kernel/Stubs', R/'ps2xTest/src']:
    for p in [root, *root.rglob('*')]:
        try: allocated[str(p)] = p.lstat().st_blocks*512
        except FileNotFoundError: pass
save('fork-allocation-before.json', dict(utc=utc(), allocated=allocated, paths=len(allocated)))

s = sample()
admission(s)
save('admission-open.json', dict(utc=utc(), reservation_internal=IRES,
                                 reservation_ssd=SSD_CAP, build_dir_cap=BUILD_CAP, floor=2*G, guard=512*M,
                                 sample=s, bound=bound(s),
                                 internal_free_required=2*G+512*M+max(0, IRES-s['internal_allocated']),
                                 ssd_free_required=2*G+512*M+max(0, SSD_CAP-s['ssd_allocated']),
                                 note=('E29 CHANGE 2/3: internal_allocated now covers EVIDENCE ONLY -- the '
                                       '1.6 GB mainline E18 tree at /tmp/e18-mpeg-link is pinned, not owned, '
                                       'and is neither rebuilt nor deleted. The bypass build is charged to '
                                       'the SSD caps (build dir <= 6 GB, all e29-* <= 16 GB).')))
print('fork allocation paths', len(allocated))
print('internal free', s['internal_free'], 'required', 2*G+512*M+max(0, IRES-s['internal_allocated']))
print('ssd free', s['ssd_free'], 'required', 2*G+512*M+max(0, SSD_CAP-s['ssd_allocated']))
print('bound', bound(s))
print('# E29 OPEN TAIL COMPLETE')
