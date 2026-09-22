"""E29 Mission 2 step 3 -- configure the DEV-ONLY bypass build into the NEW SSD dir.

The cmake argv is LOADED from E18's committed `configure-command.json` and
asserted equal to a literal transcription, exactly as E25 did. The ONE value
E29 changes is `-B`: the bypass build goes to a NEW dir on the SSD, because the
internal volume cannot hold a second tree and the brief forbids a /tmp build.
Every other flag is byte-equal to E18's and E25's, so the only difference
between this binary and the mainline one is the 46-line bypass diff.
"""
import subprocess, time
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'

pinned = json.loads((E.parent / 'E18' / 'configure-command.json').read_text())
LITERAL = ['cmake', '-S', str(R), '-B', '/tmp/e18-mpeg-link/runtime', '-G', 'Ninja',
           '-DCMAKE_BUILD_TYPE=Release',
           '-DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang',
           '-DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++',
           '-DCMAKE_OSX_ARCHITECTURES=arm64',
           '-DPS2X_BUILD_STUDIO=OFF', '-DPS2X_BUILD_RUNTIME=ON', '-DPS2X_BUILD_TEST=ON',
           '-DPS2X_ENABLE_RUNTIME_LOGS=ON', '-DPS2X_ENABLE_AGRESSIVE_LOGS=ON',
           '-DPS2X_ENABLE_IOP_RPC_TRACE=ON', '-DPS2X_STRICT_RETURN_DIAGNOSTICS=OFF',
           '-DPS2X_ENABLE_FFMPEG=ON']
assert pinned['argv'] == LITERAL, 'E18 recipe does not match the literal transcription'
assert pinned['jobs'] == 2, pinned

argv = list(pinned['argv'])
bidx = argv.index('-B') + 1
changed_from = argv[bidx]
argv[bidx] = str(NEWB)                      # the ONE declared difference
assert argv[argv.index('-S') + 1] == str(R), 'must -S the fork worktree'
assert NEWB.exists(), 'reconfigure: build dir must exist'

s0 = sample(); admission(s0)
t0 = time.time()
p = subprocess.run(argv, text=True, capture_output=True, cwd=str(W))
el = round(time.time() - t0, 1)
(E / 'configure-2.log').write_text(p.stdout + ('\n--- stderr ---\n' + p.stderr if p.stderr else ''))
s1 = sample()

row = dict(utc=utc(), argv=argv, recipe_source='E18/configure-command.json (asserted == literal)',
           only_difference=dict(flag='-B', e18=changed_from, e29=str(NEWB),
                                why='internal cannot hold two trees; brief forbids a /tmp build'),
           rc=p.returncode, elapsed_s=el, stdout_bytes=len(p.stdout.encode()),
           stderr_bytes=len(p.stderr.encode()), jobs=pinned['jobs'],
           sample_before=s0, sample_after=s1, bound_after=bound(s1))
save('configure-2.json', row)
print(json.dumps({k: v for k, v in row.items() if k not in ('sample_before', 'sample_after')}, indent=2))
print('# E29 CONFIGURE TAIL COMPLETE rc=%d' % p.returncode)
assert p.returncode == 0, p.stderr[-2000:]
