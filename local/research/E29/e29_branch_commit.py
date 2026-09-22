"""E29 -- commit the bypass on `e29-movie-bypass`, then RETURN to mainline.

One commit on the branch (the project's stacked-branch rule: one commit per
branch, amend if it needs changing). NEVER merged, NEVER pushed. The check-back
happens immediately afterwards so the window in which the fork's HEAD is moved
is as short as possible -- the V1 worker is auditing fork HEAD concurrently.
"""
import subprocess
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
BRANCH = 'e29-movie-bypass'
REL = 'ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp'

def g(*a, check=True):
    p = subprocess.run(['git', '-C', str(R), *a], text=True, capture_output=True)
    if check: assert p.returncode == 0, dict(argv=a, rc=p.returncode, err=p.stderr, out=p.stdout)
    return p.stdout

assert g('rev-parse', '--abbrev-ref', 'HEAD').strip() == BRANCH
MSG = """[E29] DEV-ONLY startup-movie bypass behind PS2X_SKIP_MOVIE (default OFF)

Development bring-up scaffolding for the native gameplay path. NOT a fix, and
NOT on any default path: with PS2X_SKIP_MOVIE unset the faithful movie path is
byte-for-byte what it was at 3adc0478, and the full 458-test suite is 458/458.

One env-gated block in getMpegPicture, above the four-term guard that reaches
waitExternal(EeWaitReason::Mpeg, kMpegPictureWaitType, ...). E27 named that
latch and E28 closed the guest half; the bypass suspends only the PARK, after
the producer dispatch and the guest's own sceMpegAddBs feed, so a flag-on run
reproduces the faithful run up to and including the 5,040-byte parser feed and
diverges only where the title would otherwise stop forever. Marking the
playback ended puts the state machine in the state finishPlaybackStream() and
the program-end path already produce, so the guest takes its OWN end-of-stream
exit rather than blocking. The decoder is deliberately not flushed: the bypass
synthesizes no frames.

With the flag ON, five of the project's own tests fail by construction -- the
MPEG non-stream R1/R2/R4/R6 contract tests and "sceMpegGetPicture waits for new
decoder output instead of duplicating the last frame". That is the measured
reason this is a flag and not a change: those five are the regression bar the
faithful fix (E30) must hold WITHOUT one.

Branch is local-only. Never merge, never push.

Orchestrated-By: Muse Code
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
"""
(E / 'branch-commit-message.txt').write_text(MSG)
g('add', '--', REL)
g('commit', '-F', str(E / 'branch-commit-message.txt'))
commit = g('rev-parse', 'HEAD').strip()
show = g('show', '--stat', '--format=%H%n%an%n%s', 'HEAD')
status_on_branch = g('status', '--short')

checkback_utc = utc()
g('checkout', 'ssx3')
after = dict(utc=utc(),
             ref=g('rev-parse', '--abbrev-ref', 'HEAD').strip(),
             head=g('rev-parse', 'HEAD').strip(),
             status=g('status', '--short'),
             mpeg_sha=sha(R / REL),
             branch_head=g('rev-parse', BRANCH).strip(),
             branch_parent=g('rev-parse', BRANCH + '^').strip())

checks = dict(
  branch_has_exactly_one_commit=g('rev-list', '--count', f'{BASE_SHA}..{BRANCH}').strip() == '1',
  branch_parent_is_fork_point=after['branch_parent'] == BASE_SHA,
  back_on_mainline=after['ref'] == 'ssx3',
  mainline_head_is_base=after['head'] == BASE_SHA,
  mainline_status_pinned=after['status'] == '?? ps2_log.txt\n',
  mainline_mpeg_restored=after['mpeg_sha'] == 'f83ed02e21eba7cbbcecf8443740b13f8ee07ecdb77991da571fef38404ef600',
  branch_not_merged_into_mainline=g('branch', '--merged', 'ssx3').find(BRANCH) == -1,
  nothing_pushed=g('log', '--oneline', f'fork/ssx3..{BRANCH}', check=False).count('\n') == 1,
)
green = all(checks.values())
save('branch-commit.json', dict(utc=utc(), branch=BRANCH, commit=commit,
                                fork_point=BASE_SHA, checkback_utc=checkback_utc,
                                status_on_branch_after_commit=status_on_branch,
                                show=show, after=after, checks=checks, green=green,
                                pushed=False, merged=False))
print(show)
print(json.dumps(dict(commit=commit, checkback_utc=checkback_utc, after={k: v for k, v in after.items() if k != 'status'},
                      status=after['status'], checks=checks), indent=2))
print('# E29 BRANCH-COMMIT TAIL COMPLETE green=' + ('1' if green else '0'))
assert green, checks
