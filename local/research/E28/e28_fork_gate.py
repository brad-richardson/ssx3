"""E28 gate 1, run BEFORE anything else touches a build: fork triple-agree.

Mission 1 of the brief: "fork triple-agree `3adc0478` FIRST (any fork red ->
table + stop -- do not build on a moved fork)". This tool is standalone and
read-only. It exits non-zero on ANY disagreement, so no later step can run on a
moved fork. It asserts nothing away: a red result is SAVED and then raised.
"""
import subprocess
from e28_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'

def run(argv):
    p = subprocess.run([str(x) for x in argv], text=True, capture_output=True)
    return dict(argv=[str(x) for x in argv], rc=p.returncode, stdout=p.stdout, stderr=p.stderr)

head = run(['git', '-C', R, 'rev-parse', 'HEAD', 'refs/remotes/fork/ssx3'])
remote = run(['git', '-C', R, 'ls-remote', 'fork', 'refs/heads/ssx3'])
status = run(['git', '-C', R, 'status', '--short'])

checks = {}
checks['head_rc0'] = head['rc'] == 0
checks['remote_rc0'] = remote['rc'] == 0
checks['status_rc0'] = status['rc'] == 0
lines = head['stdout'].splitlines()
checks['head_equals_base'] = lines[:1] == [BASE_SHA]
checks['ref_equals_base'] = lines[1:2] == [BASE_SHA]
checks['ls_remote_equals_base'] = bool(remote['stdout'].split()) and remote['stdout'].split()[0] == BASE_SHA
# E23/E24 both recorded `status --short` as exactly `?? ps2_log.txt` with a
# preexisting AppleDouble Git-index warning on stderr only. Carried verbatim.
checks['worktree_clean_as_pinned'] = status['stdout'] == '?? ps2_log.txt\n'

green = all(checks.values())
out = dict(utc=utc(), gate='fork triple-agree', expected=BASE_SHA,
           head=lines[0] if lines else None,
           remote_ref=lines[1] if len(lines) > 1 else None,
           ls_remote=remote['stdout'].split()[0] if remote['stdout'].split() else None,
           status_short=status['stdout'],
           status_stderr_preexisting=status['stderr'],
           checks=checks, green=green,
           commands=[head, remote, status])
save('fork-gate.json', out)
print(json.dumps({k: v for k, v in out.items() if k != 'commands'}, indent=2))
print('# E28 FORK GATE TAIL COMPLETE green=' + ('1' if green else '0'))
if not green:
    raise SystemExit('FORK RED - table and stop; do not build on a moved fork')
