"""E29 Mission 2 step 1 -- cut and check out `e29-movie-bypass`.

Deferred to the LAST possible moment: the V1 worker is auditing fork HEAD
concurrently, so the mainline ref is left alone until the build lane actually
needs it. Checkout and check-back times are both recorded.

The branch is cut IN the main fork worktree on purpose. A `git worktree add` or
a second clone would lack the 9,454 gitignored GENERATED guest sources, which
are not in git and cannot be reproduced without a re-recomp the brief forbids.
`git checkout -b` from the sha HEAD is already on moves no tracked file.
"""
import subprocess, sys
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
BRANCH = 'e29-movie-bypass'

def g(*argv, check=True):
    p = subprocess.run(['git', '-C', str(R), *argv], text=True, capture_output=True)
    row = dict(argv=list(argv), rc=p.returncode, stdout=p.stdout, stderr=p.stderr)
    if check: assert p.returncode == 0, row
    return row

before = dict(utc=utc(),
              head=g('rev-parse', 'HEAD')['stdout'].strip(),
              ref=g('rev-parse', '--abbrev-ref', 'HEAD')['stdout'].strip(),
              status=g('status', '--short')['stdout'],
              branch_exists=g('rev-parse', '--verify', BRANCH, check=False)['rc'] == 0)
assert before['head'] == BASE_SHA, before
assert before['status'] == '?? ps2_log.txt\n', before
assert before['ref'] == 'ssx3', before
assert not before['branch_exists'], 'branch already exists -- refusing to re-cut'

# A tracked-file inventory before and after: the checkout must move NOTHING.
def tree_sha(): return g('rev-parse', 'HEAD^{tree}')['stdout'].strip()
tree_before = tree_sha()
mpeg_before = sha(R / 'ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp')

checkout_utc = utc()
co = g('checkout', '-b', BRANCH, BASE_SHA)

after = dict(utc=utc(),
             head=g('rev-parse', 'HEAD')['stdout'].strip(),
             ref=g('rev-parse', '--abbrev-ref', 'HEAD')['stdout'].strip(),
             status=g('status', '--short')['stdout'],
             tree=tree_sha(),
             mpeg_sha=sha(R / 'ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp'))

checks = dict(
    branch_name_exact=after['ref'] == BRANCH,
    fork_point_is_base=after['head'] == BASE_SHA,
    tree_unmoved=after['tree'] == tree_before,
    mpeg_unmoved=after['mpeg_sha'] == mpeg_before,
    status_unchanged=after['status'] == before['status'],
    worktree_is_the_main_fork_worktree=str(R) == g('rev-parse', '--show-toplevel')['stdout'].strip(),
)
green = all(checks.values())
save('branch-cut.json', dict(utc=utc(), branch=BRANCH, fork_point=BASE_SHA,
                             checkout_utc=checkout_utc, checkback_utc=None,
                             before=before, after=after, checks=checks, green=green,
                             command=co,
                             why_in_place=('a separate worktree/clone would lack the gitignored '
                                           'generated guest sources; re-recomp is not a permitted mutation')))
print(json.dumps(dict(branch=BRANCH, fork_point=BASE_SHA, checkout_utc=checkout_utc,
                      ref=after['ref'], head=after['head'], status=after['status'],
                      checks=checks), indent=2))
print('# E29 BRANCH TAIL COMPLETE green=' + ('1' if green else '0'))
assert green, checks
