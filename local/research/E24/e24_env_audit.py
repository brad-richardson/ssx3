"""E24 environment audit: what the host restart took, named against E23's own
protected-build manifest. Read-only. Asserts nothing; it RECORDS the gate."""
import subprocess
from collections import Counter
from e24_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
PRIOR = E.parent / 'E23'

manifest = json.loads((PRIOR / 'protected-build-before.json').read_text())
present, missing = [], []
by_tree_missing, by_tree_bytes = Counter(), Counter()
for row in manifest:
    p = Path(row['path'])
    tree = '/'.join(p.parts[:3])
    if p.exists():
        present.append(dict(path=row['path'], sha_equal=sha(p) == row['sha256']))
    else:
        missing.append(row['path'])
        by_tree_missing[tree] += 1
        by_tree_bytes[tree] += row['bytes']

final = json.loads((PRIOR / 'final-audit.json').read_text())
key_binaries = {}
for key in ('runner', 'suite', 'fixture', 'cadence_fixture'):
    row = final[key]
    p = Path(row['path'])
    entry = dict(path=row['path'], expected_bytes=row['bytes'], expected_sha=row['sha256'],
                 present=p.exists())
    if p.exists():
        entry.update(actual_bytes=p.stat().st_size, actual_sha=sha(p))
        entry['sha_equal'] = entry['actual_sha'] == row['sha256']
    key_binaries[key] = entry

# The instrument the brief requires be REUSED by copy + re-sha, never rebuilt.
proven = json.loads((E.parent / 'E21/parser-build.json').read_text())['observer']
dylib_src = PRIOR / 'parser/e21-parser-observer.dylib'
instrument = dict(source=str(dylib_src), present=dylib_src.exists(),
                  expected_sha=proven['sha256'], expected_bytes=proven.get('bytes'))
if dylib_src.exists():
    instrument.update(actual_bytes=dylib_src.stat().st_size, actual_sha=sha(dylib_src))
    instrument['sha_equal'] = instrument['actual_sha'] == proven['sha256']

# Retained title artifacts from the e23a boot -- these live on the SSD and are
# the reference this lane mines where the boot cannot run.
RUN = P / 'run'
retained = {name: pin_or_missing(RUN / name) for name in
            ('boot-e23a-1.log', 'syscalls-e23a-on.txt', 'park-e23a-1/park-snapshot.json',
             'park-e23a-1/park-snapshot.txt', 'e23a-join/e7-events.txt', 'e23a-parser/parser-events.txt',
             'e23a-parser/parser-input.bin')}
retained['E23 observed/parser-input.bin'] = pin_or_missing(PRIOR / 'observed/parser-input.bin')
retained['E23 observed/parser-events.txt'] = pin_or_missing(PRIOR / 'observed/parser-events.txt')

def command(args):
    p = subprocess.run(args, text=True, capture_output=True)
    return dict(argv=[str(x) for x in args], rc=p.returncode, stdout=p.stdout, stderr=p.stderr)

tmp_state = command(['ls', '-la', '/tmp'])
snapshots = command(['tmutil', 'listlocalsnapshots', '/'])
lease = Path('/tmp/ssx3-p-lane-lease')

out = dict(
    utc=utc(),
    trigger='host restart between E23 close (2026-09-22T00:23:30Z) and E24 open (2026-09-22T11:31:22Z)',
    protected_build_trees=[dict(path=str(b), present=b.exists()) for b in PROTECTED_BUILDS],
    protected_files_manifest=len(manifest),
    protected_files_present=len(present),
    protected_files_missing=len(missing),
    protected_missing_by_tree={k: dict(files=v, bytes=by_tree_bytes[k]) for k, v in by_tree_missing.items()},
    protected_missing_bytes=sum(by_tree_bytes.values()),
    key_binaries=key_binaries,
    instrument=instrument,
    retained_title_artifacts=retained,
    derived_data_project_dirs=[p.name for p in Path.home().joinpath(
        'Library/Developer/Xcode/DerivedData').glob('*')
        if not p.name.startswith(('CMAKE_TRY_COMPILE', 'CompilerId', 'CompilationCache'))],
    local_snapshots=snapshots,
    tmp_listing_rc=tmp_state['rc'],
    tmp_entries=sorted(x.split()[-1] for x in tmp_state['stdout'].splitlines()[1:] if x.split()),
    lease_present=lease.exists(),
    runner_processes=command(['pgrep', '-x', 'ps2EntryRunner']),
    resources=sample(),
)
save('env-audit.json', out)
print(json.dumps({k: v for k, v in out.items()
                  if k not in ('retained_title_artifacts', 'tmp_entries', 'key_binaries', 'resources')}, indent=2))
print('KEY BINARIES:', json.dumps({k: dict(present=v['present'], sha_equal=v.get('sha_equal'))
                                   for k, v in key_binaries.items()}))
print('RETAINED:', json.dumps({k: v.get('present') for k, v in retained.items()}))
print('# E24 ENV AUDIT TAIL COMPLETE')
