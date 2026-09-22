"""E25 open: toolchain identity vs the E18 recipe, fork allocation baseline,
first admission. Read-only apart from its own receipts."""
import subprocess
from e25_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'

def cap(argv):
    argv = [str(x) for x in argv]
    try:
        p = subprocess.run(argv, text=True, capture_output=True)
    except FileNotFoundError as exc:
        # Record the absence; never let a missing optional probe stop the audit.
        return dict(argv=argv, rc=None, stdout='', stderr=str(exc), present=False)
    return dict(argv=argv, rc=p.returncode, stdout=p.stdout.strip(),
                stderr=p.stderr.strip(), present=True)

# E18's recorded toolchain, from its own configure log and P1's REPORT.
EXPECTED = dict(
    c_compiler_id='Clang 23.1.1', cxx_compiler_id='Clang 23.1.1',
    cmake='cmake version 4.4.3', pkg_config='3.0.7',
    libavcodec='63.1.101', libavformat='63.1.101', libavutil='61.1.101',
    libswresample='7.1.101', libswscale='10.1.101',
    c_compiler_path='/opt/homebrew/opt/llvm/bin/clang',
    cxx_compiler_path='/opt/homebrew/opt/llvm/bin/clang++')

actual = dict(
    clang=cap(['/opt/homebrew/opt/llvm/bin/clang', '--version']),
    clangxx=cap(['/opt/homebrew/opt/llvm/bin/clang++', '--version']),
    cmake=cap(['cmake', '--version']),
    ninja=cap(['ninja', '--version']),
    pkg_config=cap(['pkg-config', '--version']),
    ld_lld=cap(['/opt/homebrew/opt/llvm/bin/lld', '-flavor', 'darwin', '--version']),
    ld_system=cap(['ld', '-v']),
    xcode=cap(['xcodebuild', '-version']),
    uname=cap(['uname', '-a']),
)
for m in ('libavcodec', 'libavformat', 'libavutil', 'libswresample', 'libswscale'):
    actual[m] = cap(['pkg-config', '--modversion', m])

def ver(row):
    return row['stdout'].splitlines()[0] if row['stdout'] else ''

compare = dict(
    clang_version=('Homebrew clang version 23.1.1' in actual['clang']['stdout'],
                   ver(actual['clang'])),
    clangxx_version=('Homebrew clang version 23.1.1' in actual['clangxx']['stdout'],
                     ver(actual['clangxx'])),
    cmake_version=(ver(actual['cmake']) == EXPECTED['cmake'], ver(actual['cmake'])),
    pkg_config_version=(ver(actual['pkg_config']) == EXPECTED['pkg_config'],
                        ver(actual['pkg_config'])),
)
for m in ('libavcodec', 'libavformat', 'libavutil', 'libswresample', 'libswscale'):
    compare[m] = (ver(actual[m]) == EXPECTED[m], ver(actual[m]))
compare['c_compiler_path_exists'] = (Path(EXPECTED['c_compiler_path']).exists(), EXPECTED['c_compiler_path'])
compare['cxx_compiler_path_exists'] = (Path(EXPECTED['cxx_compiler_path']).exists(), EXPECTED['cxx_compiler_path'])
drift = [k for k, v in compare.items() if not v[0]]

save('toolchain-audit.json', dict(utc=utc(), expected_source=(
    'E18 configure.log (compiler ids, pkg-config, ffmpeg module versions) + '
    'P1/REPORT.md (cmake version); ninja version was not recorded by any prior lane'),
    expected=EXPECTED, actual=actual,
    comparison={k: dict(match=v[0], actual=v[1]) for k, v in compare.items()},
    drift=drift, drift_free=not drift,
    ninja_version_unrecorded_upstream=ver(actual['ninja'])))

# --- fork allocation baseline for the storage ledger ---------------------
allocated = {}
for root in [R/'.git', R/'ps2xRuntime/src/lib/Kernel/Stubs', R/'ps2xTest/src']:
    for p in [root, *root.rglob('*')]:
        try: allocated[str(p)] = p.lstat().st_blocks*512
        except FileNotFoundError: pass
save('fork-allocation-before.json', dict(utc=utc(), allocated=allocated))

s = sample()
admission(s)
save('admission-open.json', dict(utc=utc(), reservation_internal=IRES,
                                 reservation_ssd=16*G, floor=2*G, guard=512*M,
                                 sample=s, bound=bound(s)))
print(json.dumps({k: dict(match=v[0], actual=v[1]) for k, v in compare.items()}, indent=2))
print('DRIFT:', drift or 'none')
print('ninja (unrecorded upstream):', ver(actual['ninja']))
print('ADMISSION internal_free', s['internal_free'], 'ssd_free', s['ssd_free'])
print('# E25 OPEN TAIL COMPLETE')
