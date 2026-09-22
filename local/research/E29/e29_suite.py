"""E29 -- the 458-test suite on the NEW bypass binary with the flag OFF.

CWD MATTERS: E28 ran the suite with cwd = the FORK WORKTREE ROOT, and one test
("VU0 macro mappings cover all S1/S2 enums") reads a file relative to it. Run
from the binary's own directory, that test fails -- on the MAINLINE binary too,
measured. E29 reproduces E28's cwd exactly so the 458/458 gate means the same
thing it meant for E28.

This is the FAITHFUL-EQUIVALENCE gate: with PS2X_SKIP_MOVIE unset, the bypass
build must be indistinguishable from the mainline build on every test the
project has. It is ALSO the corroboration the standing SSD rule demands -- a
binary that read back as zeros cannot run 458 tests.

The flag's absence is asserted, not assumed.
"""
import subprocess, sys, time
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
LABEL = sys.argv[1] if len(sys.argv) > 1 else 'flagoff'
FLAG = sys.argv[2] if len(sys.argv) > 2 else None   # None = OFF

env = dict(os.environ)
env.pop('PS2X_SKIP_MOVIE', None)
if FLAG is not None:
    env['PS2X_SKIP_MOVIE'] = FLAG
assert (FLAG is None) == ('PS2X_SKIP_MOVIE' not in env)

binary = BYPASS_SUITE
assert binary.exists(), binary
t = time.time()
p = subprocess.run([str(binary)], cwd=str(R), env=env,
                   text=True, capture_output=True, timeout=1800)
el = round(time.time() - t, 1)
out = p.stdout + p.stderr
(E / f'suite-{LABEL}.txt').write_text(out)

def grab(key):
    for line in out.splitlines():
        if line.strip().startswith(key):
            return line.strip()
    return None

total, passed, failed = grab('Total Tests:'), grab('Passed:'), grab('Failed:')
row = dict(utc=utc(), label=LABEL, flag_value=FLAG, cwd=str(R),
           flag_in_env='PS2X_SKIP_MOVIE' in env,
           binary=str(binary), binary_sha256=sha(binary), binary_bytes=binary.stat().st_size,
           rc=p.returncode, elapsed_s=el, stdout_bytes=len(out.encode()),
           total=total, passed=passed, failed=failed,
           tail=out.splitlines()[-8:])
green = (p.returncode == 0 and failed == 'Failed: 0' and total == 'Total Tests: 458')
row['green'] = green
save(f'suite-{LABEL}.json', row)
print(json.dumps({k: v for k, v in row.items() if k != 'tail'}, indent=2))
print('\n'.join(row['tail']))
print('# E29 SUITE TAIL COMPLETE label=%s green=%s' % (LABEL, '1' if green else '0'))
